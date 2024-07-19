from library import *
from enemies import *
from coinManager import *
from shopManager import *
from player import *

W = 1920
H = 1080
NGARU = True

keys = [0] * 512  #init keys to avoid index error (pygame has 512 keycodes)
# to access the state of a key (true for down false for up) use "keys[pygame.KEYCODE]"
# eg) if keys[pygame.KEY_a]:
#         print("a down")


player = Player(W/2, H/2)
enemiesOnScreen = []
coinManager = CoinManager()
shopManager = shopManager(W, H)


class Dev:
    def __init__(self):
        self.dev = False
        self.col = (255,255,255)
        self.pause = 0
        self.god = 0
        self.skip = 0
        

    def button(self, window, X,Y,name, var):
        col1 = (255,0,0)
        if var == 1:
            col1 = (0,255,0)
        posX = W - 450 + 50 + (100 * X)
        posY = 50 + (100 * Y)
        drawRect(window, (posX, posY, 50, 50), col1)
        drawText(window, name, (255,255,255),(posX, posY + 50), 30, drawAsUI=True)
        if AABBCollision((posX, posY, 50, 50), (mouse.x, mouse.y, 5, 5)) and mouse.pressed[0]:
            var += 1
        return var
    
    def giveStat(self, window, X,Y,name, func, col):
        posX = W - 450 + 50 + (100 * X)
        posY = 50 + (100 * Y)
        drawRect(window, (posX, posY, 50, 50), col)
        drawText(window, name, (255,255,255),(posX, posY + 50), 30, drawAsUI=True)
        if AABBCollision((posX, posY, 50, 50), (mouse.x, mouse.y, 5, 5)) and mouse.pressed[0]:
            func()


    def update(self, window):
        drawRect(window, (0, 1080-36, 100, 36), self.col)
        drawText(window, f"DEV", (0,0,0),(23, 1080-36), 30, drawAsUI=True)
        self.col = (200,200,200)
        if AABBCollision((0, H-36, 100, 36), (mouse.x, mouse.y, 5, 5)):
            self.col = (255,255,255)
            if mouse.pressed[0]:
                player.coins = 99999999999999999
                self.dev = True
        if self.dev == True:
            drawRect(window, (1920 - 500, 0, 500, 1080), (100,100,100))
            drawRect(window, (1920 - 500, 0, 32, 32), (255,0,0))

            self.pause = self.button(window,0,0,"Pause",self.pause)
            self.god = self.button(window,1,0,"God",self.god)
            self.skip = self.button(window,2,0,"Skip Wave",self.skip)
            self.giveStat(window,0,1,"spdUp",player.speedUp,(150,150,150))
            self.giveStat(window,0,2,"atkSpd",player.atkSpeedUp,(150,150,150))
            self.giveStat(window,0,3,"dmgUp",player.dmgUp,(150,150,150))
            self.giveStat(window,0,4,"BSpd",player.bulletSpeedUp,(150,150,150))
            self.giveStat(window,0,5,"actvCool",player.activeCooldown,(150,150,150))
            self.giveStat(window,1,1,"shotgun",player.shotgun,(0,255,255))
            self.giveStat(window,1,2,"lifeSteal",player.lifeStealUp,(0,255,255))
            self.giveStat(window,1,3,"hotShots",player.hotShot,(0,255,255))
            self.giveStat(window,1,4,"shield",player.shield,(0,255,255))
            self.giveStat(window,1,5,"pheonix",player.lifeUp,(0,255,255))
            self.giveStat(window,1,6,"forager",player.forager,(0,255,255))
            self.giveStat(window,1,7,"fighter",player.fighter,(0,255,255))
            self.giveStat(window,1,8,"peircing",player.piercing,(0,255,255))
            self.giveStat(window,2,1,"minigun",player.minigun,(255,255,0))
            self.giveStat(window,2,2,"homing",player.homingSpeed,(255,255,0))
            self.giveStat(window,2,3,"doubleShot",player.doubleShot,(255,255,0))
            self.giveStat(window,3,1,"dash",player.buyDash,(255,0,0))
            self.giveStat(window,3,2,"boost",player.buyBoost,(255,0,0))
            self.giveStat(window,3,3,"halo",player.buyBulletHalo,(255,0,0))
            self.giveStat(window,3,4,"sword",player.buySword,(255,0,0))

            if AABBCollision((W - 500, 0, 32, 32), (mouse.x, mouse.y, 5, 5)) and mouse.pressed[0]:
                self.dev = False

        if self.god == 1:
            player.health = 100
        elif self.god == 2:
            self.god = 0
        if self.pause == 1:
            waveManager.waveTimer = 1
            waveManager.spawnTimer = 2
        elif self.pause == 2:
            self.pause = 0
        if self.skip == 1:
            waveManager.maxWaveTimer = 2
            waveManager.waveTimer = 0
            waveManager.spawnTimer = 2
            enemiesOnScreen.clear()
            self.skip = 0

        


