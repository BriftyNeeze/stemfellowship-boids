import pygame
import numpy as np
from copy import deepcopy
from boundary import Boundary


def _setRuleWeights(self):
    self.maxSpeed = 5
    self.maxAcceleration = 1

    self.alignmentWeight = 0.25
    self.cohesionWeight = 0.1
    self.separationWeight = 0.3
    self.mouseFollowWeight = 0.2
    self.randomPerturbationWeight = 0.05
    self.escapeWeight = 0.75

    self.alignmentRadius = 70
    self.cohesionRadius = 100
    self.separationRadius = 50
    self.mouseFollowRadius = 200
    self.escapeDistance = 150
    self.matingDistance = 30


def _ruleCohesion(self, flock, cKDTree):

    acceleration = pygame.Vector2(0, 0)

    # option 1
    q = cKDTree.query_ball_point((self.position.x, self.position.y), self.alignmentRadius)
    for i in range(min(len(q), 15)):
        bird = flock[q[i]]
        if self.boundary.periodicDisplacement(self.position, bird.position).length() <= self.cohesionRadius:
            acceleration += self.boundary.periodicDisplacement(bird.position, self.position)

    # option 2
    # dis, q = cKDTree.query([(self.position.x, self.position.y)], 10)
    # for i in range(len(q[0])):
    #     if i == len(flock):
    #         break
    #     bird = flock[q[0][i]]
    #     distance = dis[0][i]
    #     if distance <= self.cohesionRadius:
    #         acceleration += self.boundary.periodicDisplacement(bird.position, self.position)

    # for bird in flock:
    #     if self.boundary.periodicDisplacement(self.position, bird.position).length() <= self.cohesionRadius:
    #         acceleration += self.boundary.periodicDisplacement(bird.position, self.position)

    if acceleration.x == 0 and acceleration.y == 0:
        return acceleration
    return acceleration.normalize()


def _ruleAlignment(self, flock, cKDTree):
    acceleration = pygame.Vector2(0, 0)

    # Option 1 ball Point
    q = cKDTree.query_ball_point((self.position.x, self.position.y), self.alignmentRadius)
    for i in range(min(len(q), 15)):
        bird = flock[q[i]]
        if bird == self:
            continue
        if self.boundary.periodicDisplacement(self.position, bird.position).length() <= self.alignmentRadius:
            acceleration += bird.velocity

    # Option 2 Regular
    # dis, q = cKDTree.query([(self.position.x, self.position.y)], 10)
    # for i in range(len(q[0])):
    #     if i == len(flock):
    #         break
    #     bird = flock[q[0][i]]
    #     distance = dis[0][i]
    #     if bird == self:
    #         continue
    #     if distance <= self.alignmentRadius:
    #         acceleration += bird.velocity

    # for bird in flock:
    #     if bird == self:
    #         continue
    #     if self.boundary.periodicDisplacement(self.position, bird.position).length() <= self.alignmentRadius:
    #         acceleration += bird.velocity

    if acceleration.length() == 0:
        return acceleration
    return acceleration.normalize()


def _ruleSeparation(self, flock, cKDTree):
    acceleration = pygame.Vector2(0, 0)

    # option 1
    q = cKDTree.query_ball_point((self.position.x, self.position.y), self.separationRadius)
    for i in range(min(len(q), 15)):
        bird = flock[q[i]]
        if bird == self:
            continue
        if self.boundary.periodicDisplacement(self.position, bird.position).length() <= self.separationRadius:
            pos_vector = self.boundary.periodicDisplacement(bird.position, self.position)
            if pos_vector.length() == 0:
                continue
            acceleration -= pos_vector / (pos_vector.length() ** 2)

    # option 2
    # dis, q = cKDTree.query([(self.position.x, self.position.y)], 10)
    # for i in range(len(q[0])):
    #     if i == len(flock):
    #         break
    #     bird = flock[q[0][i]]
    #     distance = dis[0][i]
    #     if distance <= self.separationRadius:
    #         pos_vector = self.boundary.periodicDisplacement(bird.position, self.position)
    #         if pos_vector.length() == 0:
    #             continue
    #         acceleration -= pos_vector / (pos_vector.length() ** 2)

    # for bird in flock:
    #     if bird == self:
    #         continue
    #     if self.boundary.periodicDisplacement(self.position, bird.position).length() <= self.separationRadius:
    #         pos_vector = self.boundary.periodicDisplacement(bird.position, self.position)
    #         if pos_vector.length() == 0:
    #             continue
    #         acceleration -= pos_vector / (pos_vector.length() ** 2)

    if acceleration.x == 0 and acceleration.y == 0:
        return acceleration
    return acceleration.normalize()


def _ruleRandomPerturbation(self):
    acceleration = pygame.Vector2(0, 0)
    x_random = np.random.default_rng().random()
    y_random = 1 - x_random ** 2
    acceleration.x = x_random
    acceleration.y = y_random
    return acceleration


