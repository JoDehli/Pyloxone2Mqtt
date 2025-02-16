import logging
import json

from aiomqtt import Topic
from .event_bus import EventBus
from .const import LOX_MQTT_TEMPLATES
from .handlers import switch_handler, presence_detector_handler, jalousie_handler, gate_handler, lightcontrollerv2_handler

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class HomeAssistant:
    def __init__(
        self,
        event_bus: EventBus,
    ):
        self.event_bus = event_bus
        self.LoxAPP3 = ""

    async def generate_ha_mqtt_autodiscovery(self, messages: list[dict]):
        publish_queue = []

        for message in messages:
            if message["topic"].matches("loxone2mqtt/LoxAPP3"):
                self.LoxAPP3 = message["payload"]

                for key, value in self.LoxAPP3["controls"].items():
                    if value["type"] in LOX_MQTT_TEMPLATES:
                        handler = self._get_handler(value["type"])
                        if handler:
                            topic, attributes_topic, payload, attributes_payload = handler(key, value, self.LoxAPP3)
                            publish_queue.append({"topic": Topic(f"homeassistant/{attributes_topic}"), "payload": json.dumps(attributes_payload)})  
                            publish_queue.append({"topic": Topic(f"homeassistant/{topic}"), "payload": json.dumps(payload)})  


        # Publish all collected messages at once
        if publish_queue:
            await self.event_bus.publish_batch(publish_queue)

    def _get_handler(self, control_type: str):
        handlers = {
            "Switch": switch_handler.handle_switch,
            "PresenceDetector": presence_detector_handler.handle_presence_detector,
            "Jalousie": jalousie_handler.handle_jalousie,
            "Gate": gate_handler.handle_gate,
            "LightControllerV2": lightcontrollerv2_handler.handle_lightcontrollerv2,
        }
        return handlers.get(control_type)

    # async def publish(self, messages: dict | list[dict]):
    #     """
    #     Publish MQTT messages using the persistent connection.
    #     """
    #     if isinstance(messages, list):
    #         for message in messages:
    #             await self.event_bus.publish(self.client, message)
    #     else:
    #         await self.event_bus.publish(self.client, messages)

    # @staticmethod
    # async def _publish(client: Client, message: dict):
    #     """
    #     Publish a single MQTT message with error handling.
    #     """
    #     try:
    #         await client.publish(f"homeassistant/{message['topic']}", str(message["payload"]))
    #         _LOGGER.debug(f"Published {message['topic']}: {message['payload']}")
    #     except MqttError as e:
    #         _LOGGER.error(f"Failed to publish {message['topic']}: {e}")

    # def _get_tls_context(self):
    #     """
    #     Create and return an SSL/TLS context if TLS is enabled.
    #     """
    #     import ssl
    #     if not self.tls_cert:
    #         raise ValueError("TLS is enabled, but no certificate file is provided.")
    #     return ssl.create_default_context(cafile=self.tls_cert)
