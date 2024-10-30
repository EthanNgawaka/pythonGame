from enemies import *
from player import *

clock = pygame.time.Clock()
maxFPS = 60

def drawFPS(dt, window):
    drawText(window, f"fps: {1/dt:.2f}", (0,0,0), (100,100), 40, True)

class Background(Entity):
    def update(self, dt):
        pass
    def draw(self, window):
        drawRect(window, [0,0,W,H], (125,125,125))

def main():
    window = init(W, H, "Untitled Roguelike")
    running = True

    # this will def be diff later but for now just setup the main scene #

    mainScene = Scene()
    mainScene.add_entity(Background(), "bg", -1)
    mainScene.add_entity(Player(W/2, H/2), "player", 0)

    for i in range(3):
        mainScene.add_entity(Fly(pygame.Vector2(random.randint(0,100), random.randint(0,100))), "fly")

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
