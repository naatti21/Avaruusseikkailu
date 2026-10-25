extends SceneTree
func _initialize() -> void:
	call_deferred("capture")
func capture() -> void:
	var stage = (load("res://scenes/hero_benchmark.tscn") as PackedScene).instantiate()
	root.add_child(stage)
	await process_frame
	stage.set_process(false)
	var args := OS.get_cmdline_user_args()
	var output := args[0] if not args.is_empty() else "/tmp/hero-evidence"
	DirAccess.make_dir_recursive_absolute(output)
	for beat in [0,1,2]:
		stage.set_beat(beat)
		stage._move_camera(1.0 if beat==2 else 0.5)
		for frame in range(6):
			await process_frame
		stage.overlay.text = "DESKTOP SOFTWARE PREVIEW — NOT ANDROID FPS\nSame metre-scale assets; device acceptance pending"
		await process_frame
		await RenderingServer.frame_post_draw
		var image := root.get_texture().get_image()
		var error := image.save_png(output+"/beat-"+str(beat)+".png")
		assert(error==OK)
		print("CAPTURE ",beat," objects=",Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)," draws=",Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)," primitives=",Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME))
	# Supplemental asset inspection, not a fourth cinematic gameplay stage.
	stage.courier.position = Vector3(0,0,1000)
	stage.camera.position = stage.courier.position+Vector3(26,16,-40)
	stage.camera.look_at(stage.courier.position)
	stage.station.visible = false
	stage.distant_station.visible = false
	stage.windows.visible = false
	for tug in stage.traffic:
		tug.visible = false
	stage.caption_label.text = "QA / COURIER · 30.12 m"
	for frame in range(6):
		await process_frame
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(output+"/courier-detail.png")==OK)
	quit()
