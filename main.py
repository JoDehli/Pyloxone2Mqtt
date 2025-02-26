import asyncio
import logging
import os

from dotenv import load_dotenv

from lib.event_bus import EventBus
from lib.loxone_websocket import LoxoneWebSocketClient
from lib.mqtt_client import MQTTClient
from lib.homeassistant import HomeAssistant

load_dotenv()  # Load .env file

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
_LOGGER = logging.getLogger(__name__)

async def main():
    logging.info("Starting application with log level: %s", log_level)

    # Read MQTT configuration from environment variables
    mqtt_broker = os.getenv("MQTT_BROKER", None)
    mqtt_username = os.getenv("MQTT_USERNAME")
    mqtt_password = os.getenv("MQTT_PASSWORD")
    mqtt_port = int(os.getenv("MQTT_PORT", 1883))
    mqtt_tls = os.getenv("MQTT_TLS", "false").lower() == "true"
    mqtt_tls_cert = os.getenv("MQTT_TLS_CERT")
    mqtt_topics = os.getenv("MQTT_TOPICS", "mqtt2loxone/#").split(
        ","
    )  # Default: subscribe to mqtt2loxone

    # Read FastAPI and WebSocket configuration
    # start_fastapi = os.getenv("START_FASTAPI", "true").lower() == "true"
    # start_websocket = os.getenv("START_WEBSOCKET", "true").lower() == "true"

    # Loxone WebSocket configuration
    websocket_url = os.getenv("WEBSOCKET_URL", None)
    websocket_port = os.getenv("WEBSOCKET_PORT", "443")  # Default: secure WebSocket
    websocket_username = os.getenv("WEBSOCKET_USERNAME")
    websocket_password = os.getenv("WEBSOCKET_PASSWORD")

    # Instantiate the event bus
    event_bus = EventBus()

    # # Initialize LoxoneWebsocket
    websocket_client = (
        LoxoneWebSocketClient(
            host=websocket_url,
            port=websocket_port,
            username=websocket_username,
            password=websocket_password,
            event_bus=event_bus,
        )
    )

    # Initialize MQTT client
    mqtt_client = MQTTClient(
        broker=mqtt_broker,
        event_bus=event_bus,
        topics=mqtt_topics,
        username=mqtt_username,
        password=mqtt_password,
        port=mqtt_port,
        tls=mqtt_tls,
        tls_cert=mqtt_tls_cert,
    )

    # Initialize HomeAssistant
    homeassistant = HomeAssistant(
        event_bus=event_bus,
    )    

    # Standard subscriptions
    await event_bus.subscribe("pyloxone", websocket_client.send)
    await event_bus.subscribe("loxone2mqtt", mqtt_client.publish_batch)
    await event_bus.subscribe("homeassistant", mqtt_client.publish_batch)
    #subscribe to loxone2mqtt topic so the HA MQTT AutoDiscovery can be started
    await event_bus.subscribe("loxone2mqtt", homeassistant.generate_ha_mqtt_autodiscovery)
    ###
    # # Start FastAPI as a task
    # api_task = asyncio.create_task(uvicorn.run(app, host="0.0.0.0", port=8000))
    #    # Start tasks
    # await event_bus.subscribe("mqtt_out", mqtt_client.publish)

    tasks = [
        asyncio.create_task(mqtt_client.connect_and_listen()),
        asyncio.create_task(websocket_client.connect_and_listen()),
        asyncio.create_task(event_bus.run()),
    ]
    try:
        await asyncio.gather(*tasks)
    except RuntimeError as e:
        _LOGGER.error("Application error: %s", e)
        # Optionally cleanup here
        return

if __name__ == "__main__":
    asyncio.run(main())