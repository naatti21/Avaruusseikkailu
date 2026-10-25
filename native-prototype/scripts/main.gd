extends Node3D
## Real 3D spatial navigation probe. No simulated screen panning or pointless free flight.

const SHIP_START := Vector3(0.0, 0.7, 8.0)
const ISO_OFFSET := Vector3(15.0, 18.0, 21.0)
const SPEED := 4.8
const ARRIVAL_DISTANCE := 1.2
const DESTINATIONS := {
	"station": Vector3(7.0, 0.7, -4.0),
	"beacon": Vector3(-7.0, 0.7, -5.0)
}

var ship: Node3D
var camera: Camera3D
var current_target: String = ""
var is_traveling := false
var scanned := false
var docked := false
var info_label: Label
var hint_label: Label
var action_button: Button
var station_button: Button
var beacon_button: Button


func _ready() -> void:
	_create_environment()
	_create_scene()
	_create_interface()
	_set_info("Valitse asema tai tutkimuspoiju.", "Näpäytä 3D-kohdetta tai käytä alareunan painikkeita.")


func _create_environment() -> void:
	var world := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.014, 0.025, 0.048)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.30, 0.42, 0.55)
	env.ambient_light_energy = 0.65
	world.environment = env
	add_child(world)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-53.0, 27.0, 0.0)
	sun.light_energy = 1.7
	sun.light_color = Color(0.70, 0.86, 1.0)
	add_child(sun)


func _material(tint: Color, glow: bool = false) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = tint
	mat.metallic = 0.38
	mat.roughness = 0.43
	if glow:
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.emission_enabled = true
		mat.emission = tint
		mat.emission_energy_multiplier = 1.6
	return mat


func _box(parent: Node3D, at: Vector3, size: Vector3, mat: StandardMaterial3D, tilt: float = 0.0) -> void:
	var mesh := BoxMesh.new()
	mesh.size = size
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	instance.material_override = mat
	instance.position = at
	instance.rotation_degrees.y = tilt
	parent.add_child(instance)


func _sphere(parent: Node3D, at: Vector3, radius: float, mat: StandardMaterial3D) -> void:
	var mesh := SphereMesh.new()
	mesh.radius = radius
	mesh.height = radius * 2.0
	mesh.radial_segments = 10
	mesh.rings = 6
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	instance.material_override = mat
	instance.position = at
	parent.add_child(instance)


func _ring(parent: Node3D, at: Vector3, radius: float, mat: StandardMaterial3D) -> void:
	var mesh := TorusMesh.new()
	mesh.inner_radius = radius - 0.10
	mesh.outer_radius = radius + 0.10
	mesh.rings = 24
	mesh.ring_segments = 8
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	instance.material_override = mat
	instance.position = at
	parent.add_child(instance)


