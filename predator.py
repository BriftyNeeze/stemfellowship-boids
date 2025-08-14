import pygame
import numpy as np
from copy import deepcopy
from boundary import Boundary


def _ruleHunting(self, flock):
    acceleration = pygame.Vector2(0, 0)
    for bird in flock:
        if self.boundary.periodicDisplacement(bird.position, self.position).length() <= self.huntingRadius:
            if self.boundary.periodicDisplacement(bird.position, self.position).length() < acceleration.length() or acceleration.length() == 0:
                acceleration = self.boundary.periodicDisplacement(bird.position, self.position)

    if acceleration.length() == 0:
        return acceleration
    return acceleration.normalize()

def _ruleRandomPerturbation(self):
    acceleration = pygame.Vector2(0, 0)
    x_random = np.random.default_rng().random()
    y_random = 1 - x_random ** 2
    acceleration.x = x_random
    acceleration.y = y_random
    return acceleration

def _ruleSeparation(self, hunters):
    acceleration = pygame.Vector2(0, 0)

    for predator in hunters:
        if predator == self:
            continue
        if self.boundary.periodicDisplacement(self.position, predator.position).length() <= self.separationRadius:
            pos_vector = self.boundary.periodicDisplacement(predator.position, self.position)
            if pos_vector.length() == 0:
                continue
            acceleration -= pos_vector / (pos_vector.length() ** 2)

    if acceleration.length() == 0:
        return acceleration
    return acceleration.normalize()

class Predator:
    def __init__(self, x, y):
        # init position
        self.position = pygame.Vector2(x, y)
        # init velocity
        vx = np.random.uniform(-1, 1)
        vy = np.random.uniform(-1, 1)
        self.velocity = pygame.Vector2(vx, vy)
        self.velocity.normalize_ip()
        self.velocity *= np.random.uniform(1, 5)
        self.maxSpeed = 7
        # init acceleration
        self.acceleration = pygame.Vector2(0, 0)
        self.maxAcceleration = 2
        # init boundary
        self.boundary = Boundary(0, 800, 0, 600)
        # init display
        self.size = 5
        self.angle = 0
        self.color = (255, 0, 0)
        self.secondaryColor = (0, 0, 0)
        self.stroke = 2
        self.mouseDown = False
        self.mousePos = pygame.Vector2(0, 0)
        # init rule weights
        self.setRuleWeights()
        self.hunger = 0

    def setRuleWeights(self):
        self.eatingRadius = 50
        self.huntingRadius = 300
        self.huntingWeight = 0.5
        self.randomPerturbationWeight = 0.05

        self.eatingCooldown = 60
        self.eatingCounter = 60

        self.loseHungerCooldown = 150
        self.loseHungerCounter = 210

        self.separationRadius = 100
        self.separationWeight = 0.3

    def computeAcceleration(self, hunters, flock):
        self.acceleration *= 0
        hunt = self.ruleHunting(flock)
        self.acceleration += hunt * self.huntingWeight
        randomPerturbation = self.ruleRandomPerturbation()
        self.acceleration += randomPerturbation * self.randomPerturbationWeight
        separation = self.ruleSeparation(hunters)
        self.acceleration += separation * self.separationWeight

    def ruleHunting(self, flock):
        if self.eatingCounter > self.eatingCooldown // 6:
            return pygame.Vector2(0, 0)
        return _ruleHunting(self, flock)

    def ruleRandomPerturbation(self):
        return _ruleRandomPerturbation(self)

    def ruleSeparation(self, hunters):
        return _ruleSeparation(self, hunters)

    def attemptEat(self, hunters, flock, cKDTree):
        dis, q = cKDTree.query((self.position.x, self.position.y), 1)
        if q == len(flock):
            return
        if dis > self.eatingRadius:
            return
        self.eatingCounter = self.eatingCooldown
        bird = flock[q]
        flock.remove(bird)
        self.hunger += 1
        if self.hunger >= 8:
            self.hunger = 0
            hunters.append(Predator(self.position.x+10, self.position.y+10))
            self.maxSpeed = max(2.0, self.maxSpeed-1.5)
        # for bird in flock:
        #     if self.boundary.periodicDisplacement(bird.position, self.position).length() <= self.eatingRadius:
        #         self.eatingCounter = self.eatingCooldown
        #         flock.remove(bird)
        #         self.hunger += 1
        #         if self.hunger >= 8:
        #             self.hunger = 0
        #             hunters.append(Predator(self.position.x+10, self.position.y+10))
        #             self.maxSpeed = max(2.0, self.maxSpeed-1.2)
        #         break

    def update(self, hunters, flock, cKDTree):
        self.computeAcceleration(hunters, flock)

        self.velocity += self.acceleration
        self.velocity = limit(self.velocity, self.maxSpeed)
        if self.eatingCounter > self.eatingCooldown // 6:
            self.velocity = limit(self.velocity, self.maxSpeed/2)
        self.position += self.velocity
        self.boundary.periodicProject(self.position)

        self.angle = np.arctan2(self.velocity.y, self.velocity.x) + np.pi / 2

        if self.eatingCounter == 0:
            self.attemptEat(hunters, flock, cKDTree)
        else:
            self.eatingCounter -= 1

        if self.loseHungerCounter == 0:
            self.hunger -= 1
            self.loseHungerCounter = self.loseHungerCooldown
            if self.hunger <= -2:
                hunters.remove(self)
        else:
            self.loseHungerCounter -= 1

    def Draw(self, screen, distance, scale):
        ps = []
        # initialize a 3x3 np array
        points = np.zeros((3, 2), dtype=int)

        # create a triangle
        points[0, :] = np.array([0, -self.size])
        points[1, :] = np.array([np.sqrt(self.size), np.sqrt(self.size)])
        points[2, :] = np.array([-np.sqrt(self.size), np.sqrt(self.size)])

        for point in points:
            rotation_matrix = np.array(
                [[np.cos(self.angle), -np.sin(self.angle)], [np.sin(self.angle), np.cos(self.angle)]])
            rotated = np.matmul(rotation_matrix, point)

            x = int(rotated[0] * scale) + self.position.x
            y = int(rotated[1] * scale) + self.position.y
            ps.append((x, y))

        pygame.draw.polygon(screen, self.secondaryColor, ps)
        pygame.draw.polygon(screen, self.color, ps, self.stroke)


def limit(vector, length):
    tmp = deepcopy(vector)
    if tmp.length() > length:
        tmp.normalize_ip()
        tmp *= length
    return tmp