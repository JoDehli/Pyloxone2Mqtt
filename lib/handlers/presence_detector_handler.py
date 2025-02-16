import copy
from ..const import LOX_MQTT_TEMPLATES

def handle_presence_detector(key, value, LoxAPP3):
    topic = f"device/{key}/config"
    attributes_topic = f"device/{key}/attributes"

    payload = copy.deepcopy(LOX_MQTT_TEMPLATES["PresenceDetector"])
    payload["dev"].update({
        "ids": key,
        "name": value["name"],
        "suggested_area": LoxAPP3["rooms"][value["room"]]["name"]
    })
    payload["cmps"]["id1"].update({
        "unique_id": key,
        "name": value["name"],
        "state_topic": f"loxone2mqtt/{value['states']['active']}",
        "command_topic": f"mqtt2loxone/{value['states']['active']}",
        "json_attributes_topic": f"homeassistant/{attributes_topic}"
    })

    attributes_payload = {
        "Loxone Device ID": key,
        "Loxone State ID": value["states"]["active"],
        "Loxone Room": LoxAPP3["rooms"][value["room"]]["name"],
        "Loxone Category": LoxAPP3["cats"][value["cat"]]["name"],
        "Loxone Control": "PresenceDetector"
    }

    return topic, attributes_topic, payload, attributes_payload
