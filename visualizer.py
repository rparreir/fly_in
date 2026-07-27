import sys
import io
import math
import contextlib
import pygame
from parser import Parser
from simulator import Simulator
from models import Network

W, H = 1200, 700
BG = (8, 24, 14)
TURN_MS = 1500          # duracao de cada turno (ms)
SWEEP_SECS = 5.0        # segundos por volta do radar
FLOOR = 0.35            # brilho minimo (nunca desaparece de todo)
DRONE_COLOR = pygame.Color(240, 60, 60)


def color_of(name: str | None) -> pygame.Color:
    """Traduz o nome da cor do mapa. Fallback para nomes desconhecidos."""
    if name:
        try:
            return pygame.Color(name)
        except ValueError:
            pass
    return pygame.Color(120, 200, 120)


def fade(color: pygame.Color, b: float) -> tuple[int, int, int]:
    """Mistura a cor com o fundo conforme o brilho b (0..1)."""
    b = max(0.0, min(1.0, b))
    return (int(BG[0] + (color.r - BG[0]) * b),
            int(BG[1] + (color.g - BG[1]) * b),
            int(BG[2] + (color.b - BG[2]) * b))


def drone_offset(did: int) -> tuple[float, float]:
    """Desvio FIXO por drone (espiral de angulo dourado). Estavel: o
    mesmo drone tem sempre o mesmo desvio -> nao salta, nao se sobrepoe."""
    ang = did * 2.39996323            # angulo dourado (rad)
    rad = 7 + 3.0 * (did % 3)
    return (rad * math.cos(ang), rad * math.sin(ang))


def run_sim(net: Network) -> list[dict[int, str]]:
    """Corre a simulacao, captura o output, e devolve a zona de cada
    drone em cada turno. NAO mexe no simulador."""
    assert net.start is not None
    sim = Simulator(net, net.nb_drones)

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        sim.simulate_travel()
    linhas = buffer.getvalue().splitlines()

    pos = {i: net.start.name for i in range(1, net.nb_drones + 1)}
    estados = [dict(pos)]
    for linha in linhas:
        for mov in linha.split():            # "D1-A" ou "D1-a-b"
            resto = mov[1:]
            did, _, destino = resto.partition("-")
            destino = destino.split("-")[0] if "-" in destino else destino
            pos[int(did)] = destino
        estados.append(dict(pos))
    return estados


