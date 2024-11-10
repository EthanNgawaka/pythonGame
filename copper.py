from game import *

def spawn_copper(pos, qty):
    for i in range(qty):
        theta = random.uniform(-math.pi,math.pi)
        vel = pygame.Vector2(math.cos(theta), math.sin(theta)) * random.randint(0,800)
        game.curr_scene.add_entity(Copper(pos, vel), "coin")

class Copper(Entity):
    def __init__(self, pos, vel):
        self.rect = Rect(pos, (12,12))
        self.vel = vel
        self.distThreshold = 250
        self.forces = pygame.Vector2()

    def attract(self):
        player = game.get_entity_by_id("player")

        attractionSpeed = 60
        distVec = pygame.Vector2(player.rect.x-self.rect.x, player.rect.y-self.rect.y)
        if distVec.length() < self.distThreshold:
            self.distThreshold = 999
            if distVec.length() > 0:
                self.vel += distVec.normalize()*attractionSpeed

        self.collision(player)

    def bound_to_screen(self): # this is temp
        bounds = [
            pygame.Rect(-100,-100, 100, H+200), # left
            pygame.Rect(W,-100, 100, H+200), # right
            pygame.Rect(-100,-100, W+200, 100), # top
            pygame.Rect(-100, H, W+200, 100), # bottom
        ]
        for b in bounds:
            col = AABBCollision(b, self.rect)
            if col:
                if col[0] != 0:
                    self.vel.x = 0
                if col[1] != 0:
                    self.vel.y = 0
                self.move(-pygame.Vector2(col))

    def collision(self, player):
        if AABBCollision(self.rect, player.rect):
            player.copper += 1
            self.remove_self()

    def physics(self, dt):
        accel = self.forces
        self.vel += accel*dt
        self.move(self.vel*dt)
        self.vel*=0.95

    def update(self, dt):
        self.attract()
        self.physics(dt)
        self.bound_to_screen()

    def draw(self, window):
        drawCircle(window, (self.rect.center,self.rect.w/2), (255, 153, 51))
