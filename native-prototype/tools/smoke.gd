extends SceneTree

const RULES = preload("res://scripts/docking_rules.gd")


func _initialize() -> void:
	call_deferred("_run")


func _assert(condition: bool, note: String) -> bool:
	if not condition:
		printerr("FAIL: " + note)
	return condition


func _run() -> void:
	var scene := load("res://scenes/main.tscn") as PackedScene
	if not _assert(scene != null, "main scene load"):
		quit(1)
		return
	var stage = scene.instantiate()
	root.add_child(stage)
	await process_frame
	var ok := true
	ok = _assert(stage.ship_length_units <= 4.0, "ship length") and ok
	ok = _assert(stage.capital_diameter_units >= 80.0, "capital is enormous relative to ship") and ok
	ok = _assert(stage.outpost_diameter_units >= 12.0, "outpost scale") and ok
	stage.begin_approach("capital")
	ok = _assert(stage.phase == "approach", "capital approach starts") and ok
	stage.skip_approach()
	ok = _assert(stage.phase == "clearance", "capital clearance starts") and ok
	stage.choose_option("inspect")
	ok = _assert(stage.phase == "result", "capital result") and ok
	ok = _assert(stage.resources["time"] == 2, "legal scan delay") and ok
	ok = _assert(stage.resources["credits"] == 300, "legal scan not fined") and ok
	stage.reset_trial()
	stage.set_cargo("unregistered")
	stage.begin_approach("capital")
	stage.skip_approach()
	stage.choose_option("inspect")
	ok = _assert(stage.resources["credits"] == 210, "unregistered cargo penalized on scan") and ok
	stage.reset_trial()
	stage.begin_approach("outpost")
	stage.skip_approach()
	stage.choose_option("manual")
	ok = _assert(stage.resources["hull"] == 92, "outer docking wears hull") and ok
	ok = _assert(stage.resources["credits"] == 190, "credits carry over between approaches") and ok
	var resource_snapshot: Dictionary = {"credits": 0, "coolant": 0, "heat": 0, "hull": 100, "time": 0, "docks": 0}
	var invalid: Dictionary = RULES.resolve("outpost", "legal", "manual", resource_snapshot)
	ok = _assert(not invalid["ok"], "unaffordable choice rejected") and ok
	var no_coolant := RULES.resolve("capital", "unregistered", "cold", resource_snapshot)
	ok = _assert(not no_coolant["ok"], "coolant cannot go below zero") and ok
	stage.queue_free()
	await process_frame
	if ok:
		print("PASS: real-3D scale, docking phases, legal/illegal scan and outpost consequences")
		quit(0)
	else:
		quit(1)
