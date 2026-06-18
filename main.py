from parser import Parser
import sys


def main():
    arg_map = sys.argv[1]
    parse = Parser()
    parse.open_map(arg_map)


if __name__ == "__main__":
    main()
