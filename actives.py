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
    cooldown = 30
    def onAction(self):
        self.player.AOE_blast(250, 30)

class Patch(ActiveCard):
    name="Patch"
    desc="Hotfixes!"
    basePrice=100
    cooldown = 120
    def onAction(self):
        self.player.heal(self.player.maxHealth*0.1)

ACTIVE_CARDS = {
    "common":[
        Patch,
    ],
    "rare":[
        Blast,
    ],
    "legendary":[
    ],
    "devil_deal":[ # definitely not stealing from isaac
    ],
}
