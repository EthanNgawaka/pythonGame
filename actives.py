from bullets import EnemyBullet
from card import *

class ActiveCard(Card):
    name="name"
    desc="description"
    basePrice=0
    cooldown=0
    def __init__(self):
        super().__init__()

        i = len(self.player.deck.actives())
        dims = (game.W*0.26,game.H*0.06)
        pad = (game.W - dims[0]*3)/4
        cardRectx = pad*(i+1) + (i)*dims[0]
        cardRecty = game.H-dims[1]

        self.rect = Rect((cardRectx, cardRecty),dims)
        game.curr_scene.add_entity(self, "active card")

        self.activation_key = self.player.get_active_key(i)

        self.timer = 0

    def onAction(self):
        pass

    def update(self, dt):
        wave = game.get_entity_by_id("wave")
        if self.timer > 0 and wave.timer < wave.length:
            self.timer -= dt
            return

        if game.key_pressed(self.activation_key):
            self.onAction()
            self.timer = self.cooldown

    def draw(self, window):
        drawRect(window, self.rect, (255,255,255))

        string = pygame.key.name(self.activation_key).upper()
        drawText(window, string, (0,0,0), self.rect.topleft+pygame.Vector2(10,10), 35)

        string = self.name.upper()
        drawText(window, string, (0,0,0), self.rect.center, 35, True)

        string = f"{max(0,self.timer):.2f}s"
        if self.timer <= 0:
            string = "READY"
        rect = self.rect.center.copy()
        rect.x += self.rect.w * 0.37
        drawText(window, string, (0,0,0), rect, 35, True)

        if self.timer/self.cooldown > 0:
            over_rect = self.rect.copy()
            over_rect.w *= self.timer/self.cooldown
            drawRect(window, over_rect, (55,55,55,128))

class Blast(ActiveCard):
    name="Big Boom"
    desc="Boom boom (idk what to name this)"
    basePrice=100
    cooldown = 45
    def onAction(self):
        self.player.AOE_blast(250, 30)

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
        Patch,
    ],
    "rare":[
        Blast, EMP, Repulse,
    ],
    "legendary":[
    ],
    "devil_deal":[ # definitely not stealing from isaac
    ],
}
