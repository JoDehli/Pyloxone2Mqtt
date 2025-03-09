from dataclasses import dataclass

@dataclass
class Room:
    name: str
    uuid: str

@dataclass
class Category:
    name: str
    uuid: str

@dataclass
class Device:
    type: str
    name: str
    room: str
    category: str
