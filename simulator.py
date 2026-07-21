class Drone:
    def __init__(self, drone_id: int, path: list[str]) -> None:
        self.id = drone_id
        self.path = path
        self.pos = 0

class Simulator():
    def __init__(self, network, main_path, nb_drones) -> None:
        self.path = list(main_path.keys())[0]
        self.network = network
        self.drones = [Drone(i, list(self.path)) for i in range(1, nb_drones + 1)]
    
    def check_availability(self, check_hub: str, ocupation: dict[str, int]) -> bool:
        if check_hub in (self.network.start.name, self.network.end.name):
            return True
        hub_capacity = self.network.zones[check_hub].max_drones
        return ocupation.get(check_hub, 0) < hub_capacity
    
    
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

            ocupation: dict[str, int] = {}
            for dr in self.drones:
                zona = dr.path[dr.pos]
                ocupation[zona] = ocupation.get(zona, 0) + 1
            
            for d in self.drones:
                
                if d.pos == len(d.path) - 1:
                    continue
                
                current = d.path[d.pos]
                next_hub = d.path[d.pos + 1]
                
                if self.check_availability(next_hub, ocupation):
                    ocupation[current] -= 1
                    ocupation[next_hub] = ocupation.get(next_hub, 0) + 1
                    d.pos += 1
                    print(f"drone name:{d.id} travelled to {d.path[d.pos]}\n")
    
    
            
                
            