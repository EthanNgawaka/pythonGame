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
class Shop(Menu):
    def __init__(self):
        super().__init__(
            "shop", 100000,
            (pygame.Color("#503197"), pygame.Color("#18215d"))
        )
        w, h = game.W*0.75, game.H*0.5
        self.openRect = pygame.Rect((game.W-w)/2,(game.H-h)/2,w,h)
        self.closeRect = pygame.Rect((game.W-w)/2,game.H*1.2,w,h)
        self.rect = self.closeRect.copy()

        self.cards = []

    def add_elements(self):
        # exit button
        self.create_centered_button(
            (self.rect.w/2, self.rect.h),
            (self.rect.w/5,self.rect.h/5),
            pygame.Color("#18215d"), Text("EXIT",(255,255,255),45),
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

            dims = (self.rect.w*0.21,self.rect.h*0.7)
            cardRectx = (i+1)*self.rect.w/4
            cardRecty = self.rect.h*0.4
            cardBtn = self.create_centered_button(
                (cardRectx, cardRecty),
                dims,
                pygame.Color("#503197"), Text(self.cards[i].name,(255,255,255),35),
                func
            )

            labelRect = pygame.Rect(0,0,0,0)
            labelRect.center = (cardBtn.rect.w/2, cardBtn.rect.h*1.1)
            labelTxt = Text("$"+str(self.cards[i].basePrice), (255,255,255),35)
            self.UIRoot.add_element(Label(cardBtn, labelRect, labelTxt))

    def gen_cards(self, rarity):
        for i in range(3):
            rand_card = cards[rarity][random.randint(0,len(cards[rarity])-1)]
            self.cards.append(rand_card())

    def close(self, elem):
        super().close(elem)
        game.get_entity_by_id("wave").new_round()

    def open(self):
        if not self.isOpen:
            self.cards = []
            num = game.get_entity_by_id("wave").num
            rarity = "legendary"  if num == 8 else ("rare" if num == 4 else "common")
            self.gen_cards(rarity)
            super().open()