class Mouse:
    def __init__(self):
        self.pressed = [False,False]
        self.down = [False,False]
        self.x = 0
        self.y = 0
    
    def update(self):
        self.pressed = [False,False]
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
dev = Dev()
boostResetCap = 0
class WaveManager:
    def __init__(self):
        self.spawnRate = 2
        self.spawnTimer = 0
        self.maxWaveTimer = 60
        self.waveTimer = self.maxWaveTimer
        self.swapVal = 1
        self.wave = 1

    def newWave(self):
        player.shieldCur = player.shieldMax
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
        if player.spawnMultiplyer >= 1:
            if player.spawnMultiplyer* 0.2 >= 1:
                self.spawnRate = 1
            else:
                self.spawnRate = 2 - player.spawnMultiplyer* 0.2
        if self.waveTimer > 0:
            self.waveTimer -= dt
            if self.spawnTimer > 0:
                self.spawnTimer -= dt
            else:
                self.spawnTimer = self.spawnRate
                self.spawnEnemy(enemiesOnScreen)
        elif self.swapVal == 1 and len(enemiesOnScreen) == 0 and len(coinManager.coins) == 0:
            if player.boostState == True:
                global boostResetCap
                player.boostTime = 0
                boostResetCap = 1
                player.dmg = player.dmghold
                player.attackRate = player.atshold
                player.speed = player.spdhold
            self.swapVal = 0
            shopManager.store = True
        
        if shopManager.store:
            shopManager.update(dt, mouse, player)
            if not shopManager.store:
                self.swapVal = 20

    def draw(self, dt, window, shopManager):
        
        drawText(window, f"Time left: {math.ceil(self.waveTimer)}", (255,255,255),(W-200, 50), 30, drawAsUI=True) # hard coded pos shd change this
        drawText(window, f"Wave {self.wave}", (255,255,255),(W-200, 20), 30, drawAsUI=True) # hard coded pos shd change this
        if shopManager.store and len(enemiesOnScreen) == 0:
            shopManager.draw(window)
        elif self.swapVal > 1:
            self.swapVal -= 1
            shopManager.draw(window)
            shopManager.update(dt, mouse)
            if self.swapVal == 1:
                if self.wave == 3:
                    shopManager.type = "rare"
                elif self.wave == 7:
                    shopManager.type = "legendary"
                else:
                    shopManager.type = "shop"
                shopManager.newCards()
                self.newWave()
                


waveManager = WaveManager()

def update(window, dt):
    global keys, enemiesOnScreen, mouse, boostResetCap

    if waveManager.swapVal == 1: # if not in store or transitioning from store
        if boostResetCap == 1 and player.boostState == True:
            player.dmghold = player.dmg
            player.atshold = player.attackRate
            player.spdhold = player.speed
            boostResetCap = 0
        
        player.update(window, dt, keys, player, W, H)
    coinManager.update(dt, player)
    waveManager.update(dt, enemiesOnScreen, shopManager, mouse, coinManager, player)
    for enemy in enemiesOnScreen:
        enemy.update(window,player,dt,enemiesOnScreen,coinManager);
    
    

        

    #input stuff
    mouse.update()
    keys = pygame.key.get_pressed()
    camera.update(dt)

def draw(window, dt):
    drawRect(window, (camera.pos[0], camera.pos[1], W, H), (50, 50, 50))
    player.draw(window, player, dt)
    coinManager.draw(window)
    for enemy in enemiesOnScreen:
        enemy.draw(window);
    waveManager.draw(dt, window, shopManager)
    
    drawText(window, f"FPS: {1/dt}", (255,255,255),(W-150, 150), 30, drawAsUI=True)

    if player.actives["Space"]:
            cool = player.actives["Space"][1]
            perc = cool/player.actives["Space"][0]
            name = player.actives["Space"][3]
            amogus = player.actives["Space"][4]
            if cool <= 0:
                col = (255,255,255)
            else:
                col = (150,150,150)
            drawRect(window,(50,H - 200,100,200),(100,100,100))
            drawRect(window,(50,H - 200 + perc*200,100,200),col)
            drawText(window, name, (0,0,0),(50 + amogus, H - 100), 30, drawAsUI=True)
            drawText(window, f"{round(player.actives["Space"][1], 1)}", (0,0,0),(90, H - 50), 30, drawAsUI=True)

    if player.actives["E"]:
            cool = player.actives["E"][1]
            perc = cool/player.actives["E"][0]
            name = player.actives["E"][3]
            amogus = player.actives["E"][4]
            if cool <= 0:
                col = (255,255,255)
            else:
                col = (150,150,150)
            drawRect(window,(200,H - 200,100,200),(100,100,100))
            drawRect(window,(200,H - 200 + perc*200,100,200),col)
            drawText(window, name, (0,0,0),(200 + amogus, H - 100), 30, drawAsUI=True)
            drawText(window, f"{round(player.actives["E"][1], 1)}", (0,0,0),(240, H - 50), 30, drawAsUI=True)

    if player.actives["Q"]:
            cool = player.actives["Q"][1]
            perc = cool/player.actives["Q"][0]
            name = player.actives["Q"][3]
            amogus = player.actives["Q"][4]
            if cool <= 0:
                col = (255,255,255)
            else:
                col = (150,150,150)
            drawRect(window,(350,H - 200,100,200),(100,100,100))
            drawRect(window,(350,H - 200 + perc*200,100,200),col)
            drawText(window, name, (0,0,0),(350 + amogus, H - 100), 30, drawAsUI=True)
            drawText(window, f"{round(player.actives["Q"][1], 1)}", (0,0,0),(390, H - 50), 30, drawAsUI=True)
    player.choiceDesc(window)
    player.statShow(window, W)
    global NGARU
    if NGARU == True:
        dev.update(window)
        

maxFPS = 60
clock = pygame.time.Clock()
def main():
    window = init(W, H, "bingus 2.0")
    running = True

    while running:  # main game loop
        dt = clock.tick(maxFPS) / 1000.0
        update(window, dt)
        draw(window, dt)
        running = player.running
        
            

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if keys[pygame.K_ESCAPE]:
            running = False

    print("Done")


if __name__ == "__main__":
    main()
