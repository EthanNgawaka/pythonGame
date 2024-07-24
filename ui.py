from library import *

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


    def update(self, window, player):
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


class Button:
    def __init__(self, rect, text, cols, triggerFunc, parent): # [x,y,w,h], string, [rectCol, rectHovCol, textCol], triggerFunc
        self.rect = rect
        self.rectCol = cols[0]
        self.rectHovCol = cols[1]
        self.textCol = cols[2]
        self.triggerFunc = triggerFunc
        self.text = text
        self.textSize = 50
        self.hovered = False
        self.parent = parent

    def update(self, mouse):
        self.hovered = False
        drawingRect = addRects(self.rect, [self.parent.x, self.parent.y, 0, 0])
        
        if AABBCollision(drawingRect, [mouse.x, mouse.y, 0, 0]):
            self.hovered = True
            if mouse.pressed[0]:
                self.triggerFunc(self.parent)

    def draw(self, window):
        drawingRect = addRects(self.rect, [self.parent.x, self.parent.y, 0, 0])
        drawCol = self.rectCol
        if self.hovered:
            drawingRect = enlargeRect(drawingRect, 1.1, 1.1)
            drawCol = self.rectHovCol

        drawRect(window, drawingRect, drawCol)
        drawText(window, self.text, self.textCol, [drawingRect[0]+drawingRect[2]/2, drawingRect[1]+drawingRect[3]/2], self.textSize, True, True)

class Menu:
    def __init__(self):
        self.w = W/6
        self.h = H/2
        self.x = (W/2) - (self.w/2)
        self.y = (H/2) - (self.h/2)
        self.rect = (self.x,self.y,self.w,self.h)
        self.quit = True
        self.dev = Dev()
        self.devTrigger = True
        self.open = False
        self.pressed = False


        # BUTTON INIT --------------------------------------------- #
        # open dev panel
        def devFunc(parent):
            if parent.devTrigger:
                parent.devTrigger = False
            else:
                parent.devTrigger = True
        devRect = [(self.w-250)/2,40,250,70]
        self.devButton = Button(devRect, "DEV", [(150,150,150), (200, 200, 200), (255,255,255)], devFunc, self)

        # resume
        def resumeFunc(parent):
            parent.unpause()
        resumeRect = [(self.w-250)/2,130,250,70]
        self.resumeButton = Button(resumeRect, "RESUME", [(150,150,150), (200, 200, 200), (255,255,255)], resumeFunc, self)

        # exit
        def exitFunc(parent):
            parent.quit = False
        exitRect = [(self.w-250)/2,220,250,70]
        self.exitButton = Button(exitRect, "EXIT", [(255,0,0), (255, 100, 100), (255,255,255)], exitFunc, self)
        # -------------------------------------------------------- #

    def unpause(self):
        self.dev.dev = False
        self.open = False

    def update(self, keys):
        esc = keys[pygame.K_ESCAPE]
        if esc and not self.pressed:
            self.pressed = True
            if self.open:
                self.unpause()
            else:
                self.open = True

        if not esc:
            self.pressed = False

    def draw(self, window, player):

        # draw menu
        drawRect(window,self.rect,(100,100,100))

        # draw Buttons
        self.exitButton.update(mouse)
        self.exitButton.draw(window)

        self.devButton.update(mouse)
        self.devButton.draw(window)

        self.resumeButton.update(mouse)
        self.resumeButton.draw(window)

        # draw chips
        index = 0
        for i in player.chipList:
            drawRect(window,(1500,(50* index),200,40),(255,255,255))
            drawText(window, player.chipList[index], (0,0,0),(5 + (1500),50 * index), 30, drawAsUI=True)
            index += 1

        # handling dev menu
        if self.devTrigger == False:
            self.devTrigger = True
            if self.dev.dev == True:
                self.dev.dev = False
            else:
                self.dev.dev = True
        if self.dev.dev == True:
            self.dev.update(window, player)

        #drawRect(window,((W/2)-1,0,2,H),(255,255,255)) testing for center
        
