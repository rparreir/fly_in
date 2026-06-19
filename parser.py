import sys
from models import HubType, Zone, Network


class Parser():
    def __init__(self) -> None:
        self.extrac_nb_drones: dict[str, str] = {}
        self.extrac_start_hub: dict[str, str] = {}
        self.extrac_end_hub: dict[str, str] = {}
        self.extrac_hubs: dict[str, str] = {}
        self.extrac_connections: dict[str, str] = {}

        self.network = Network()

    def open_map(self, arg_map: str):
        try:
            with open(arg_map) as map:
                for line in map:
                    print(line)
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    self.extrac_values(line)

            if self.extrac_nb_drones:
                num_drones = int(self.extrac_nb_drones["nb_drones"])
                # preciso de adiconar aqui uma validaçao
                self.network.nb_drones = num_drones
            else:
                print("Error: number of drones not defined")
                sys.exit(1)
            if self.extrac_start_hub:
                start = self.parse_zone(self.extrac_start_hub,
                                        HubType.START_HUB)
                # preciso de adiconar aqui uma validaçao
                self.network.start = start[0]
                self.network.zones[start[0].name] = start[0]
            else:
                print("Error: start hub not defined")
                sys.exit(1)
            if self.extrac_end_hub:
                end = self.parse_zone(self.extrac_end_hub, HubType.END_HUB)
                # preciso de adiconar aqui uma validaçao
                self.network.end = end[0]
                self.network.zones[end[0].name] = end[0]
            else:
                print("Error: end hub not defined")
                sys.exit(1)
            if self.extrac_hubs:
                hubs = self.parse_zone(self.extrac_hubs, HubType.HUB)
                # preciso de adiconar aqui uma validaçao
                for zone in hubs:
                    self.network.zones[zone.name] = zone

        except FileNotFoundError:
            print("Error: Map file not found")
            sys.exit(1)
        except ValueError:
            print("Error: wrong file format")
            sys.exit(1)

    def extrac_values(self, line: str):
        try:
            key, value = line.split(':', 1)
            if line.startswith("nb_drones"):
                self.extrac_nb_drones[key.strip()] = value.strip()
            elif line.startswith("start_hub"):
                self.extrac_start_hub[key.strip()] = value.strip()
            elif line.startswith("end_hub"):
                self.extrac_end_hub[key.strip()] = value.strip()
            elif line.startswith("hub"):
                name = value.split()[0]
                self.extrac_hubs[name] = value.strip()
            elif line.startswith("connection"):
                name0 = value.split()[0]
                self.extrac_connections[name0] = value.strip()
        except (ValueError, IndexError):
            print("Error: wrong Value")
            sys.exit(1)

    def parse_meta(self, meta):
        meta_result = {}
        for token in meta:
            token = token.strip("[]")
            key, val = token.split("=", 1)
            meta_result[key] = val
        return meta_result

    def parse_zone(self, value: dict[str, str], role: HubType):
        result = []
        for raw in value.values():
            name, x, y, *meta = raw.split()
            meta_dict = self.parse_meta(meta)
            zone = Zone(role, name, int(x), int(y),
                        zone_type=meta_dict.get("zone", "normal"),
                        color=meta_dict.get("color"),
                        max_drones=int(meta_dict.get("max_drones", 1))
                        )
            result.append(zone)
        return result
    
    def parse_connections(self)
