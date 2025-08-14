class Boundary:
    def __init__(self, min_x, max_x, min_y, max_y):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def size_x(self):
        return self.max_x - self.min_x

    def size_y(self):
        return self.max_y - self.min_y

    def periodicProject(self, p):
        while p.x > self.max_x:
            p.x -= self.size_x()
        while p.x < self.min_x:
            p.x += self.size_x()
        while p.y > self.max_y:
            p.y -= self.size_y()
        while p.y < self.min_y:
            p.y += self.size_y()

    def periodicDisplacement(self, p, q):
        # gives the vector pointing from q to p, taking into account periodic boundary conditions
        displacement = p - q
        if displacement.x > self.size_x() / 2:
            displacement.x -= self.size_x()
        if displacement.x < -self.size_x() / 2:
            displacement.x += self.size_x()
        if displacement.y > self.size_y() / 2:
            displacement.y -= self.size_y()
        if displacement.y < -self.size_y() / 2:
            displacement.y += self.size_y()
        return displacement