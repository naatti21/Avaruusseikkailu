extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var model := load("res://design-review/c07-v4/c07_a_v4.glb") as PackedScene
	var scene := load("res://scenes/c07_a4_android_benchmark.tscn") as PackedScene
	if model == null or scene == null:
		printerr("FAIL: C-07 A4 model or isolated benchmark scene missing")
		quit(1)
		return
	var stage = scene.instantiate()
	root.add_child(stage)
	await process_frame
	stage.set_process(false)
	var ok: bool = stage.ship != null and stage.camera != null and stage.camera.current
	ok = ok and stage.ship.scale == Vector3.ONE and stage.ship.name.begins_with("UNAPPROVED")
	ok = ok and stage.lighting_index == 0 and not stage.fill.visible
	for index in [0,1,2,3]:
		stage.set_view(index)
		ok = ok and stage.view_index == index
		ok = ok and stage.camera.position.is_finite()
		ok = ok and stage.camera.projection == Camera3D.PROJECTION_PERSPECTIVE
	stage.set_lighting(1)
	ok = ok and stage.lighting_index == 1 and stage.fill.visible and stage.rim.visible
	ok = ok and absf(stage.env_node.environment.ambient_light_energy-1.0)<0.001
	ok = ok and stage.env_node.environment.reflected_light_source == Environment.REFLECTION_SOURCE_SKY
	stage.set_lighting(2)
	ok = ok and stage.lighting_index == 2 and stage.fill.visible and not stage.rim.visible
	ok = ok and absf(stage.env_node.environment.ambient_light_energy-1.2)<0.001
	ok = ok and stage.env_node.environment.reflected_light_source == Environment.REFLECTION_SOURCE_BG
	stage.set_lighting(3)
	ok = ok and stage.lighting_index == 3 and stage.fill.visible and stage.rim.visible
	ok = ok and stage.engine_bounce.visible
	ok = ok and stage.sun.light_energy > 4.0
	stage.set_lighting(4)
	ok = ok and stage.lighting_index == 0 and not stage.fill.visible and not stage.rim.visible
	ok = ok and not stage.engine_bounce.visible
	ok = ok and absf(stage.sun.light_energy-2.0)<0.001
	ok = ok and absf(stage.env_node.environment.ambient_light_energy-0.85)<0.001
	stage.reset_metrics()
	ok = ok and stage.samples_ms.is_empty() and stage.measured_seconds == 0
	stage.queue_free()
	await process_frame
	if ok:
		print("PASS: same A4 GLB, unit scale, 4 views, 4 lighting modes, no production selection")
		quit(0)
	else:
		printerr("FAIL: C-07 A4 Android benchmark guardrails")
		quit(1)
