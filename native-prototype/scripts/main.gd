extends Node3D
## Native mobile 3D docking 0.3: physical relative scale + brief decisions.
## One Godot unit is approximately ten metres in this local test zone.

const RULES = preload("res://scripts/docking_rules.gd")
const APPROACH_SECONDS := 4.5
const SHIP_START_CAPITAL := Vector3(0.0, 0.0, 240.0)
const SHIP_START_OUTPOST := Vector3(0.0, 0.0, 120.0)
const SHIP_END_CAPITAL := Vector3(0.0, 0.0, -4.0)
const SHIP_END_OUTPOST := Vector3(0.0, 0.0, -42.0)
const STATION_LOCATION := Vector3(0.0, 0.0, -65.0)

# Observables used by the headless tests.
var ship_length_units := 3.0
var capital_diameter_units := 90.0
var outpost_diameter_units := 18.0
var phase := "choose"
var current_facility := ""
var cargo := "legal"
var resources: Dictionary = RULES.initial_resources()

var ship: Node3D
var camera: Camera3D
var capital: Node3D
var outpost: Node3D
var title_label: Label
var stats_label: Label
var info_label: Label
var detail_label: Label
var left_button: Button
var right_button: Button
var aux_button: Button
var elapsed := 0.0
var message := ""

func _ready() -> void:
	_build_lights()
	_build_3d()
	_build_ui()
	reset_trial()


func _material(color: Color, glow: bool = false) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = 0.40
	mat.metallic = 0.35
	if glow:
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.emission_enabled = true
		mat.emission = color
		mat.emission_energy_multiplier = 1.3
	return mat


func _box(parent: Node3D, location: Vector3, size: Vector3, material: Material) -> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	instance.material_override = material
	instance.position = location
	parent.add_child(instance)
	return instance


func _sphere(parent: Node3D, location: Vector3, radius: float, material: Material) -> void:
	var mesh := SphereMesh.new()
	mesh.radius = radius
	mesh.height = radius * 2.0
	mesh.radial_segments = 10
	mesh.rings = 6
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	instance.material_override = material
	instance.position = location
	parent.add_child(instance)


func _torus(parent: Node3D, location: Vector3, radius: float, material: Material) -> void:
	var mesh := TorusMesh.new()
	mesh.inner_radius = radius - 1.3
	mesh.outer_radius = radius + 1.3
	mesh.rings = 64
	mesh.ring_segments = 12
	var node := MeshInstance3D.new()
	node.mesh = mesh
	node.material_override = material
	node.position = location
	node.rotation_degrees.x = 90.0
	parent.add_child(node)


func _floating_label(parent: Node3D, text_value: String, location: Vector3) -> void:
	var label := Label3D.new()
	label.text = text_value
	label.position = location
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.font_size = 48
	label.pixel_size = 0.018
	label.outline_size = 12
	label.modulate = Color(0.8, 0.93, 1.0)
	parent.add_child(label)


func _build_lights() -> void:
	var world := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.006, 0.012, 0.029)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.36, 0.49, 0.62)
	env.ambient_light_energy = 0.85
	world.environment = env
	add_child(world)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-45.0, 30.0, 0.0)
	light.light_color = Color(0.78, 0.86, 1.0)
	light.light_energy = 2.0
	add_child(light)


