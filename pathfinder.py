from models import Network
import heapq
import sys



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
            return 0.999
        else:
            return float("inf")
        
    def find_path(self, start: str, end: str, banned_hub: set[str]) -> tuple[float, list[str]]:
        dist: dict[str, float] = {name: float("inf") 
                                  for name in self.network.zones}
        dist[start] = 0
        prev = {}
        visited = set()
        heap = [(0, start)]
        
        while heap:
            node_cost, node = heapq.heappop(heap)
            if node in visited:
                continue
            else:
                visited.add(node)
            if node == end:
                break
            
            for neighbor in self.network.adjacency[node]:   
                if neighbor in visited:
                    continue
                if self.network.zones[neighbor].zone_type == "blocked":
                    continue
                if neighbor in banned_hub:
                    continue
                new_node_cost = node_cost + self.cost_calculator(neighbor)
            
                if new_node_cost < dist[neighbor]:
                    dist[neighbor] = new_node_cost
                    prev[neighbor] = node
                    heapq.heappush(heap, (new_node_cost, neighbor))

        if dist[end] == float("inf"):
            return float("inf"), []
        path = [end]
        while path[-1] != start:
            path.append(prev[path[-1]])
        return dist[end], path[::-1]
    
    def get_paths(self, start, end):
        paths: dict[tuple[str, ...], float] = {}
        banned_hubs = set()
        
        while True:
            soma, path = self.find_path(start,
                                      end,
                                      banned_hubs)
            if not path:
                break
            key = tuple(path)
            paths[key] = round(soma)
            for hub in path[1:-1]:
                banned_hubs.add(hub)
        
        
        return paths