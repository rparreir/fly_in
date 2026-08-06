"""Pygame radar-style visualizer for the fly-in drone simulation."""
import pygame
from models import HubType, Network
import math


class Visualizer:
    """Render the network as a radar and animate the drones turn by turn."""

    def __init__(self, network: Network, turn: list[list[str]]) -> None:
        """Build the per-turn drone states and set up the pygame window."""
        self.network = network
        self.turn = turn
        self.current_pos = 0
        self.states = self.build_states()
        self.sweep_angle = 0.0
        self.M = 150
        self.min_x, self.max_x, self.min_y, self.max_y = self.bounding_box()
        pygame.init()
        info = pygame.display.Info()
        self.W, self.H = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.W, self.H))
        self.clock = pygame.time.Clock()
        self.last_time = 0
        self.t = 0.0
        self.font_hubs = pygame.font.SysFont("monospace", 8)
        self.font_drones = pygame.font.SysFont("monospace", 15)
        self.font_info = pygame.font.SysFont("monospace", 12)
        self.current_turn = 0

    def bounding_box(self) -> tuple[float, float, float, float]:
        """Return (min_x, max_x, min_y, max_y) of all zone coordinates."""
        min_x = float("inf")
        max_x = float("-inf")
        min_y = float("inf")
        max_y = float("-inf")
        for zone in self.network.zones.values():
            if zone.x < min_x:
                min_x = zone.x
            if zone.x > max_x:
                max_x = zone.x
            if zone.y < min_y:
                min_y = zone.y
            if zone.y > max_y:
                max_y = zone.y
        return min_x, max_x, min_y, max_y

    def to_screen(self, x: float, y: float) -> tuple[int, int]:
        """Convert map (x, y) to screen pixels within the margin."""
        range_x = self.max_x - self.min_x
        range_y = self.max_y - self.min_y
        norm_x = (x - self.min_x) / range_x if range_x else 0.5
        norm_y = (y - self.min_y) / range_y if range_y else 0.5
        px = self.M + norm_x * (self.W - 2 * self.M)
        py = self.M + norm_y * (self.H - 2 * self.M)
        return int(px), int(py)

    def draw_hubs(self) -> None:
        """Draw every zone as a coloured circle with its name."""
        name_color = (150, 220, 170)
        for zone in self.network.zones.values():
            col = zone.color
            if col:
                try:
                    color = pygame.Color(col)
                except ValueError:
                    color = pygame.Color(120, 200, 120)
            else:
                color = pygame.Color(120, 200, 120)
            px, py = self.to_screen(zone.x, zone.y)
            if zone.hub_type == HubType.START_HUB:
                pygame.draw.circle(self.screen,
                                   (color), (px, py), 35)
                label = self.font_hubs.render(f"{zone.name}", True,
                                              (name_color))
                self.screen.blit(label, (int(px) + 25, int(py) + 25))
            elif zone.hub_type == HubType.END_HUB:
                pygame.draw.circle(self.screen,
                                   (color), (px, py), 35)
                label = self.font_hubs.render(f"{zone.name}", True,
                                              (name_color))
                self.screen.blit(label, (int(px) + 25, int(py) + 25))
            else:
                pygame.draw.circle(self.screen,
                                   (color), (px, py), 12)
                label = self.font_hubs.render(f"{zone.name}", True,
                                              (name_color))
                self.screen.blit(label, (int(px) + 10, int(py) + 10))

    def draw_connections(self) -> None:
        """Draw a line for each connection between two zones."""
        for conn in self.network.connections:
            a = self.network.zones[conn.zone_a]
            b = self.network.zones[conn.zone_b]
            point_a = self.to_screen(a.x, a.y)
            point_b = self.to_screen(b.x, b.y)
            pygame.draw.line(self.screen, (22, 60, 30), point_a, point_b, 2)

    def make_radar_rings(self) -> None:
        """Draw the concentric radar rings centred on the screen."""
        r = 3000
        while r > 0:
            pygame.draw.circle(self.screen, (22, 60, 40),
                               (self.W // 2, self.H // 2), r, 1)
            r -= 150

    def draw_radar_lines(self) -> None:
        """Draw the radar crosshair (centre horizontal and vertical lines)."""
        x, y = self.screen.get_size()
        cx, cy = (x // 2), (y // 2)
        pygame.draw.line(self.screen, (22, 60, 40), (0, cy), (x, cy), 1)
        pygame.draw.line(self.screen, (22, 60, 40), (cx, 0), (cx, y), 1)

    def draw_sweep(self) -> None:
        """Advance and draw the rotating radar sweep with a fading trail."""
        self.sweep_angle += 0.02
        cx, cy = (self.W // 2), (self.H // 2)
        raio = 3000
        end_x = cx + math.cos(self.sweep_angle) * raio
        end_y = cy + math.sin(self.sweep_angle) * raio

        surf = pygame.Surface((self.W, self.H), pygame.SRCALPHA)

        N = 700
        pygame.draw.line(self.screen, (120, 255, 150),
                         (cx, cy), (end_x, end_y), 3)
        for i in range(1, N):
            ang = self.sweep_angle - i * 0.001
            ex = cx + math.cos(ang) * raio
            ey = cy + math.sin(ang) * raio
            alpha = int(100 * (1 - i / N))
            pygame.draw.line(surf, (80, 205, 125, alpha),
                             (cx, cy), (ex, ey), 3)
        self.screen.blit(surf, (0, 0))

    def build_states(self) -> list[dict[int, str]]:
        """Reconstruct each drone's zone per turn from the sim output."""
        assert self.network.start is not None
        start_name = self.network.start.name
        n_drones = self.network.nb_drones
        pos = {i: start_name for i in range(1, n_drones + 1)}
        states = [dict(pos)]

        for turn in self.turn:
            for token in turn:
                resto = token[1:]
                drone, _, dest = resto.partition("-")
                if "-" in dest:
                    a, b = dest.split("-", 1)
                    pos[int(drone)] = a + ">" + b
                else:
                    pos[int(drone)] = dest
            states.append(dict(pos))
        return states

    def zone_xy(self, state: str) -> tuple[float, float]:
        """Coords of a state: a zone, or a connection midpoint if in flight."""
        if state in self.network.zones:
            z = self.network.zones[state]
            return z.x, z.y
        a, b = state.split(">", 1)
        za, zb = self.network.zones[a], self.network.zones[b]
        return (za.x + zb.x) / 2, (za.y + zb.y) / 2

    def draw_drones(self) -> None:
        """Draw each drone, interpolating between its current and next zone."""
        next_p = min(self.current_pos + 1, len(self.states) - 1)
        for drone, zona in self.states[self.current_pos].items():
            ax, ay = self.to_screen(*self.zone_xy(zona))
            bx, by = self.to_screen(*self.zone_xy(self.states[next_p][drone]))
            x = ax + (bx - ax) * self.t
            y = ay + (by - ay) * self.t

            pygame.draw.circle(self.screen,
                               (120, 255, 150), (int(x), int(y)), 5)
            label = self.font_drones.render(f"D{drone}", True, (120, 255, 150))
            if drone % 2 == 0:
                self.screen.blit(label, (int(x) - 10, int(y) + 13))
            else:
                self.screen.blit(label, (int(x) - 6, int(y) - 30))

    def advance_turn(self) -> None:
        """Advance the interpolation clock and step to the next turn."""
        now = pygame.time.get_ticks()
        dt = now - self.last_time
        self.last_time = now
        self.t += dt / 1500
        if self.t >= 1 and self.current_pos < len(self.states) - 1:
            self.t = 0
            self.current_turn += 1
            if self.current_pos < len(self.states) - 1:
                self.current_pos += 1

    def draw_current_turn(self) -> None:
        """Draw the HUD: current turn, landing status and controls."""
        lb_t = self.font_drones.render(f"CURRENT TURN - [{self.current_turn}]",
                                       True, (120, 255, 150))
        self.screen.blit(lb_t, (30, 30))
        if self.current_pos == len(self.states) - 1:
            all_land = self.font_drones.render("ALL DRONES HAVE LANDED",
                                               True, (120, 255, 150))
            self.screen.blit(all_land, (230, 30))
        info_lab = self.font_info.render("[SPACE] - RESTART",
                                         True, (150, 220, 170))
        self.screen.blit(info_lab, (50, 60))

    def run(self) -> None:
        """Run the main game loop until the window is closed."""
        try:
            running = True
            while running:
                self.screen.fill((8, 24, 14))
                self.make_radar_rings()
                self.draw_radar_lines()
                self.draw_connections()
                self.advance_turn()
                self.draw_drones()
                self.draw_hubs()
                self.draw_sweep()
                self.draw_current_turn()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_SPACE:
                            self.current_pos = 0
                            self.t = 0
                            self.current_turn = 0
                pygame.display.flip()
                self.clock.tick(60)
            pygame.quit()
        except KeyboardInterrupt:
            print("\nAdeus")