func _build_3d() -> void:
	var hull := _material(Color(0.60, 0.74, 0.82))
	var dark := _material(Color(0.11, 0.19, 0.27))
	var teal := _material(Color(0.18, 0.82, 0.76), true)
	var yellow := _material(Color(1.0, 0.65, 0.29), true)
	var steel := _material(Color(0.33, 0.47, 0.58))

	# About 30 metres long. Will remain tiny against the large station.
	ship = Node3D.new()
	ship.name = "Courier30m"
	add_child(ship)
	_box(ship, Vector3.ZERO, Vector3(0.85, 0.35, 3.0), hull)
	_box(ship, Vector3(0.0, -0.09, 0.05), Vector3(2.5, 0.17, 0.76), hull)
	_box(ship, Vector3(0.0, 0.24, -0.45), Vector3(0.52, 0.25, 0.72), dark)
	_box(ship, Vector3(-0.32, 0.02, 1.30), Vector3(0.28, 0.24, 0.22), teal)
	_box(ship, Vector3(0.32, 0.02, 1.30), Vector3(0.28, 0.24, 0.22), teal)

	# Corporate station: 900 metre external ring, about 1 km long spine.
	capital = Node3D.new()
	capital.name = "CorporateMegastation"
	capital.position = STATION_LOCATION
	add_child(capital)
	_torus(capital, Vector3.ZERO, 45.0, steel)
	_torus(capital, Vector3(0.0, 0.0, 2.0), 42.0, teal)
	_box(capital, Vector3(0.0, 0.0, -23.0), Vector3(15.0, 14.0, 100.0), steel)
	_box(capital, Vector3(0.0, 0.0, 24.0), Vector3(12.0, 9.0, 11.0), dark)
	_box(capital, Vector3(0.0, 0.0, 31.5), Vector3(10.0, 7.0, 1.5), teal)
	for i in range(12):
		var angle := TAU * float(i) / 12.0
		var x := cos(angle) * 43.0
		var y := sin(angle) * 43.0
		_sphere(capital, Vector3(x, y, 2.5), 1.1, yellow)
		if i % 3 == 0:
			_box(capital, Vector3(x * 0.5, y * 0.5, 0.0), Vector3(3.0, 2.6, 8.0), steel)
	# A handful of tiny traffic craft provide a readable visual scale.
	for i in range(7):
		var xx := -28.0 + float(i) * 9.0
		_box(capital, Vector3(xx, -11.0 + float(i % 3) * 8.0, 34.0 + float(i % 2) * 8.0),
			Vector3(1.5, 0.45, 3.0), hull)
	_floating_label(capital, "CORPORATE TRAFFIC CONTROL", Vector3(0.0, 50.0, 0.0))

	# 180 metre independent outpost, visibly smaller and less equipped.
	outpost = Node3D.new()
	outpost.name = "RemoteOutpost"
	outpost.position = STATION_LOCATION
	add_child(outpost)
	_box(outpost, Vector3.ZERO, Vector3(10.0, 3.8, 8.0), steel)
	_box(outpost, Vector3(0.0, 3.0, -1.0), Vector3(7.0, 3.0, 6.0), dark)
	_box(outpost, Vector3(-7.0, 0.0, -2.0), Vector3(4.0, 0.3, 6.0), dark)
	_box(outpost, Vector3(7.0, 0.0, -2.0), Vector3(4.0, 0.3, 6.0), dark)
	_box(outpost, Vector3(0.0, 0.0, 4.5), Vector3(5.0, 0.8, 1.0), yellow)
	_sphere(outpost, Vector3(0.0, 5.0, 0.0), 1.0, teal)
	_floating_label(outpost, "FREEPORT 17", Vector3(0.0, 8.0, 0.0))
	outpost.visible = false

	camera = Camera3D.new()
	camera.name = "CinematicCamera"
	camera.projection = Camera3D.PROJECTION_PERSPECTIVE
	camera.fov = 65.0
	camera.near = 0.10
	camera.far = 900.0
	add_child(camera)
	# Visible through the whole approach, contrasting with the old orthographic demo.
	camera.current = true


func _panel_box() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.027, 0.065, 0.106, 0.96)
	style.border_color = Color(0.16, 0.34, 0.44)
	style.set_border_width_all(2)
	style.set_corner_radius_all(22)
	return style


