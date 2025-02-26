import logging
import json
import time

from aiomqtt import Topic
from .event_bus import EventBus
from .const import LOX_MQTT_TEMPLATES
from .handlers import switch_handler, presence_detector_handler, jalousie_handler, gate_handler, lightcontrollerv2_handler, infoonlyanalog_handler, infoonlydigital_handler, energymanager2_handler

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
        publish_queue_devices = []
        publish_queue_attributes = []


        for message in messages:
            if message["topic"].matches("loxone2mqtt/LoxAPP3"):
                self.LoxAPP3 = message["payload"]

                for key, value in self.LoxAPP3["controls"].items():
                    if value["type"] in LOX_MQTT_TEMPLATES:
                        handler = self._get_handler(value["type"])
                        if handler:
                            topic, payload, attributes = handler(key, value, self.LoxAPP3)
                            publish_queue_devices.append({"topic": Topic(f"homeassistant/{topic}"), "payload": json.dumps(payload)})  
                            for top, attr in attributes.items():
                                publish_queue_attributes.append({"topic": Topic(f"homeassistant/{top}"), "payload": json.dumps(attr)})  

        #
        # to fix: this does not work, as the attributes are not published before the device is discovered
        # temporary work around: launch code twice, so on reload the attributes are already existing
        #
        # Publish attributes first, so they are available when the device is discovered
        if publish_queue_attributes:
            await self.event_bus.publish_batch(publish_queue_attributes)
        # Publish all collected messages at once
        if publish_queue_devices:
            await self.event_bus.publish_batch(publish_queue_devices)

    def _get_handler(self, control_type: str):
        handlers = {
            "Switch": switch_handler.handle_switch,
            "PresenceDetector": presence_detector_handler.handle_presence_detector,
            "Jalousie": jalousie_handler.handle_jalousie,
            "Gate": gate_handler.handle_gate,
            "LightControllerV2": lightcontrollerv2_handler.handle_lightcontrollerv2,
            "InfoOnlyAnalog": infoonlyanalog_handler.handle_infoonlyanalog,
            "InfoOnlyDigital": infoonlydigital_handler.handle_infoonlydigital,
            "EnergyManager2": energymanager2_handler.handle_energymanager2,
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
