from parser import Parser
import sys
from pathfinder import *


def main():
    arg_len = len(sys.argv)
    if arg_len <= 1 or arg_len > 2:
        print("Usage: python3 main.py example_map.txt")
        sys.exit(1)
    arg_map = sys.argv[1]
    parse = Parser()
    parse.open_map(arg_map)
    pathfinder = Pathfinder(parse.network)
    
    banned_hubs = set()
    soma, path = pathfinder.find_path(parse.network.start.name,
                                      parse.network.end.name,
                                      banned_hubs)
    if not path:
        print("no path")
        sys.exit(1)
    print(f"The shortes path is {path}, it a total cost of {soma} turns")
    for hub in path[1:-1]:
            banned_hubs.add(hub)

    while path:
        soma, path = pathfinder.find_path(parse.network.start.name,
                                      parse.network.end.name,
                                      banned_hubs)
        if not path:
            break
        for hub in path[1:-1]:
            banned_hubs.add(hub)
        
        print(f"other paths:\n{path} it the sum of {soma} turns")
    
        

if __name__ == "__main__":
    main()
