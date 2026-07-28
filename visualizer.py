import pygame


class Visualizer:
    def __init__(self, network):
        self.network = network
        self.W, self.H, self.M = 1200, 700, 60
        self.min_x, self.max_x, self.min_y, self.max_y = self.bounding_box()
        pygame.init()
        self.screen = pygame.display.set_mode((self.W, self.H))
        self.clock = pygame.time.Clock()

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
            px, py = self.to_screen(zone.x, zone.y)
            pygame.draw.circle(self.screen, (240, 0, 240), (px, py), 12)

    def draw_connections(self):
        for conn in self.network.connections:
            a = self.network.zones[conn.zone_a]
            b = self.network.zones[conn.zone_b]
            point_a = self.to_screen(a.x, a.y)
            point_b = self.to_screen(b.x, b.y)
            pygame.draw.line(self.screen, (240, 240, 240), point_a, point_b, 1)

    def run(self):
        running = True
        while running:
            self.screen.fill((8, 24, 14))
            self.draw_connections()
            self.draw_hubs()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
