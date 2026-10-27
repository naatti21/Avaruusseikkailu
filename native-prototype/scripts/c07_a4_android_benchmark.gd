extends Node3D
## Dedicated Android lookdev. Candidate C-07 A4 is NOT approved for gameplay.
const MODEL := "res://design-review/c07-v4/c07_a_v4.glb"
var ship: Node3D
var camera: Camera3D
var env_node: WorldEnvironment
var sun: DirectionalLight3D
var fill: DirectionalLight3D
var rim: DirectionalLight3D
var title_label: Label
var metrics_label: Label
var view_button: Button
var lighting_button: Button
var orbit_button: Button
var view_index := 0
var lighting_index := 0
var orbiting := false
var orbit_angle := 0.0
var measured_seconds := 0.0
var refresh_seconds := 0.0
var samples_ms: Array[float] = []

func _ready() -> void:
	_world()
	_model()
	_camera()
	_ui()
	set_view(0)
	set_lighting(0)

func _world() -> void:
	env_node = WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.006,0.012,0.029)
	# In the balanced mode, the procedural sky is REFLECTION lighting only.
	# Keep the background dark: no bright painted space backdrop.
	var reflection_sky := Sky.new()
	var sky_material := ProceduralSkyMaterial.new()
	sky_material.sky_top_color = Color(0.20,0.27,0.35)
	sky_material.sky_horizon_color = Color(0.48,0.53,0.58)
	sky_material.ground_bottom_color = Color(0.07,0.10,0.14)
	sky_material.ground_horizon_color = Color(0.31,0.38,0.44)
	reflection_sky.sky_material = sky_material
	e.sky = reflection_sky
	e.reflected_light_source = Environment.REFLECTION_SOURCE_BG
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.36,0.49,0.62)
	e.ambient_light_energy = 0.85
	env_node.environment = e
	add_child(env_node)
	sun = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-45.0,30.0,0.0)
	sun.light_color = Color(0.78,0.86,1.0)
	sun.light_energy = 2.0
	add_child(sun)
	fill = DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(28,-128,0)
	fill.light_color = Color(0.63,0.77,0.91)
	fill.light_energy = 0.8
	fill.visible = false
	add_child(fill)
	# Separately controllable cool rim to reveal engine silhouette without
	# lifting the entire shadow side into a flat grey.
	rim = DirectionalLight3D.new()
	rim.rotation_degrees = Vector3(-12.0,165.0,0.0)
	rim.light_color = Color(0.45,0.66,0.90)
	rim.light_energy = 0.75
	rim.visible = false
	add_child(rim)

func _model() -> void:
	var packed := load(MODEL) as PackedScene
	assert(packed != null,"C-07 A4 model missing")
	ship = packed.instantiate() as Node3D
	assert(ship != null,"C-07 A4 should be Node3D")
	ship.name = "UNAPPROVED_C07_A4"
	add_child(ship)
	ship.scale = Vector3.ONE

func _camera() -> void:
	camera = Camera3D.new()
	camera.current = true
	camera.projection = Camera3D.PROJECTION_PERSPECTIVE
	camera.fov = 55.0
	camera.near = 0.1
	camera.far = 800.0
	add_child(camera)

func _label(font_size: int) -> Label:
	var l := Label.new()
	l.add_theme_font_size_override("font_size",font_size)
	l.add_theme_color_override("font_color",Color(0.90,0.95,1.0))
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return l

func _button(value: String) -> Button:
	var b := Button.new()
	b.text = value
	b.custom_minimum_size = Vector2(0,85)
	b.add_theme_font_size_override("font_size",18)
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return b

func _ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var root_control := Control.new()
	root_control.set_anchors_preset(Control.PRESET_FULL_RECT)
	root_control.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(root_control)
	var top := VBoxContainer.new()
	top.anchor_left = 0.025
	top.anchor_right = 0.975
	top.offset_top = 20
	root_control.add_child(top)
	title_label = _label(24)
	metrics_label = _label(18)
	top.add_child(title_label)
	top.add_child(metrics_label)
	var bottom := VBoxContainer.new()
	bottom.anchor_left = 0.025
	bottom.anchor_right = 0.975
	bottom.anchor_top = 1.0
	bottom.anchor_bottom = 1.0
	bottom.offset_top = -220
	bottom.offset_bottom = -18
	bottom.add_theme_constant_override("separation",6)
	root_control.add_child(bottom)
	var row_a := HBoxContainer.new()
	row_a.add_theme_constant_override("separation",8)
	bottom.add_child(row_a)
	view_button = _button("KUVAKULMA")
	lighting_button = _button("VALAISTUS")
	view_button.pressed.connect(func(): set_view(view_index + 1))
	lighting_button.pressed.connect(func(): set_lighting(lighting_index + 1))
	row_a.add_child(view_button)
	row_a.add_child(lighting_button)
	var row_b := HBoxContainer.new()
	row_b.add_theme_constant_override("separation",8)
	bottom.add_child(row_b)
	orbit_button = _button("KIERRÄ")
	orbit_button.pressed.connect(_toggle_orbit)
	var reset_button := _button("NOLLAA MITTAUS")
	reset_button.pressed.connect(reset_metrics)
	row_b.add_child(orbit_button)
	row_b.add_child(reset_button)

