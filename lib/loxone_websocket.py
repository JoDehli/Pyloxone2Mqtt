import asyncio
import logging

import aiofiles
import websockets
from aiomqtt import Topic

from .event_bus import EventBus
from .pyloxone_api.connection import LoxoneConnection

_LOGGER = logging.getLogger(__name__)
#_LOGGER.setLevel("DEBUG")


class LoxoneWebSocketClient:
    def __init__(self, host:str, port:str, username:str, password:str, event_bus: EventBus):

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.event_bus = event_bus

    async def publish_to_eventbus(self, message: dict) -> None:
        #_LOGGER.debug("Publishing message to event bus websocket_in %s", message)
        await self.event_bus.publish(Topic("websocket_in/"), message)

    @staticmethod
    async def token_safe(data) -> None:
         async with aiofiles.open("token.json", "w") as file:
            await file.write(str(data))

    @staticmethod
    async def token_load() -> None:
        try:
            async with aiofiles.open("token.json", "r") as file:
                content = await file.read()
                try:
                    content = eval(content)
                except:
                    return None
                return content
        except FileNotFoundError:
            return None

    async def connect_and_listen(self) -> None:
        reconnect_attempts = 0
        max_reconnect_attempts = 15
        reconnect_delay = 10  # seconds
        while reconnect_attempts < max_reconnect_attempts:
            try:
                token = await self.token_load()
                api = LoxoneConnection(
                    host=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    token=token,
                    token_safe_callback=self.token_safe
                )
                asyncio.create_task(api.start_listening(callback=self.publish_to_eventbus))
                
                break  # Exit the loop if connection is successful

            except Exception as e:
                _LOGGER.error("Connection failed: %s. Reconnecting in %d seconds...", e, reconnect_delay)
                reconnect_attempts += 1
                await asyncio.sleep(reconnect_delay)

        if reconnect_attempts == max_reconnect_attempts:
            _LOGGER.error("Max reconnect attempts reached. Could not establish connection.")

    async def send(self, message: dict):
        """Send a message to the WebSocket."""
        _LOGGER.info("Sending message to WebSocket %s", message )
        #async with websockets.connect(self.uri) as websocket:
        #    await websocket.send(message["payload"])
