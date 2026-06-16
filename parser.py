import sys


class Parser():
    def __init__(self) -> None:
        self.extrac_nb_drones: dict[str, str] = {}
        self.extrac_start_hub: dict[str, str] = {}
        self.extrac_end_hub: dict[str, str] = {}
        self.extrac_hubs: dict[str, str] = {}
        self.extrac_connections: dict[str, str] = {}

    def get_configs(self, line: str):
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

    def open_map(self, arg_map: str):
        try:
            with open(arg_map) as map:
                for line in map:
                    print(line)
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    self.get_configs(line)

        except FileNotFoundError:
            print("Error: Map file not found")
            sys.exit(1)
        except ValueError:
            print("Error: wrong file format")
            sys.exit(1)


def main():
    arg_map = sys.argv[1]
    parse = Parser()
    parse.open_map(arg_map)
    print("\ntestes\n======================")
    print(f"nb_drones: {parse.extrac_nb_drones}")
    print(f"start: {parse.extrac_start_hub}")
    print(f"end: {parse.extrac_end_hub}")
    print(f"hubs: {parse.extrac_hubs}")
    print(f"connections: {parse.extrac_connections}")


if __name__ == "__main__":
    main()
