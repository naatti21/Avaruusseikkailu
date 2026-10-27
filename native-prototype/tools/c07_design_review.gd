extends SceneTree
## Isolated v3 choice sheet. The production model and main scene are never replaced.
const MODELS := {"baseline":"res://production/models/c07_courier.glb", "A":"res://design-review/c07-v3/c07_option_a.glb", "B":"res://design-review/c07-v3/c07_option_b.glb"}
var failed := false
func _initialize() -> void: call_deferred("_run")
func check(ok: bool, message: String) -> void:
	print(("PASS: " if ok else "FAIL: ") + message)
	if not ok: failed = true
func _run() -> void:
	var option := OS.get_environment("C07_DESIGN")
	check(option in MODELS,"explicit valid design selection")
	if not option in MODELS:
		quit(1)
		return
	var capture := "--capture" in OS.get_cmdline_user_args()
	var game := "--game-lighting" in OS.get_cmdline_user_args()
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root.content_scale_aspect = Window.CONTENT_SCALE_ASPECT_IGNORE
	root.content_scale_size = Vector2i.ZERO
	root.size = Vector2i(1440,1000)
	root.msaa_3d = Viewport.MSAA_4X
	var stage = load("res://scenes/production_art_preview.tscn").instantiate()
	root.add_child(stage)
	await process_frame
	stage.set_process(false)
	stage.remove_child(stage.model)
	stage.model.free()
	stage.model = load(MODELS[option]).instantiate()
	stage.add_child(stage.model)
	for child in stage.get_children():
		if child is CanvasLayer: child.hide()
	var meshes: Array[MeshInstance3D] = []
	stage._collect_meshes(stage.model,meshes)
	var lo := Vector3(INF,INF,INF)
	var hi := Vector3(-INF,-INF,-INF)
	var cockpit_lo := lo
	var cockpit_hi := hi
	var engine_left_lo := lo
	var engine_left_hi := hi
	var engine_right_lo := lo
	var engine_right_hi := hi
	var triangles := 0
	var surfaces := 0
	var materials := {}
	for instance in meshes:
		check(instance.global_transform.basis.get_scale().is_equal_approx(Vector3.ONE), "unit-scale " + instance.name)
		for s in range(instance.mesh.get_surface_count()):
			surfaces += 1
			var arrays := instance.mesh.surface_get_arrays(s)
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
			triangles += indices.size()/3 if indices.size() else vertices.size()/3
			check(arrays[Mesh.ARRAY_NORMAL].size() == vertices.size(), "vertex normals " + instance.name)
			var material := instance.mesh.surface_get_material(s) as StandardMaterial3D
			check(material != null, "real material " + instance.name)
			if material: materials[material.get_instance_id()] = true
			for v in vertices:
				var p: Vector3 = instance.global_transform * v
				lo = lo.min(p)
				hi = hi.max(p)
				if "cockpit" in instance.name:
					cockpit_lo = cockpit_lo.min(p)
					cockpit_hi = cockpit_hi.max(p)
				if "propulsion" in instance.name:
					if p.x < 0:
						engine_left_lo = engine_left_lo.min(p)
						engine_left_hi = engine_left_hi.max(p)
					else:
						engine_right_lo = engine_right_lo.min(p)
						engine_right_hi = engine_right_hi.max(p)
	var size := hi-lo
	check(absf(size.z-30)<.75 and absf(size.x-12)<.75 and absf(size.y-8)<.75, "metre dimensions near 30 x 12 x 8: " + str(size))
	check(triangles <= 100000 and surfaces <= 32 and materials.size() <= 8, "study geometry/material budget")
	var cockpit_center := (cockpit_lo+cockpit_hi)/2
	var engine_offset := 0.0
	if option != "baseline":
		engine_offset = absf((engine_left_lo.z+engine_left_hi.z-engine_right_lo.z-engine_right_hi.z)/2)
		if option == "A":
			check(absf(cockpit_center.x)<.1 and engine_offset<.1,"A central cockpit and paired aft drives")
		else:
			check(cockpit_center.x < -1.5 and engine_offset>2.0,"B offset cockpit and staggered propulsion")
	var camera: Camera3D = stage.camera
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.keep_aspect = Camera3D.KEEP_WIDTH
	# Exactly the review baseline's studio lighting, or the actual native game builder.
	if game:
		for child in stage.get_children():
			if child is WorldEnvironment or child is Light3D:
				stage.remove_child(child)
				child.free()
		var owner = load("res://scripts/main.gd").new()
		owner._build_lights()
		var count := 0
		for child in owner.get_children():
			owner.remove_child(child)
			stage.add_child(child)
			if child is Light3D: count += 1
		owner.free()
		check(count==1,"actual game light builder, no studio fill")
	else:
		for child in stage.get_children():
			if child is WorldEnvironment:
				var env: Environment = child.environment
				env.ambient_light_color = Color(.78,.81,.85)
				env.ambient_light_energy = .75
				var sky := Sky.new()
				var sm := ProceduralSkyMaterial.new()
				sm.sky_top_color = Color(.36,.40,.46)
				sm.sky_horizon_color = Color(.64,.66,.68)
				sm.ground_bottom_color = Color(.12,.13,.15)
				sm.ground_horizon_color = Color(.48,.5,.52)
				sky.sky_material = sm
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
	var views := {"front":Vector3(0,0,1),"side":Vector3(1,0,0),"top":Vector3(0,1,.001),"rear":Vector3(0,0,-1),"three-quarter":Vector3(1,.65,1.25),"rear-quarter":Vector3(-1,.55,-1.25)}
	if game: views = {"three-quarter":views["three-quarter"],"rear-quarter":views["rear-quarter"]}
	var metrics := {"option":option,"model_sha256":FileAccess.get_sha256(MODELS[option]),"renderer":RenderingServer.get_current_rendering_method(),"lighting":"main.gd::_build_lights" if game else "studio","dimensions_xyz_m":[size.x,size.y,size.z],"cockpit_center_x_m":cockpit_center.x,"engine_stagger_m":engine_offset if option != "baseline" else null,"triangles":triangles,"surfaces":surfaces,"materials":materials.size(),"views":{},"selected":false,"android_tested":false}
	var output := OS.get_environment("C07_CAPTURE_DIR")
	if capture:
		check(not output.is_empty(),"explicit capture destination")
		if output.is_empty():
			quit(1)
			return
		DirAccess.make_dir_recursive_absolute(output)
	for name in views:
		# Fixed common box, not per-model magnification: direct scale-faithful comparison.
		camera.position = views[name].normalized()*70
		camera.look_at(Vector3.ZERO)
		var plo := Vector2(INF,INF)
		var phi := Vector2(-INF,-INF)
		for x in [-6.5,6.5]:
			for y in [-4.5,4.5]:
				for z in [-15.5,15.5]:
					var q: Vector3 = camera.global_transform.affine_inverse()*Vector3(x,y,z)
					plo = plo.min(Vector2(q.x,q.y))
					phi = phi.max(Vector2(q.x,q.y))
		var ext := phi-plo
		camera.size = maxf(ext.x,ext.y*1.44)*1.12
		for x in [lo.x,hi.x]:
			for y in [lo.y,hi.y]:
				for z in [lo.z,hi.z]:
					var p := Vector3(x,y,z)
					if camera.is_position_behind(p) or not Rect2(Vector2(20,20),Vector2(root.size)-Vector2(40,40)).has_point(camera.unproject_position(p)):
						check(false,"model fits " + name)
		if capture:
			await process_frame
			await RenderingServer.frame_post_draw
			var img := root.get_texture().get_image()
			check(img.get_size()==Vector2i(1440,1000),"full-resolution " + name)
			check(img.save_png(output.path_join(name+".png"))==OK,"actual viewport " + name)
			metrics.views[name]={"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),"primitives":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)}
	if capture:
		var f := FileAccess.open(output.path_join("metrics.json"),FileAccess.WRITE)
		f.store_string(JSON.stringify(metrics,"\t")+"\n")
	stage.queue_free()
	await process_frame
	quit(1 if failed else 0)
