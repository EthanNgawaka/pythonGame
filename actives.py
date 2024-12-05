from bullets import *
from card import *

class DebugMode(ActiveCard):
    name="Debug Mode"
    desc="Let's slow down things a lil"
    basePrice=300
    cooldown=60
    def onAction(self):
        game.slow_down_time(0.1, 10)
        # idk if i keep this but it makes the player shoot and move way faster so it doesnt take away allll control
        self.player.change_stat_temporarily("atkRate", -self.player.atkRate*0.75, 1)

class Overclock(ActiveCard):
    name="Overclock"
    desc="TEMP ALL STATS UP"
    basePrice=200
    cooldown=45
    def onAction(self):
        self.player.change_stat_temporarily("dmg", self.player.dmg*0.75, 10)
        self.player.change_stat_temporarily("atkRate", -self.player.atkRate*0.75, 10)
        self.player.change_stat_temporarily("speed", self.player.speed*0.75, 10)

class Blast(ActiveCard):
    name="Big Boom"
    desc="Boom boom (idk what to name this)"
    basePrice=100
    cooldown = 45
    def onAction(self):
        self.player.AOE_blast(250, 30)

class Webbed(ActiveCard):
    name="Webbed"
    desc="Create a slowing web that slows enemies AND you"
    basePrice=100
    cooldown = 15
    def onAction(self):
        spawn_web(self.player.rect.center, 200, 20)

class Patch(ActiveCard):
    name="Patch"
    desc="Hotfixes!"
    basePrice=100
    cooldown = 120
    def onAction(self):
        self.player.heal(self.player.maxHealth*0.1)

class Repulse(ActiveCard):
    name="Repulse"
    desc="Push all enemies and bullets away"
    basePrice=100
    cooldown=10
    def __init__(self):
        super().__init__()
        self.r = game.W
    def onAction(self):
        self.r = 0
        for e in game.get_entities_by_id("enemy"):
            if not isinstance(e, EnemyBullet):
                e.vel = -(self.player.rect.center - e.rect.center).normalize()*3000
                e.stun = 0.4
            else:
                e.vel = -(self.player.rect.center - e.rect.center).normalize()*e.vel.length()

    def draw(self, window):
        super().draw(window)
        if abs(self.r-game.W) > 1:
            drawCircle(window, (self.player.rect.center, self.r), pygame.Color("#53d0ff"), 10)
        self.r = lerp(self.r, game.W, 0.05)

class EMP(ActiveCard):
    name="EMP"
    desc="stands for electro magnetic penis"
    basePrice=100
    cooldown=30
    def __init__(self):
        super().__init__()
        self.r = game.W
    def onAction(self):
        self.r = 0
        for e in game.get_entities_by_id("enemy"):
            if not isinstance(e, EnemyBullet):
                e.stun = 6

    def draw(self, window):
        super().draw(window)
        if abs(self.r-game.W) > 10:
            drawCircle(window, (self.player.rect.center, self.r), pygame.Color("#53d0ff"), 10)
        self.r = lerp(self.r, game.W, 0.05)

ACTIVE_CARDS = {
    "common":[
        Patch, Webbed,
    ],
    "rare":[
        Blast, EMP, Repulse, Overclock,
        DebugMode, 
    ],
    "legendary":[
    ],
    "devil_deal":[ # definitely not stealing from isaac
    ],
}
