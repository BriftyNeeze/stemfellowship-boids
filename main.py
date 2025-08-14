import pygame
import numpy as np
import random
import scipy as sp
from copy import deepcopy
from bird import Bird
from boundary import Boundary
from predator import Predator


Width, Height = 1920, 1080
Width *= 0.5
Height *= 0.5
white, black = (217, 217, 217), (12, 12, 12)
size = (Width, Height)

window = pygame.display.set_mode(size, pygame.RESIZABLE)
clock = pygame.time.Clock()
fps = 60

scale = 10
Distance = 5
speed = 0.0005

flock = []
hunters = []
flock_graph = []
game_counter = 0
n = 50
m = 5

pygame.font.init()
population_font = pygame.font.SysFont('Comic Sans MS', 30)

graph_font = pygame.font.SysFont("Comic Sans MS", 20)
flock_positions = []
for i in range(n):
    flock.append(Bird(random.randint(20, int(Width) - 20), random.randint(20, int(Height) - 20)))
    flock_positions.append((flock[i].position.x, flock[i].position.y))
for i in range(m):
    hunters.append(Predator(random.randint(20, int(Width) - 20), random.randint(20, int(Height) - 20)))
keyPressed = False
run = True

flock_positions = np.array(flock_positions)

cKDTree = sp.spatial.cKDTree(flock_positions)

while run:

    clock.tick(fps)
    window.fill((10, 10, 15))
    flock_positions = []
    for i in range(len(flock)):
        flock_positions.append((flock[i].position.x, flock[i].position.y))

    flock_positions = np.array(flock_positions)

    cKDTree = sp.spatial.cKDTree(flock_positions)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            keyPressed = True

    # update the window size
    Width, Height = window.get_size()

    for boid in flock:
        boid.radius = scale
        boid.boundary = Boundary(0, Width, 0, Height)
        boid.mousePos = pygame.Vector2(pygame.mouse.get_pos())
        boid.mouseDown = pygame.mouse.get_pressed()[0]
        boid.update(flock, hunters, cKDTree)
        boid.Draw(window, Distance, scale)

    for boid in hunters:
        boid.radius = scale
        boid.boundary = Boundary(0, Width, 0, Height)
        boid.mousePos = pygame.Vector2(pygame.mouse.get_pos())
        boid.mouseDown = pygame.mouse.get_pressed()[0]
        boid.update(hunters, flock, cKDTree)
        boid.Draw(window, Distance, scale)

    flock_population = population_font.render(f'Flock Size: {len(flock)}', False, (255, 255, 255))
    window.blit(flock_population, (5, 5))

    label_population_zero = graph_font.render("0 -", False, (255, 255, 255))
    window.blit(label_population_zero, (10, 170))

    label_population_mid = graph_font.render("50 -", False, (255, 255, 255))
    window.blit(label_population_mid, (10, 115))
    if game_counter % 120 == 0:
        flock_graph.append(len(flock))
        if len(flock_graph) > 10:
            flock_graph = flock_graph[1:]
    for i in range(len(flock_graph) - 1):
        line = pygame.draw.line(window, (255, 255, 255), (50 + i * 20, -flock_graph[i] + 180), (70 + i * 20, -flock_graph[i + 1] + 180), 2)

    keyPressed = False
    game_counter += 1
    pygame.display.flip()
pygame.quit()
