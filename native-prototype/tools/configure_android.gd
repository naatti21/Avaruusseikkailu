@tool
extends EditorScript

func _run() -> void:
	var settings := EditorInterface.get_editor_settings()
	var sdk := OS.get_environment("ANDROID_HOME")
	var java := OS.get_environment("JAVA_HOME")
	if sdk.is_empty() or java.is_empty():
		printerr("Android SDK or Java environment path missing")
		return
	settings.set_setting("export/android/android_sdk_path", sdk)
	settings.set_setting("export/android/java_sdk_path", java)
	settings.save()
	print("Android export SDK configured")
