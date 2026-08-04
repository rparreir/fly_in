import pygame
from models import HubType
import math


class Visualizer:
    def __init__(self, network, turn: list[list[str]]):
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

    def bounding_box(self):
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

    def to_screen(self, x, y):
        range_x = self.max_x - self.min_x
        range_y = self.max_y - self.min_y
        norm_x = (x - self.min_x) / range_x if range_x else 0.5
        norm_y = (y - self.min_y) / range_y if range_y else 0.5
        px = self.M + norm_x * (self.W - 2 * self.M)
        py = self.M + norm_y * (self.H - 2 * self.M)
        return int(px), int(py)

    def draw_hubs(self):
        for zone in self.network.zones.values():
            col = zone.color
            if col:
                try:
                    color = pygame.Color(col)
                except ValueError:
                    color = pygame.Color(22, 60, 40)
            else:
                color = pygame.Color(22, 60, 40)
            px, py = self.to_screen(zone.x, zone.y)
            if zone.hub_type == HubType.START_HUB:
                pygame.draw.circle(self.screen,
                                   (color), (px, py), 20)
            elif zone.hub_type == HubType.END_HUB:
                pygame.draw.circle(self.screen,
                                   (color), (px, py), 20)
            else:
                pygame.draw.circle(self.screen,
                                   (color), (px, py), 12)

    def draw_connections(self):
        for conn in self.network.connections:
            a = self.network.zones[conn.zone_a]
            b = self.network.zones[conn.zone_b]
            point_a = self.to_screen(a.x, a.y)
            point_b = self.to_screen(b.x, b.y)
            pygame.draw.line(self.screen, (22, 60, 30), point_a, point_b, 2)

    def make_radar_rings(self):
        r = 3000
        while r > 0:
            pygame.draw.circle(self.screen, (22, 60, 40),
                               (self.W // 2, self.H // 2), r, 1)
            r -= 150

    def draw_radar_lines(self):
        x, y = self.screen.get_size()
        cx, cy = (x // 2), (y // 2)
        pygame.draw.line(self.screen, (22, 60, 40), (0, cy), (x, cy), 1)
        pygame.draw.line(self.screen, (22, 60, 40), (cx, 0), (cx, y), 1)

    def draw_sweep(self):
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

    def build_states(self):
        start_name = self.network.start.name
        n_drones = self.network.nb_drones
        pos = {i: start_name for i in range(1, n_drones + 1)}
        states = [dict(pos)]

        for turn in self.turn:
            for token in turn:
                resto = token[1:]
                drone, zona = resto.split("-", 1)
                pos[int(drone)] = zona
            states.append(dict(pos))
        return states

    def draw_drones(self):
        for drone, zona in self.states[self.current_pos].items():
            z = self.network.zones[zona]
            px, py = self.to_screen(z.x, z.y)
            pygame.draw.circle(self.screen, ("yellow"), (px, py), 5)

    def advance_time(self):
        now = pygame.time.get_ticks()
        if now - self.last_time > 7000:
            self.last_time = now
            if self.current_pos < len(self.states) - 1:
                self.current_pos += 1

    def run(self):
        try:
            running = True
            while running:
                self.screen.fill((8, 24, 14))
                self.make_radar_rings()
                self.draw_radar_lines()
                self.draw_connections()
                self.draw_hubs()
                self.advance_time()
                self.draw_drones()
                self.draw_sweep()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                pygame.display.flip()
                self.clock.tick(60)
            pygame.quit()
        except KeyboardInterrupt:
            print("Adeus")
