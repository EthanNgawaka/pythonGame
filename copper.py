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
        self.sprite = Spritesheet(self.rect, "./assets/coin.png", (32,32), 0.05)
        self.sprite.addState("normal", 0, 10)
        self.sprite.addState("glitched", 1, 7)
        self.sprite.setState("normal")
        self.glitch_cooldown = 0
        
        
    def attract(self):
        player = game.get_entity_by_id("player")

        attractionSpeed = 60
        distVec = pygame.Vector2(player.rect.x-self.rect.x, player.rect.y-self.rect.y)
        wave = game.get_entity_by_id("wave")
        end_of_round = len(game.get_entities_by_id('enemy')) <= 0 and wave.timer >= wave.length
        if distVec.length() < self.distThreshold or end_of_round:
            self.distThreshold = 999
            if distVec.length() > 0:
                self.vel += distVec.normalize()*attractionSpeed

        self.collision(player)

    def bound_to_screen(self): # this is temp
        bounds = [
            pygame.Rect(-100,-100, 100, game.H+200), # left
            pygame.Rect(game.W,-100, 100, game.H+200), # right
            pygame.Rect(-100,-100, game.W+200, 100), # top
            pygame.Rect(-100, game.H, game.W+200, 100), # bottom
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
        self.sprite.update(dt)
        self.glitch_cooldown -= dt
        if self.glitch_cooldown <= 0:
            self.glitch_cooldown = random.uniform(0.1,0.5)
            if random.uniform(0, 100) <= 5:
                self.sprite.setState("glitched")
            else:
                self.sprite.setState("normal")

    def draw(self, window):
        self.sprite.draw(self.rect.scale(4,4), window)