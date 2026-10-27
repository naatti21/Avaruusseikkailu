extends SceneTree
## Uses PR #11's exact imported model slot and scene. No alternate render mesh.
var failed := false
func _initialize() -> void:
	call_deferred("_run")

func check(condition: bool, message: String) -> void:
	if not condition:
		failed = true
		printerr("FAIL: ", message)
	else:
		print("PASS: ", message)

func _run() -> void:
	var capture := "--capture" in OS.get_cmdline_user_args()
	var game_lighting := "--game-lighting" in OS.get_cmdline_user_args()
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root.content_scale_aspect = Window.CONTENT_SCALE_ASPECT_IGNORE
	root.content_scale_size = Vector2i.ZERO
	root.size = Vector2i(1440, 1000)
	root.msaa_3d = Viewport.MSAA_4X
	var stage = load("res://scenes/production_art_preview.tscn").instantiate()
	root.add_child(stage)
	await process_frame
	stage.set_process(false)
	check(stage.visual_state == "candidate_not_approved", "C-07 is a candidate, never approved by import")
	check(stage.model != null, "C-07 imports through the PR11 intake slot")
	if stage.model == null:
		quit(1)
		return
	var meshes: Array[MeshInstance3D] = []
	stage._collect_meshes(stage.model, meshes)
	var lo := Vector3(INF, INF, INF)
	var hi := Vector3(-INF, -INF, -INF)
	var surfaces := 0
	var triangles := 0
	var materials := {}
	for instance in meshes:
		check(instance.global_transform.basis.get_scale().is_equal_approx(Vector3.ONE), "unit-scale imported assembly " + instance.name)
		for s in range(instance.mesh.get_surface_count()):
			surfaces += 1
			var arrays := instance.mesh.surface_get_arrays(s)
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
			var uv: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
			triangles += indices.size() / 3 if indices.size() else vertices.size() / 3
			check(normals.size() == vertices.size() and uv.size() == vertices.size(), "normals and UVs on " + instance.name)
			for vertex in vertices:
				var p: Vector3 = instance.global_transform * vertex
				lo = lo.min(p)
				hi = hi.max(p)
			var material := instance.mesh.surface_get_material(s) as StandardMaterial3D
			check(material != null and material.albedo_texture != null and material.normal_enabled and material.normal_texture != null and material.roughness_texture != null and material.emission_enabled, "embedded PBR maps on " + instance.name)
			if material: materials[material.get_instance_id()] = true
	var size := hi - lo
	check(absf(size.z - 30) < 0.5 and absf(size.x - 12) < 0.5 and absf(size.y - 8) < 0.5, "actual imported vertex dimensions ~30 x 12 x 8 m: " + str(size))
	check(surfaces <= 20 and triangles <= 100000, "runtime geometry budget: %d surfaces / %d triangles" % [surfaces, triangles])
	check(materials.size() <= 2, "shared PBR atlas material")
	# Same mesh, fixed orthographic projections. Inspect shape without perspective tricks.
	var views := {"front":Vector3(0,0,1), "side":Vector3(1,0,0), "top":Vector3(0,1,0.001), "rear":Vector3(0,0,-1), "three-quarter":Vector3(1,.65,1.25), "rear-quarter":Vector3(-1,.55,-1.25)}
	var camera: Camera3D = stage.camera
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 38.0
	camera.keep_aspect = Camera3D.KEEP_WIDTH
	for child in stage.get_children():
		if child is CanvasLayer: child.hide()
	# Neutral lookdev lighting. Shadows are real rasterized mesh shadows.
	for child in stage.get_children():
		if child is WorldEnvironment:
			var env: Environment = child.environment
			env.ambient_light_color = Color(.78,.81,.85)
			env.ambient_light_energy = 0.75
			var sky := Sky.new()
			var sky_material := ProceduralSkyMaterial.new()
			sky_material.sky_top_color = Color(.36,.40,.46)
			sky_material.sky_horizon_color = Color(.64,.66,.68)
			sky_material.ground_bottom_color = Color(.12,.13,.15)
			sky_material.ground_horizon_color = Color(.48,.5,.52)
			sky.sky_material = sky_material
			env.sky = sky
			env.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
		if child is DirectionalLight3D:
			child.rotation_degrees = Vector3(-38,-28,0)
			child.shadow_enabled = true
			child.directional_shadow_max_distance = 110
			child.light_energy = 1.8
	var fill := DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(30,130,0)
	fill.light_color = Color(.62,.73,1)
	fill.light_energy = .65
	stage.add_child(fill)
	if game_lighting:
		# Run the actual native prototype light builder off-tree: no gameplay _ready,
		# storage, ship replacement or copied approximate lighting constants.
		for child in stage.get_children():
			if child is WorldEnvironment or child is Light3D:
				stage.remove_child(child)
				child.free()
		var lighting_owner = load("res://scripts/main.gd").new()
		lighting_owner._build_lights()
		var light_count := 0
		for child in lighting_owner.get_children():
			lighting_owner.remove_child(child)
			stage.add_child(child)
			if child is Light3D: light_count += 1
		lighting_owner.free()
		check(light_count == 1, "actual game lighting without studio fill")
		views = {"three-quarter":views["three-quarter"], "rear-quarter":views["rear-quarter"]}
	var metrics := {"renderer":RenderingServer.get_current_rendering_method(), "dimensions_xyz_m":[size.x,size.y,size.z], "triangles":triangles, "surfaces":surfaces, "materials":materials.size(), "views":{}, "visual_approved":false, "android_tested":false, "lighting":"main.gd::_build_lights" if game_lighting else "studio", "glb_sha256":FileAccess.get_sha256("res://production/models/c07_courier.glb"), "viewport_size":[root.size.x,root.size.y]}
	var output := OS.get_environment("C07_CAPTURE_DIR")
	if capture:
		check(not output.is_empty(), "explicit capture output directory")
		if output.is_empty():
			quit(1)
			return
		DirAccess.make_dir_recursive_absolute(output)
	for key in views:
		camera.position = (lo+hi)/2 + views[key].normalized()*70
		camera.look_at((lo+hi)/2)
		# Fit all bound corners in this projection, including the long top view.
		var projected_lo := Vector2(INF,INF)
		var projected_hi := Vector2(-INF,-INF)
		for x in [lo.x,hi.x]:
			for y in [lo.y,hi.y]:
				for z in [lo.z,hi.z]:
					var q: Vector3 = camera.global_transform.affine_inverse() * Vector3(x,y,z)
					projected_lo = projected_lo.min(Vector2(q.x,q.y))
					projected_hi = projected_hi.max(Vector2(q.x,q.y))
		var extent := projected_hi - projected_lo
		camera.size = maxf(extent.x, extent.y * float(root.size.x)/root.size.y) * 1.18
		# Check every imported bound corner, not merely the model origin.
		for x in [lo.x,hi.x]:
			for y in [lo.y,hi.y]:
				for z in [lo.z,hi.z]:
					var p := Vector3(x,y,z)
					var pixel := camera.unproject_position(p)
					if camera.is_position_behind(p) or not Rect2(Vector2(20,20),Vector2(root.size)-Vector2(40,40)).has_point(pixel):
						check(false,"whole model fits " + key)
		if capture:
			for frame in range(3): await process_frame
			await RenderingServer.frame_post_draw
			var img := root.get_texture().get_image()
			check(img.get_size() == Vector2i(1440,1000), "full resolution review image " + key)
			check(img.save_png(output.path_join(key+".png")) == OK, "Godot viewport saved " + key)
			metrics.views[key] = {"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),"rendered_primitives":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)}
	if capture:
		var file := FileAccess.open(output.path_join("godot-metrics.json"),FileAccess.WRITE)
		file.store_string(JSON.stringify(metrics,"\t")+"\n")
	stage.select_slot(1)
	check(stage.visual_state == "awaiting_artist", "colony remains missing; no fallback")
	stage.select_slot(2)
	check(stage.visual_state == "awaiting_artist", "berth remains missing; no fallback")
	stage.queue_free()
	await process_frame
	quit(1 if failed else 0)
