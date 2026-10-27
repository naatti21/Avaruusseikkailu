extends SceneTree
## Automated Linux desktop Godot/GL screenshots. Not an Android emulator.
const SCENE := "res://scenes/c07_a4_android_benchmark.tscn"
const MODEL := "res://design-review/c07-v4/c07_a_v4.glb"
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var out := OS.get_environment("C07_CAPTURE_DIR")
	if out.is_empty():
		printerr("FAIL: destination missing")
		quit(1)
		return
	var packed := load(SCENE) as PackedScene
	if packed == null:
		printerr("FAIL: no benchmark scene")
		quit(1)
		return
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root.content_scale_aspect = Window.CONTENT_SCALE_ASPECT_IGNORE
	root.content_scale_size = Vector2i.ZERO
	root.size = Vector2i(1440,1000)
	root.msaa_3d = Viewport.MSAA_4X
	var stage = packed.instantiate()
	root.add_child(stage)
	await process_frame
	stage.set_process(false)
	stage.orbiting = false
	for child in stage.get_children():
		if child is CanvasLayer:
			child.hide()
	if DirAccess.make_dir_recursive_absolute(out) != OK:
		printerr("FAIL: destination cannot be created")
		quit(1)
		return
	if stage.ship.scale != Vector3.ONE or not stage.ship.name.begins_with("UNAPPROVED"):
		printerr("FAIL: art candidate was changed")
		quit(1)
		return
	var modes := ["game","balanced","inspection","hero"]
	var record := {
		"model_sha256":FileAccess.get_sha256(MODEL),
		"scene":SCENE,
		"renderer":RenderingServer.get_current_rendering_method(),
		"capture_platform":"Linux Godot GL Compatibility desktop; NOT Android",
		"visual_approval":false,
		"views":[]
	}
	var failed := false
	for mode in range(4):
		stage.set_lighting(mode)
		for angle in [0,2]:
			stage.set_view(angle)
			stage.orbiting = false
			for i in range(3):
				await process_frame
			await RenderingServer.frame_post_draw
			var name: String = str(modes[mode]) + ("-front.png" if angle==0 else "-rear.png")
			var image := root.get_texture().get_image()
			if image.get_size() != Vector2i(1440,1000) or image.save_png(out.path_join(name)) != OK:
				failed = true
				printerr("FAIL image: ",name)
			else:
				print("CAPTURE PASS: ",name)
				record["views"].append(name)
	var f := FileAccess.open(out.path_join("capture-manifest.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify(record,"\t")+"\n")
	f.close()
	stage.queue_free()
	await process_frame
	quit(1 if failed or record["views"].size()!=8 else 0)