def _ruleMouseFollow(self):
    acceleration = pygame.Vector2(0, 0)
    if self.mouseDown:
        acceleration = self.boundary.periodicDisplacement(self.mousePos, self.position)
    if acceleration.length() != 0:
        return acceleration.normalize()
    return acceleration


def _ruleWind(self):
    acceleration = pygame.Vector2(0, 0)

    # if pygame.key.get_pressed()['w']:
    #     acceleration.y -= 10

    return acceleration

def _ruleEscape(self, hunters):
    acceleration = pygame.Vector2(0, 0)
    for predator in hunters:
        if self.boundary.periodicDisplacement(predator.position, self.position).length() <= self.escapeDistance:
            pos_vector = self.boundary.periodicDisplacement(self.position, predator.position)
            acceleration += pos_vector / pos_vector.length()**2

    if acceleration.length() == 0:
        return acceleration
    return acceleration.normalize()


class Bird:
    def __init__(self, x, y):
        # init position
        self.position = pygame.Vector2(x, y)
        # init velocity
        vx = np.random.uniform(-1, 1)
        vy = np.random.uniform(-1, 1)
        self.velocity = pygame.Vector2(vx, vy)
        self.velocity.normalize_ip()
        self.velocity *= np.random.uniform(1, 5)
        self.maxSpeed = 5
        # init acceleration
        self.acceleration = pygame.Vector2(0, 0)
        self.maxAcceleration = 1
        # init boundary
        self.boundary = Boundary(0, 800, 0, 600)
        # init display
        self.size = 3
        self.angle = 0
        self.color = (255, 255, 255)
        self.secondaryColor = (0, 0, 0)
        self.stroke = 2
        self.mouseDown = False
        self.mousePos = pygame.Vector2(0, 0)
        # init rule weights
        self.setRuleWeights()
        self.mateCooldown = 100
        self.mateCounter = 60

        self.sex = np.random.randint(0, 2)
        if self.sex == 0:
            self.color = (150, 150, 150)
        else:
            self.color = (255, 255, 255)

    def computeAcceleration(self, flock, hunters, cKDTree):
        self.acceleration *= 0
        alignment = self.ruleAlignment(flock, cKDTree)
        self.acceleration += alignment * self.alignmentWeight
        cohesion = self.ruleCohesion(flock, cKDTree)
        self.acceleration += cohesion * self.cohesionWeight
        separation = self.ruleSeparation(flock, cKDTree)
        self.acceleration += separation * self.separationWeight
        randomPerturbation = self.ruleRandomPerturbation()
        self.acceleration += randomPerturbation * self.randomPerturbationWeight
        mouseFollow = self.ruleMouseFollow()
        self.acceleration += mouseFollow * self.mouseFollowWeight
        # wind = self.ruleWind()
        # self.acceleration += wind
        escape = self.ruleEscape(hunters)
        self.acceleration += escape * self.escapeWeight

    def update(self, flock, hunters, cKDTree):
        self.computeAcceleration(flock, hunters, cKDTree)

        self.velocity += self.acceleration
        self.velocity = limit(self.velocity, self.maxSpeed)

        self.position += self.velocity
        self.boundary.periodicProject(self.position)

        self.angle = np.arctan2(self.velocity.y, self.velocity.x) + np.pi / 2

        if self.mateCounter == 0:
            self.mate(flock, cKDTree)
        else:
            self.mateCounter -= 1

    def mate(self, flock, cKDTree):
        q = cKDTree.query_ball_point((self.position.x, self.position.y), self.matingDistance)

        for i in range(min(len(q), 5)):
            bird = flock[q[i]]
            if self.boundary.periodicDisplacement(bird.position, self.position).length() <= self.matingDistance:
                if bird.mateCounter == 0 and self.sex != bird.sex:
                    if np.random.randint(0, len(flock)) >= 25:
                        self.mateCounter = self.mateCooldown
                        bird.mateCounter = bird.mateCooldown
                        continue
                    flock.append(Bird(self.position.x+10, self.position.y+10))

        # for bird in flock:
        #     if self.boundary.periodicDisplacement(bird.position, self.position).length() <= self.matingDistance:
        #         if bird.mateCounter == 0 and self.sex != bird.sex:
        #             if np.random.randint(0, len(flock)) >= 25:
        #                 self.mateCounter = self.mateCooldown
        #                 bird.mateCounter = bird.mateCooldown
        #                 continue
        #             flock.append(Bird(self.position.x+10, self.position.y+10))

    def setRuleWeights(self):
        _setRuleWeights(self)

    def ruleAlignment(self, flock, cKDTree):
        return _ruleAlignment(self, flock, cKDTree)

    def ruleCohesion(self, flock, cKDTree):
        return _ruleCohesion(self, flock, cKDTree)

    def ruleSeparation(self, flock, cKDTree):
        return _ruleSeparation(self, flock, cKDTree)

    def ruleRandomPerturbation(self):
        return _ruleRandomPerturbation(self)

    def ruleMouseFollow(self):
        return _ruleMouseFollow(self)

    def ruleWind(self):
        return _ruleWind(self)

    def ruleEscape(self, hunters):
        return _ruleEscape(self, hunters)

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


