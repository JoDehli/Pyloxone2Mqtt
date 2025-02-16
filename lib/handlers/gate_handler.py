import copy
from ..const import LOX_MQTT_TEMPLATES

def handle_gate(key, value, LoxAPP3):
    topic = f"device/{key}/config"
    attributes_topic = f"device/{key}/attributes"
    dev_class = {0: "garage", 1: "gate", 2: "gate", 3: "gate", 4: "gate", 5: "gate", 6: "gate"}.get(value["details"]["animation"], "unknown")

    payload = copy.deepcopy(LOX_MQTT_TEMPLATES["Gate"])
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
        "command_topic": f"mqtt2loxone/{value['states']['position']}",
        "set_position_topic": f"mqtt2loxone/{value['states']['position']}",
        "json_attributes_topic": f"homeassistant/{attributes_topic}",
        "device_class": dev_class
    })

    attributes_payload = {
        "Loxone Device ID": key,
        "Loxone State ID": value["states"]["position"],
        "Loxone Room": LoxAPP3["rooms"][value["room"]]["name"],
        "Loxone Category": LoxAPP3["cats"][value["cat"]]["name"],
        "Loxone Control": "Gate",
        "HA Device Class": dev_class
    }

    return topic, attributes_topic, payload, attributes_payload
