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
        w, h = W*0.75, H*0.5
        self.openRect = pygame.Rect((W-w)/2,(H-h)/2,w,h)
        self.closeRect = pygame.Rect((W-w)/2,H*1.2,w,h)
        self.rect = self.closeRect.copy()
        self.cards = []
        self.isOpen = False
        self.UIRoot = None
        self.uiTag = "shop"

    def gen_cards(self, rarity):
        for i in range(3):
            rand_card = cards[rarity][random.randint(0,len(cards[rarity])-1)]
            self.cards.append(rand_card())

    def add_elements(self):
        player = game.get_entity_by_id("player")
        # exit button
        closeRect = pygame.Rect(0,0,self.rect.w/5,self.rect.h/5)
        closeRect.center = (self.rect.w/2, self.rect.h+closeRect.h/2)
        closeBtn = Button(
            self.UIRoot, closeRect,
            (255,0,0), Text("EXIT",(255,255,255),45),
            self.close
        )

        # card buttons
        for i in range(0,3):
            def func(e, index=i):
                player = game.get_entity_by_id('player')
                if player.copper >= self.cards[index].basePrice:
                    player.copper -= self.cards[index].basePrice
                    player.deck.add_card(self.cards[index])
                    e.remove_self()

            cardRect = pygame.Rect(0,0,self.rect.w/4,self.rect.h*0.6)
            pad = (self.rect.w-3*cardRect.w)/4
            cardRect.x = i*cardRect.w+(i+1)*pad
            cardRect.y = self.rect.h/6
            cardBtn = Button(
                self.UIRoot, cardRect,
                (0,0,0), Text(self.cards[i].name,(255,255,255),35),
                func
            )
            labelRect = pygame.Rect(0,0,0,0)
            labelRect.center = (cardRect.w/2, cardRect.h*1.2)
            labelTxt = Text("$"+str(self.cards[i].basePrice), (255,255,255),35)
            self.UIRoot.add_element(cardBtn)
            self.UIRoot.add_element(Label(cardBtn, labelRect, labelTxt))

        self.UIRoot.add_element(closeBtn)

    def close(self, elem):
        self.isOpen = False
        game.curr_scene.UIPriority.remove("shop")
        game.get_entity_by_id("wave").new_round()

    def lerp(self, targ_rect, t):
        vec1 = pygame.Vector2(self.rect.x, self.rect.y)
        vec2 = pygame.Vector2(targ_rect.x, targ_rect.y)
        vec3 = vec1.lerp(vec2, t)
        self.rect.x = vec3.x
        self.rect.y = vec3.y

    def open(self):
        if not self.isOpen:
            self.isOpen = True
            game.curr_scene.UIPriority.append("shop")
            self.cards = []
            self.UIRoot = UI_Root(game.get_entity_by_id("bg"), self.rect, (255,0,255))
            self.UIRoot.uiTag = "shop"
            game.curr_scene.add_entity(self.UIRoot, "shop ui root", 10000)
            rarity = "common"
            if game.get_entity_by_id("wave").num == 4:
                rarity = "rare"
            if game.get_entity_by_id("wave").num == 4:
                rarity = "legendary"
            self.gen_cards(rarity)
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
