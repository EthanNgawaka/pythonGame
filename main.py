from library import *
from enemies import *
from coinManager import *
from shopManager import *
from player import *
from particles import *
from ui import *

NGARU = True
escC = False
esc = False

player = Player(W/2, H/2)

particleManager = ParticleManager()
coinManager = CoinManager()
shopManager = shopManager(W, H)
enemyManager = EnemyManager(coinManager, player, particleManager)

boostResetCap = 0
menu = Menu()
class WaveManager:
    def __init__(self, enemyManager, coinManager, shopManager, player):
        self.spawnRate = 2
        self.spawnTimer = 0
        self.maxWaveTimer = 60
        self.waveTimer = self.maxWaveTimer
        self.swapVal = 1
        self.wave = 1
        self.enemyManagerRef = enemyManager
        self.coinManagerRef = coinManager
        self.shopManagerRef = shopManager
        self.playerRef = player

    def newWave(self):
        self.playerRef.shieldCur = self.playerRef.shieldMax
        self.waveTimer = self.maxWaveTimer
        self.spawnTimer = 0
        self.wave += 1

    def spawnEnemy(self):
        spawnLoc = random.randint(0,3)
        enemyType = Fly
        spawnOffset = 60 # max enemy H/W so no one spawns on screen

        match spawnLoc:
            case 0: # left
                self.enemyManagerRef.spawnEnemy(enemyType,[-spawnOffset,random.randint(0,H-spawnOffset)])
            case 1: # right
                self.enemyManagerRef.spawnEnemy(enemyType,[W+spawnOffset,random.randint(0,H-spawnOffset)])
            case 2: # up
                self.enemyManagerRef.spawnEnemy(enemyType,[random.randint(0,W-spawnOffset),-spawnOffset])
            case 3: # down
                self.enemyManagerRef.spawnEnemy(enemyType,[random.randint(0,W-spawnOffset),H+spawnOffset])

    def update(self, dt, mouse):
        if self.playerRef.spawnMultiplyer >= 1:
            if self.playerRef.spawnMultiplyer* 0.2 >= 1:
                self.spawnRate = 1
            else:
                self.spawnRate = 2 - self.playerRef.spawnMultiplyer* 0.2
        if self.waveTimer > 0:
            self.waveTimer -= dt
            if self.spawnTimer > 0:
                self.spawnTimer -= dt
            else:
                self.spawnTimer = self.spawnRate
                self.spawnEnemy()
        elif self.swapVal == 1 and len(self.enemyManagerRef.enemies) == 0 and len(self.coinManagerRef.coins) == 0:

            # Redo this player boost at some point
            if self.playerRef.boostState == True:
                global boostResetCap
                self.playerRef.boostTime = 0
                boostResetCap = 1
                self.playerRef.dmg = self.playerRef.dmghold
                self.playerRef.attackRate = self.playerRef.atshold
                self.playerRef.speed = self.playerRef.spdhold

            self.swapVal = 0
            self.shopManagerRef.store = True
        
        if self.shopManagerRef.store:
            self.shopManagerRef.update(dt, mouse, self.playerRef)
            if not self.shopManagerRef.store:
                self.swapVal = 20

    def draw(self, dt, window):
        
        drawText(window, f"Time left: {math.ceil(self.waveTimer)}", (255,255,255),(W-200, 50), 30) # hard coded pos shd change this
        drawText(window, f"Wave {self.wave}", (255,255,255),(W-200, 20), 30) # hard coded pos shd change this
        if self.shopManagerRef.store and len(self.enemyManagerRef.enemies) == 0:
            self.shopManagerRef.draw(window)
        elif self.swapVal > 1:
            self.swapVal -= 1
            self.shopManagerRef.draw(window)
            self.shopManagerRef.update(dt, mouse)
            if self.swapVal == 1:
                if self.wave == 3:
                    self.shopManagerRef.type = "rare"
                elif self.wave == 7:
                    self.shopManagerRef.type = "legendary"
                else:
                    self.shopManagerRef.type = "shop"
                self.shopManagerRef.newCards()
                self.newWave()
                


waveManager = WaveManager(enemyManager, coinManager, shopManager, player)


def update(window, dt):
    global keys, mouse, boostResetCap

    menu.update(keys)
    if menu.open == False:
        if waveManager.swapVal == 1: # if not in store or transitioning from store
            if boostResetCap == 1 and player.boostState == True:
                player.dmghold = player.dmg
                player.atshold = player.attackRate
                player.spdhold = player.speed
                boostResetCap = 0
            
            player.update(window, dt, keys, player, W, H)
        coinManager.update(dt, player)
        waveManager.update(dt, mouse)
        
        particleManager.update(dt)
        enemyManager.update(dt)

    #input stuff
    mouse.update()
    keys = pygame.key.get_pressed()
    camera.update(dt)

bgCol = (80,80,80)

def draw(window, dt):
    drawRect(window, (-W/2, -H/2, W*2, H*2), bgCol)
    shadowManager.draw(window)
    particleManager.draw(window, dt)
    player.draw(window, player, dt)
    coinManager.draw(window)
    enemyManager.draw(window)
    waveManager.draw(dt, window)
    
    drawText(window, f"FPS: {1/dt}", (255,255,255),(W-150, 150), 30)



    
    player.choiceDesc(window)
    player.statShow(window, W)

    if menu.open:
        menu.draw(window, player)

maxFPS = 60
clock = pygame.time.Clock()

def main():
    window = init(W, H, "Untitled Roguelike")
    running = True

    while running:  # main game loop
        dt = clock.tick(maxFPS) / 1000.0
        #particleManager.spawnFire(W/2,H/2) I LOOOOOVE fire

        update(window, dt)
        draw(window, dt)

        running = menu.quit

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    print("Done")


if __name__ == "__main__":
    main()
