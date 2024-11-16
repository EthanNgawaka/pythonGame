from game import *

class Bullet(Entity):
    def __init__(self, center, vel):
        player = game.get_entity_by_id("player")

        self.r = self.get_size(player.dmg*player.dmgMultiplier)
        self.rect = Rect((0,0), (self.r*2, self.r*2))
        self.rect.center = center

        self.vel = vel

        self.piercesLeft = player.piercing
        self.piercedEnemies = []

    def has_not_pierced(self, enemy):
        for e in self.piercedEnemies:
            if e == enemy:
                return False
        return True

    def get_size(self,x):
        return max(x, 3)
    
    def on_enemy_collision(self, enemy):
        self.piercesLeft -= 1
        self.piercedEnemies.append(enemy)

        if self.piercesLeft < 0:
            self.remove_self()

    def update(self, dt):
        self.move(self.vel)
        if not AABBCollision(self.rect, [0,0,game.W,game.H]):
            self.remove_self()

    def draw(self, window):
        drawCircle(window, (self.rect.center, self.r), (255,255,0))

class EnemyBullet(Entity):
    def __init__(self, center, vel, dmg):
        self.r = self.get_size(2)
        self.rect = Rect((0,0), (self.r*2, self.r*2))

        self.rect.center = center
        self.vel = vel
        self.dmg = dmg

    def get_size(self,x):
        return max(x*1.6, 4)
    
    def on_player_collision(self, player):
        self.remove_self()

    def update(self, dt):
        self.move(self.vel)
        player = game.get_entity_by_id("player")
        if AABBCollision(self.rect, player.rect):
            self.on_player_collision(player)
            player.hit(self)
        if not AABBCollision(self.rect, [0,0,game.W,game.H]):
            self.remove_self()

    def draw(self, window):
        drawCircle(window, (self.rect.center, self.r*2), (255,0,0))
