from ui import *
from enemies import *

# for debug
if DEBUG:
    from passives import *

# shop menu isnt here but oh well
class MainMenu(Menu):
    def __init__(self):
        super().__init__(
            "mainmenu", "UI",
            (pygame.Color("#503197"), pygame.Color("#18215d")),
            True
        )

    def init(self):
        super().init()
        self.open()

    def add_elements(self):
        # start button
        self.create_centered_button(
            (self.rect.w/2, self.rect.h/3), # center
            (self.rect.w/2,self.rect.h/4), # dimensions
            (60,189,60), Text("START",(255,255,255),100), # btnColor, TextObj
            lambda btn: game.switch_to_scene("main"),
        )

        # exit button
        self.create_centered_button(
            (self.rect.w/2, 2*self.rect.h/3), # center
            (self.rect.w/2,self.rect.h/4), # dimensions
            (255,0,0), Text("EXIT",(255,255,255),100), # btnColor, TextObj
            game.close,
        )

class PauseMenu(Menu):
    def __init__(self):
        super().__init__(
            "pausemenu", "UI",
            (pygame.Color("#503197"), pygame.Color("#18215d"))
        )
        self.close_on_esc = True

    def update(self, dt):
        close_input = game.key_pressed(pygame.K_ESCAPE) if game.input_mode == "keyboard" else game.controller.get_pressed("start")
        queue = game.curr_scene.UIPriority
        isTopOfQueue = queue[len(queue)-1] == self.uiTag if len(queue) > 0 else True
        if close_input:
            if self.isOpen and isTopOfQueue:
                self.close(self)
                return
            if self.UIRoot is None:
                self.open()
            return
        super().update(dt)

    def add_elements(self):
        # resume button
        self.create_centered_button(
            (self.rect.w/2, self.rect.h/8), # center
            (self.rect.w/5,self.rect.h/10), # dimensions
            (125,125,125), Text("RESUME",(255,255,255),45), # btnColor, TextObj
            self.close # onAction
        )
        
        # settings button
        def open_settings(bttn):
            game.get_entity_by_id("settingsmenu").open()

        self.create_centered_button(
            (self.rect.w/2, 2*self.rect.h/8), # center
            (self.rect.w/5,self.rect.h/10), # dimensions
            (80,80,80), Text("SETTINGS",(255,255,255),45), # btnColor, TextObj
            open_settings
        )

        # back to menu button
        self.create_centered_button(
            (self.rect.w/2, 6*self.rect.h/8), # center
            (self.rect.w/5,self.rect.h/10), # dimensions
            (55,55,55), Text("MENU",(255,255,255),45), # btnColor, TextObj
            lambda e : game.switch_to_scene("menu") # onAction
        )

        # exit button
        self.create_centered_button(
            (self.rect.w/2, 7*self.rect.h/8), # center
            (self.rect.w/5,self.rect.h/10), # dimensions
            (255,0,0), Text("EXIT",(255,255,255),45), # btnColor, TextObj
            game.close # onAction
        )

        if DEBUG:
            def open_debug(bttn):
                game.get_entity_by_id("debugmenu").open()

            # debug button
            self.create_centered_button(
                (self.rect.w/5, self.rect.h/2), # center
                (self.rect.w/5,self.rect.h/10), # dimensions
                (255,175,80), Text("DEBUG",(255,255,255),45),
                open_debug # onAction
            )
class SettingsMenu(Menu):
    def __init__(self):
        super().__init__(
            "settingsmenu", "UI",
            (pygame.Color("#503197"), pygame.Color("#18215d"))
        )
        self.close_on_esc = True

    def add_elements(self):
        # back button
        self.create_centered_button(
            (self.rect.w/2, 7*self.rect.h/8), # center
            (self.rect.w/5,self.rect.h/10), # dimensions
            (125,125,125), Text("BACK",(255,255,255),45), # btnColor, TextObj
            self.close # onAction
        )

        # fullscreen button
        self.create_centered_button(
            (self.rect.w/2, 1*self.rect.h/8), # center
            (self.rect.w/2,self.rect.h/10), # dimensions
            (125,125,125), Text("TOGGLE FULLSCREEN",(255,255,255),45), # btnColor, TextObj
            lambda e: pygame.display.toggle_fullscreen() # onAction
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
                Shotgun, Piercing, LifeStealUp, Panic
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

        def spawn_enemies(btn):
            for i in range(10):
                game.get_entity_by_id("wave").spawn_random_enemy()

        self.create_centered_button(
            (self.rect.w-w*3, self.rect.h-h), # center
            (w*3,h), # dimensions
            (255,0,0), Text("spawn 10 enemies",(255,255,255),25), # btnColor, TextObj
            spawn_enemies
        )

        def spawn_dummy(btn):
            game.curr_scene.add_entity(Dummy((W/2, H/2)),"dummy")
        self.create_centered_button(
            (self.rect.w-w*3, self.rect.h-h*4), # center
            (w*3,h), # dimensions
            (255,0,0), Text("Spawn dummy",(255,255,255),25), # btnColor, TextObj
            spawn_dummy
        )

        def pause_wave(btn):
            wave = game.get_entity_by_id("wave")
            wave.pause = not wave.pause
        self.create_centered_button(
            (self.rect.w-w*3, self.rect.h-h*2.5), # center
            (w*3,h), # dimensions
            (255,0,0), Text("pause wave",(255,255,255),25), # btnColor, TextObj
            pause_wave
        )

        def end_wave(btn):
            game.get_entity_by_id("wave").timer = 60
        self.create_centered_button(
            (self.rect.w-w*3, self.rect.h-h*7), # center
            (w*3,h), # dimensions
            (255,0,0), Text("end wave",(255,255,255),25), # btnColor, TextObj
            end_wave
        )

        def reset_cards(btn):
            game.get_entity_by_id("player").reset_stats()
        self.create_centered_button(
            (self.rect.w-w*3, self.rect.h-h*5.5), # center
            (w*3,h), # dimensions
            (255,0,0), Text("reset cards",(255,255,255),25), # btnColor, TextObj
            reset_cards
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
