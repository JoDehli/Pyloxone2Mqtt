LOX_MQTT_TEMPLATES = {
    "Switch" : {
        "dev": {
            "ids": "dev_id",
            "mf": "Loxone",
            "mdl": "Switch",
            "suggested_area": "",
        },
        "o": {"name": "Loxone2MQTT"},
        "cmps": {
            "id1": {
                "p": "switch",
                "payload_on": "1.0",
                "payload_off": "0.0",
                "state_on": "1.0",
                "state_off": "0.0",
                "command_template": "{{ 'on' if value == '1.0' else 'off' }}",
                "json_attributes_template": "{{ value_json | tojson }}",
                "device_class": "switch",
                "retain": True
            },
        },
        "qos": 2
    },
    "PresenceDetector" : {
        "dev": {
            "ids": "dev_id",
            "mf": "Loxone",
            "mdl": "Presence Detector",
            "suggested_area": "",
        },
        "o": {"name": "Loxone2MQTT"},
        "cmps": {
            "id1": {
                "p": "binary_sensor",
                "payload_on": "1.0",
                "payload_off": "0.0",
                "state_on": "1.0",
                "state_off": "0.0",
                "command_template": "{{ 'on' if value == '1.0' else 'off' }}",
                "json_attributes_template": "{{ value_json | tojson }}",
                "device_class": "presence",
                "retain": True
            }
        },
        "qos": 2
    },
    "Jalousie": {
    "dev": {
        "ids": "dev_id",
        "mf": "Loxone",
        "mdl": "Jalousie",
        "suggested_area": "",
    },
    "o": {"name": "Loxone2MQTT"},
    "cmps": {
        "id1": {
            "p": "cover",
            "payload_open": "1.0",
            "payload_close": "0.0",
            "position_open": "100",
            "position_closed": "0",
            "command_template": "{{ 'open' if value == '1.0' else 'close' }}",
            "json_attributes_template": "{{ value_json | tojson }}",
            "retain": True
        }
    },
    "qos": 2
    }

}