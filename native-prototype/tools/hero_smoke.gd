extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var station := load("res://assets/hero_station.glb") as PackedScene
	var courier := load("res://assets/courier_30m.glb") as PackedScene
	var benchmark := load("res://scenes/hero_benchmark.tscn") as PackedScene
	if station==null or courier==null or benchmark==null:
		printerr("FAIL: missing GLB or hero scene")
		quit(1)
		return
	var stage = benchmark.instantiate()
	root.add_child(stage)
	await process_frame
	var ok := stage.station!=null and stage.courier!=null and stage.camera!=null
	ok = ok and stage.STATION_METRES/stage.COURIER_METRES==60.0
	ok = ok and stage.camera.projection==Camera3D.PROJECTION_PERSPECTIVE
	for beat in [0,1,2]:
		stage.set_beat(beat)
		ok = ok and stage.beat==beat and stage.station.scale==Vector3.ONE
		ok = ok and stage.courier.scale==Vector3.ONE and stage.camera.far>=6000
	stage.queue_free()
	await process_frame
	if ok:
		print("PASS: GLB imports, stationary 1800m station, 30m courier, 3 camera beats")
		quit(0)
	else:
		printerr("FAIL: hero-benchmark invariants")
		quit(1)
