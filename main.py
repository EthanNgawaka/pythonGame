from enemies import *
from player import *
from deck import *
from ui import *
from shop import *
from wave import *
from menus import *

clock = pygame.time.Clock()
maxFPS = 60

def drawFPS(dt, window):
    drawText(window, f"fps: {1/dt:.2f}", (0,0,0), (W-100,100), 40, True)

class Background(Entity):
    def __init__(self):
        self.rect = pygame.Rect(0,0,W,H)
    def update(self, dt):
        pass
    def draw(self, window):
        drawRect(window, self.rect, (125,125,125))

def main():
    window = init(W, H, "Untitled Roguelike")
    running = True

    # this will def be diff later but for now just setup the main scene #
    # use init_entity when adding entities up first otherwise they wont
    # be really added until the next update loop
    # ( this is to stop dict len changes when iterating blah blah blah )

    mainScene = Scene()
    game.add_scene(mainScene, "main")
    game.switch_to_scene("main")

    bg = Background()
    player = Player(W/2, H/2)
    playerUi = PlayerUI(player)
    shop = Shop()
    wave = Wave()
    game.curr_scene.init_entity(bg, "bg", -100000)
    game.curr_scene.init_entity(player, "player")
    game.curr_scene.init_entity(playerUi, "playerUI", 1000)
    game.curr_scene.init_entity(wave, "wave")

    # so currently u have to init all menus idk it works but its kinda scuffed but
    # also sometimes scuffed is ok
    game.curr_scene.init_entity(shop, "shop")
    game.curr_scene.init_entity(MainMenu(), "mainmenu")
    game.curr_scene.init_entity(DebugMenu(), "debugmenu")

    # ----------------------------------------------------------------- #

    while running:
        dt = clock.tick(maxFPS) / 1000.0

        game.update(dt)
        game.draw(window)

        drawFPS(dt, window)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


    print("Done")


if __name__ == "__main__":
    main()
