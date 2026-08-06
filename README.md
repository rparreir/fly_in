# fly_in

A drone routing simulator: move a fleet of drones from a **start** zone to an
**end** zone across a weighted network of zones and capacity-limited
connections, in the **fewest possible turns**.

## Description

`fly_in` reads a map describing a network (zones and the connections between
them), then schedules the movement of `nb_drones` drones from the start zone to
the end zone. Multiple drones move **simultaneously** each turn, subject to zone
capacities and connection capacities. The program prints, turn by turn, every
drone that moved, and can optionally show a real-time **radar visualization**.

The problem is a weighted successor to *lem-in*: zones have types that change
their traversal cost, zones and connections have capacities, and the algorithm
must balance the fleet across several paths to minimise the total number of
turns.

## Map format

A map is a plain-text file. Lines starting with `#` are comments.

```
nb_drones: <n>
start_hub: <name> <x> <y> [metadata]
end_hub:   <name> <x> <y> [metadata]
hub:       <name> <x> <y> [metadata]
connection: <name_a>-<name_b> [metadata]
```

- `nb_drones` must appear on the first (non-comment) line.
- Coordinates are integers.
- Metadata is optional, inside brackets:
  - **Zones:** `zone=<type>`, `color=<value>`, `max_drones=<n>`
  - **Connections:** `max_link_capacity=<n>`
- **Zone types:** `normal` (cost 1), `priority` (preferred, cost 1),
  `restricted` (cost 2, crossed over 2 turns), `blocked` (impassable).
- `color` accepts any single-word string (used only for display).

## Installation

Requires **Python 3.10+**. The visualizer needs `pygame`:

```
make install
```

## Usage

Run the simulation (mandatory text output only):

```
python3 main.py <map_file>
```

Run it **with** the radar visualization:

```
python3 main.py <map_file> --vis
```

Makefile targets: `make run`, `make vis`, `make lint`, `make debug`,
`make clean`.

## Algorithm

1. **Parsing & validation** (`parser.py`, `validator.py`) — the map is read
   line by line into a `Network`. Invalid maps are rejected with an error
   message and a non-zero exit code.
2. **Pathfinding** (`pathfinder.py`) — Dijkstra's algorithm with a binary heap
   (`heapq`). The cost is carried by the **destination zone's type**
   (`normal`/`priority` ≈ 1, `restricted` = 2, `blocked` = ∞). Several
   **node-disjoint** paths are extracted by running Dijkstra repeatedly and
   banning the intermediate hubs of each path already found.
3. **Scheduling** (`simulator.py`) — a greedy list-scheduling step assigns each
   drone to the path that minimises `path_cost + current_load`, balancing the
   fleet across the available paths.
4. **Simulation** (`simulator.py`) — a turn-based engine advances the drones.
   Each turn a drone may step forward only if the destination zone still has
   room (`max_drones`) and the connection is below its `max_link_capacity`.
   A `restricted` zone is entered over two turns (a "flight").

## Output format

One line per turn, with the moves separated by spaces:

- `D<id>-<zone>` — drone `<id>` is now in `<zone>`.
- `D<id>-<from>-<to>` — drone `<id>` takes off across a restricted connection.

**Example input** (`maps/easy/01_linear_path.txt`):

```
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]
connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

**Expected output:**

```
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

The two drones pipeline down the single corridor: the second drone follows one
turn behind the first, and both reach the goal in 4 turns.

## Visual representation

Run with `--vis` to open a radar-style visualization (`visualizer.py`, built on
`pygame`):

- The network is drawn as a **radar**: concentric range rings, a crosshair, and
  a rotating **sweep** with a fading trail.
- **Zones** are drawn at their scaled map coordinates, coloured from the map
  metadata, with the start and end zones enlarged and every zone labelled.
- **Drones** move **smoothly** (linearly interpolated) from zone to zone across
  each turn, rather than jumping. A drone crossing a restricted connection is
  shown **mid-connection**, in flight.
- A **HUD** shows the current turn and signals when all drones have landed.
  `SPACE` restarts the animation, `ESC` quits.

The visualization makes the **pipelining** and **congestion** obvious — how
drones queue behind capacity bottlenecks and spread across parallel paths —
which is hard to read from the raw text output.

## Resources

- Dijkstra's shortest-path algorithm and priority queues (`heapq`).
- Node-disjoint paths and list-scheduling / load-balancing (makespan).
- The 42 *lem-in* project (the unweighted ancestor of this problem).
- `pygame` documentation (drawing, surfaces, alpha blending, fonts).

### Use of AI

AI (Claude / Claude Code) was used as a **tutor, reviewer and test harness**,
not as a code generator for the core logic:

- **Learning & design:** explaining Dijkstra, node-disjoint pathfinding,
  load-balancing and `pygame` concepts (with references), so the core code
  could be written from understanding.
- **Code review / rubber-ducking:** the parser, validator, pathfinder and
  simulator were written by hand and reviewed with AI.
- **Visualizer:** built layer by layer — AI provided the requirements, concepts
  and references for each layer; the code was written by the author.
- **Testing:** AI generated adversarial and randomised (fuzz) maps, which
  uncovered an infinite-loop edge case in the disjoint-path routine.
- **Documentation:** AI wrote the docstrings and this README, and added the
  type annotations in the visualizer.
