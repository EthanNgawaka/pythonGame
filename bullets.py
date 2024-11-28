from game import *
from status_effects import *

class Web(Entity):
    def __init__(self, pos, radius, lifetime):
        self.r = radius
        self.center = pos
        self.timer = lifetime
        self.drawR = 0
        self.entities_on_me = {} # ent: timer

    def collis(self, dt):
        entities = game.get_entities_by_id("enemy")
        entities.append(game.get_entity_by_id("player"))

        time_to_slow = 1.25
        for ent in entities:
            if (ent.rect.center - self.center).length() <= self.r and not isinstance(ent, EnemyBullet):
                if ent in self.entities_on_me:
                    self.entities_on_me[ent] -= dt
                    if self.entities_on_me[ent] <= 0 and ent.get_stacks_of_status_effects(Slow) < 5:
                        ent.add_status_effect(Slow)
                        self.entities_on_me[ent] = time_to_slow
                else:
                    self.entities_on_me[ent] = time_to_slow
                    if ent.get_stacks_of_status_effects(Slow) <= 0:
                        ent.add_status_effect(Slow)
            elif ent in self.entities_on_me:
                del self.entities_on_me[ent]
    
    def update(self, dt):
        self.timer -= dt
        self.collis(dt)

        if self.timer <= 0:
            self.drawR = lerp(self.drawR, 0, 0.1)
            if self.timer <= -0.5:
                self.remove_self()
        else:
            self.drawR = lerp(self.drawR, self.r, 0.1)

    def draw(self, window):
        drawCircle(window, (self.center, self.drawR), (255,255,255))

def spawn_web(pos, radius, lifetime):
    game.curr_scene.add_entity(Web(pos, radius, lifetime), "creep", 1) # def not stealing name from isaac

class Bullet(Entity):
    def __init__(self, center, vel):
        player = game.get_entity_by_id("player")

        self.r = self.get_size(player.dmg*player.dmgMultiplier*player.bulletSize)
        # so the bullet rect is actually WAY bigger than the drawn bullet
        # cause aiming feels so tedious without it unless u got bigboy damage

        w = max(self.r*1.5, 35)
        self.rect = Rect((0,0), (w,w))
        self.rect.center = center

        self.vel = vel

        self.piercesLeft = player.piercing
        self.piercedEnemies = []

        self.fire_spawn_rate = 0.05
        self.timer = 0
        self.last_fire_spawn = self.timer
        self.bouncy = False
        self.homing = False
        self.homing_thresh = 350
        self.targeting_enemy = None

    def has_not_pierced(self, enemy):
        for e in self.piercedEnemies:
            if e == enemy:
                return False
        return True

    def get_size(self,x):
        return max(x, 3)
    
    def on_enemy_collision(self, enemy):
        player = game.get_entity_by_id("player")
        self.piercesLeft -= 1
        self.piercedEnemies.append(enemy)

        if self.piercesLeft < 0:
            self.remove_self()

        if player.hotShot > 0:
            enemy.add_status_effect(Fire, player.hotShot)

        if self.bouncy:
            vec = (self.rect.center - enemy.rect.center).normalize()
            self.vel = vec * self.vel.length()

    def do_homing(self, dt):
        for e in game.get_entities_by_id("enemy"):
            if isinstance(e, EnemyBullet):
                continue
            vec = e.rect.center-self.rect.center
            if vec.length() <= self.homing_thresh and e not in self.piercedEnemies:
                mag = self.vel.length()
                norm = vec.normalize()
                self.vel = self.vel.lerp(norm*self.vel.length(), 0.1)
                self.vel = self.vel.normalize()*mag

    def update(self, dt):
        player = game.get_entity_by_id("player")

        if self.homing:
            self.do_homing(dt)
        self.move(self.vel*dt)
        if not AABBCollision(self.rect, [0,0,game.W,game.H]):
            if self.bouncy and self.piercesLeft > 0:
                if self.rect.y < 0 or self.rect.y > game.H:
                    self.vel.y *= -1
                if self.rect.x < 0 or self.rect.x > game.W:
                    self.vel.x *= -1
                self.piercesLeft -= 1
                self.move(self.vel*dt)
            else:
                self.remove_self()

        # fire particles
        if player.hotShot > 0:
            if abs(self.timer-self.last_fire_spawn) > self.fire_spawn_rate:
                self.last_fire_spawn = self.timer
                spawn_fire(*self.rect.center)
        # -------------- #

        self.timer += dt

    def draw(self, window):
        drawCircle(window, (self.rect.center, self.r), (255,255,0))

class EnemyBullet(Entity):
    def __init__(self, center, vel, dmg):
        super().__init__()
        self.r = self.get_size(2)
        self.rect = Rect((0,0), (self.r*2, self.r*2))

        self.rect.center = center
        self.vel = vel
        self.inflictFire = False
        self.dmg = dmg

        self.fire_spawn_rate = 0.1
        self.timer = 0
        self.last_fire_spawn = self.timer

    def get_size(self,x):
        return max(x*1.6, 4)
    
    def on_player_collision(self, player):
        self.remove_self()

    def update(self, dt):
        self.timer += dt
        self.move(self.vel*dt)
        player = game.get_entity_by_id("player")
        if AABBCollision(self.rect, player.rect):
            self.on_player_collision(player)
            player.hit(self)
        if not AABBCollision(self.rect, [0,0,game.W,game.H]):
            self.remove_self()

        if self.inflictFire:
            if abs(self.timer-self.last_fire_spawn) > self.fire_spawn_rate:
                self.last_fire_spawn = self.timer
                spawn_fire(*self.rect.center)

    def draw(self, window):
        drawCircle(window, (self.rect.center, self.r*2), (255,0,0))

# idk where to put this so its goin here because enemies and player import bullets.py soooo
class TemporaryStatChange(Entity):
    """
    to add a temporary state change to an enemy
    just add a new TemporaryStatChange to curr_entities
    so it can update itself independently,
    constructor takes ref to entity it affects, name of the stat, amount it changes, length of effect

    pass in no time if you want to reset the stat change on a func call instead
    """
    def __init__(self, entity, stat_name, change, time=0):
        self.stat_name = stat_name
        self.stat_change = change
        self.timer = time if time > 0 else None
        self.entity = entity

        self.add_to_attr(self.stat_change)

    def add_to_attr(self, change):
        curr_stat = getattr(self.entity, self.stat_name)
        setattr(self.entity, self.stat_name, curr_stat + change)

    def remove_self(self):
        self.add_to_attr(-self.stat_change)
        super().remove_self()

    def update(self, dt):
        if self.timer is None:
            return

        self.timer -= dt
        if self.timer <= 0:
            self.remove_self()

    def draw(self, window):
        pass