func _create_scene() -> void:
	var dark := _material(Color(0.09, 0.16, 0.24))
	var hull := _material(Color(0.62, 0.77, 0.84))
	var accent := _material(Color(0.21, 0.70, 0.73), true)
	var engine := _material(Color(0.30, 0.95, 0.85), true)
	var station_mat := _material(Color(0.38, 0.53, 0.62))
	var beacon_mat := _material(Color(0.94, 0.69, 0.34), true)

	ship = Node3D.new()
	ship.name = "PlayerShip"
	ship.position = SHIP_START
	add_child(ship)
	_box(ship, Vector3.ZERO, Vector3(0.85, 0.32, 2.4), hull)
	_box(ship, Vector3(0.0, -0.06, 0.20), Vector3(3.3, 0.13, 0.88), hull)
	_box(ship, Vector3(0.0, 0.20, -0.45), Vector3(0.46, 0.21, 0.65), dark)
	_box(ship, Vector3(-0.33, 0.04, 1.13), Vector3(0.29, 0.31, 0.30), engine)
	_box(ship, Vector3(0.33, 0.04, 1.13), Vector3(0.29, 0.31, 0.30), engine)
	_box(ship, Vector3(0.0, 0.0, -1.34), Vector3(0.42, 0.18, 0.56), accent)

	var station := Node3D.new()
	station.name = "Station"
	station.position = DESTINATIONS["station"]
	add_child(station)
	_box(station, Vector3.ZERO, Vector3(3.6, 1.0, 2.4), station_mat)
	_box(station, Vector3(0.0, 0.55, 0.0), Vector3(1.2, 0.6, 1.3), dark)
	_ring(station, Vector3.ZERO, 2.65, accent)
	_sphere(station, Vector3(0.0, 0.9, 0.0), 0.3, engine)
	_make_label(station, "KESTREL • ASEMA", Vector3(0.0, 2.3, 0.0))

	var beacon := Node3D.new()
	beacon.name = "ResearchBeacon"
	beacon.position = DESTINATIONS["beacon"]
	add_child(beacon)
	_sphere(beacon, Vector3.ZERO, 0.8, dark)
	_box(beacon, Vector3.ZERO, Vector3(0.5, 2.6, 0.5), station_mat)
	_ring(beacon, Vector3.ZERO, 1.65, beacon_mat)
	_sphere(beacon, Vector3(0.0, 1.6, 0.0), 0.24, beacon_mat)
	_make_label(beacon, "POIKKEAVA SIGNAALI", Vector3(0.0, 2.8, 0.0))

	var stone := _material(Color(0.17, 0.23, 0.29))
	var rng := RandomNumberGenerator.new()
	rng.seed = 25102026
	for i in range(24):
		var pos := Vector3(rng.randf_range(-11.0, 0.5), rng.randf_range(-1.2, -0.2), rng.randf_range(-10.0, -0.5))
		if pos.distance_to(DESTINATIONS["beacon"]) < 2.0:
			continue
		_sphere(self, pos, rng.randf_range(0.2, 0.6), stone)

	_create_grid()
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 27.0
	camera.position = ISO_OFFSET
	camera.current = true
	add_child(camera)
	camera.look_at(Vector3(0.0, 0.0, -1.0))


func _make_label(parent: Node3D, content: String, at: Vector3) -> void:
	var label := Label3D.new()
	label.text = content
	label.position = at
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.font_size = 40
	label.pixel_size = 0.007
	label.modulate = Color(0.86, 0.97, 1.0)
	label.outline_size = 8
	parent.add_child(label)


func _create_grid() -> void:
	var lines := ImmediateMesh.new()
	lines.surface_begin(Mesh.PRIMITIVE_LINES)
	for i in range(-14, 15, 2):
		var x := float(i)
		lines.surface_add_vertex(Vector3(x, -1.4, -15.0))
		lines.surface_add_vertex(Vector3(x, -1.4, 15.0))
		lines.surface_add_vertex(Vector3(-15.0, -1.4, x))
		lines.surface_add_vertex(Vector3(15.0, -1.4, x))
	lines.surface_end()
	var instance := MeshInstance3D.new()
	instance.mesh = lines
	var grid_mat := _material(Color(0.10, 0.25, 0.31), true)
	instance.material_override = grid_mat
	add_child(instance)


func _panel_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.045, 0.10, 0.16, 0.96)
	style.border_color = Color(0.22, 0.42, 0.50)
	style.set_border_width_all(2)
	style.set_corner_radius_all(24)
	return style


func _label(text_value: String, font_size: int, tint: Color) -> Label:
	var label := Label.new()
	label.text = text_value
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", tint)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label


func _button(text_value: String) -> Button:
	var button := Button.new()
	button.text = text_value
	button.custom_minimum_size.y = 90.0
	button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	button.add_theme_font_size_override("font_size", 25)
	return button


