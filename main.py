from parser import Parser
import sys
from simulator import Simulator
from visualizer import Visualizer


def main() -> None:
    arg_len = len(sys.argv)
    if arg_len < 2 or arg_len > 3:
        print("Usage: python3 main.py example_map.txt")
        sys.exit(1)

    arg_map = sys.argv[1]
    parse = Parser()
    parse.open_map(arg_map)
    sim = Simulator(parse.network, parse.network.nb_drones)
    turn = sim.simulate_travel()

    if "--vis" in sys.argv:
        Visualizer(parse.network, turn).run()


if __name__ == "__main__":
    main()
