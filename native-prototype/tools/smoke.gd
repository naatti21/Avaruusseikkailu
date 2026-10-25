extends SceneTree

func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var packed := load("res://scenes/main.tscn") as PackedScene
	if packed == null:
		printerr("FAIL: scene cannot load")
		quit(1)
		return
	var stage := packed.instantiate()
	root.add_child(stage)
	await process_frame
	if not stage.has_method("go_to_target"):
		printerr("FAIL: public target selection missing")
		quit(1)
		return
	stage.go_to_target("station")
	if not stage.is_traveling or stage.current_target != "station":
		printerr("FAIL: autopilot did not start")
		quit(1)
		return
	for i in range(40):
		stage._process(0.20)
	if stage.is_traveling:
		printerr("FAIL: station not reached")
		quit(1)
		return
	stage._interact()
	if not stage.docked:
		printerr("FAIL: docking action did not register")
		quit(1)
		return
	stage.go_to_target("beacon")
	for i in range(40):
		stage._process(0.20)
	if stage.is_traveling:
		printerr("FAIL: research beacon not reached")
		quit(1)
		return
	stage._interact()
	if not stage.scanned:
		printerr("FAIL: research action did not register")
		quit(1)
		return
	print("PASS: scene loaded; autopilot reached two real 3D points; actions registered")
	quit(0)
