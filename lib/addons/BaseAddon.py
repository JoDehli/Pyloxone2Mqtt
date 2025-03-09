from abc import ABC, abstractmethod
from lib.event_bus import EventBus


class Addon(ABC):
    MQTT_TEMPLATES = ""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.structure_file = None

    @abstractmethod
    async def generate_ha_mqtt_autodiscovery(self, messages: list[dict]) -> None:
        pass
