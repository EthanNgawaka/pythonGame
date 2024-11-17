from library import *
from enemies import *
from player import *
from deck import *
from ui import *
from shop import *
from wave import *
from menus import *

def drawFPS(dt, window):
    drawText(window, f"fps: {1/max(dt,0.0001):.2f}", (0,0,0), (game.W-100,100), 40, True)

class Background(Entity):
    def __init__(self):
        self.rect = pygame.Rect(0,0,game.W,game.H)
    def update(self, dt):
        pass
    def draw(self, window):
        drawRect(window, self.rect, (125,125,125))

def create_main_scene():
    mainScene = Scene()
    bg = Background()
    player = Player(game.W/2, game.H/2)
    playerUi = PlayerUI(player)
    shop = Shop()
    wave = Wave()
    mainScene.init_entity(bg, "bg", -100000)
    mainScene.init_entity(player, "player")
    mainScene.init_entity(playerUi, "playerUI", 1000)
    mainScene.init_entity(wave, "wave")

    # so currently u have to init all menus idk it works but its kinda scuffed but
    # also sometimes scuffed is ok
    mainScene.init_entity(shop, "shop")
    mainScene.init_entity(PauseMenu(), "pausemenu")
    mainScene.init_entity(DebugMenu(), "debugmenu")
    mainScene.init_entity(SettingsMenu(), "settingsmenu")
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
    game.switch_to_scene("menu", False)
    # ----------------------------------------------------------------- #
    """
    Notes to self:
        so far so good, enemies need tweaking and honestly just need more variation
        heres a list of things you need to do:
            - Rework menu support for controllers
            - Add more enemies
            - Make active cards function
            - Add more passives
            - Add a button to buy 20% health for 100 copper in shop
            - Make copper auto attract at end of round (maybe make it a setting somewhere its getting tedious)
            - Rework particle system
            - Camera system for camera shake
            - Rewrite menu system to use new Rect class
    """

    while running:
        dt = game.time_speed * clock.tick(maxFPS) / 1000.0

        if game.key_pressed(pygame.K_j):
            game.time_speed += 0.1
        if game.key_pressed(pygame.K_k):
            game.time_speed -= 0.1

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
