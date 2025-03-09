from lib.addons.BaseAddon import Addon

# https://www.home-assistant.io/integrations/mqtt/
class HomeAssistant(Addon):
    MQTT_TEMPLATES = {
        "Switch": {
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
                    "retain": True,
                },
            },
            "qos": 2,
        }
    }

    async def generate_ha_mqtt_autodiscovery(self, messages: list[dict]) -> None:
        for message in messages:
            if message["topic"].matches("loxone2mqtt/LoxAPP3"):
                self.structure_file = message["payload"]

            if self.structure_file:
                for key, value in self.structure_file["controls"].items():
                    if value["type"] in self.MQTT_TEMPLATES:
                        await self.event_bus.publish(topic="mqttDiscovery", message={"uuid": key, "type":value["type"]})