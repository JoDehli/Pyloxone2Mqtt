import copy
import logging
from ..const import LOX_MQTT_TEMPLATES

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

def handle_lightcontrollerv2(key, value, LoxAPP3):
    topic = f"device/{key}/config"
    attributes_topic = f"device/{key}/attributes"
    hasMasterValue = "masterValue" in value["details"]
    hasMasterColor = "masterColor" in value["details"]
    activeMoods = value["states"]["activeMoods"]
    moodList = value["states"]["moodList"]
    circuitNames = value["states"]["circuitNames"]

    #scene when hasMasterValue and/or hasmasterColor

    payload = copy.deepcopy(LOX_MQTT_TEMPLATES["LightControllerV2"])
    payload["dev"].update({
        "ids": key,
        "name": value["name"],
        "suggested_area": LoxAPP3["rooms"][value["room"]]["name"]
    })
    payload["cmps"]["id1"].update({
        "unique_id": key,
        "name": value["name"],
        "json_attributes_topic": f"homeassistant/{attributes_topic}",
        "device_class": ""
    })

    attributes_payload = {
        "Loxone Device ID": key,
        #"Loxone State ID": value["states"]["position"],
        "Loxone Room": LoxAPP3["rooms"][value["room"]]["name"],
        "Loxone Category": LoxAPP3["cats"][value["cat"]]["name"],
        "Loxone Control": "LightControllerV2",
        "HA Device Class": ""
    }

    return topic, payload, {attributes_topic: attributes_payload}