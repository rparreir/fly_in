import sys
from models import HubType, Zone, Network, Connection


class ParsingError(Exception):
    pass


class Parser():
    def __init__(self) -> None:
        self.first_line = False

        self.network = Network()

    def open_map(self, arg_map: str):
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
        except (FileNotFoundError, ParsingError) as e:
            print(f"Error: {e}")
            sys.exit(1)

    def build_network(self, line: str, idx: int):
        try:
            _, value = line.split(':', 1)

            if line.startswith("nb_drones"):
                if self.network.nb_drones:
                    raise ParsingError("can only define nb_drones once")
                self.first_line = True
                num_drones = int(value.strip())
                # preciso de adiconar aqui uma validaçao
                self.network.nb_drones = num_drones
            elif line.startswith("start_hub"):
                if self.network.start:
                    raise ParsingError("can only define starting hub once")
                start = self.parse_zone(value,
                                        HubType.START_HUB)
                # preciso de adiconar aqui uma validaçao
                self.network.start = start
                self.network.zones[start.name] = start
            elif line.startswith("end_hub"):
                if self.network.end:
                    raise ParsingError("can only define ending hub once")
                end = self.parse_zone(value, HubType.END_HUB)
                # preciso de adiconar aqui uma validaçao
                self.network.end = end
                self.network.zones[end.name] = end
            elif line.startswith("hub"):
                hubs = self.parse_zone(value, HubType.HUB)
                # preciso de adiconar aqui uma validaçao
                self.network.zones[hubs.name] = hubs
            elif line.startswith("connection"):
                connect = self.parse_connections(value)
                self.network.connections.append(connect)

        except (ValueError, IndexError, TypeError, ParsingError) as e:
            print(f"Error in (line {idx}): {e}")
            sys.exit(1)

    def parse_meta(self, meta):
        meta_result = {}
        for token in meta:
            token = token.strip("[]")
            key, val = token.split("=", 1)
            meta_result[key] = val
        return meta_result

    def parse_zone(self, value: str, role: HubType):
        name, x, y, *meta = value.split()
        meta_dict = self.parse_meta(meta)
        return Zone(role, name, int(x), int(y),
                    zone_type=meta_dict.get("zone", "normal"),
                    color=meta_dict.get("color"),
                    max_drones=int(meta_dict.get("max_drones", 1))
                    )

    def parse_connections(self, value: str):
        pair, *meta = value.split()
        zone_a, zone_b = pair.split("-")
        dict_meta = self.parse_meta(meta)
        return Connection(zone_a,
                          zone_b,
                          max_link_cap=int(dict_meta.get
                                           ("max_link_capacity", 1)))
