extends Node3D
## Renderer comparison: fixed 1 Godot unit == 1 metre. No scaling tricks.
const STATION_METRES := 1800.0
const COURIER_METRES := 30.0
const CLIP_SECONDS := 5.0
var camera: Camera3D
var station: Node3D
var courier: Node3D
var overlay: Label
var caption_label: Label
var next_button: Button
var beat := 0
var elapsed := 0.0
var history: Array[float] = []
var total_time := 0.0
var frame_count := 0
var overlay_elapsed := 0.0

func _ready() -> void:
	_build_scene()
	_build_ui()
	set_beat(0)

func _build_scene() -> void:
	var env_node := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.004,0.01,0.023)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(.32,.46,.6)
	env.ambient_light_energy = .62
	env_node.environment = env
	add_child(env_node)
	var sunlight := DirectionalLight3D.new()
	sunlight.rotation_degrees = Vector3(-44,32,15)
	sunlight.light_color = Color(.85,.91,1)
	sunlight.light_energy = 2.0
	sunlight.shadow_enabled = false
	add_child(sunlight)
	var station_resource := load("res://assets/hero_station.glb") as PackedScene
	var ship_resource := load("res://assets/courier_30m.glb") as PackedScene
	assert(station_resource != null, "Blender station GLB missing")
	assert(ship_resource != null, "Blender courier GLB missing")
	station = station_resource.instantiate() as Node3D
	courier = ship_resource.instantiate() as Node3D
	station.name = "Station1800m"
	courier.name = "Courier30m"
	add_child(station)
	add_child(courier)
	station.scale = Vector3.ONE
	courier.scale = Vector3.ONE
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_PERSPECTIVE
	camera.fov = 63
	camera.near = .3
	camera.far = 6500
	add_child(camera)
	camera.current = true
	_build_stars()

func _build_stars() -> void:
	var star := SphereMesh.new()
	star.radius = 2.4
	star.height = 4.8
	star.radial_segments = 6
	star.rings = 4
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = Color(.65,.81,1)
	star.material = m
	var multi := MultiMesh.new()
	multi.transform_format = MultiMesh.TRANSFORM_3D
	multi.mesh = star
	multi.instance_count = 280
	var rng := RandomNumberGenerator.new()
	rng.seed = 31177
	for i in range(multi.instance_count):
		var point := Vector3(rng.randf_range(-1,1),rng.randf_range(-1,1),
			rng.randf_range(-1,1)).normalized() * rng.randf_range(4200,6000)
		multi.set_instance_transform(i,Transform3D(Basis.IDENTITY,point))
	var inst := MultiMeshInstance3D.new()
	inst.multimesh = multi
	add_child(inst)

func _label(txt: String, size: int) -> Label:
	var l := Label.new()
	l.text = txt
	l.add_theme_font_size_override("font_size",size)
	l.add_theme_color_override("font_color",Color(.88,.96,1))
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return l

func _build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var canvas := Control.new()
	canvas.set_anchors_preset(Control.PRESET_FULL_RECT)
	canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(canvas)
	var header := VBoxContainer.new()
	header.anchor_left = .03
	header.anchor_right = .97
	header.offset_top = 24
	header.add_theme_constant_override("separation",8)
	canvas.add_child(header)
	caption_label = _label("",25)
	overlay = _label("Loading GLB assets...",19)
	header.add_child(caption_label)
	header.add_child(overlay)
	next_button = Button.new()
	next_button.anchor_left = .03
	next_button.anchor_right = .97
	next_button.anchor_top = 1
	next_button.anchor_bottom = 1
	next_button.offset_top = -134
	next_button.offset_bottom = -26
	next_button.add_theme_font_size_override("font_size",24)
	next_button.pressed.connect(_next)
	canvas.add_child(next_button)

func _next() -> void:
	set_beat((beat+1)%3)

func set_beat(next_beat: int) -> void:
	beat = clampi(next_beat,0,2)
	elapsed = 0.0
	if beat == 0:
		caption_label.text = "01 / PALJASTUMINEN · 1 800 m"
		next_button.text = "LÄHESTYMINEN"
	elif beat == 1:
		caption_label.text = "02 / LÄHESTYMINEN · 5 sek"
		next_button.text = "TELAKOINTIAUKKO"
	else:
		caption_label.text = "03 / TELAKOINTIAUKKO"
		next_button.text = "ALUSTA"
	_move_camera(0.0)

func _move_camera(t: float) -> void:
	var start: Vector3
	var finish: Vector3
	var target: Vector3
	if beat == 0:
		start = Vector3(90,250,3280)
		finish = start
		target = Vector3(0,0,-75)
		courier.position = Vector3(38,-80,2600)
	elif beat == 1:
		start = Vector3(145,160,2480)
		finish = Vector3(190,90,980)
		target = Vector3(0,0,0)
		courier.position = Vector3(25,-70,lerpf(2080,570,t))
	else:
		start = Vector3(105,64,520)
		finish = Vector3(72,35,366)
		target = Vector3(0,0,280)
		courier.position = Vector3(14,-15,lerpf(411,338,t))
	camera.position = start.lerp(finish,t)
	camera.look_at(target)

func _process(delta: float) -> void:
	elapsed = minf(CLIP_SECONDS,elapsed+maxf(delta,0.0))
	_move_camera(elapsed/CLIP_SECONDS)
	if delta>0 and delta<.5:
		history.append(delta*1000)
		if history.size()>600:
			history.pop_front()
		total_time+=delta
		frame_count+=1
	overlay_elapsed+=delta
	if overlay_elapsed<.7:
		return
	overlay_elapsed=0
	var samples := history.duplicate()
	samples.sort()
	var worst_percentile := 0.0
	if not samples.is_empty():
		worst_percentile=samples[min(samples.size()-1,int(samples.size()*.99))]
	var avg := float(frame_count)/maxf(total_time,.001)
	var visible := int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME))
	var renderer := str(ProjectSettings.get_setting("rendering/renderer/rendering_method"))
	overlay.text="%s | %d FPS | avg %.1f | p99 %.1f ms\nObjects %d | ship 30 m : station 1800 m | %d/3" % [
		renderer,Engine.get_frames_per_second(),avg,worst_percentile,visible,beat+1]
