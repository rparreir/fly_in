"""Data model for the drone network: zones, connections and graph."""
from enum import Enum
from typing import Optional


class ParsingError(Exception):
    """Raised when a map file is syntactically or semantically invalid."""


class HubType(Enum):
    """The kind of hub: start, end, or intermediate."""

    START_HUB = "start_hub"
    END_HUB = "end_hub"
    HUB = "hub"


class Zone():
    """A network node with coordinates and optional metadata."""

    def __init__(self,
                 hub_type: HubType,
                 name: str,
                 x: int,
                 y: int,
                 zone_type: str = "normal",
                 color: Optional[str] = None,
                 max_drones: int = 1
                 ):
        """Store role, name, position, type, colour and capacity."""
        self.hub_type = hub_type
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones


class Connection():
    """A bidirectional link between two zones."""

    def __init__(self, zone_a: str, zone_b: str, max_link_cap: int = 1):
        """Store the two zone names and the link capacity."""
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_cap = max_link_cap


class Network():
    """The full network: drones, zones, connections and adjacency."""

    def __init__(self) -> None:
        """Initialise an empty network."""
        self.nb_drones: int = 0
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.start: Optional[Zone] = None
        self.end: Optional[Zone] = None
        self.adjacency: dict[str, list[str]] = {}

    def build_adjacency(self) -> None:
        """Build the adjacency dict from the connections."""
        for name in self.zones:
            self.adjacency[name] = []
        for con in self.connections:
            self.adjacency[con.zone_a].append(con.zone_b)
            self.adjacency[con.zone_b].append(con.zone_a)