func _label(text_value: String, size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text_value
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label


func _button(text_value: String) -> Button:
	var button := Button.new()
	button.text = text_value
	button.custom_minimum_size.y = 100.0
	button.add_theme_font_size_override("font_size", 22)
	button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return button


func _build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var root_control := Control.new()
	root_control.set_anchors_preset(Control.PRESET_FULL_RECT)
	root_control.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(root_control)

	var header := PanelContainer.new()
	header.anchor_right = 1.0
	header.offset_left = 18.0
	header.offset_right = -18.0
	header.offset_top = 25.0
	header.offset_bottom = 161.0
	header.add_theme_stylebox_override("panel", _panel_box())
	root_control.add_child(header)
	var top := VBoxContainer.new()
	top.add_theme_constant_override("separation", 6)
	header.add_child(top)
	title_label = _label("", 26, Color(0.48, 0.94, 0.82))
	stats_label = _label("", 21, Color(0.82, 0.92, 1.0))
	top.add_child(title_label)
	top.add_child(stats_label)

	var footer := PanelContainer.new()
	footer.anchor_left = 0.0
	footer.anchor_right = 1.0
	footer.anchor_top = 1.0
	footer.anchor_bottom = 1.0
	footer.offset_left = 18.0
	footer.offset_right = -18.0
	footer.offset_top = -390.0
	footer.offset_bottom = -28.0
	footer.add_theme_stylebox_override("panel", _panel_box())
	root_control.add_child(footer)
	var stack := VBoxContainer.new()
	stack.add_theme_constant_override("separation", 10)
	footer.add_child(stack)
	info_label = _label("", 28, Color(0.94, 0.98, 1.0))
	detail_label = _label("", 20, Color(0.70, 0.84, 0.90))
	stack.add_child(info_label)
	stack.add_child(detail_label)
	var choices_row := HBoxContainer.new()
	choices_row.add_theme_constant_override("separation", 10)
	stack.add_child(choices_row)
	left_button = _button("VALINTA A")
	right_button = _button("VALINTA B")
	left_button.pressed.connect(_left_action)
	right_button.pressed.connect(_right_action)
	choices_row.add_child(left_button)
	choices_row.add_child(right_button)
	aux_button = _button("APUTOIMINTO")
	aux_button.pressed.connect(_aux_action)
	stack.add_child(aux_button)


func _resource_line() -> String:
	return "%d cr   •   jäähdyte %d   •   runko %d%%   •   lämpö %d   •   aika %d" % [
		int(resources["credits"]), int(resources["coolant"]),
		int(resources["hull"]), int(resources["heat"]), int(resources["time"])
	]


func _render_ui() -> void:
	stats_label.text = _resource_line()
	left_button.disabled = false
	right_button.disabled = false
	left_button.visible = true
	right_button.visible = true
	aux_button.visible = true
	if phase == "choose":
		title_label.text = "AVARUUSSEIKKAILU • TELAKOINTIKOE 0.3"
		info_label.text = "Minne lähestyt?"
		detail_label.text = "Oikea 3D-mittakaava. Pääset kokeilemaan erilaisia asemaprotokollia."
		left_button.text = "SUURASEMA\nTIUKKA VALVONTA"
		right_button.text = "OUTPOST\nVAPAA SATAMA"
		aux_button.text = "LASTI: %s · VAIHDA" % ("LAILLINEN" if cargo == "legal" else "REKISTERÖIMÄTÖN")
	elif phase == "approach":
		title_label.text = "AUTOPILOTTI • LÄHESTYMINEN"
		info_label.text = "Asema kasvaa näkyviin"
		detail_label.text = "Alus on mittakaavassa pienempi kuin asema. Matkaa lyhennetään, ei mittasuhteita."
		left_button.visible = false
		right_button.visible = false
		aux_button.text = "OHITA LÄHESTYMINEN"
	elif phase == "clearance":
		title_label.text = "LÄHESTYMISPROTOKOLLA"
		if current_facility == "capital":
			info_label.text = "Yhtiösektorin turvatarkastus"
			detail_label.text = "Valitse tarkastus tai jäähdytetty sisääntulo. Rekisteröimätön näyte on tulliriski."
		else:
			info_label.text = "Outpostin vanha ulkolaituri"
			detail_label.text = "Ei tulliprotokollaa. Pääsetkö sisään nopeasti kuluttamatta alusta?"
		var alternatives: Array[Dictionary] = RULES.choices(current_facility, cargo, resources)
		left_button.text = str(alternatives[0]["label"])
		right_button.text = str(alternatives[1]["label"])
		left_button.disabled = not alternatives[0]["enabled"]
		right_button.disabled = not alternatives[1]["enabled"]
		aux_button.visible = false
	elif phase == "result":
		title_label.text = "TELAKOINTI • TULOS"
		info_label.text = "Telakointi suoritettu"
		detail_label.text = message
		left_button.text = "SEURAAVA ASEMA"
		right_button.text = "KOKEILE UUDELLEEN"
		aux_button.visible = false


func reset_trial() -> void:
	phase = "choose"
	current_facility = ""
	elapsed = 0.0
	ship.position = SHIP_START_CAPITAL
	capital.visible = true
	outpost.visible = false
	_reset_camera()
	_render_ui()


func set_cargo(kind: String) -> void:
	if phase != "choose" or not (kind in ["legal", "unregistered"]):
		return
	cargo = kind
	_render_ui()


func begin_approach(facility: String) -> void:
	if phase != "choose" or not (facility in ["capital", "outpost"]):
		return
	current_facility = facility
	capital.visible = facility == "capital"
	outpost.visible = facility == "outpost"
	elapsed = 0.0
	phase = "approach"
	ship.position = SHIP_START_CAPITAL if facility == "capital" else SHIP_START_OUTPOST
	_reset_camera()
	_render_ui()


func _reset_camera() -> void:
	camera.position = ship.position + Vector3(10.0, 17.0, 26.0)
	camera.look_at(ship.position + Vector3(0.0, 0.0, -75.0))


func skip_approach() -> void:
	if phase != "approach":
		return
	elapsed = APPROACH_SECONDS
	ship.position = SHIP_END_CAPITAL if current_facility == "capital" else SHIP_END_OUTPOST
	_arrived()


func _arrived() -> void:
	phase = "clearance"
	_render_ui()


func choose_option(option: String) -> void:
	if phase != "clearance":
		return
	var outcome: Dictionary = RULES.resolve(current_facility, cargo, option, resources)
	if not outcome["ok"]:
		detail_label.text = str(outcome["message"])
		return
	resources = outcome["state"]
	message = str(outcome["message"])
	phase = "result"
	_render_ui()


func _left_action() -> void:
	match phase:
		"choose": begin_approach("capital")
		"clearance": choose_option("inspect" if current_facility == "capital" else "queue")
		"result": reset_trial()


func _right_action() -> void:
	match phase:
		"choose": begin_approach("outpost")
		"clearance": choose_option("cold" if current_facility == "capital" else "manual")
		"result": reset_trial()


func _aux_action() -> void:
	if phase == "choose":
		set_cargo("unregistered" if cargo == "legal" else "legal")
	elif phase == "approach":
		skip_approach()


func _unhandled_input(event: InputEvent) -> void:
	# The visible destination is selectable; large UI buttons remain the fallback.
	if phase != "choose":
		return
	var pointer := Vector2.ZERO
	if event is InputEventScreenTouch:
		if not event.pressed:
			return
		pointer = event.position
	elif event is InputEventMouseButton:
		if not event.pressed or event.button_index != MOUSE_BUTTON_LEFT:
			return
		pointer = event.position
	else:
		return
	var screen_h := get_viewport().get_visible_rect().size.y
	if pointer.y < 175.0 or pointer.y > screen_h - 400.0:
		return
	if camera.is_position_behind(STATION_LOCATION):
		return
	var pixel_radius := 115.0
	if pointer.distance_to(camera.unproject_position(STATION_LOCATION)) <= pixel_radius:
		begin_approach("capital")


func _process(delta: float) -> void:
	if phase == "approach":
		elapsed = minf(APPROACH_SECONDS, elapsed + maxf(delta, 0.0))
		var t := elapsed / APPROACH_SECONDS
		var eased := 1.0 - pow(1.0 - t, 2.1)
		var start := SHIP_START_CAPITAL if current_facility == "capital" else SHIP_START_OUTPOST
		var finish := SHIP_END_CAPITAL if current_facility == "capital" else SHIP_END_OUTPOST
		ship.position = start.lerp(finish, eased)
		if t >= 1.0:
			_arrived()
	# A dynamic perspective angle, not the old stationary isometric map.
	var camera_offset := Vector3(12.0, 13.0, 25.0) if current_facility == "capital" else Vector3(8.0, 9.0, 18.0)
	var desired_position := ship.position + camera_offset
	camera.position = camera.position.lerp(desired_position, minf(delta * 2.0, 1.0))
	var focus := ship.position + Vector3(0.0, 0.0, -72.0 if current_facility == "capital" else -34.0)
	camera.look_at(focus)
