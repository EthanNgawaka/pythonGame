from game import *

class Point:
    def __init__(self, pos, targ_entity=None, locked=False):
        self.pos = pos
        self.target_entity = targ_entity
        print(targ_entity)
        self.locked = locked

class Bend(Entity):
    def __init__(self, len, points):
        super().__init__()
        self.length = len
        self.points = points
        self.joint = Vec2()

    def update(self, dt):
        p1 = self.points[0]
        p2 = self.points[1]
        A = p1.pos
        B = p2.pos
        mid = A + (B-A)/2
        AtoB = B-A
        unit = AtoB.normalize()
        normal = Vec2(-unit.y, unit.x)
        if AtoB.x < 0:
            normal *= -1
        self.joint = mid - normal * max(0,self.length - AtoB.length())

        if (p1.pos - p2.pos).length() > self.length:
            if not p1.locked:
                p1.pos = p2.pos + (A-B).normalize()*self.length
            else:
                p2.pos = p1.pos + (B-A).normalize()*self.length

        if p1.target_entity is not None:
            p1.pos = p1.pos.lerp(p1.target_entity.rect.center, 1)

        if p2.target_entity is not None:
            p2.pos = p2.pos.lerp(p2.target_entity.rect.center, 1)

    def draw(self, window):
        drawLine(window, self.points[0].pos, self.joint)
        drawLine(window, self.points[1].pos, self.joint)

