from parser import Parser
import sys


def main():
    arg_len = len(sys.argv)
    if arg_len <= 1 or arg_len > 2:
        print("Usage: python3 main.py example_map.txt")
        sys.exit(1)
    arg_map = sys.argv[1]
    parse = Parser()
    parse.open_map(arg_map)
    print("is running")


if __name__ == "__main__":
    main()
