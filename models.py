from enum import Enum
from typing import Optional


class HubType(Enum):
    START_HUB = "start_hub"
    END_HUB = "end_hub"
    HUB = "hub"


class Zone():
    def __init__(self,
                 hub_type: HubType,
                 name: str,
                 x: int,
                 y: int,
                 zone_type: str = "normal",
                 color: Optional[str] = None,
                 max_drones: int = 1
                 ):
        self.hub_type = hub_type
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones


class Connection():
    def __init__(self, zone_a: str, zone_b: str, max_link_cap: int = 1):
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_cap = max_link_cap