func _direction(i: int) -> Vector3:
	match i:
		0: return Vector3(1,.65,1.25)
		1: return Vector3(1,.23,0)
		2: return Vector3(-1,.55,-1.25)
		3: return Vector3(0,1.4,.08)
		_: return Vector3(1,.65,1.25)

func _view_label() -> String:
	match view_index:
		0: return "ETUVIISO"
		1: return "SIVU"
		2: return "TAKAVIISO"
		3: return "YLÄ"
		_: return "ETUVIISO"

func _position_camera() -> void:
	var direction := _direction(view_index).normalized()
	if orbiting:
		direction = Basis(Vector3.UP,orbit_angle) * direction
	camera.position = direction * 50
	camera.look_at(Vector3.ZERO)

func set_view(index: int) -> void:
	view_index = posmod(index,4)
	orbit_angle = 0
	_position_camera()
	_update_labels()

func set_lighting(index: int) -> void:
	# 0 = ORIGINAL game light (pixel-faithful reference for the old APK).
	# 1 = BALANCED CINEMATIC experiment (reflection + controlled fill/rim).
	# 2 = ORIGINAL inspection fill (pixel-faithful reference for the old APK).
	# The C-07 GLB and all of its textures remain unchanged in every mode.
	lighting_index = posmod(index,3)
	var environment: Environment = env_node.environment
	environment.reflected_light_source = Environment.REFLECTION_SOURCE_BG
	environment.ambient_light_energy = 0.85
	sun.light_energy = 2.0
	fill.visible = false
	rim.visible = false
	match lighting_index:
		1:
			environment.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
			environment.ambient_light_energy = 1.0
			sun.light_energy = 2.35
			fill.visible = true
			rim.visible = true
		2:
			environment.ambient_light_energy = 1.2
			fill.visible = true
	reset_metrics()
	_update_labels()

func _toggle_orbit() -> void:
	orbiting = not orbiting
	orbit_angle = 0
	_position_camera()
	_update_labels()

func reset_metrics() -> void:
	measured_seconds = 0
	refresh_seconds = 0
	samples_ms.clear()

func _update_labels() -> void:
	if title_label == null:
		return
	var light_names: Array[String] = ["PELIN NYKYVALO", "TASAPAINOTETTU", "TARKASTUSVALO"]
	var short_names: Array[String] = ["PELI", "TASAPAINO", "TARKASTUS"]
	var light_name: String = light_names[lighting_index]
	title_label.text = "C-07 A4 | VAIN GRAFIIKKATESTI\n%s | %s\nEI HYVÄKSYTTY PELIMALLI" % [_view_label(),light_name]
	if view_button != null:
		view_button.text = "KULMA: %s" % _view_label()
		lighting_button.text = "VALO: %s" % short_names[lighting_index]
		orbit_button.text = "KIERRÄ: %s" % ("KYLLÄ" if orbiting else "EI")

func _process(delta: float) -> void:
	if orbiting:
		orbit_angle += delta*0.18
		_position_camera()
	measured_seconds += delta
	if delta > 0.0 and delta < 0.5:
		samples_ms.append(delta*1000)
		if samples_ms.size()>600:
			samples_ms.pop_front()
	refresh_seconds += delta
	if refresh_seconds < 0.8:
		return
	refresh_seconds=0
	var sorted := samples_ms.duplicate()
	sorted.sort()
	var avg := 0.0
	var p99 := 0.0
	if not sorted.is_empty():
		var total := 0.0
		for ms in sorted:
			total += ms
		avg = float(sorted.size())*1000.0/maxf(total,1.0)
		p99 = sorted[min(sorted.size()-1,int(floor(sorted.size()*.99)))]
	metrics_label.text = "%s | %d FPS | avg %.1f\np99 %.1f ms | draws %d | %.1f min\nFPS/p99 perustuu ruutuaikaan, ei GPU-profilointiin" % [
		str(RenderingServer.get_current_rendering_method()),
		Engine.get_frames_per_second(),avg,p99,
		int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)),measured_seconds/60.0]
