extends Node3D
## Look-development inspection scene, NOT a playable level.
## Approved art is loaded from versioned source asset slots. No primitive placeholders.
const SLOTS := [
	{"name": "C-07 / RAAHTIALUS", "path": "res://production/models/c07_courier.glb"},
	{"name": "TWIN CYLINDER / YHDYSKUNTA", "path": "res://production/models/twin_cylinder_colony.glb"},
	{"name": "TWIN CYLINDER / TELAKKASEKTORI", "path": "res://production/models/twin_cylinder_berth.glb"}
]
var camera: Camera3D
var model: Node3D
var info: Label
var counters: Label
var slot: int = 0
var visual_state := "awaiting_artist"
var view_center := Vector3.ZERO
var view_distance := 100.0
var orbit := 0.0

func _ready() -> void:
	_setup()
	select_slot(0)

func _setup() -> void:
	var environment_node := WorldEnvironment.new()
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.008, 0.014, 0.03)
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.40, 0.49, 0.58)
	environment.ambient_light_energy = 0.8
	environment_node.environment = environment
	add_child(environment_node)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52, 28, -8)
	sun.light_energy = 2.0
	add_child(sun)
	camera = Camera3D.new()
	camera.fov = 52.0
	camera.near = 0.1
	camera.far = 30000.0
	camera.current = true
	add_child(camera)
	var layer := CanvasLayer.new()
	add_child(layer)
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(root)
	var top := VBoxContainer.new()
	top.anchor_left = 0.025
	top.anchor_right = 0.975
	top.offset_top = 20
	root.add_child(top)
	info = Label.new()
	info.add_theme_font_size_override("font_size", 25)
	info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	top.add_child(info)
	counters = Label.new()
	counters.add_theme_font_size_override("font_size", 18)
	top.add_child(counters)
	var next := Button.new()
	next.anchor_left = 0.025
	next.anchor_right = 0.975
	next.anchor_top = 1.0
	next.anchor_bottom = 1.0
	next.offset_top = -130
	next.offset_bottom = -26
	next.text = "SEURAAVA MALLI"
	next.add_theme_font_size_override("font_size", 24)
	next.pressed.connect(func(): select_slot((slot + 1) % SLOTS.size()))
	root.add_child(next)

func select_slot(index: int) -> void:
	slot = clampi(index, 0, SLOTS.size() - 1)
	if model != null:
		model.queue_free()
		model = null
	var item: Dictionary = SLOTS[slot]
	orbit = 0.0
	view_center = Vector3.ZERO
	view_distance = 80
	var path: String = item["path"]
	if not ResourceLoader.exists(path):
		visual_state = "awaiting_artist"
		info.text = "%s\nODOTTAA HYVAKSYTTAVAA 3D-MALLIA" % item["name"]
	else:
		var resource := load(path) as PackedScene
		if resource == null:
			visual_state = "load_error"
			info.text = "GLB IMPORT ERROR: %s" % item["name"]
		else:
			model = resource.instantiate() as Node3D
			add_child(model)
			visual_state = "candidate_not_approved"
			info.text = "%s\nTAIDEMALLI - EI VIELA HYVAKSYTTY" % item["name"]
			var size_box := _world_bounds(model)
			view_center = size_box.get_center()
			var longest := maxf(size_box.size.x, maxf(size_box.size.y, size_box.size.z))
			view_distance = maxf(14, longest * 2.8)
	_update_camera()

func _world_bounds(root_node: Node3D) -> AABB:
	var all_meshes: Array[MeshInstance3D] = []
	_collect_meshes(root_node, all_meshes)
	var started := false
	var whole := AABB()
	for instance in all_meshes:
		var local: AABB = instance.get_aabb()
		for dx in [0, 1]:
			for dy in [0, 1]:
				for dz in [0, 1]:
					var corner: Vector3 = local.position + local.size * Vector3(dx, dy, dz)
					var pt: Vector3 = instance.global_transform * corner
					if not started:
						whole = AABB(pt, Vector3.ZERO)
						started = true
					else:
						whole = whole.expand(pt)
	return whole

func _collect_meshes(parent: Node, output: Array[MeshInstance3D]) -> void:
	if parent is MeshInstance3D:
		output.append(parent as MeshInstance3D)
	for child in parent.get_children():
		_collect_meshes(child, output)

func _update_camera() -> void:
	var offset := Vector3(sin(orbit), 0.28, cos(orbit)).normalized()
	camera.position = view_center + offset * view_distance
	camera.look_at(view_center)

func _process(delta: float) -> void:
	orbit += delta * 0.07
	_update_camera()
	counters.text = "Vain tarkastusnakymä | %s | %d FPS\nEi lupaa julkaisuun ilman visuaalista ja Android-testausta" % [
		RenderingServer.get_current_rendering_method(),
		Engine.get_frames_per_second()
	]
