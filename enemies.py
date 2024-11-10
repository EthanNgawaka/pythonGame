from game import *
from player import *
from copper import *
from particles import *

# =================== Enemy Base =================== #
class Enemy(Entity):
    def __init__(self, pos):
        self.rect = Rect(pos,(0,0))
        self.vel = pygame.Vector2()
        self.drag = 0.96
        self.invMass = 1
        self.forces = pygame.Vector2()
        self.value = 10
        self.dmg = 1
        self.stun = 0
        self.repulsionThresh = 30
        self.col = pygame.Color("red")
        self.speed = 1000
        self.health  = 10

    def movement(self):
        pass

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

    def collision(self):
        bullets = game.get_entities_by_type(Bullet)
        player = game.get_entity_by_id("player")

        if AABBCollision(player.rect, self.rect):
            self.on_player_collision(player)

        for bullet in bullets:
            if AABBCollision(bullet.rect, self.rect) and bullet.has_not_pierced(self):
                bullet.on_enemy_collision(self)
                self.on_bullet_collision(bullet)
    def get_copper_drop_qty(self):
        # returns a random qty btwn the value and half the value of the enemy
        # here you can add whatever modifiers like forager etc
        return random.randint(round(self.value/2),self.value)

    def on_death(self):
        pass

    def repulse(self):
        enemies = game.get_entities_by_type(self.__class__)
        for e in enemies:
            vec = pygame.Vector2(e.rect.x-self.rect.x, e.rect.y-self.rect.y)
            if vec.length() < self.repulsionThresh:
                unitVec = self.get_unit_vec_to_entity(e)
                e.add_force(unitVec*self.speed)
                self.add_force(unitVec*-self.speed)

    def on_player_collision(self, player):
        player = game.get_entity_by_id("player")
        vec = self.get_unit_vec_to_entity(player)
        self.vel = vec * -player.kb
        self.forces = pygame.Vector2()

        player.hit(self)
        self.stun = 0.5

    def on_bullet_collision(self, bullet):
        player = game.get_entity_by_id("player")
        self.health -= player.dmg * player.dmgMultiplier

        vec = bullet.vel.normalize()
        self.vel = vec * player.kb
        self.forces = pygame.Vector2()
        if self.health <= 0 and self.alive:
            self.die()
        self.stun = 0.1

    def die(self):
        blood_explosion(*self.rect.center)
        self.on_death()
        self.remove_self()
        spawn_copper(self.rect.center, self.get_copper_drop_qty())
    
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

    def update(self, dt):
        self.physics(dt)
        if self.stun > 0:
            self.stun -= dt
            return
        self.collision()
        self.movement()
        self.bound_to_screen()
        self.repulse()

    def draw(self, window):
        drawCircle(window, (self.rect.center, self.rect.w/2), self.col)

# ===================Enemy Types=================== #
class Fly(Enemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.rect = Rect(pos, (30,30))
        self.col = (255,0,0)
        self.speed = 1100
        self.drag = 0.98
        self.health = 10
        self.value = 8
        self.dmg = 10

    def movement(self):
        player = game.get_entity_by_id("player")
        self.add_force(self.get_unit_vec_to_entity(player)*self.speed)

class Cockroach(Enemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.col = pygame.Color("saddlebrown")
        self.speed = 2000
        self.speedRange = [1000,2200]
        self.drag = 0.9
        self.dmg = 10
        self.value = 20
        self.health = 16

        self.movementTimer = 0
        self.movementRot = 90
        self.movementRotTarg = 90
        self.movementThresh = 0

        self.scatterTimer = 0
        self.rect = Rect(pos, (30,30))

    def on_player_collision(self, player):
        super().on_player_collision(player)
        self.scatterTimer = 1.5
        self.stun = 0
        self.speed = 8000

    def movement(self):
        player = game.get_entity_by_id("player")
        move_vec = self.get_unit_vec_to_entity(player)
        perp_vec = move_vec.rotate(self.movementRot) # why degrees we stop using degs in fkin yr9
        self.movementRot = lerp(self.movementRot, self.movementRotTarg, 0.3)

        if self.scatterTimer > 0:
            move_vec *= -1 # run away from player

        self.add_force((move_vec + perp_vec)*self.speed)
        if self.scatterTimer > 0:
            self.speed = 2500

    def update(self, dt):
        super().update(dt)
        self.movementTimer+=dt
        if self.movementThresh <= self.movementTimer:
            self.movementThresh += random.uniform(0.25,1.25)
            self.movementRotTarg *= -1
            self.speed = random.uniform(*self.speedRange)

        self.scatterTimer -= dt

# TODO make baby cockroaches scatter when one is killed by player
class BabyCockroach(Cockroach):
    def __init__(self, pos):
        super().__init__(pos)
        self.rect = Rect(pos, (20,20))
        self.health = 2
        self.value = 2
        self.dmg = 4
        self.speedRange = [2000,3000]
    
    def draw(self, window):
        drawCircle(window, (self.rect.center, self.rect.w/4), self.col)

class MotherCockroach(Cockroach):
    def __init__(self, pos):
        super().__init__(pos)
        self.rect = Rect(pos, (50,50))
        self.speedRange = [500,1000]
        self.health = 30
        self.value = 40

    def on_death(self):
        for i in range(random.randint(8,15)):
            spawn_pos = pygame.Vector2(self.rect.topleft)
            spawn_pos.x += random.uniform(0, self.rect.w)
            spawn_pos.y += random.uniform(0, self.rect.h)
            game.curr_scene.add_entity(BabyCockroach(spawn_pos),"enemy")



class Mosquito(Enemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.rect = Rect(pos, (30,30))
        self.health = 12
        self.speed = 200

        self.atkTimer = 0
        self.lastAttack = 0
        self.dmg = 10
        self.atkRate = 2.5
        self.atkThresh = 550
        self.col = pygame.Color("black")

    def movement(self):
        player = game.get_entity_by_id("player")
        p_pos = pygame.Vector2(player.rect.center)
        s_pos = pygame.Vector2(self.rect.center)
        if (p_pos - s_pos).length() > self.atkThresh:
            f_vec = self.get_unit_vec_to_entity(player)*self.speed
            self.add_force(f_vec)

        theta = random.uniform(math.pi, -math.pi)
        self.vel += (pygame.Vector2(math.cos(theta), math.sin(theta))*random.randint(-30,30))

    def shoot(self):
        player = game.get_entity_by_id("player")
        p_pos = pygame.Vector2(player.rect.center)
        s_pos = pygame.Vector2(self.rect.center)
        innac = 10
        theta = vec_angle_to(s_pos,p_pos) + random.uniform(math.pi/innac, -math.pi/innac)
        vec = pygame.Vector2(math.cos(theta), math.sin(theta)) * random.uniform(5,10)
        game.curr_scene.add_entity(EnemyBullet(self.rect.center, vec, self.dmg), "enemy bullet")

    def on_bullet_collision(self, blt):
        super().on_bullet_collision(blt)
        self.atkTimer = 0.1
        self.lastAttack = 0

    def update(self, dt):
        super().update(dt)
        player = game.get_entity_by_id("player")
        p_pos = pygame.Vector2(player.rect.center)
        s_pos = pygame.Vector2(self.rect.center)
        if (p_pos - s_pos).length() < self.atkThresh:
            self.atkTimer -= dt
            if abs(self.lastAttack - self.atkTimer) > self.atkRate:
                self.lastAttack = self.atkTimer
                for i in range(8):
                    self.shoot()

