from enemies import *
from player import *
from deck import *
from ui import *
from shop import *

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

class MainMenu(Entity):
    def __init__(self):
        w, h = W*0.6, H*0.7
        self.openRect = pygame.Rect((W-w)/2,(H-h)/2,w,h)
        self.closeRect = pygame.Rect((W-w)/2,H*1.2,w,h)
        self.rect = self.closeRect.copy()
        self.isOpen = False
        self.UIRoot = None

    def add_elements(self):
        # exit button
        closeRect = pygame.Rect(0,0,self.rect.w/5,self.rect.h/5)
        closeRect.center = (self.rect.w/2, 4*self.rect.h/5)
        closeBtn = Button(
            self.UIRoot, closeRect,
            (255,0,0), Text("EXIT",(255,255,255),45),
            lambda e : pygame.quit()
        )
        resumeRect = pygame.Rect(0,0,self.rect.w/5,self.rect.h/5)
        resumeRect.center = (self.rect.w/2, self.rect.h/5)
        resumeBtn = Button(
            self.UIRoot, resumeRect,
            (125,125,125), Text("RESUME",(255,255,255),45),
            self.close
        )
        testRect = pygame.Rect(0,0,self.rect.w/3,self.rect.h/5)
        testRect.center = (self.rect.w/2, self.rect.h/2)
        testBtn = Button(
            self.UIRoot, testRect,
            (125,125,125), Text("Funny Button",(255,255,255),45),
            lambda e : print("ahhaha poopy")
        )
        self.UIRoot.add_element(testBtn)
        self.UIRoot.add_element(resumeBtn)
        self.UIRoot.add_element(closeBtn)

    def close(self, elem):
        self.isOpen = False

    def lerp(self, targ_rect, t):
        vec1 = pygame.Vector2(self.rect.x, self.rect.y)
        vec2 = pygame.Vector2(targ_rect.x, targ_rect.y)
        vec3 = vec1.lerp(vec2, t)
        self.rect.x = vec3.x
        self.rect.y = vec3.y

    def open(self):
        if not self.isOpen:
            self.isOpen = True
            self.UIRoot = UI_Root(game.get_entity_by_id("bg"), self.rect, (255,0,255))
            game.curr_scene.add_entity(self.UIRoot, "main menu ui root", 10000)
            self.add_elements()
    
    def draw(self, window):
        pass
    
    def update(self, dt):
        if game.key_pressed(pygame.K_ESCAPE):
            if self.isOpen:
                self.close(self)
                return
            if self.UIRoot is None:
                self.open()
            return

        if self.isOpen:
            self.lerp(self.openRect, 0.1)
        else:
            if self.UIRoot is not None:
                dist = abs(self.rect.y - self.closeRect.y)
                self.lerp(self.closeRect, 0.1)
                if dist < 80: # arbitrary seems to work fine tho
                    self.UIRoot.remove_self()
                    self.UIRoot = None

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
    mainScene.init_entity(bg, "bg", -1)
    mainScene.init_entity(player, "player", 0)
    mainScene.init_entity(playerUi, "playerUI", 100)
    mainScene.init_entity(shop, "shop")
    mainScene.init_entity(MainMenu(), "mainmenu")

    """
    for i in range(3):
        mainScene.init_entity(Fly(pygame.Vector2(random.randint(0,100), random.randint(0,100))), "fly")
    """


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
