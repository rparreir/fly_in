from models import Zone, Connection, Network, ParsingError


VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}


class Validator():
    def validate_nb_drones(self, nb_drones: int) -> None:
        if nb_drones <= 0:
            raise ParsingError(f"invalid number of drones {nb_drones}")

    def validate_zone(self, zone: Zone, network: Network) -> None:
        if zone.zone_type not in VALID_ZONE_TYPES:
            raise ParsingError(f"invalid zone type '{zone.zone_type}'")
        if zone.max_drones <= 0:
            raise ParsingError(f"max_drones must be > 0: {zone.max_drones}")
        if "-" in zone.name:
            raise ParsingError(f"invalid name "
                               f"'{zone.name}' cant containe '-' ")
        if zone.name in network.zones:
            raise ParsingError(f"duplicate zone name '{zone.name}'")

    def validate_connection(self, conn: Connection) -> None:
        if conn.max_link_cap <= 0:
            raise ParsingError(f"invalid number of max link "
                               f"connections {conn.max_link_cap}")

    def validate_network(self, network: Network) -> None:
        if network.start is None:
            raise ParsingError("No start hub defined!")
        if network.end is None:
            raise ParsingError("No end hub defined!")

        seen: set = set()
        for conn in network.connections:
            if conn.zone_a not in network.zones:
                raise ParsingError(f"unknown zone '{conn.zone_a}'")
            if conn.zone_b not in network.zones:
                raise ParsingError(f"unknown zone '{conn.zone_b}'")

            key = frozenset({conn.zone_a, conn.zone_b})
            if key in seen:
                raise ParsingError(f"duplicate connection "
                                   f"{conn.zone_a}-{conn.zone_b}")
            seen.add(key)
