extends SceneTree

func _initialize() -> void:
	call_deferred("_configure")


func _configure() -> void:
	var sdk := OS.get_environment("ANDROID_HOME")
	var java := OS.get_environment("JAVA_HOME")
	if sdk.is_empty() or java.is_empty():
		printerr("Android SDK or Java environment path missing")
		quit(1)
		return
	var settings := EditorInterface.get_editor_settings()
	settings.set_setting("export/android/android_sdk_path", sdk)
	settings.set_setting("export/android/java_sdk_path", java)
	settings.save()
	print("Android export SDK configured")
	quit(0)
