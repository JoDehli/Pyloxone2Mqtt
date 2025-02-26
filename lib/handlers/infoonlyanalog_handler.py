import copy
import re
from ..const import LOX_MQTT_TEMPLATES, cfmt



def _parse_digits_after_decimal(format_string):
    """Parse digits after the decimal point from the format string."""
    pattern = r"\.(\d+)"
    match = re.search(pattern, format_string)
    if match:
        digits = int(match.group(1))
        return digits
    return None

def _clean_unit(lox_format):
    search = re.search(cfmt, lox_format, flags=re.X)
    if search:
        unit = lox_format.replace(search.group(0).strip(), "").strip()
        if unit == "%%":
            unit = unit.replace("%%", "%")
        return unit
    else:
        return lox_format

SENSOR_TYPES = {
        "temperature": {
            "name": "Temperature",
            "suggested_display_precision": 1,
            "loxone_format_string": "°C",
            "native_unit_of_measurement": "°C",
            "state_class": "measurement",
            "device_class": "temperature",
        },
        "temperature_fahrenheit": {
            "name": "Temperature",
            "suggested_display_precision": 1,
            "loxone_format_string": "F",
            "native_unit_of_measurement": "F",
            "state_class": "measurement",
            "device_class": "temperature",
        },
        "windstrength": {
            "name": "Wind Strength",
            "suggested_display_precision": 1,
            "loxone_format_string": "km/h",
            "native_unit_of_measurement": "km/h",
            "state_class": "measurement",
            "device_class": "wind_speed",
        },
        "kwh": {
            "name": "Kilowatthour",
            "suggested_display_precision": 1,
            "loxone_format_string": "kWh",
            "native_unit_of_measurement": "kWh",
            "state_class": "total_increasing",
            "device_class": "energy",
        },
        "wh": {
            "name": "Watthour",
            "suggested_display_precision": 1,
            "loxone_format_string": "Wh",
            "native_unit_of_measurement": "Wh",
            "state_class": "total_increasing",
            "device_class": "energy",
        },
        "power": {
            "name": "Watt",
            "suggested_display_precision": 1,
            "loxone_format_string": "W",
            "native_unit_of_measurement": "W",
            "state_class": "measurement",
            "device_class": "power",
        },
        "light_level": {
            "name": "Light Level",
            "loxone_format_string": "lx",
            "native_unit_of_measurement": "lx",
            "state_class": "measurement",
            "device_class": "illuminance",
        },
        "humidity_or_battery": {
            "name": "Humidity or Battery",
            "suggested_display_precision": 1,
            "loxone_format_string": "%",
            "native_unit_of_measurement": "%",
            "state_class": "measurement",
            "device_class": "battery",
        },
    }

def handle_infoonlyanalog(key, value, LoxAPP3):

    SENSOR_FORMATS = {desc["loxone_format_string"]: sensor_key for sensor_key, desc in SENSOR_TYPES.items()}
    
    attr_native_unit_of_measurement = _clean_unit(value["details"]["format"])
    attr_suggested_display_precision = _parse_digits_after_decimal(value["details"]["format"])
    device_class = SENSOR_TYPES[SENSOR_FORMATS.get(attr_native_unit_of_measurement)]["device_class"] if attr_native_unit_of_measurement in SENSOR_FORMATS else None
    state_class = SENSOR_TYPES[SENSOR_FORMATS.get(attr_native_unit_of_measurement)]["state_class"] if attr_native_unit_of_measurement in SENSOR_FORMATS else "measurement"

    topic = f"device/{key}/config"
    attributes_topic = f"device/{key}/attributes"


    payload = copy.deepcopy(LOX_MQTT_TEMPLATES["InfoOnlyAnalog"])
    payload["dev"].update({
        "ids": key,
        "name": value["name"],
        "suggested_area": LoxAPP3["rooms"][value["room"]]["name"]
    })
    payload["cmps"]["id1"].update({
        "unique_id": key,
        "name": value["name"],
        "state_topic": f"loxone2mqtt/{value['states']['value']}",
        "suggested_display_precision": attr_suggested_display_precision,
        "json_attributes_topic": f"homeassistant/{attributes_topic}",
        "unit_of_measurement": attr_native_unit_of_measurement,
        "device_class": device_class,
        "state_class": state_class
    })

    attributes_payload = {
        "Loxone Device ID": key,
        "Loxone State ID": value["states"]["value"],
        "Loxone Room": LoxAPP3["rooms"][value["room"]]["name"],
        "Loxone Category": LoxAPP3["cats"][value["cat"]]["name"],
        "Loxone Control": "InfoOnlyDigital",
        "HA Device Class": device_class,
        "HA State Class": state_class
    }

    return topic, payload, {attributes_topic: attributes_payload}