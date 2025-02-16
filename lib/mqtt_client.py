import asyncio
import logging
import time
from gmqtt import Client
from gmqtt import constants as MQTTconstants
from gmqtt.mqtt.constants import PubAckReasonCode

from .event_bus import EventBus

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel("ERROR")

class MQTTClient:
    def __init__(
        self,
        broker: str,
        event_bus: EventBus,
        topics: list[str],
        username: str = None,
        password: str = None,
        port: int = 1883,
        tls: bool = False,
        tls_cert: str = None,
    ):
        """
        Initialize the MQTT client.

        :param broker: MQTT broker address
        :param event_bus: Shared event bus instance
        :param topics: List of topics to subscribe to
        :param username: Username for MQTT authentication (optional)
        :param password: Password for MQTT authentication (optional)
        :param tls: Whether to enable TLS (default: False)
        :param tls_cert: Path to the TLS certificate file (optional, required if tls=True)
        """
        self.broker = broker
        self.port = 8883 if tls else 1883 # TODO: Should probably be configurable
        self.event_bus = event_bus
        self.topics = topics
        self.unique_id = f"{username}_{int(time.time())}"
        self.username = username
        self.password = password
        self.port = port
        self.tls = tls
        self.tls_cert = tls_cert
        self.reconnect_delay = 10  # seconds

        # Event to signal connection status
        self._conn = asyncio.Event()

        self.client = Client(client_id=self.unique_id, logger=_LOGGER)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.set_auth_credentials(username, password)
        self.client.set_config({'reconnect_retries': MQTTconstants.UNLIMITED_RECONNECTS, 'reconnect_delay': self.reconnect_delay})

    async def connect_and_listen(self):
        """Connect to the MQTT broker, subscribe to topics, and listen for messages with reconnect logic."""
        
        # No reconnection limit for first connection
        while True:
            try:
                _LOGGER.info(f"Attempting MQTT connection to {self.broker}:{self.port}")
                await self.client.connect(
                    host=self.broker, 
                    port=self.port, 
                    ssl=self.tls,
                    )
                
                return
            except Exception as e:
                _LOGGER.error(f"Failed to connect to MQTT broker: {e}")
                _LOGGER.warning(f"Retrying connection in {self.reconnect_delay} seconds...")
                await asyncio.sleep(self.reconnect_delay)
    
    def _on_connect(self, session_present, result, properties, userdata):
        _LOGGER.info(f"Connected to MQTT Server {self.broker}:{self.port}")
        # Connection successful, subscribe to topics
        _LOGGER.info(f"Subscribing {self.topics}")
        for topic in self.topics:
            self.client.subscribe(topic)

        self._conn.set()

    async def publish_message(self, topic: str, message: str | bytes, retain: bool = False, qos: int = 0) -> None:
        try:
            if not self._conn.is_set():
                _LOGGER.warning("MQTT publish attempted without connection")
                return

            # Convert topic to string if it's not already
            topic_str = str(topic)
            
            self.client.publish(topic_str, message, qos=qos, retain=retain)
            _LOGGER.debug(f"Published: {topic_str} = {message!r} (retain={retain})")

        except Exception as e:
            _LOGGER.error(f"Fatal error during publish: {e}")
            raise

    async def publish_batch(self, messages: dict|list[dict]):
        if not self._conn.is_set():
            _LOGGER.warning("MQTT publish attempted without connection")
            return

        if isinstance(messages, dict):
            await self.publish_message(
                str(messages["topic"]), 
                messages["payload"], 
                messages["retain"] if "retain" in messages else False, 
                messages["qos"] if "qos" in messages else 0
            )
            return

        for message in messages:
            await self.publish_message(
                str(message["topic"]), 
                message["payload"], 
                message["retain"] if "retain" in message else False, 
                message["qos"] if "qos" in message else 0
            )

    async def _on_message(self, client, topic, payload: bytes, qos, properties):
        try:
            asyncio.create_task(self.event_bus.publish(
                topic, {"payload": payload.decode()}
            ))
        except Exception as e:
            _LOGGER.error(f"Error processing message: {e}")
            return PubAckReasonCode.UNSPECIFIED_ERROR
        return PubAckReasonCode.SUCCESS

    def _on_disconnect(self,client, packet, exc=None):
        _LOGGER.info("MQTT disconnected")
        if exc:
            _LOGGER.error(f"Disconnect error: {exc}")
        self._conn.clear()
