from game import *
from player import *
from copper import *
from particles import *

# =================== Enemy Base =================== #
class Enemy(Entity):
    def __init__(self, pos):
        self.rect = Rect(pos,(30,30))
        self.fire_immunity = False
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
        self.maxHealth = self.health
        self.baseDmg = self.dmg
        self.inflictFire = False
        self.atkRate = 0
        self.dmg_taken_multiplier = 1

    def take_dmg(self, amnt):
        self.health -= amnt * self.dmg_taken_multiplier

    def movement(self):
        pass

    def add_force(self, vec):
        self.forces += vec

    def bound_to_screen(self): # this is temp
        if self.rect.x < 0 and self.vel.x < 0:
            self.rect.x = 0
            self.vel.x = 0
        if self.rect.x+self.rect.w > game.W and self.vel.x > 0:
            self.rect.x = game.W - self.rect.w
            self.vel.x = 0

        if self.rect.y < 0 and self.vel.y < 0:
            self.rect.y = 0
            self.vel.y = 0
        if self.rect.y+self.rect.h > game.H and self.vel.y > 0:
            self.rect.y = game.H - self.rect.h
            self.vel.y = 0

    def collision(self):
        bullets = game.get_entities_by_type(Bullet)
        player = game.get_entity_by_id("player")

        if AABBCollision(player.rect, self.rect):
            self.on_player_collision(player)

        for bullet in bullets:
            if AABBCollision(bullet.rect, self.rect) and bullet.has_not_pierced(self):
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
    def get_list_of_status_effects_of_type(self, status_type):
        all_statuses = game.get_entities_by_type(status_type)
        filtered = [s for s in all_statuses if s.ent == self]
        return filtered
    def get_stacks_of_status_effects(self, status_type):
        return len(self.get_list_of_status_effects_of_type(status_type))

    def add_status_effect(self, status_type, stacks=1):
        # a status effect "stack" is just an entity that
        # changes something about another entity every frame
        # status effects can scale linearly, exponentially or whatever with stacks
        # although linear is the easiest (1 stack -5hp/s, 2stack -10hp/s etc)
        # exponential is possible to (example of this is fire)
        for _ in range(stacks):
            game.curr_scene.add_entity(status_type(self), "status player")

    def hit(self, dmg, vec):
        self.take_dmg(dmg)
        self.vel = vec
        self.forces = pygame.Vector2()
        self.stun = 0.1

    def on_bullet_collision(self, bullet):
        player = game.get_entity_by_id("player")
        dmg = player.dmg * player.dmgMultiplier
        if player.lifesteal > 0:
            player.heal(player.lifesteal/4)

        vec = bullet.vel.normalize()
        self.hit(dmg, vec*player.kb)

        if self.health <= 0 and self.alive:
            self.die(math.atan2(vec.y,vec.x))
        bullet.on_enemy_collision(self)

    def die(self, theta=None):
        blood_explosion(*self.rect.center, self.maxHealth, theta)
        self.on_death()
        self.remove_self()
        spawn_copper(self.rect.center, self.get_copper_drop_qty())

        player = game.get_entity_by_id("player")
        if player.lifesteal > 0:
            player.heal(player.lifesteal)
    
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
        if self.health <= 0 and self.alive:
            self.die()
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
        self.col = (72,192,114)
        self.speed = 900
        self.drag = 0.98
        self.health = 10
        self.value = 8
        self.dmg = 10
        self.baseDmg = self.dmg
        self.maxHealth = self.health

    def movement(self):
        player = game.get_entity_by_id("player")
        self.add_force(self.get_unit_vec_to_entity(player)*self.speed)

class BabyFly(Fly):
    def __init__(self, pos):
        super().__init__(pos)
        self.rect.dimensions = pygame.Vector2(15,15)
        self.speed = 700
        self.health = 5
        self.maxHealth = self.health
        self.value = 1
        self.dmg = 5
        self.baseDmg = self.dmg

