extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func bounds(node: Node3D) -> AABB:
	var result := AABB()
	var started := false
	for mesh in meshes(node):
		for vertex in mesh.mesh.get_faces():
			var p: Vector3 = mesh.global_transform * vertex
			if not started:
				result = AABB(p,Vector3.ZERO)
				started = true
			else:
				result = result.expand(p)
	return result
func meshes(node: Node) -> Array[MeshInstance3D]:
	var found: Array[MeshInstance3D] = []
	if node is MeshInstance3D:
		found.append(node)
	for child in node.get_children():
		found.append_array(meshes(child))
	return found
func throat_hit(node: Node3D) -> float:
	var closest := -INF
	for mesh in meshes(node):
		var faces: PackedVector3Array = mesh.mesh.get_faces()
		for i in range(0,faces.size(),3):
			var hit = Geometry3D.ray_intersects_triangle(Vector3(0,0,800),Vector3(0,0,-1),mesh.global_transform*faces[i],mesh.global_transform*faces[i+1],mesh.global_transform*faces[i+2])
			if hit != null:
				closest = maxf(closest,hit.z)
	return closest
func _run() -> void:
	var benchmark := load("res://scenes/hero_benchmark.tscn") as PackedScene
	if benchmark == null:
		quit(1)
		return
	var stage = benchmark.instantiate()
	root.add_child(stage)
	await process_frame
	stage.set_process(false)
	var station_box := bounds(stage.station)
	var far_box := bounds(stage.distant_station)
	stage.courier.position = Vector3.ZERO
	var ship_box := bounds(stage.courier)
	var ok: bool = absf(station_box.size.x-6000)<1 and absf(far_box.size.x-6000)<1
	ok = ok and absf(ship_box.size.z-30)<0.5 and ship_box.size.x<76 and ship_box.size.y<48
	ok = ok and stage.STATION_METRES/stage.COURIER_METRES==200.0
	var rear_hit := throat_hit(stage.station)
	ok = ok and rear_hit>=517 and rear_hit<=521 # No disk or hull blocking the real entrance.
	for beat in [0,1,2]:
		stage.set_beat(beat)
		for t in [0.0,0.5,1.0]:
			stage._move_camera(t)
			ok = ok and stage.beat==beat and stage.station.scale==Vector3.ONE
			ok = ok and stage.courier.scale==Vector3.ONE and stage.camera.far>=18000
			ok = ok and stage.camera.projection==Camera3D.PROJECTION_PERSPECTIVE
			ok = ok and stage.camera.position.is_finite()
			var pixel: Vector2 = stage.camera.unproject_position(stage.courier.global_position)
			var viewport_size: Vector2 = stage.camera.get_viewport().get_visible_rect().size
			ok = ok and not stage.camera.is_position_behind(stage.courier.global_position)
			ok = ok and pixel.x>0 and pixel.x<viewport_size.x and pixel.y>100 and pixel.y<viewport_size.y-140
	stage.set_beat(1)
	stage._next()
	ok = ok and stage.beat==2 # Approach skip remains immediately available.
	stage.set_beat(0)
	ok = ok and stage.distant_station.visible and not stage.station.visible
	stage.set_beat(2)
	ok = ok and stage.station.visible and not stage.distant_station.visible
	stage.history.clear()
	stage._process(0.75)
	ok = ok and stage.history.size()==1 and absf(stage.history[0]-750.0)<0.01
	print("Measured imported meshes: station ",station_box.size,"; courier ",ship_box.size,"; throat rear hit z=",rear_hit)
	stage.queue_free()
	await process_frame
	if ok:
		print("PASS: imported dimensions, unit scale, LOD extents, open 200m throat, three camera stages and skip")
		quit(0)
	else:
		printerr("FAIL: hero geometry/camera invariants")
		quit(1)
