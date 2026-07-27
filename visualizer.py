import pygame

pygame.init()

screen = pygame.display.set_mode((1200, 700))
x = 0.0
running = True
clock = pygame.time.Clock()
delta_time = 0.1

while running:
    screen.fill((0, 143, 17))
    x += 50 * delta_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    pygame.display.flip()
    delta_time = clock.tick(60) / 1000
    delta_time = max(0.001, min(0.1, delta_time))

pygame.quit()
