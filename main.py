from library import *
from enemies import *
from coinManager import *
from shopManager import *
from player import *
from particles import *

W = 1920
H = 1080
NGARU = True
pause = False
escC = False
esc = False

keys = [0] * 512  #init keys to avoid index error (pygame has 512 keycodes)
# to access the state of a key (true for down false for up) use "keys[pygame.KEYCODE]"
# eg) if keys[pygame.KEY_a]:
#         print("a down")


player = Player(W/2, H/2)
enemiesOnScreen = []
particlesOnScreen = []
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
        drawRect(window, (W - 500, 0, 500, H), (100,100,100))
        drawRect(window, (W - 500, 0, 32, 32), (255,0,0))

        self.pause = self.button(window,0,0,"Pause",self.pause)
        self.god = self.button(window,1,0,"God",self.god)
        self.skip = self.button(window,2,0,"Skip Wave",self.skip)
        #commons
        self.giveStat(window,0,1,"spdUp",player.speedUp,(150,150,150))
        self.giveStat(window,0,2,"atkSpd",player.atkSpeedUp,(150,150,150))
        self.giveStat(window,0,3,"dmgUp",player.dmgUp,(150,150,150))
        self.giveStat(window,0,4,"BSpd",player.bulletSpeedUp,(150,150,150))
        self.giveStat(window,0,5,"acc",player.accuracyUp,(150,150,150))
        self.giveStat(window,0,6,"actvCool",player.activeCooldown,(150,150,150))
        #rare
        self.giveStat(window,1,1,"shotgun",player.shotgun,(0,255,255))
        self.giveStat(window,1,2,"lifesteal",player.lifeStealUp,(0,255,255))
        self.giveStat(window,1,3,"hotShot",player.hotShot,(0,255,255))
        self.giveStat(window,1,4,"shield",player.shield,(0,255,255))
        self.giveStat(window,1,5,"pheonix",player.lifeUp,(0,255,255))
        self.giveStat(window,1,6,"forag",player.forager,(0,255,255))
        self.giveStat(window,1,7,"fight",player.fighter,(0,255,255))
        self.giveStat(window,1,8,"peirce",player.piercing,(0,255,255))
        #legendary
        self.giveStat(window,2,1,"minigun",player.minigun,(255,255,0))
        self.giveStat(window,2,2,"homing",player.homingSpeed,(255,255,0))
        self.giveStat(window,2,3,"2xshot",player.doubleShot,(255,255,0))
        #abilities
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

class Menu:
    def __init__(self):
        self.w = W/6
        self.h = H/2
        self.x = (W/2) - (self.w/2)
        self.y = (H/2) - (self.h/2)
        self.rect = (self.x,self.y,self.w,self.h)
        self.quit = True
        self.escC = False
        self.dev = Dev()
        

    def button(self,window,text,y,of,col,txtcol):
        buttrect = [self.x + (self.w/20),(y * (self.h/9.6 + self.h/(self.h/9.6))) + (self.y + self.h/50),self.w - (self.w/10),self.h/9.6]
        drawRect(window,(buttrect), col)
        drawText(window, text, txtcol,((buttrect[0]+(buttrect[2]/2)) - of,buttrect[1]+(buttrect[3] /5)), 30, drawAsUI=True)
        if AABBCollision((buttrect),(mouse.x - 2.5,mouse.y - 2.5,5,5)) and mouse.pressed[0] == True:
            return False
        else:
            return True
        
    def pause(self):
        global pause
        esc = keys[pygame.K_ESCAPE]
        if esc:
            self.dev.dev = False
            if self.escC:
                esc = False
            else:
                esc = True
                if pause == True:
                    pause = False
                elif pause == False:
                    pause = True
            self.escC = True
        else:
            self.escC = False

    def draw(self, window):

        drawRect(window,self.rect,(100,100,100))
        self.quit = self.button(window,"QUIT",7,30,(200,0,0),(255,255,255))
        devButton = self.button(window,"DEV",0,20,(200,200,200),(0,0,0))
        index = 0
        for i in player.chipList:
            drawRect(window,(1500,(50* index),200,40),(255,255,255))
            drawText(window, player.chipList[index], (0,0,0),(5 + (1500),50 * index), 30, drawAsUI=True)
            index += 1
        if devButton == False:
            if self.dev.dev == True:
                self.dev.dev = False
            else:
                self.dev.dev = True
        if self.dev.dev == True:
            self.dev.update(window)
            


        #drawRect(window,((W/2)-1,0,2,H),(255,255,255)) testing for center
        

        

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
boostResetCap = 0
menu = Menu()
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
        ran = random.randint(1,100)
        enemyType = BasicEnemy
        if ran >= 1 and ran <= 25:
            enemyType = DasherEnemy # edit this at some point when we add new enemies
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
    global keys, enemiesOnScreen, particlesOnScreen, mouse, boostResetCap, pause
    if pause == False:
        if waveManager.swapVal == 1: # if not in store or transitioning from store
            if boostResetCap == 1 and player.boostState == True:
                player.dmghold = player.dmg
                player.atshold = player.attackRate
                player.spdhold = player.speed
                boostResetCap = 0
            
            player.update(window, dt, keys, player, W, H)
        coinManager.update(dt, player)
        waveManager.update(dt, enemiesOnScreen, shopManager, mouse, coinManager, player)
        
        
        for part in particlesOnScreen:
            part.update(particlesOnScreen,dt)
        for enemy in enemiesOnScreen:
            enemy.update(window,player,dt,enemiesOnScreen,coinManager,particlesOnScreen)


    
    

        

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
    for part in particlesOnScreen:
        part.draw(window)
    global NGARU, pause
    if pause:
        menu.draw(window)
    
    
        

maxFPS = 60
clock = pygame.time.Clock()
def main():
    window = init(W, H, "bingus 2.0")
    running = True

    while running:  # main game loop
        dt = clock.tick(maxFPS) / 1000.0
        update(window, dt)
        draw(window, dt)
        menu.pause()
        running = menu.quit
            

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    print("Done")


if __name__ == "__main__":
    main()
