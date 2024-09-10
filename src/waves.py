from library import *
from enemies import *
from world import *
from scene import *

class WaveManager(Entity):
    def __init__(self, game):
        super().__init__("WaveManager", [0,0,0,0], "Manager", game)
        self.spawnRate = 2
        self.spawnTimer = 0
        self.maxWaveTimer = 1
        self.waveTimer = self.maxWaveTimer
        self.swapVal = 1
        self.wave = 1
        
        self.update_refs()

    def update_refs(self):
        try:
            self.enemyManagerRef = self.game.curr_world.entities["Manager"]["EnemyManager"]
            self.coinManagerRef = self.game.curr_world.entities["Manager"]["CoinManager"]
            self.shopManagerRef = self.game.curr_world.entities["Manager"]["ShopManager"]
            self.playerRef = self.game.curr_world.entities["Player"]["player"]
        except AttributeError as e: # if world isnt initialized yet
            print("world not ready")
            self.enemyManagerRef = None
            self.coinManagerRef = None
            self.shopManagerRef = None
            self.playerRef = None

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

    def update(self, dt):
        self.update_refs()
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
        else:
            noEnemies = len(self.enemyManagerRef.enemies) <= 0
            noCoins = len(self.coinManagerRef.coins) <= 0
            if noEnemies and noCoins:
                # if no enemies and coins on screen and wave is over
                self.shopManagerRef.openShop()


    def draw(self, window):
        self.update_refs()
        
        drawText(window, f"Time left: {math.ceil(self.waveTimer)}", (255,255,255),(W-200, 50), 30) # hard coded pos shd change this
        drawText(window, f"Wave {self.wave}", (255,255,255),(W-200, 20), 30) # hard coded pos shd change this

