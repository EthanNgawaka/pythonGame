from library import *
from enemies import *
from coinManager import *
from shopManager import *
from player import *

W = 1600
H = 900
keys = [0] * 512  #init keys to avoid index error (pygame has 512 keycodes)
# to access the state of a key (true for down false for up) use "keys[pygame.KEYCODE]"
# eg) if keys[pygame.KEY_a]:
#         print("a down")


player = Player(W/2, H/2)
enemiesOnScreen = []
coinManager = CoinManager()
shopManager = shopManager(W, H)
spawnTimer = 0
waveTimer = 1

class Mouse:
    def __init__(self):
        self.pressed = [False,False]
        self.down = [False,False]
        self.x = 0
        self.y = 0
    
    def update(self):
        mousePos = pygame.mouse.get_pos()
        self.x = mousePos[0]
        self.y = mousePos[1]
        pressed = pygame.mouse.get_pressed(num_buttons=3)
        if pressed[0]:
            if self.down[0]:
                self.pressed[0] = False
            else:
                self.pressed[0] = True
            self.down[0] = True
        else:
            self.down[0] = False

        if pressed[1]:
            if self.down[1]:
                self.pressed[1] = False

            else:
                self.pressed[1] = True
            self.down[1] = True
        else:
            self.down[1] = False

mouse = Mouse()

class WaveManager:
    def __init__(self):
        self.spawnRate = 2
        self.spawnTimer = 0
        self.maxWaveTimer = 3
        self.waveTimer = self.maxWaveTimer
        self.swapVal = 1
        self.wave = 1

    def newWave(self):
        self.waveTimer = self.maxWaveTimer
        self.spawnTimer = 0
        self.wave += 1

    def spawnEnemy(self, enemiesOnScreen):
        spawnLoc = random.randint(0,3)
        enemyType = BasicEnemy # edit this at some point when we add new enemies
        match spawnLoc:
            case 0: # left
                enemiesOnScreen.append(enemyType(-player.rect[2],random.randint(0,H-player.rect[3])))
            case 1: # right
                enemiesOnScreen.append(enemyType(W+player.rect[2],random.randint(0,H-player.rect[3])))
            case 2: # up
                enemiesOnScreen.append(enemyType(random.randint(0,W-player.rect[3]), -player.rect[3]))
            case 3: # down
                enemiesOnScreen.append(enemyType(random.randint(0,W-player.rect[3]), H+player.rect[3]))

    def update(self, dt, enemiesOnScreen, shopManager, mouse, coinManager, player):
        if self.waveTimer > 0:
            self.waveTimer -= dt
            if self.spawnTimer > 0:
                self.spawnTimer -= dt
            else:
                self.spawnTimer = self.spawnRate
                self.spawnEnemy(enemiesOnScreen)
        elif self.swapVal == 1 and len(enemiesOnScreen) == 0 and len(coinManager.coins) == 0:
            self.swapVal = 0
            shopManager.store = True
        
        if shopManager.store:
            shopManager.update(dt, mouse, player)
            if not shopManager.store:
                self.swapVal = 20

    def draw(self, dt, window, shopManager):
        drawText(window, f"Time left: {math.ceil(self.waveTimer)}", (255,255,255),(W-200, 50), 30) # hard coded pos shd change this
        drawText(window, f"Wave {self.wave}", (255,255,255),(W-200, 20), 30) # hard coded pos shd change this
        if shopManager.store and len(enemiesOnScreen) == 0:
            shopManager.draw(window)
        elif self.swapVal > 1:
            self.swapVal -= 1
            shopManager.draw(window)
            shopManager.update(dt, mouse)
            if self.swapVal == 1:
                shopManager.newCards()
                self.newWave()


waveManager = WaveManager()

def update(window, dt):
    global keys, enemiesOnScreen, mouse

    if waveManager.swapVal == 1: # if not in store or transitioning from store
        player.update(window, dt, keys)
        coinManager.update(dt, player)
    waveManager.update(dt, enemiesOnScreen, shopManager, mouse, coinManager, player)
    
    for enemy in enemiesOnScreen:
        enemy.update(window,player,dt,enemiesOnScreen,coinManager);

    #input stuff
    mouse.update()
    keys = pygame.key.get_pressed()

def draw(window, dt):
    drawRect(window, (0, 0, W, H), (50, 50, 50))
    player.draw(window)
    coinManager.draw(window)
    for enemy in enemiesOnScreen:
        enemy.draw(window);
    waveManager.draw(dt, window, shopManager)
    
    drawText(window, f"FPS: {1/dt}", (255,255,255),(W-150, 150), 30)

maxFPS = 60
clock = pygame.time.Clock()
def main():
    window = init(W, H, "bingus 2.0")
    running = True
    while running:  # main game loop
        dt = clock.tick(maxFPS) / 1000.0
        update(window, dt)
        draw(window, dt)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if keys[pygame.K_ESCAPE]:
            running = False

    print("Done")


if __name__ == "__main__":
    main()
