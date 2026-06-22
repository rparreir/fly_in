import sys
from models import HubType, Zone, Network, Connection, ParsingError
from validator import Validator


class Parser():
    def __init__(self) -> None:
        self.first_line = False

        self.network = Network()
        self.validator = Validator()

    def open_map(self, arg_map: str) -> None:
        try:
            with open(arg_map) as map:
                for idx, line in enumerate(map, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    self.build_network(line, idx)

                    if self.first_line is False:
                        raise ParsingError("nb_drones must be in the first "
                                           "line!")
            self.validator.validate_network(self.network)
        except (FileNotFoundError, ParsingError) as e:
            print(f"Error: {e}")
            sys.exit(1)

    def build_network(self, line: str, idx: int) -> None:
        try:
            _, value = line.split(':', 1)

            if line.startswith("nb_drones"):
                if self.network.nb_drones:
                    raise ParsingError("can only define nb_drones once")
                self.first_line = True
                num_drones = int(value.strip())
                self.validator.validate_nb_drones(num_drones)
                self.network.nb_drones = num_drones
            elif line.startswith("start_hub"):
                if self.network.start:
                    raise ParsingError("can only define starting hub once")
                start = self.parse_zone(value,
                                        HubType.START_HUB)
                self.validator.validate_zone(start, self.network)
                self.network.start = start
                self.network.zones[start.name] = start
            elif line.startswith("end_hub"):
                if self.network.end:
                    raise ParsingError("can only define ending hub once")
                end = self.parse_zone(value, HubType.END_HUB)
                self.validator.validate_zone(end, self.network)
                self.network.end = end
                self.network.zones[end.name] = end
            elif line.startswith("hub"):
                hubs = self.parse_zone(value, HubType.HUB)
                self.validator.validate_zone(hubs, self.network)
                self.network.zones[hubs.name] = hubs
            elif line.startswith("connection"):
                connect = self.parse_connections(value)
                self.validator.validate_connection(connect)
                self.network.connections.append(connect)
        except (ValueError, IndexError, TypeError, ParsingError) as e:
            print(f"Error in (line {idx}): {e}")
            sys.exit(1)

    def parse_meta(self, meta: list[str]) -> dict[str, str]:
        meta_result = {}
        for token in meta:
            token = token.strip("[]")
            key, val = token.split("=", 1)
            meta_result[key] = val
        return meta_result

    def parse_zone(self, value: str, role: HubType) -> Zone:
        name, x, y, *meta = value.split()
        meta_dict = self.parse_meta(meta)
        return Zone(role, name, int(x), int(y),
                    zone_type=meta_dict.get("zone", "normal"),
                    color=meta_dict.get("color"),
                    max_drones=int(meta_dict.get("max_drones", 1))
                    )

    def parse_connections(self, value: str) -> Connection:
        pair, *meta = value.split()
        zone_a, zone_b = pair.split("-")
        dict_meta = self.parse_meta(meta)
        return Connection(zone_a,
                          zone_b,
                          max_link_cap=int(dict_meta.get
                                           ("max_link_capacity", 1)))
