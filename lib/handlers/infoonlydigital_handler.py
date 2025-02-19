import copy
from ..const import LOX_MQTT_TEMPLATES

def handle_infoonlydigital(key, value, LoxAPP3):

    topic = f"device/{key}/config"
    attributes_topic = f"device/{key}/attributes"


    payload = copy.deepcopy(LOX_MQTT_TEMPLATES["InfoOnlyDigital"])
    payload["dev"].update({
        "ids": key,
        "name": value["name"]
    })

    payload["cmps"]["id1"].update({
        "unique_id": key,
        "name": value["name"],
        "state_topic": f"loxone2mqtt/{value['states']['active']}",
        "json_attributes_topic": f"homeassistant/{attributes_topic}",
    })

    attributes_payload = {
        "Loxone Device ID": key,
        "Loxone State ID": value["states"]["active"],
        "Loxone Category": LoxAPP3["cats"][value["cat"]]["name"],
        "Loxone Control": "InfoOnlyDigital",
        "HA Device Class": "None"
    }

    if "room" in value:
        attributes_payload.update({
            "Loxone Room": LoxAPP3["rooms"][value["room"]]["name"]
        }) 

        
    return topic, attributes_topic, payload, attributes_payload