class Cockroach(Enemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.col = pygame.Color("saddlebrown")
        self.speed = 2000
        self.speedRange = [1000,2200]
        self.drag = 0.9
        self.dmg = 10
        self.baseDmg = self.dmg
        self.value = 15
        self.health = 16
        self.maxHealth = self.health

        self.movementTimer = 0
        self.movementRot = 90
        self.movementRotTarg = 90
        self.movementThresh = 0
        self.maxSpeed = 2500

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
            self.speed = self.maxSpeed

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
        self.baseDmg = self.dmg
        self.speedRange = [1500,2600]
        self.maxHealth = self.health
    
    def draw(self, window):
        drawCircle(window, (self.rect.center, self.rect.w/4), self.col)

class MotherCockroach(Cockroach):
    def __init__(self, pos):
        super().__init__(pos)
        self.rect = Rect(pos, (50,50))
        self.speedRange = [500,1000]
        self.health = 30
        self.value = 10
        self.maxSpeed = 1200
        self.maxHealth = self.health

    def on_death(self):
        for i in range(random.randint(15,35)):
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
        self.baseDmg = self.dmg
        self.atkRate = 2.25
        self.baseAtkRate = self.atkRate
        self.atkThresh = 750
        self.col = pygame.Color("black")
        self.maxHealth = self.health

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
        vec = pygame.Vector2(math.cos(theta), math.sin(theta)) * random.uniform(5,10) * 60
        game.curr_scene.add_entity(EnemyBullet(self.rect.center, vec, self.dmg), "enemy bullet")
        self.add_force(-vec*6)


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

class AntSwarm:
    def __init__(self, pos):
        for i in range(random.randint(2,4)):
            off = pygame.Vector2(random.uniform(-100, 100),random.uniform(-100, 100))
            game.curr_scene.add_entity(Ant(pos+off), "enemy")

class Ant(Enemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.rect.dimensions = pygame.Vector2(25,25)
        self.drag = 0.8
        self.speed = 2500
        self.atkThresh = 200
        self.timer = 0
        self.value = 2
        self.col = pygame.Color(127,90,90)
        self.dmg = 5
        self.baseDmg = self.dmg
        self.dir = 1
        self.maxHealth = self.health

    def bound_to_screen(self): # this is temp
        if self.rect.x < 0 and self.vel.x < 0:
            self.rect.x = 0
            self.vel.x = 0
            self.dir *= -1

        if self.rect.x+self.rect.w > game.W and self.vel.x > 0:
            self.rect.x = game.W - self.rect.w
            self.vel.x = 0
            self.dir *= -1

        if self.rect.y < 0 and self.vel.y < 0:
            self.rect.y = 0
            self.vel.y = 0
            self.dir *= -1

        if self.rect.y+self.rect.h > game.H and self.vel.y > 0:
            self.rect.y = game.H - self.rect.h
            self.vel.y = 0
            self.dir *= -1

    def movement(self):
        player = game.get_entity_by_id("player")
        p_pos = pygame.Vector2(player.rect.center)
        s_pos = pygame.Vector2(self.rect.center)
        dist = (p_pos - s_pos).length()
        angle = self.dir*lerp(0, 90, self.atkThresh/dist)
        self.add_force(self.get_unit_vec_to_entity(player).rotate(angle)*self.speed)

    def update(self, dt):
        super().update(dt)
        self.timer += dt

class FireAntSwarm:
    def __init__(self, pos):
        num = random.randint(2,6)
        for i in range(num):
            off = pygame.Vector2(random.uniform(-100, 100),random.uniform(-100, 100))
            game.curr_scene.add_entity(FireAnt(pos+off), "enemy")

class FireAnt(Ant):
    def __init__(self, pos):
        super().__init__(pos)
        self.atkRate = 4.35 + random.uniform(-0.5,1.5)
        self.baseAtkRate = self.atkRate
        self.last_shot = 0
        self.col = (255,50,50)
        self.fire_immunity = True
        self.thresh = 500
        self.maxHealth = self.health

    def shoot(self):
        player = game.get_entity_by_id("player")
        p_pos = pygame.Vector2(player.rect.center)
        s_pos = pygame.Vector2(self.rect.center)
        theta = vec_angle_to(s_pos,p_pos)
        vec = pygame.Vector2(math.cos(theta), math.sin(theta)) * random.uniform(5,10) * 80
        bllt = EnemyBullet(self.rect.center, vec, self.dmg)
        bllt.inflictFire = True # this just enables the fire
        game.curr_scene.add_entity(bllt, "enemy bullet")
        self.add_force(-vec*6)

    def update(self, dt):
        player = game.get_entity_by_id("player")
        p_pos = pygame.Vector2(player.rect.center)
        s_pos = pygame.Vector2(self.rect.center)
        super().update(dt)
        if abs(self.timer - self.last_shot) >= self.atkRate and (p_pos-s_pos).length() <= self.thresh:
            self.last_shot = self.timer
            self.shoot()

class TermiteSwarm:
    # lil bit of an inbetween class cause of the way enemies are spawned
    #just spawns x amount of termites
    def __init__(self, pos):
        for i in range(random.randint(5,25)):
            off = pygame.Vector2(random.uniform(-100, 100),random.uniform(-100, 100))
            game.curr_scene.add_entity(Termite(pos+off), "enemy")

class Termite(Enemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.rect.dimensions = pygame.Vector2(15,15)
        self.drag = 1
        self.speed = 2500
        self.atkThresh = 200
        self.timer = 0
        self.value = 2
        self.col = pygame.Color(255,120,120)
        self.dmg = 5
        self.baseDmg = self.dmg
        self.health = 4
        self.maxHealth = self.health

    def movement(self):
        player = game.get_entity_by_id("player")
        p_pos = pygame.Vector2(player.rect.center)
        s_pos = pygame.Vector2(self.rect.center)

        other_termites = game.get_entities_by_type(Termite)
        other_termites.remove(self)

        protected_range = 100
        protected_range_squared = protected_range**2
        visual_range = 40
        visual_range_squared = visual_range**2
        centering_factor = 0.01
        matching_factor = 0.01
        avoidfactor = 0.01
        turnfactor = 10
        minSpeed = 280
        maxSpeed = 400

        close_dp = pygame.Vector2()
        avg_pos = pygame.Vector2()
        avg_vel = pygame.Vector2()
        neighbors = 0
        for other_termite in other_termites:
            dp = self.rect.topleft - other_termite.rect.topleft

            if dp.length() < visual_range:
                sqrd_dist = dp.length()**2
                if sqrd_dist < protected_range_squared:
                    close_dp += dp

                elif sqrd_dist < visual_range_squared:
                    neighbors += 1

        if neighbors > 0:
            avg_pos /= neighbors
            avg_vel /= neighbors
            

        targ = player.rect.center
        self.vel += (avg_pos - self.rect.topleft + targ)*centering_factor + (avg_vel - self.vel)*matching_factor
        self.vel += close_dp*avoidfactor

        margin = 0.05
        if self.rect.y < game.H*margin:
            self.vel.y += turnfactor
        if self.rect.y > game.H*(1-margin):
            self.vel.y -= turnfactor

        if self.rect.x < game.W*margin:
            self.vel.x += turnfactor
        if self.rect.x > game.W*(1-margin):
            self.vel.x -= turnfactor

        speed = self.vel.length()
        if speed < minSpeed:
            self.vel = self.vel.normalize() * minSpeed
        if speed > maxSpeed:
            self.vel = self.vel.normalize() * maxSpeed

    def repulse(self):
        pass

class Snail(Enemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.rect = Rect(pos, (40,40))
        self.col = (255,0,0)
        self.col1 = (255,0,0)
        self.col2 = (50,50,50)
        self.speed = 3100
        self.drag = 0.8
        self.health = 10
        self.value = 8
        self.dmg = 10
        self.baseDmg = self.dmg
        self.timer = 0
        self.maxHealth = self.health

    def movement(self):
        player = game.get_entity_by_id("player")
        vec = self.get_unit_vec_to_entity(player)*self.speed
        vec *= self.get_moving()
        self.add_force(vec)
        self.speed = (abs(math.sin(4*(self.timer-math.pi/2)))*3100)

    def update(self, dt):
        super().update(dt)
        self.timer += dt
        if self.get_moving() > 0:
            self.col = self.col1
        else:
            self.col = self.col2

    def get_moving(self):
        return max(0,math.sin(self.timer*math.pi/2)-0.2)

    def on_bullet_collision(self, bullet):
        if self.get_moving() > 0:
            super().on_bullet_collision(bullet)
            return
        bullet.remove_self()
        player = game.get_entity_by_id("player")
        vec = player.rect.center - self.rect.center
        vel = vec.normalize()*bullet.vel.length()
        game.curr_scene.add_entity(EnemyBullet(bullet.rect.center, vel, self.dmg), "enemy bullet")

# TODO (Make it attract everything )
class MagneticSnail(Snail):
    def __init__(self, pos):
        super().__init__(pos)
        self.suckage = 30
        self.suckage_thresh = 650
    
    def update(self, dt):
        super().update(dt)
        if self.get_moving() <= 0:
            # attract player, bullets, enemies excluding self
            player = game.get_entity_by_id("player")
            diff = self.rect.center-player.rect.center
            vec = (diff).normalize()
            d_sqrd = max(diff.length()*diff.length()/100000,1)
            player.vel += (vec*self.suckage) * 1/(d_sqrd)

            for bullet in game.get_entities_by_type(Bullet):
                diff = self.rect.center-bullet.rect.center
                if diff.length() > self.suckage_thresh:
                    continue
                vec = diff.normalize()*self.suckage/20
                speed = bullet.vel.length()
                bullet.vel += vec
                bullet.vel = bullet.vel.normalize()*speed

class Dummy(Enemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.rect = Rect((W/2, H/2), (30, 30))
        self.health = 9999
        self.timer = 0
        self.dps = 0
        self.last_hit = 0
        self.dps_check_thresh = 1
        self.dmg_done = 0
        self.first_hit = 0
        self.maxHealth = self.health
        self.disp_dps = 0

    def update(self, dt):
        super().update(dt)
        self.timer += dt
        if abs(self.last_hit - self.timer) < self.dps_check_thresh:
            time = abs(self.first_hit - self.last_hit)
            if time == 0:
                return
            
            self.dps = self.dmg_done/time
            return
        
        self.dps = 0
        self.dmg_done = 0
        self.first_hit = 0

    def draw(self, window):
        super().draw(window)
        if self.dps > 0:
            self.disp_dps = self.dps
        drawText(window, f"DPS: {self.disp_dps:.2f}", (0,0,0), self.rect.center - pygame.Vector2(0,self.rect.h*2), 40, True)
        drawText(window, f"dmg_done: {self.dmg_done:.2f}", (0,0,0), self.rect.center - pygame.Vector2(0,self.rect.h*4), 40, True)

    def on_bullet_collision(self, bullet):
        player = game.get_entity_by_id("player")
        bullet.on_enemy_collision(self)
        dmg = (player.dmg * player.dmgMultiplier)
        self.dmg_done += dmg
        self.last_hit = self.timer
        if self.first_hit == 0:
            self.first_hit = self.timer

class MotherFly(Enemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.rect = Rect(pos, (60,60))
        self.health = 45
        self.maxHealth = self.health
        self.speed = 200

        self.atkTimer = 0
        self.lastAttack = 0
        self.dmg = 10
        self.baseDmg = self.dmg
        self.atkRate = 5
        self.baseAtkRate = self.atkRate
        self.atkThresh = game.W
        self.col = pygame.Color("black")

        self.atkTimer = 0

    def on_death(self):
        for i in range(random.randint(5,20)):
            spawn_pos = pygame.Vector2(self.rect.topleft)
            spawn_pos.x += random.uniform(0, self.rect.w)
            spawn_pos.y += random.uniform(0, self.rect.h)
            game.curr_scene.add_entity(BabyFly(spawn_pos),"enemy")

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
        EnemyType = BabyFly if random.uniform(0,1) <= 0.75 else Mosquito
        fac = 100 if EnemyType is Mosquito else 40
        vec = pygame.Vector2(math.cos(theta), math.sin(theta)) * random.uniform(5,10) * fac
        enemy = EnemyType(self.rect.center)
        enemy.vel = vec
        enemy.value = 0
        game.curr_scene.add_entity(enemy, "enemy")
        self.add_force(-vec*6)


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
                for i in range(random.randint(4,8)):
                    self.shoot()
