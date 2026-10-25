extends RefCounted
## Small deterministic rules model. All time is in game units, not wall-clock time.
## Credits/heat/coolant/hull are trial-only resources.

static func choices(facility: String, cargo: String, resources: Dictionary) -> Array[Dictionary]:
	var credits: int = int(resources.get("credits", 0))
	var coolant: int = int(resources.get("coolant", 0))
	if facility == "capital":
		var second_text := "JÄÄHDYTÄ\n−1 jäähdyte · +1 aika"
		var first_text := "AVOIN SKANNAUS\n+2 aika"
		if cargo == "unregistered":
			first_text = "AVOIN SKANNAUS\n+2 aika · lasti menetetään · −90 cr"
		return [
			{"id": "inspect", "label": first_text, "enabled": true},
			{"id": "cold", "label": second_text, "enabled": coolant > 0}
		]
	return [
		{"id": "queue", "label": "ODOTA LAITURIA\n+2 aika · ei vauriota", "enabled": true},
		{"id": "manual", "label": "ULKOTELAKOINTI\n+0 aika · −8 runko · −20 cr", "enabled": credits >= 20}
	]


static func resolve(facility: String, cargo: String, option: String, resources: Dictionary) -> Dictionary:
	var state := resources.duplicate(true)
	var valid := false
	for item in choices(facility, cargo, resources):
		if item["id"] == option and item["enabled"]:
			valid = true
			break
	if not valid:
		return {"ok": false, "state": resources.duplicate(true), "message": "Toiminto ei ole käytettävissä."}
	var summary := ""
	if facility == "capital":
		if option == "inspect":
			state["time"] += 2
			state["heat"] = 0
			if cargo == "unregistered":
				state["credits"] -= 90
				summary = "Tulli löysi rekisteröimättömän näytteen. Lasti takavarikoitu; sakko 90 cr."
			else:
				summary = "Skannaus valmis. Laillinen lasti hyväksyttiin ilman sakkoa."
		else:
			state["time"] += 1
			state["coolant"] -= 1
			state["heat"] += 1
			if cargo == "unregistered":
				summary = "Jäähdytys vaimensi rahtinäytteen signaalin. Läpäisit tarkastusikkunan; lämpökuorma kasvoi."
			else:
				summary = "Jäähdytetty sisääntulo. Säästit aikaa mutta käytit jäähdytettä."
	else:
		if option == "queue":
			state["time"] += 2
			summary = "Huoltovarsi valmisteltiin. Alus telakoitui ilman vaurioita."
		else:
			state["hull"] -= 8
			state["credits"] -= 20
			summary = "Nopea ulkotelakointi onnistui. Runko kului ja huolto veloitti 20 cr."
	state["docks"] += 1
	return {"ok": true, "state": state, "message": summary}


static func initial_resources() -> Dictionary:
	return {"credits": 300, "coolant": 2, "heat": 0, "hull": 100, "time": 0, "docks": 0}
