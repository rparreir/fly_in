from models import Network

class Pathfinder():
    def __init__(self, network: Network) -> None:
        self.network = network

    def cost_calculator(self, name: str) -> float:
        type_of_zone = self.network.zones[name].zone_type
        if type_of_zone == "normal":
            return 1
        elif type_of_zone == "restricted":
            return 2
        elif type_of_zone == "priority":
            return 1
        else:
            return float("inf")