import copy
import re
from ..const import LOX_MQTT_TEMPLATES, cfmt

def handle_energymanager2(key, value, LoxAPP3):

    topic = f"device/{key}/config"
    attributes = {}

    # todo: Evaluate HasSsoc & HasSpwr
    
    payload = copy.deepcopy(LOX_MQTT_TEMPLATES["EnergyManager2"])
    payload["dev"].update({
        "ids": key,
        "name": value["name"],
        "suggested_area": LoxAPP3["rooms"][value["room"]]["name"]
    })
    for state in ["Gpwr","Spwr","Ppwr"]:
        attributes_topic = f"device/{key}/attributes_{state}"
        payload["cmps"][state].update({
            "unique_id": f"{key}_{state}",
            "state_topic": f"loxone2mqtt/{value['states'][state]}",
            "json_attributes_topic": f"homeassistant/{attributes_topic}_state",
        })
        attributes[attributes_topic]= {
            "Loxone Device ID": key,
            "Loxone State ID": value["states"][state],
            "Loxone Room": LoxAPP3["rooms"][value["room"]]["name"],
            "Loxone Category": LoxAPP3["cats"][value["cat"]]["name"],
            "Loxone Control": "EnergyManager2",
            "HA Device Class": "power",
            "HA State Class": "measurement"
            }

    for state in ["Ssoc"]:
        attributes_topic = f"device/{key}/attributes_{state}"
        payload["cmps"][state].update({
            "unique_id": f"{key}_{state}",
            "state_topic": f"loxone2mqtt/{value['states'][state]}",
            "json_attributes_topic": f"homeassistant/{attributes_topic}_state",
        })
        attributes[attributes_topic]= {
            "Loxone Device ID": key,
            "Loxone State ID": value["states"][state],
            "Loxone Room": LoxAPP3["rooms"][value["room"]]["name"],
            "Loxone Category": LoxAPP3["cats"][value["cat"]]["name"],
            "Loxone Control": "EnergyManager2",
            "HA Device Class": "battery",
            "HA State Class": "measurement"
            }    

    for state in ["MinSoc","MaxSpwr"]:
        attributes_topic = f"device/{key}/attributes_{state}"
        payload["cmps"][state].update({
            "unique_id": f"{key}_{state}",
            "state_topic": f"loxone2mqtt/{value['states'][state]}",
            "command_topic": f"mqtt2loxone/{value['uuidAction']}'/set'{{state}}",
            "json_attributes_topic": f"homeassistant/{attributes_topic}_state",
        })
        attributes[attributes_topic]= {
            "Loxone Device ID": key,
            "Loxone State ID": value["states"][state],
            "Loxone Room": LoxAPP3["rooms"][value["room"]]["name"],
            "Loxone Category": LoxAPP3["cats"][value["cat"]]["name"],
            "Loxone Control": "EnergyManager2",
            "HA Device Class": "battery"
            }             

    attributes_topic = f"device/{key}/attributes_manage"

    payload["cmps"]["manage"].update({
        "unique_id": f"{key}_manage",
        "command_topic": f"mqtt2loxone/{value['uuidAction']}'/manage'",
        "json_attributes_topic": f"homeassistant/{attributes_topic}_state",
    })
    attributes[attributes_topic]= {
        "Loxone Device ID": key,
        "Loxone State ID": value["states"][state],
        "Loxone Room": LoxAPP3["rooms"][value["room"]]["name"],
        "Loxone Category": LoxAPP3["cats"][value["cat"]]["name"],
        "Loxone Control": "EnergyManager2"
        } 

    return topic, payload, attributes