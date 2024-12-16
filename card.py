from game import *

class Card(Entity):
    def __init__(self):
        self.rect = None#Rect((game.W,game.H),(128,128))
        self.player = game.get_entity_by_id("player")

    def update(self, dt):
        self.passive()

    def draw(self, window):
        pass

    def on_pickup(self): # triggered on pickup
        pass

    def passive(self): # triggered every frame
        pass

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

        self.img = Image("./assets/active_icon.png", *self.rect)

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
        #drawRect(window, self.rect, (255,255,255))
        self.img.draw(window,self.rect.copy())

        name = self.name.upper()
        rec = self.rect.copy().center
        rec.x = self.rect.x + 35*1.5
        rec.y -= 35/2

        time = f"{max(0,round(self.timer))}s"
        if self.timer <= 0:
            time = "READY"

        drawText(window, name+" | "+time, pygame.Color("#22ff00"), rec, 35, False)

        if self.timer/self.cooldown > 0:
            over_rect = self.rect.copy()
            over_rect.w *= self.timer/self.cooldown
            drawRect(window, over_rect, (55,55,55,128))
