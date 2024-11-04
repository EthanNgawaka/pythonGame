from game import *
from player import *
from copper import *

# =================== Enemy Base =================== #
class Enemy(Entity):
    def __init__(self):
        self.rect = pygame.Rect(0,0,0,0)
        self.vel = pygame.Vector2()
        self.drag = 0.96
        self.invMass = 1
        self.forces = pygame.Vector2()
        self.value = 10

    def add_force(self, vec):
        self.forces += vec

    def bound_to_screen(self): # this is temp
        if self.rect.x < 0 and self.vel.x < 0:
            self.rect.x = 0
            self.vel.x = 0
        if self.rect.x+self.rect.w > W and self.vel.x > 0:
            self.rect.x = W - self.rect.w
            self.vel.x = 0

        if self.rect.y < 0 and self.vel.y < 0:
            self.rect.y = 0
            self.vel.y = 0
        if self.rect.y+self.rect.h > H and self.vel.y > 0:
            self.rect.y = H - self.rect.h
            self.vel.y = 0
    
    def on_player_collision(self, player):
        print("shd probably override this owo (player collision on enemy)")

    def on_bullet_collision(self, bullet):
        print("shd probably override this owo (bullet collision on enemy)")

    def collision(self):
        bullets = game.get_entities_by_type(Bullet)
        player = game.get_entity_by_id("player")

        if AABBCollision(player.rect, self.rect):
            self.on_player_collision(player)

        for bullet in bullets:
            if AABBCollision(bullet.rect, self.rect):
                bullet.remove_self() # at some point handle this from the bullet
                self.on_bullet_collision(bullet)
    def get_copper_drop_qty(self):
        # returns a random qty btwn the value and half the value of the enemy
        # here you can add whatever modifiers like forager etc
        return random.randint(round(self.value/2),self.value)

    
    def get_unit_vec_to_entity(self, player): # not only player just any entity
        theta = vec_angle_to(pygame.Vector2(self.rect.center), pygame.Vector2(player.rect.center))
        vec = pygame.Vector2(math.cos(theta), math.sin(theta))
        return vec

    def physics(self, dt):
        accel = self.forces*self.invMass
        self.vel += accel*dt

        self.move(self.vel*dt)
        self.vel *= self.drag

        self.forces = pygame.Vector2()

        self.bound_to_screen()

# ===================Enemy Types=================== #
class Fly(Enemy):
    def __init__(self, pos):
        super().__init__()
        self.rect = pygame.Rect(pos, (30,30))
        self.col = (255,0,0)
        self.speed = 1100
        self.drag = 0.98
        self.health = 15
        self.repulsionThresh = 30
        self.value = 10

    def repulse(self):
        enemies = game.get_entities_by_type(Fly)
        for e in enemies:
            vec = pygame.Vector2(e.rect.x-self.rect.x, e.rect.y-self.rect.y)
            if vec.length() < self.repulsionThresh:
                unitVec = self.get_unit_vec_to_entity(e)
                e.add_force(unitVec*self.speed)
                self.add_force(unitVec*-self.speed)

    def movement(self):
        player = game.get_entity_by_id("player")
        self.add_force(self.get_unit_vec_to_entity(player)*self.speed)

    def on_player_collision(self, player):
        pass

    def on_bullet_collision(self, bullet):
        player = game.get_entity_by_id("player")
        self.health -= player.dmg * player.dmgMultiplier

        vec = bullet.vel.normalize()
        self.vel = vec * player.kb
        self.forces = pygame.Vector2()
        if self.health <= 0:
            self.remove_self()
            spawn_copper(self.rect.center, self.get_copper_drop_qty())

    def update(self, dt):
        self.collision()
        self.movement()
        self.physics(dt)
        self.bound_to_screen()
        self.repulse()

    def draw(self, window):
        drawCircle(window, (self.rect.center, self.rect.w/2), self.col)
