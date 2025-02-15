import logging
import json
import copy

from aiomqtt import Client, MqttError
from .event_bus import EventBus
from .const import LOX_MQTT_TEMPLATES

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class HomeAssistant:
    def __init__(
        self,
        broker: str,
        event_bus: EventBus,
        topics: list[str],
        username: str = None,
        password: str = None,
        port: int = None,
        tls: bool = False,
        tls_cert: str = None,
    ):
        """
        Initialize the MQTT client and Home Assistant integration.
        """
        self.broker = broker
        self.event_bus = event_bus
        self.topics = topics
        self.username = username
        self.password = password
        self.port = port
        self.tls = tls
        self.tls_cert = tls_cert
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 10  # seconds
        self.LoxAPP3 = ""
        self.client = None  # Persistent MQTT client

    async def connect(self):
        """
        Establish a persistent MQTT connection.
        """
        if self.client is None:
            self.client = Client(
                self.broker,
                username=self.username,
                password=self.password,
                port=self.port,
                tls_context=self._get_tls_context() if self.tls else None,
            )
            await self.client.__aenter__()
            _LOGGER.debug("Connected to MQTT broker")

    async def disconnect(self):
        """
        Disconnect the persistent MQTT connection.
        """
        if self.client:
            await self.client.__aexit__(None, None, None)
            self.client = None
            _LOGGER.debug("Disconnected from MQTT broker")

    async def generate_ha_mqtt_autodiscovery(self, messages: list[dict]):
        """
        Generate and publish Home Assistant MQTT discovery messages based on Loxone data.
        """
        publish_queue = []

        for message in messages:
            # Wait for the LoxAPP3.json
            if message["topic"].matches("loxone2mqtt/LoxAPP3"):
                self.LoxAPP3 = message["payload"]  
                # Sweep through all Control entries      
                for key, value in self.LoxAPP3["controls"].items():
                    # Check if this Loxone Control is already supported
                    if value["type"] in LOX_MQTT_TEMPLATES:
                        # Fill out all fields in the template
                        match value["type"]:
                            case "Switch":
                                topic = f"device/{key}/config"
                                attributes_topic = f"device/{key}/attributes"

                                payload = copy.deepcopy(LOX_MQTT_TEMPLATES[value["type"]])
                                payload["dev"].update({
                                    "ids": key,
                                    "name": value["name"],
                                    "suggested_area": self.LoxAPP3["rooms"][value["room"]]["name"]
                                })
                                payload["cmps"]["id1"].update({
                                    "unique_id": key,
                                    "name": value["name"],
                                    "state_topic": f"loxone2mqtt/{value['states']['active']}",
                                    #to configure
                                    "command_topic": f"mqtt2loxone/{value['states']['active']}",
                                    "json_attributes_topic": f"homeassistant/{attributes_topic}"
                                })

                                attributes_payload = {
                                    "device_id": key,
                                    "state_id": value["states"]["active"],
                                    "room": self.LoxAPP3["rooms"][value["room"]]["name"],
                                    "cat": self.LoxAPP3["cats"][value["cat"]]["name"],
                                    "device_type": "Switch"
                                }
                            case "PresenceDetector":
                                topic = f"device/{key}/config"
                                attributes_topic = f"device/{key}/attributes"

                                payload = copy.deepcopy(LOX_MQTT_TEMPLATES[value["type"]])
                                payload["dev"].update({
                                    "ids": key,
                                    "name": value["name"],
                                    "suggested_area": self.LoxAPP3["rooms"][value["room"]]["name"]
                                })
                                payload["cmps"]["id1"].update({
                                    "unique_id": key,
                                    "name": value["name"],
                                    "state_topic": f"loxone2mqtt/{value['states']['active']}",
                                    #to configure
                                    "command_topic": f"mqtt2loxone/{value['states']['active']}",
                                    "json_attributes_topic": f"homeassistant/{attributes_topic}"
                                })

                                attributes_payload = {
                                    "device_id": key,
                                    "state_id": value["states"]["active"],
                                    "room": self.LoxAPP3["rooms"][value["room"]]["name"],
                                    "cat": self.LoxAPP3["cats"][value["cat"]]["name"],
                                    "device_type": "Switch"
                                }
                            case "Jalousie":
                                topic = f"device/{key}/config"
                                attributes_topic = f"device/{key}/attributes"
                                dev_class = {0: "blind", 1: "shutter", 2: "curtain", 4: "curtain", 5: "curtain", 6: "awning"}.get(value["details"]["animation"], "unknown")
                                payload = copy.deepcopy(LOX_MQTT_TEMPLATES[value["type"]])
                                payload["dev"].update({
                                    "ids": key,
                                    "name": value["name"],
                                    "suggested_area": self.LoxAPP3["rooms"][value["room"]]["name"]
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
                                    "device_id": key,
                                    "state_id": value["states"]["position"],
                                    "room": self.LoxAPP3["rooms"][value["room"]]["name"],
                                    "cat": self.LoxAPP3["cats"][value["cat"]]["name"],
                                    "device_type": "Jalousie",
                                    "device_class": dev_class

                                }



                        # Collect messages instead of publishing immediately
                        publish_queue.append({"topic": topic, "payload": json.dumps(payload)})
                        publish_queue.append({"topic": attributes_topic, "payload": json.dumps(attributes_payload)})

        # Publish all collected messages at once
        if publish_queue:
            await self.publish(publish_queue)

    async def publish(self, messages: dict | list[dict]):
        """
        Publish MQTT messages using the persistent connection.
        """
        await self.connect()
        if isinstance(messages, list):
            for message in messages:
                await self._publish(self.client, message)
        else:
            await self._publish(self.client, messages)

    @staticmethod
    async def _publish(client: Client, message: dict):
        """
        Publish a single MQTT message with error handling.
        """
        try:
            await client.publish(f"homeassistant/{message['topic']}", str(message["payload"]))
            _LOGGER.debug(f"Published {message['topic']}: {message['payload']}")
        except MqttError as e:
            _LOGGER.error(f"Failed to publish {message['topic']}: {e}")

    def _get_tls_context(self):
        """
        Create and return an SSL/TLS context if TLS is enabled.
        """
        import ssl
        if not self.tls_cert:
            raise ValueError("TLS is enabled, but no certificate file is provided.")
        return ssl.create_default_context(cafile=self.tls_cert)