def main() -> None:
    parse = Parser()
    parse.open_map(sys.argv[1])
    net = parse.network
    assert net.start is not None and net.end is not None
    start_name, end_name = net.start.name, net.end.name
    total = net.nb_drones
    estados = run_sim(net)

    pygame.init()
    screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
    pygame.display.set_caption("Fly-in radar")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 15)
    big = pygame.font.SysFont("monospace", 18, bold=True)

    xs = [z.x for z in net.zones.values()]
    ys = [z.y for z in net.zones.values()]
    min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)

    def to_screen(x: float, y: float, w: int, h: int) -> tuple[int, int]:
        m = 120
        fx = 0.5 if max_x == min_x else (x - min_x) / (max_x - min_x)
        fy = 0.5 if max_y == min_y else (y - min_y) / (max_y - min_y)
        return (int(m + fx * (w - 2 * m)), int(m + fy * (h - 2 * m)))

    def brilho(px: int, py: int, cx: int, cy: int, sweep: float) -> float:
        ang = math.atan2(py - cy, px - cx)
        delta = (sweep - ang) % (2 * math.pi)
        raw = 1.0 - delta / (2 * math.pi)
        return FLOOR + (1.0 - FLOOR) * raw

    turn = 0
    t = 0.0
    paused = False
    last = pygame.time.get_ticks()

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                if e.key == pygame.K_SPACE:
                    turn, t = 0, 0.0
                if e.key == pygame.K_p:
                    paused = not paused

        now = pygame.time.get_ticks()
        dt = now - last
        last = now
        if not paused and turn < len(estados) - 1:
            t += dt / TURN_MS
            if t >= 1.0:
                t, turn = 0.0, turn + 1

        w, h = screen.get_size()
        cx, cy = w // 2, h // 2
        R = int(math.hypot(w / 2, h / 2)) + 40
        sweep = (now / 1000.0) * (2 * math.pi / SWEEP_SECS) % (2 * math.pi)
        prox = min(turn + 1, len(estados) - 1)

        # ---- estatisticas (a partir do estado do turno atual) ----
        no_start = sum(1 for z in estados[turn].values() if z == start_name)
        no_end = sum(1 for z in estados[turn].values() if z == end_name)

        screen.fill(BG)

        # ---- radar: aneis, cruz, sweep + rasto ----
        for r in range(120, R, 120):
            pygame.draw.circle(screen, (22, 60, 40), (cx, cy), r, 1)
        pygame.draw.line(screen, (22, 60, 40), (0, cy), (w, cy), 1)
        pygame.draw.line(screen, (22, 60, 40), (cx, 0), (cx, h), 1)

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        steps = 28
        trail = math.radians(65)
        for k in range(steps):
            a0 = sweep - trail * k / steps
            a1 = sweep - trail * (k + 1) / steps
            alpha = int(75 * (1 - k / steps))
            pygame.draw.polygon(overlay, (60, 230, 110, alpha), [
                (cx, cy),
                (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                (cx + R * math.cos(a1), cy + R * math.sin(a1))])
        screen.blit(overlay, (0, 0))
        pygame.draw.line(screen, (120, 255, 150), (cx, cy),
                         (cx + R * math.cos(sweep),
                          cy + R * math.sin(sweep)), 2)

        # ---- connections ----
        for con in net.connections:
            za, zb = net.zones[con.zone_a], net.zones[con.zone_b]
            pygame.draw.line(screen, (30, 75, 48),
                             to_screen(za.x, za.y, w, h),
                             to_screen(zb.x, zb.y, w, h), 2)

        # ---- hubs (start/end maiores) ----
        for name, z in net.zones.items():
            p = to_screen(z.x, z.y, w, h)
            b = brilho(p[0], p[1], cx, cy, sweep)
            especial = name in (start_name, end_name)
            rad = 24 if especial else 12
            pygame.draw.circle(screen, fade(color_of(z.color), b), p, rad)
            pygame.draw.circle(screen, fade(pygame.Color(210, 240, 210), b),
                               p, rad, 1)
            screen.blit(font.render(name, True,
                                    fade(pygame.Color(180, 215, 185), b)),
                        (p[0] + rad + 4, p[1] - 8))

        # ---- drones: em transito. Parados no start/end nao se desenham
        #      (ficam "dentro" do hub; ve-se pelo contador do HUD) ----
        for did in estados[turn]:
            zona = estados[turn][did]
            dest = estados[prox][did]
            # parado no start/end -> nao desenha
            if zona == dest and zona in (start_name, end_name):
                continue
            de = net.zones[zona]                      # onde esta
            pa = net.zones[dest]                       # para onde vai
            x = de.x + (pa.x - de.x) * t              # lerp (movimento suave)
            y = de.y + (pa.y - de.y) * t
            px, py = to_screen(x, y, w, h)
            ox, oy = drone_offset(did)                # desvio fixo do drone
            px, py = px + int(ox), py + int(oy)
            b = brilho(px, py, cx, cy, sweep)
            pygame.draw.circle(screen, fade(DRONE_COLOR, b), (px, py), 5)
            screen.blit(font.render(f"D{did}", True, fade(DRONE_COLOR, b)),
                        (px + 7, py - 7))

        # ---- HUD ----
        done = turn >= len(estados) - 1
        info = big.render(
            f"turn {turn}    start {no_start}/{total}    end {no_end}/{total}"
            + ("    ALL LANDED" if done else ""),
            True, (230, 245, 220))
        screen.blit(info, (20, 16))
        screen.blit(font.render("[SPACE] restart   [P] pause   [ESC] sair",
                                True, (120, 175, 140)), (20, 44))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
