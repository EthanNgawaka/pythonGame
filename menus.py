from ui import *

# for debug
if DEBUG:
    from passives import *

# shop menu isnt here but oh well
class MainMenu(Menu):
    def __init__(self):
        super().__init__(
            "mainmenu", "UI",
            (pygame.Color("#503197"), pygame.Color("#18215d"))
        )

    def update(self, dt):
        queue = game.curr_scene.UIPriority
        isTopOfQueue = queue[len(queue)-1] == self.uiTag if len(queue) > 0 else True
        if game.key_pressed(pygame.K_ESCAPE):
            if self.isOpen and isTopOfQueue:
                self.close(self)
                return
            if self.UIRoot is None:
                self.open()
            return
        super().update(dt)

    def add_elements(self):
        # exit button
        self.create_centered_button(
            (self.rect.w/2, 4*self.rect.h/5), # center
            (self.rect.w/5,self.rect.h/5), # dimensions
            (255,0,0), Text("EXIT",(255,255,255),45), # btnColor, TextObj
            lambda e : pygame.quit() # onAction
        )

        # resume button
        self.create_centered_button(
            (self.rect.w/2, self.rect.h/5), # center
            (self.rect.w/5,self.rect.h/5), # dimensions
            (125,125,125), Text("RESUME",(255,255,255),45), # btnColor, TextObj
            self.close # onAction
        )

        if DEBUG:
            def open_debug(bttn):
                game.get_entity_by_id("debugmenu").open()

            # debug button
            self.create_centered_button(
                (self.rect.w/2, self.rect.h/2), # center
                (self.rect.w/5,self.rect.h/5), # dimensions
                (255,175,80), Text("DEBUG",(255,255,255),45),
                open_debug # onAction
            )

class DebugMenu(Menu):
    def __init__(self):
        super().__init__(
            "debugmenu", "UI",
            (pygame.Color("#503197"), pygame.Color("#18215d"))
        )
        self.change_rect_dimensions(200,100)
        self.close_on_esc = True

        # need to find a better way to sync to cards available in shop idk
        # its just a debug menu
        self.cards = {
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

    def add_elements(self):
        # resume button
        w = self.rect.w/20
        h = self.rect.w/20
        self.create_centered_button(
            (self.rect.w-w/2, h/2), # center
            (w,h), # dimensions
            (255,0,0), Text("X",(255,255,255),25), # btnColor, TextObj
            self.close # onAction
        )

        i = 1
        player = game.get_entity_by_id("player")
        for rarity in self.cards:
            labelRect = pygame.Rect(0,0,0,0)
            labelRect.center = (i*self.rect.w/4, self.rect.h/10)
            labelTxt = Text(rarity, (255,255,255),45)
            self.UIRoot.add_element(Label(self.UIRoot, labelRect, labelTxt))

            j = 0
            for card in self.cards[rarity]:
                self.create_centered_button(
                    (labelRect.center[0], labelRect.center[1]+50+j*100), # center
                    (self.rect.w/7,self.rect.h/12), # dimensions
                    (255,0,0), Text(card.name,(255,255,255),25), # btnColor, TextObj
                    lambda e, index=j, rar=rarity: player.deck.add_card(self.cards[rar][index]())
                )
                j+=1

            i += 1
