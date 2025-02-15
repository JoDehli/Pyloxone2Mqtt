import asyncio
import logging
from typing import Any, Callable, Dict, Awaitable

from aiomqtt import Topic

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel("DEBUG")


class EventBus:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.subscribers: Dict[str, list[Callable[[Any], Awaitable[None]]]] = {}

    async def publish(self, topic: str|Topic, message: Any) -> None:
        """Publish a message to the event bus."""
        if isinstance(topic, str):
            topic = Topic(topic)
        await self.queue.put((topic, message))

    async def subscribe(self, topic: str, callback: Callable[[Any], Awaitable[None]]) -> None:
        """Subscribe to a specific topic."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)

    async def run(self) -> None:
        """Run the event bus as a separate task."""
        while True:
            topic, message = await self.queue.get()

            # Messages to Loxone from Mqtt
            if topic.matches("mqtt2loxone/#"):
                _LOGGER.debug("Received message from mqtt to Loxone topic %s: %s", topic, message)
                new_topic = Topic(str(topic).replace("mqtt2loxone/", "pyloxone/"))
                await self.queue.put((new_topic, message))
                continue

            # Messages to Mqtt from Loxone
            if topic.matches("loxone2mqtt/#"):
                #_LOGGER.debug("Received message from Loxone to mqtt topic %s: %s", topic, message)
                for mqtt_callback in self.subscribers["loxone2mqtt"]:
                    messages = []
                    for k, v in message.items():
                        new_topic = Topic(f"loxone2mqtt/{k}")
                        new_message = {"topic":new_topic, "payload": v}
                        messages.append(new_message)
                    await mqtt_callback(messages)
                continue

            if topic.matches("pyloxone/#") and "pyloxone" in self.subscribers:
                for pyloxone_callback in self.subscribers["pyloxone"]:
                    message.update({"original-topic": str(topic)})
                    await pyloxone_callback(message)
                    continue

            if topic.matches("websocket_in/#"):
                #_LOGGER.debug("Received message from websocket_in topic %s", topic)
                new_topic = Topic(str(topic).replace("websocket_in/", "loxone2mqtt/"))
                await self.queue.put((new_topic, message))
                continue
