from game import *
from status_effects import *

class Bullet(Entity):
    def __init__(self, center, vel):
        player = game.get_entity_by_id("player")

        self.r = self.get_size(player.dmg*player.dmgMultiplier)
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

    def update(self, dt):
        player = game.get_entity_by_id("player")
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
