extends SceneTree
func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var scene := load("res://scenes/production_art_preview.tscn") as PackedScene
	if scene == null:
		printerr("FAIL: production art preview scene missing")
		quit(1)
		return
	var stage = scene.instantiate()
	root.add_child(stage)
	await process_frame
	var ok: bool = stage.camera != null and stage.camera.current
	for index in [0, 1, 2]:
		stage.select_slot(index)
		ok = ok and stage.slot == index
		ok = ok and stage.visual_state in ["awaiting_artist", "candidate_not_approved"]
		ok = ok and stage.view_distance > 0.0
		ok = ok and stage.camera.position.is_finite()
	stage.queue_free()
	await process_frame
	if ok:
		print("PASS: isolated art scene, three deterministic import slots, no false visual approval")
		quit(0)
	else:
		printerr("FAIL: production art scene/intake state")
		quit(1)
