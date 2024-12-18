from actives import *
from game import *
from ui import *
from passives import *

class ShopCardButton(Button):
    def __init__(self, root_entity, relative_rect, col, text, onAction, card):
        super().__init__(root_entity, relative_rect, col, text, onAction)
        self.card = card

        labelRect = Rect((0,0),(0,0))
        labelRect.center = (self.rect.w/2, self.rect.h*-0.1)
        labelTxt = Text("$"+str(self.card.basePrice), (255,255,255),35)
        self.root.add_element(Label(self, labelRect, labelTxt), 4)

        self.hoveredY = self.rect.y - self.rect.h*0.07
        self.restY = self.rect.y+self.rect.h/2
        self.targetY = 0
        self.rect.y = self.restY

        self.suck = False
        self.vel = Vec2()
        self.init_dist = 0
        self.accel = Vec2()
        self.suck_timer = 0
        self.suck_max = 4
        self.start_rect = self.rect.copy()
        self.start_rect.y = self.hoveredY
        self.highlight = False

    def draw_name(self, window):
        drawingRect = self.get_relative_rect().inflate(self.drawingInflation.x, self.drawingInflation.y)
        drawingRect.center = (drawingRect.center[0]+self.shake.x, drawingRect.center[1]+self.shake.y)
        vec = drawingRect.center
        vec.y -= self.rect.h*0.45
        drawingRect.h *= 0.1
        drawRect(window, drawingRect, pygame.Color("#4b0090"))
        drawText(window, self.text.string, self.text.col, vec, round(self.text.size+self.drawingInflation.x/2), True)

        try: # if the card is an active
            if (self.card.cooldown):
                drawingRect.y += drawingRect.h
                vec.y += drawingRect.h*0.99
                drawRect(window, drawingRect, pygame.Color("#250047"))
                drawText(window, str(self.card.cooldown)+"s cooldown", self.text.col, vec, round(self.text.size+self.drawingInflation.x/2), True)
                drawingRect.y -= drawingRect.h
        except:
            pass # not an active

        drawingRect.h /= 0.1
        drawingRect.y += drawingRect.h * 0.6
        drawingRect.h *= 0.4
        drawRect(window, drawingRect, pygame.Color("#4b0090"))
        text_rect = self.get_relative_rect().copy()
        text_rect.center += self.shake
        text_rect.y += text_rect.h * 0.6
        text_rect.h *= 0.4
        drawWrappedText(window, 
            self.card.desc.upper(),
            self.text.col, round(self.text.size),
            text_rect, [100,50,5]
        )

        # TODO: Draw card image here!!

    def ease_out_elastic(self, t):
        if t == 0:
            return 0
        if t == 1:
            return 1
        c4 = 2*math.pi/3
        return math.pow(2,-10*t)*math.sin((t*10-0.75)*c4)+1

    def update(self, dt):
        if not self.suck:
            super().update(dt)
            return

        self.disabled = True
        center_screen = Vec2(game.W/2, game.H/2)
        t2 = self.suck_timer/self.suck_max
        t = self.ease_out_elastic(1-t2)
        #self.rect.center = self.rect.center.lerp(Vec2(game.W/2, game.H/2), t)
        self.rect.center = (1-t)*self.start_rect.center + t*center_screen
        self.suck_timer -= dt
        if self.suck_timer <= 0:
            self.remove_self()

    def draw(self, window):
        super().draw(window)
        if not self.suck:
            if self.hovered:
                self.targetY = self.hoveredY
            else:
                self.targetY = self.restY
            self.rect.y = lerp(self.rect.y, self.targetY, 0.1)

class Shop(Menu):
    def __init__(self):
        super().__init__(
            "shop", 4,
            (pygame.Color("#503197"), pygame.Color("#18215d"))
        )
        w, h = game.W, game.H
        self.openRect = Rect((0,0),(w,h))
        self.closeRect = self.openRect.copy()
        self.closeRect.y += self.openRect.h
        self.rect = self.closeRect.copy()

        self.heal_cost = 50

        self.cards = []

    def create_card_ui_elem(self, center, wh, bttnCol, txtObj, func, desc):
        # params( (x, y), (w, h), Text(), onAction )
        rect = Rect((0,0),(wh))
        rect.center = center
        btn = ShopCardButton(self.UIRoot, rect, bttnCol, txtObj, func, desc)
        self.UIRoot.add_element(btn, 4)
        return btn

    def add_elements(self):
        # exit button
        self.create_centered_button(
            (4.95*self.rect.w/6, self.rect.w/20),
            (self.rect.w/5,self.rect.h/10),
            pygame.Color("#4b0090"), Text("EXIT",(255,255,255),45),
            self.close,
            4
        )

        # heal button
        heal_percentage = 0.30
        def heal(btn):
            player = game.get_entity_by_id('player')
            if player.copper >= self.heal_cost and player.health < player.maxHealth:
                player.copper -= self.heal_cost
                player.heal(player.maxHealth*heal_percentage)
                self.heal_cost *= 1.25
                self.heal_cost = round(self.heal_cost/10)*10
                btn.text.string = f"+{round(heal_percentage*player.maxHealth)} Health : ${self.heal_cost}"
                return True
            return False
        player = game.get_entity_by_id('player')
        self.create_centered_button(
            (self.rect.w/2, self.rect.w/20),
            (self.rect.w/3,self.rect.w/15),
            pygame.Color(90,180,90), Text(f"+{round(heal_percentage*player.maxHealth)} Health : ${self.heal_cost}",(255,255,255),45),
            heal,
            4
        )

        # card buttons
        for i in range(0,3):
            def func(e, index=i):
                player = game.get_entity_by_id('player')
                if player.copper >= self.cards[index].basePrice:
                    player.copper -= self.cards[index].basePrice
                    player.deck.add_card(self.cards[index]())
                    e.suck = True
                    e.suck_timer = e.suck_max
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
        wave = game.get_entity_by_id("wave")
        for i in range(3):
            #rand_card = merged_cards[rarity][random.randint(0,len(merged_cards[rarity])-1)]
            card_type = "PASSIVE"
            print(wave.num)
            if wave.num > 1:
                print("AH")
                if random.uniform(0,1) >= 0.8:
                    card_type = "ACTIVE"
                elif wave.num % 3 == 0:
                    if random.uniform(0,1) >= 0.9: # 20% + 10% == 30% chance to be active on rare shops
                        card_type = "ACTIVE"

            card_type = ACTIVE_CARDS if card_type == "ACTIVE" else PASSIVE_CARDS
            rand_card = card_type[rarity][random.randint(0, len(card_type[rarity])-1)]
            self.cards.append(rand_card)

    def close(self, elem):
        super().close(elem)
        game.get_entity_by_id("wave").new_round()

    def open(self):
        if not self.isOpen:
            self.cards = []
            num = game.get_entity_by_id("wave").num
            rarity = "legendary"  if num == 9 else ("rare" if num % 3 == 0 else "common")
            self.gen_cards(rarity)
            super().open()
