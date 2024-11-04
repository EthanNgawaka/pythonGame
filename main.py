from enemies import *
from player import *
from deck import *
from ui import *
from shop import *
from wave import *

clock = pygame.time.Clock()
maxFPS = 120

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
    bg = Background()
    player = Player(W/2, H/2)
    playerUi = PlayerUI(player)
    shop = Shop()
    wave = Wave()
    wave.length = 1
    mainScene.init_entity(bg, "bg", -1)
    mainScene.init_entity(player, "player", 0)
    mainScene.init_entity(playerUi, "playerUI", 100)
    mainScene.init_entity(shop, "shop")
    mainScene.init_entity(MainMenu(), "mainmenu")
    mainScene.init_entity(wave, "wave")

    game.add_scene(mainScene, "main")
    game.switch_to_scene("main")
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
