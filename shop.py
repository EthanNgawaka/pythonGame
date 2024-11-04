from game import *
from ui import *
from passives import *

cards = {
    "common":[
        SpeedUp, DamageUp, AccuracyUp,
        AttackSpeedUp, BulletSpeedUp, MaxHealthUp
    ],
    "rare":[
        Shotgun, Piercing, LifeStealUp
    ],
    "legendary":[
        DoubleShot, Minigun
    ],
}

class Shop(Entity):
    def __init__(self):
        w, h = W*0.6, H*0.5
        self.openRect = pygame.Rect((W-w)/2,(H-h)/2,w,h)
        self.closeRect = pygame.Rect((W-w)/2,H*1.2,w,h)
        self.rect = self.closeRect.copy()
        self.cards = []
        self.isOpen = False
        self.UIRoot = None

    def gen_cards(self, rarity):
        for i in range(3):
            rand_card = cards[rarity][random.randint(0,len(cards[rarity])-1)]
            self.cards.append(rand_card())

    def add_elements(self):
        player = game.get_entity_by_id("player")
        # exit button
        closeRect = pygame.Rect(0,0,self.rect.w/5,self.rect.h/5)
        closeRect.center = (self.rect.w/2, self.rect.h)
        closeBtn = Button(
            self.UIRoot, closeRect,
            (255,0,0), Text("EXIT",(255,255,255),45),
            self.close
        )

        # card button
        for i in range(1,4):
            cardRect = pygame.Rect(0,0,self.rect.w/5,self.rect.h/5)
            cardRect.center = (i*self.rect.w/4, self.rect.h/4)
            cardBtn = Button(
                self.UIRoot, cardRect,
                (0,0,0), Text(self.cards[i-1].name,(255,255,255),45),
                # use def index param here because
                # each lambda isnt in its own scope so it only stores
                # a ref to i which then just uses the last value of i
                # so all the cards are the same as the last one (sigh)
                lambda e, index=i-1:(
                    player.deck.add_card(self.cards[index]),
                    e.remove_self()
                )
            )
            self.UIRoot.add_element(cardBtn)

        self.UIRoot.add_element(closeBtn)

    def close(self, elem):
        self.isOpen = False
        print(self.isOpen)

    def lerp(self, targ_rect, t):
        vec1 = pygame.Vector2(self.rect.x, self.rect.y)
        vec2 = pygame.Vector2(targ_rect.x, targ_rect.y)
        vec3 = vec1.lerp(vec2, t)
        self.rect.x = vec3.x
        self.rect.y = vec3.y

    def open(self):
        if not self.isOpen:
            self.isOpen = True
            self.cards = []
            self.UIRoot = UI_Root(game.get_entity_by_id("bg"), self.rect, (255,0,255))
            game.curr_scene.add_entity(self.UIRoot, "shop ui root", 10000)
            self.gen_cards("rare")
            self.add_elements()

    
    def draw(self, window):
        pass
    
    def update(self, dt):
        if self.isOpen:
            self.lerp(self.openRect, 0.1)
        else:
            if self.UIRoot is not None:
                dist = abs(self.rect.y - self.closeRect.y)
                self.lerp(self.closeRect, 0.1)
                if dist < 80: # arbitrary seems to work fine tho
                    self.UIRoot.remove_self()
                    self.UIRoot = None
