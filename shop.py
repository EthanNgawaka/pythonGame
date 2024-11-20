from game import *
from ui import *
from passives import *

class ShopCard(Button):
    def __init__(self, root_entity, relative_rect, col, text, onAction, card):
        super().__init__(root_entity, relative_rect, col, text, onAction)
        print(self.uiTag)
        self.card = card

        labelRect = Rect((0,0),(0,0))
        labelRect.center = (self.rect.w/2, self.rect.h*-0.1)
        labelTxt = Text("$"+str(self.card.basePrice), (255,255,255),35)
        self.root.add_element(Label(self, labelRect, labelTxt))

        self.hoveredY = self.rect.y - self.rect.h*0.07
        self.restY = self.rect.y+self.rect.h/2
        self.targetY = 0
        self.rect.y = self.restY

    def draw_name(self, window):
        drawingRect = self.get_relative_rect().inflate(self.drawingInflation.x, self.drawingInflation.y)
        drawingRect.center = (drawingRect.center[0]+self.shake.x, drawingRect.center[1]+self.shake.y)
        vec = drawingRect.center
        vec.y -= self.rect.h*0.45
        drawingRect.h *= 0.1
        drawRect(window, drawingRect, pygame.Color("#4b0090"))
        drawText(window, self.text.string, self.text.col, vec, round(self.text.size+self.drawingInflation.x/2), True)

        drawingRect.h /= 0.1
        drawingRect.y += drawingRect.h * 0.6
        drawingRect.h *= 0.4
        drawRect(window, drawingRect, pygame.Color("#4b0090"))
        text_rect = self.get_relative_rect().copy()
        text_rect.center += self.shake
        text_rect.y += text_rect.h * 0.6
        text_rect.h *= 0.4
        drawWrappedText(window, 
            self.card.desc,
            self.text.col, round(self.text.size),
            text_rect, [100,50,5]
        )

        # TODO: Draw card image here!!

    def draw(self, window):
        super().draw(window)
        if self.hovered:
            self.targetY = self.hoveredY
        else:
            self.targetY = self.restY
        self.rect.y = lerp(self.rect.y, self.targetY, 0.1)

class Shop(Menu):
    def __init__(self):
        super().__init__(
            "shop", 100000,
            (pygame.Color("#503197"), pygame.Color("#18215d"))
        )
        w, h = game.W, game.H
        self.openRect = Rect((0,0),(w,h))
        self.closeRect = self.openRect.copy()
        self.closeRect.y += self.openRect.h
        self.rect = self.closeRect.copy()

        self.heal_cost = 100

        self.cards = []

    def create_card_ui_elem(self, center, wh, bttnCol, txtObj, func, desc):
        # params( (x, y), (w, h), Text(), onAction )
        rect = Rect((0,0),(wh))
        rect.center = center
        btn = ShopCard(self.UIRoot, rect, bttnCol, txtObj, func, desc)
        self.UIRoot.add_element(btn)
        return btn

    def add_elements(self):
        # exit button
        self.create_centered_button(
            (4.95*self.rect.w/6, self.rect.w/20),
            (self.rect.w/5,self.rect.h/10),
            pygame.Color("#4b0090"), Text("EXIT",(255,255,255),45),
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
            (self.rect.w/2, self.rect.w/20),
            (self.rect.w/3,self.rect.w/15),
            pygame.Color(90,180,90), Text(f"+35% Health : ${self.heal_cost}",(255,255,255),45),
            heal
        )

        # card buttons
        for i in range(0,3):
            def func(e, index=i):
                player = game.get_entity_by_id('player')
                if player.copper >= self.cards[index].basePrice:
                    player.copper -= self.cards[index].basePrice
                    player.deck.add_card(self.cards[index])
                    e.remove_self()
                    return True
                return False

            dims = (self.rect.w*0.26,self.rect.h*0.55)
            pad = (self.rect.w - dims[0]*3)/4
            cardRectx = dims[0]/2 + pad*(i+1) + (i)*dims[0]
            cardRecty = self.rect.h-dims[1]/2
            cardBtn = self.create_card_ui_elem(
                (cardRectx, cardRecty),
                dims,
                pygame.Color("#503197"), Text(self.cards[i].name,(255,255,255),35),
                func, self.cards[i]
            )

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
