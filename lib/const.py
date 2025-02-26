cfmt = r"""(%(?:(?:[-+0 #]{0,5})(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:h|l|ll|w|I|I32|I64)?[cCdiouxXeEfgGaAnpsSZ])|%%)"""

LOX_MQTT_TEMPLATES = {
    "Switch" : {
        "dev": {
            "mf": "Loxone",
            "mdl": "Switch",
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
            "mf": "Loxone",
            "mdl": "Presence Detector",
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
            "mf": "Loxone",
            "mdl": "Jalousie",
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
        },
    "Gate": {
        "dev": {
            "mf": "Loxone",
            "mdl": "Gate",
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
                "device_class": None,
                "retain": True
            }
        },
        "qos": 2
#         },
#    "LightControllerV2": {
#         "dev": {
#             "mf": "Loxone",
#             "mdl": "LightControllerV2",
#         },
#         "o": {"name": "Loxone2MQTT"},
#         "cmps": {
#             "id1": {
#                 "p": "cover",
#                 "json_attributes_template": "{{ value_json | tojson }}",
#                 "retain": True
#             }
#         },
#         "qos": 2
        },
    "InfoOnlyAnalog" : {
        "dev": {
            "mf": "Loxone",
            "mdl": "InfoOnlyAnalog",
        },
        "o": {"name": "Loxone2MQTT"},
        "cmps": {
            "id1": {
                "p": "sensor",
                "json_attributes_template": "{{ value_json | tojson }}",
                "retain": True
            },
        },
        "qos": 2
    },
    "InfoOnlyDigital" : {
        "dev": {
            "mf": "Loxone",
            "mdl": "InfoOnlyDigital",
        },
        "o": {"name": "Loxone2MQTT"},
        "cmps": {
            "id1": {
                "p": "binary_sensor",
                "payload_off": "0.0",
                "payload_on": "1.0",
                "json_attributes_template": "{{ value_json | tojson }}",
                "retain": True
            },
        },
        "qos": 2
    },
    "EnergyManager2" : {
        "dev": {
            "mf": "Loxone",
            "mdl": "EnergyManager2",
        },
        "o": {"name": "Loxone2MQTT"},
        "cmps": {
            "Gpwr": {
                "p": "sensor",
                "name": "Grid Power",
                "suggested_display_precision": 3,
                "unit_of_measurement": "kW",
                "state_class": "measurement",
                "device_class": "power",
                "json_attributes_template": "{{ value_json | tojson }}",
                "retain": True
            },
            "Spwr": {
                "p": "sensor",
                "name": "Storage Power",
                "suggested_display_precision": 3,
                "unit_of_measurement": "kW",
                "state_class": "measurement",
                "device_class": "power",
                "json_attributes_template": "{{ value_json | tojson }}",
                "retain": True
            },       
            "Ppwr": {
                "p": "sensor",
                "name": "Production Power",
                "suggested_display_precision": 3,
                "unit_of_measurement": "kW",
                "state_class": "measurement",
                "device_class": "power",
                "json_attributes_template": "{{ value_json | tojson }}",
                "retain": True
            },   
            "Ssoc": {
                "p": "sensor",
                "name": "Storage State of Charge",
                "suggested_display_precision": 2,
                "unit_of_measurement": "%",
                "state_class": "measurement",
                "device_class": "battery",
                "json_attributes_template": "{{ value_json | tojson }}",
                "retain": True
            },
            "MinSoc": {
                "p": "number",
                "name": "Minimum Storage State of Charge",
                "step": 1,
                "unit_of_measurement": "%",
                "mode": "box",
                "device_class": "battery",
                "json_attributes_template": "{{ value_json | tojson }}",
                "retain": True
            },       
            "MaxSpwr": {
                "p": "number",
                "name": "Max Storage Power",
                "suggested_display_precision": 3,
                "unit_of_measurement": "kW",
                "mode": "box",
                "device_class": "power",
                "json_attributes_template": "{{ value_json | tojson }}",
                "retain": True
            },
            "manage": {
                "p": "button",
                "name": "Manage",
                "json_attributes_template": "{{ value_json | tojson }}",
                "payload_press": "",
                "retain": True
            },                                                             
        },
        "qos": 2
    }                        
}