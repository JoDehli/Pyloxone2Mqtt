import copy
from ..const import LOX_MQTT_TEMPLATES

def handle_jalousie(key, value, LoxAPP3):
    topic = f"device/{key}/config"
    attributes_topic = f"device/{key}/attributes"
    dev_class = {0: "blind", 1: "shutter", 2: "curtain", 4: "curtain", 5: "curtain", 6: "awning"}.get(value["details"]["animation"], "unknown")

    payload = copy.deepcopy(LOX_MQTT_TEMPLATES["Jalousie"])
    payload["dev"].update({
        "ids": key,
        "name": value["name"],
        "suggested_area": LoxAPP3["rooms"][value["room"]]["name"]
    })
    payload["cmps"]["id1"].update({
        "unique_id": key,
        "name": value["name"],
        "position_topic": f"loxone2mqtt/{value['states']['position']}",
        "position_open": 0,
        "position_closed": 1,
        "command_topic": f"mqtt2loxone/{value['states']['up']}",
        "set_position_topic": f"mqtt2loxone/{value['states']['up']}",
        "json_attributes_topic": f"homeassistant/{attributes_topic}",
        "device_class": dev_class
    })
    if dev_class == "blinds":
        payload["cmps"]["id1"].update({
            "tilt_command_topic": f"mqtt2loxone/{value['states']['up']}",
            "tilt_status_topic": f"loxone2mqtt/{value['states']['position']}",
            "tilt_min": 0,
            "tilt_max": 100,
            "tilt_closed_value": 0,
            "tilt_opened_value": 100
        })

    attributes_payload = {
        "Loxone Device ID": key,
        "Loxone State ID": value["states"]["position"],
        "Loxone Room": LoxAPP3["rooms"][value["room"]]["name"],
        "Loxone Category": LoxAPP3["cats"][value["cat"]]["name"],
        "Loxone Control": "Jalousie",
        "HA Device Class": dev_class
    }

    return topic, attributes_topic, payload, attributes_payload
