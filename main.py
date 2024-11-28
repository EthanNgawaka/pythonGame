from library import *
from enemies import *
from player import *
from deck import *
from ui import *
from shop import *
from wave import *
from menus import *
from status_effects import *

def drawFPS(dt, window):
    drawText(window, f"fps: {1/max(dt,0.0001):.2f}", (0,0,0), (game.W-100,100), 40, True)

class Background(Entity):
    def __init__(self):
        self.rect = pygame.Rect(0,0,game.W,game.H)
    def update(self, dt):
        pass
    def draw(self, window):
        drawRect(window, self.rect, (125,125,125), 0, True)

"""
draw layer looks like:

    0 - bg
    1 - creep/bg decals
    2 - particles
    3 - main (enemies player basically everything else)
    4 - shop ui
    5 - player ui
    6 - ui
"""

def create_main_scene():
    mainScene = Scene()
    bg = Background()
    player = Player(game.W/2, game.H/2)
    playerUi = PlayerUI(player)
    shop = Shop()
    wave = Wave()
    mainScene.init_entity(bg, "bg", 0)
    mainScene.init_entity(player, "player")
    mainScene.init_entity(playerUi, "playerUI", 5)
    playerUi.draw_on_top = True
    mainScene.init_entity(wave, "wave")

    # so currently u have to init all menus idk it works but its kinda scuffed but
    # also sometimes scuffed is ok
    mainScene.init_entity(shop, "shop", 4)
    mainScene.init_entity(PauseMenu(), "pausemenu", 6)
    mainScene.init_entity(DebugMenu(), "debugmenu", 6)
    mainScene.init_entity(SettingsMenu(), "settingsmenu", 6)
    return mainScene

def create_menu_scene():
    scene = Scene()
    bg = Background()
    menu = MainMenu()
    scene.init_entity(bg, "bg", -100000)
    scene.init_entity(menu, "menu", "UI")

    return scene

def main():
    game.init_window("Untitled Roguelike")
    running = True

    # use init_entity when adding entities up first otherwise they wont
    # be really added until the next update loop
    # ( this is to stop dict len changes when iterating blah blah blah )
    mainScene = create_main_scene()
    menuScene = create_menu_scene()

    game.add_scene(mainScene, "main")
    game.add_scene(menuScene, "menu")
    #game.switch_to_scene("menu", False)
    game.switch_to_scene("main", False) # skips menu and transition
    #game.get_entity_by_id("wave").timer = 60 # skip straight to shop
    # ----------------------------------------------------------------- #
    """
    K - kinda done
    X - fully done
    Notes to self:
        so far so good, enemies need tweaking and honestly just need more variation
        heres a list of things you need to do:
            - Add more passives
            - Add more enemies
            X Rework menu support for controllers
            - Add key mapping
            - Make active cards function
            X Add a button to buy 20% health for 100 copper in shop
            X Make copper auto attract at end of round (maybe make it a setting somewhere its getting tedious)
            X Rework particle system
            X Camera system for camera shake
            X Rewrite menu system to use new Rect class
    """

    time_slow_timer = 0
    while running:
        real_dt = clock.tick(maxFPS) / 1000.0
        dt = game.time_speed * real_dt

        if game.key_pressed(pygame.K_j):
            game.time_speed += 0.1
        if game.key_pressed(pygame.K_k):
            game.time_speed -= 0.1

        if game.time_speed < 1:
            time_slow_timer += real_dt
            game.time_speed = min(1, math.pow(time_slow_timer, 5))
            if game.time_speed >= 1:
                game.time_speed = 1
                time_slow_timer = 0

        game.update(dt)
        game.draw(game.window)

        drawFPS(dt, game.window)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


    print("Done")


if __name__ == "__main__":
    main()
