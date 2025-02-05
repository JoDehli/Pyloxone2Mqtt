import asyncio
import logging

from aiomqtt import Client, MqttError

from .event_bus import EventBus

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel("DEBUG")

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

    async def connect_and_listen(self):
        """Connect to the MQTT broker, subscribe to topics, and listen for messages with reconnect logic."""

        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                async with Client(
                        self.broker,
                        port=self.port,
                        username=self.username,
                        password=self.password,
                        tls_context=self._get_tls_context() if self.tls else None,
                ) as client:
                    # Subscribe to the specified topics

                    for topic in self.topics:
                        await client.subscribe(topic)

                    self.reconnect_attempts = 0
                    # Listen for messages and publish them to the event bus
                    _LOGGER.debug("Connected to MQTT broker %s", self.broker)
                    async for message in client.messages:
                        await self.event_bus.publish(
                            message.topic, {"payload": message.payload.decode()}
                        )
                break  # Exit the loop if connection is successful

            except Exception as e:
                _LOGGER.error("MQTT connection failed: %s. Reconnecting in %d seconds...", e, self.reconnect_delay)
                self.reconnect_attempts += 1
                await asyncio.sleep(self.reconnect_delay)

        if self.reconnect_attempts == self.max_reconnect_attempts:
            _LOGGER.error("Max reconnect attempts reached. Could not establish MQTT connection.")
            raise RuntimeError("Max reconnect attempts reached. Exiting application.")

    async def publish(self, message: dict|list[dict]):
        """Publish a message to an MQTT topic."""
        async with Client(
            self.broker,
            username=self.username,
            password=self.password,
            tls_context=self._get_tls_context() if self.tls else None,
        ) as client:
            if isinstance(message, list):
                _LOGGER.debug("Publishing batch of %d messages", len(message))
                for m in message:
                     await self._publish(client, m)
            else:
                await self._publish(client, message)

    @staticmethod
    async def _publish(client: Client, message: dict):
        """Send a single message with error handling."""
        try:
            await client.publish(str(message["topic"]), message["payload"])
            _LOGGER.debug("Published to %s: %s", message["topic"], message["payload"])
        except MqttError as e:
            _LOGGER.error("Failed to publish message to %s: %s", str(message["topic"]), e)

    def _get_tls_context(self):
        """Create and return an SSL/TLS context if TLS is enabled."""
        import ssl

        if not self.tls_cert:
            raise ValueError("TLS is enabled, but no certificate file is provided.")

        tls_context = ssl.create_default_context(cafile=self.tls_cert)
        return tls_context