func _create_interface() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var layout := Control.new()
	layout.set_anchors_preset(Control.PRESET_FULL_RECT)
	layout.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(layout)

	var header := PanelContainer.new()
	header.anchor_right = 1.0
	header.offset_left = 22.0
	header.offset_right = -22.0
	header.offset_top = 26.0
	header.offset_bottom = 150.0
	header.add_theme_stylebox_override("panel", _panel_style())
	layout.add_child(header)
	var head_box := VBoxContainer.new()
	head_box.add_theme_constant_override("separation", 3)
	header.add_child(head_box)
	head_box.add_child(_label("AVARUUSSEIKKAILU  •  3D-OHJAUSKOE", 25, Color(0.51, 0.91, 0.86)))
	head_box.add_child(_label("Näpäytä kohdetta. Alus lähestyy itse.", 23, Color(0.90, 0.95, 1.0)))

	var footer := PanelContainer.new()
	footer.anchor_left = 0.0
	footer.anchor_right = 1.0
	footer.anchor_top = 1.0
	footer.anchor_bottom = 1.0
	footer.offset_left = 22.0
	footer.offset_right = -22.0
	footer.offset_top = -298.0
	footer.offset_bottom = -32.0
	footer.add_theme_stylebox_override("panel", _panel_style())
	layout.add_child(footer)
	var stack := VBoxContainer.new()
	stack.add_theme_constant_override("separation", 11)
	footer.add_child(stack)
	info_label = _label("", 26, Color(0.94, 0.98, 1.0))
	stack.add_child(info_label)
	hint_label = _label("", 20, Color(0.67, 0.80, 0.87))
	stack.add_child(hint_label)
	var commands := HBoxContainer.new()
	commands.add_theme_constant_override("separation", 12)
	stack.add_child(commands)
	station_button = _button("ASEMA")
	beacon_button = _button("POIJU")
	commands.add_child(station_button)
	commands.add_child(beacon_button)
	station_button.pressed.connect(func() -> void: go_to_target("station"))
	beacon_button.pressed.connect(func() -> void: go_to_target("beacon"))
	action_button = _button("TOIMI")
	action_button.visible = false
	stack.add_child(action_button)
	action_button.pressed.connect(_interact)


func _set_info(title: String, hint: String) -> void:
	info_label.text = title
	hint_label.text = hint


func go_to_target(id: String) -> void:
	if not DESTINATIONS.has(id):
		return
	current_target = id
	is_traveling = true
	action_button.visible = false
	if id == "station":
		_set_info("Autopilotti → avaruusasema", "Lähestyminen käynnissä. Kamera seuraa alusta.")
	else:
		_set_info("Autopilotti → tutkimuspoiju", "Lähestyminen käynnissä. Voit valita uuden kohteen.")


func _unhandled_input(event: InputEvent) -> void:
	var tap := Vector2.ZERO
	if event is InputEventScreenTouch:
		if not event.pressed:
			return
		tap = event.position
	elif event is InputEventMouseButton:
		if not event.pressed or event.button_index != MOUSE_BUTTON_LEFT:
			return
		tap = event.position
	else:
		return
	var viewport_size := get_viewport().get_visible_rect().size
	if tap.y < 170 or tap.y > viewport_size.y - 300:
		return
	var nearest := ""
	var best := 90.0
	for id in DESTINATIONS:
		var point: Vector3 = DESTINATIONS[id]
		if camera.is_position_behind(point):
			continue
		var distance := tap.distance_to(camera.unproject_position(point))
		if distance < best:
			best = distance
			nearest = id
	if not nearest.is_empty():
		go_to_target(nearest)


func _process(delta: float) -> void:
	if is_traveling:
		var to: Vector3 = DESTINATIONS[current_target] - ship.position
		if to.length() <= ARRIVAL_DISTANCE:
			is_traveling = false
			_arrived()
		else:
			var direction := to.normalized()
			ship.position = ship.position.move_toward(DESTINATIONS[current_target], SPEED * delta)
			var heading := atan2(-direction.x, -direction.z)
			ship.rotation.y = lerp_angle(ship.rotation.y, heading, minf(delta * 3.0, 1.0))
	var center := Vector3(0.0, 0.0, -1.0) + ship.position * 0.14
	camera.position = camera.position.lerp(center + ISO_OFFSET, minf(delta * 2.0, 1.0))
	camera.look_at(center)


func _arrived() -> void:
	if current_target == "station":
		_set_info("Avaruusasema saavutettu", "Etäisyys ja sijainti ohjasivat alusta oikeassa 3D-tilassa.")
		action_button.text = "TELAKOIDU"
	else:
		_set_info("Tutkimuspoiju saavutettu", "Poikkeava signaali voidaan analysoida.")
		action_button.text = "ANALYSOI SIGNAALI"
	action_button.visible = true


func _interact() -> void:
	if is_traveling:
		return
	if current_target == "station":
		docked = true
		_set_info("Telakointi onnistui", "Koe: saapuminen kohteeseen. Valitse seuraavaksi poiju.")
	else:
		scanned = true
		_set_info("Tutkimusdata tallennettu", "Koe: kohteen tutkiminen. Valitse seuraavaksi asema.")
	action_button.visible = false
