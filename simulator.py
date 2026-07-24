from pathfinder import *
import sys

class Drone:
    def __init__(self, drone_id: int, path: list[str]) -> None:
        self.id = drone_id
        self.path = path
        self.pos = 0
        self.flying = False


class Simulator():
    def __init__(self, network, nb_drones) -> None:
        pathfinder = Pathfinder(network)
        all_paths = pathfinder.get_paths(network.start.name,
                                        network.end.name)
        print(all_paths)
        if not all_paths:
            print("no path found")
            sys.exit(1)
        
        carga = {p: 0 for p in all_paths}
        self.drones = []
        for i in range(1, nb_drones + 1):
            best_p = None
            best_value = float("inf")
            for p in carga:
                valor = all_paths[p] + carga[p]  
                if valor < best_value:
                    best_value = valor
                    best_p = p
            carga[best_p] += 1
            self.drones.append(Drone(i, list(best_p)))
        self.network = network
        
    
    def check_availability(self, check_hub: str, ocupation: dict[str, int]) -> bool:
        if check_hub in (self.network.start.name, self.network.end.name):
            return True
        hub_capacity = self.network.zones[check_hub].max_drones
        return ocupation.get(check_hub, 0) < hub_capacity
    
    def link_capacity(self, a: str, b: str) -> int:
        for con in self.network.connections:
            if {con.zone_a, con.zone_b} == {a, b}:
                return con.max_link_cap
        return 1
    
    def is_zone_restric(self, zone_name: str):
        for name, zone in self.network.zones.items():
            
            if name == zone_name:
                if zone.zone_type == "restricted":
                    return True
        return False

    
    
    def check_if_all_landed(self) -> bool:
        for d in self.drones:
            last_hub = len(d.path) - 1
            if last_hub != d.pos:
                return False
        return True 
    
    def simulate_travel(self):
        turn = 0
        
        
        while True:
            if self.check_if_all_landed():
                print("all landed")
                break
            turn += 1
            
            print(f"Current turn {turn}")
            
            
            self.drones.sort(key=lambda d: d.pos, reverse=True)

            travessias: dict[frozenset[str], int] = {}
            ocupation: dict[str, int] = {}
            for dr in self.drones:
                zona = dr.path[dr.pos]
                ocupation[zona] = ocupation.get(zona, 0) + 1
            
            for d in self.drones:
                if d.pos == len(d.path) - 1:
                    continue
                
                current = d.path[d.pos]
                next_hub = d.path[d.pos + 1]
                link = frozenset({current, next_hub})
                
                if d.flying:
                    d.flying = False
                    continue
                

                if self.is_zone_restric(next_hub):
                    if (self.check_availability(next_hub, ocupation)
                        and travessias.get(link, 0) < self.link_capacity(current, next_hub)):
                        print(f"drone {d.id} is chilling in the air")
                        ocupation[current] -= 1
                        ocupation[next_hub] = ocupation.get(next_hub, 0) + 1
                        travessias[link] = travessias.get(link, 0) + 1
                        d.pos += 1
                        d.flying = True
                    continue
                elif (self.check_availability(next_hub, ocupation)
                        and travessias.get(link, 0) < self.link_capacity(current, next_hub)):
                    ocupation[current] -= 1
                    ocupation[next_hub] = ocupation.get(next_hub, 0) + 1
                    travessias[link] = travessias.get(link, 0) + 1
                    d.pos += 1
                    print(f"drone name:{d.id} travelled to {d.path[d.pos]}\n")
                

    
            
                
            