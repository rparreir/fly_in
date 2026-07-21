from parser import Parser
import sys
from pathfinder import *
from simulator import Simulator

def main():
    arg_len = len(sys.argv)
    if arg_len <= 1 or arg_len > 2:
        print("Usage: python3 main.py example_map.txt")
        sys.exit(1)
    arg_map = sys.argv[1]
    parse = Parser()
    parse.open_map(arg_map)
    
    pathfinder = Pathfinder(parse.network)
    main_path, other_paths = pathfinder.get_paths(parse.network.start.name,
                                                  parse.network.end.name)
    
    sim = Simulator(parse.network, main_path, parse.network.nb_drones)
    sim.simulate_travel()
    
    
        

if __name__ == "__main__":
    main()
