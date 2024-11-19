from game import *
from ui import *
from passives import *

class ShopCard(Button):
    def __init__(self, root_entity, relative_rect, col, text, onAction, description):
        super().__init__(root_entity, relative_rect, col, text, onAction)
        print(self.uiTag)
        self.description = description

    def draw(self, window):
        super().draw(window)
        if self.hovered:
            shop = game.get_entity_by_id('shop')
            x = shop.rect.center[0]
            y = shop.rect.y - game.H*0.15
            drawText(
                window, self.description, (255,255,255),
                (x,y), 45, True
             )

class Shop(Menu):
    def __init__(self):
        super().__init__(
            "shop", 100000,
            (pygame.Color("#503197"), pygame.Color("#18215d"))
        )
        w, h = game.W*0.75, game.H*0.5
        self.openRect = pygame.Rect((game.W-w)/2,(game.H-h)*0.65,w,h)
        self.closeRect = pygame.Rect((game.W-w)/2,game.H*1.2,w,h)
        self.rect = self.closeRect.copy()

        self.heal_cost = 100

        self.cards = []

    def create_card_ui_elem(self, center, wh, bttnCol, txtObj, func, desc):
        # params( (x, y), (w, h), Text(), onAction )
        rect = pygame.Rect((0,0),(wh))
        rect.center = center
        btn = ShopCard(self.UIRoot, rect, bttnCol, txtObj, func, desc)
        self.UIRoot.add_element(btn)
        return btn

    def add_elements(self):
        # exit button
        self.create_centered_button(
            (self.rect.w/2, self.rect.h),
            (self.rect.w/5,self.rect.h/5),
            pygame.Color("#18215d"), Text("EXIT",(255,255,255),45),
            self.close
        )

        # heal button
        def heal(btn):
            player = game.get_entity_by_id('player')
            if player.copper >= self.heal_cost and player.health < player.maxHealth:
                player.copper -= self.heal_cost
                player.heal(player.maxHealth*0.35)
                self.heal_cost *= 1.25
                self.heal_cost = round(self.heal_cost/10)*10
                btn.text.string = f"+35% Health : ${self.heal_cost}"
                return True
            return False
        self.create_centered_button(
            (self.rect.w/5, self.rect.h),
            (self.rect.w/3,self.rect.w/15),
            pygame.Color(90,180,90), Text(f"+35% Health : ${self.heal_cost}",(255,255,255),45),
            heal
        )

        # card buttons
        rect = pygame.Rect((self.rect.w*0.1,-game.H*0.2), (self.rect.w*0.8, game.H*0.15)) # text box area idk
        def f(btn):
            return
        btn = Button(self.UIRoot, rect, (0,0,0), Text("",(0,0,0),0), f)
        btn.disabled = True
        btn.outlined = True
        self.UIRoot.add_element(btn)
        for i in range(0,3):
            def func(e, index=i):
                player = game.get_entity_by_id('player')
                if player.copper >= self.cards[index].basePrice:
                    player.copper -= self.cards[index].basePrice
                    player.deck.add_card(self.cards[index])
                    e.remove_self()
                    return True
                return False

            dims = (self.rect.w*0.21,self.rect.h*0.7)
            cardRectx = (i+1)*self.rect.w/4
            cardRecty = self.rect.h*0.4
            cardBtn = self.create_card_ui_elem(
                (cardRectx, cardRecty),
                dims,
                pygame.Color("#503197"), Text(self.cards[i].name,(255,255,255),35),
                func, self.cards[i].desc
            )

            labelRect = pygame.Rect(0,0,0,0)
            labelRect.center = (cardBtn.rect.w/2, cardBtn.rect.h*1.1)
            labelTxt = Text("$"+str(self.cards[i].basePrice), (255,255,255),35)
            self.UIRoot.add_element(Label(cardBtn, labelRect, labelTxt))

    def gen_cards(self, rarity):
        for i in range(3):
            rand_card = PASSIVE_CARDS[rarity][random.randint(0,len(PASSIVE_CARDS[rarity])-1)]
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
