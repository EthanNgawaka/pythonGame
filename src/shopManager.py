import sys
import os

sys.path.append(os.path.abspath("../lib"))

from library import *
from world import *
from scene import *
# idea here is to have a list of cards w/ properties like name, basePrice, and col
# then in player class we have a func called triggerCardFunc(name), which takes name and finds the function of the same name in player class
# ie we chose a speedUp card, the card calls player.triggerCardFunc("speedUp") which runs the necessary code to make the card func

# TODO: Reorganize this cause its a mess, make it into a json file maybe?
shopCards = [
        {"name": "speedUp", "basePrice": 50, "col": (0,255,255),"id": 1},
        {"name": "dmgUp", "basePrice": 150, "col": (200,0,0),"id": 2},
        {"name": "atkSpeedUp", "basePrice": 100, "col": (255,0,255),"id": 3},
        {"name": "healthUp", "basePrice": 50, "col": (0,255,0),"id": 4},
        {"name": "bulletSpeed", "basePrice": 50, "col": (0,255,0),"id": 5},
        {"name": "activecooldown", "basePrice": 100, "col": (10,10,10),"id": 6},
        {"name": "accuracyUp", "basePrice": 100, "col": (0,255,0),"id": 7},
]
rareCards = [
        {"name": "shotgun", "basePrice": 100, "col": (199,199,199),"id": 8},
        {"name": "dash", "basePrice": 100, "col": (0,255,255),"id": 9},
        {"name": "halo", "basePrice": 100, "col": (0,255,255),"id": 10},
        {"name": "forager", "basePrice": 150, "col": (0,0,255),"id": 11},
        {"name": "fighter", "basePrice": 200, "col": (255,255,255),"id": 12},
        {"name": "shieldUp", "basePrice": 150, "col": (0,0,255),"id": 13},
        {"name": "boost", "basePrice": 200, "col": (0,0,255),"id": 14},
        {"name": "piercing", "basePrice": 150, "col": (0,255,0),"id": 15},
        {"name": "lifeStealUp", "basePrice": 150, "col": (0,255,0),"id": 16},
        {"name": "hotShotUp", "basePrice": 150, "col": (0,255,0),"id": 17},
        {"name": "pheonix", "basePrice": 300, "col": (0,255,255),"id": 18},
]
legendaryCards = [
        {"name": "homingSpeed", "basePrice": 300, "col": (255,255,0),"id": 19},
        {"name": "minigun", "basePrice": 200, "col": (0,255,255),"id": 20},
        {"name": "doubleShot", "basePrice": 250, "col": (0,255,255),"id": 21}
        #{"name": "sword", "basePrice": 250, "col": (255,255,255)}, thought this was gonna be its own player? is ok if not just confused i was just adding it here to see it in game :D
]
class Choice:
    def __init__(self, choiceSpacing, name, price, col, id):
        self.choiceW = 150
        self.rect = [choiceSpacing[0], choiceSpacing[1], self.choiceW, self.choiceW]
        self.col = col
        self.name = name
        self.price = price
        self.cost = price
        self.id = id

    def draw(self, window, parent):
        pos = parent.getDrawRect(self.rect)
        drawRect(window, pos, self.col)
        drawText(window, self.name, (255,255,255), (pos[0]+pos[2]/2,pos[1]-50), 30, True)
        drawText(window, f"${self.cost}", (255,255,255), (pos[0]+pos[2]/2,pos[1]+pos[3]+50), 30, True)

    def update(self, mouse, parent, player):
        pos = parent.getDrawRect(self.rect)
        if self.name in player.itemQty.keys():
            self.cost = self.price*(1+player.itemQty[self.name]/10)
        else:
            self.cost = self.price
        self.cost = math.floor(self.cost)

        if AABBCollision(pos, [parent.game.mouse.x,parent.game.mouse.y,0,0]) and parent.store:
            player.choicehovering = self.name
            player.choicehoveringID = self.id
            if parent.game.mouse.pressed[0] and player.coins >= self.cost:
                print("AH")
                player.coins -= self.cost
                player.triggerCardFunc(self.name)
                parent.choices.remove(self)
        

class shopManager(Entity):
    def __init__(self, gameRef):
        super().__init__("ShopManager", [0,0,0,0], "Manager", gameRef)
        self.type = "shop"
        self.choiceW = 150
        backgroundW = 900
        backgroundH = 600
        self.bgCol = (55,55,55)
        self.choices = []

        self.newCards()

        spacing = ((W-backgroundW)/2,(H-backgroundH)/2)
        self.backgroundRectTarget = [spacing[0], spacing[1], backgroundW, backgroundH]
        self.backgroundRect = [spacing[0], H + backgroundH, backgroundW, backgroundH]
        self.spawnPos = self.backgroundRect
        self.closeButtonRect = [backgroundW-50, 0, 50, 50]
        self.store = False
        self.opening = False
        self.closing = False

    def newCards(self):
        backgroundW = 900
        backgroundH = 600
        self.choices = [] 
        choiceSpacing = [(backgroundW - self.choiceW*3)/4, (backgroundH-self.choiceW)/2]
        
        for i in range(3):
            match self.type:
                case "shop":
                    randomCardChoice = shopCards[random.randint(0,len(shopCards)-1)]
                case "rare":
                    randomCardChoice = rareCards[random.randint(0,len(rareCards)-1)]
                case "legendary":
                    randomCardChoice = legendaryCards[random.randint(0,len(legendaryCards)-1)]

            self.choices.append(
                    Choice(
                        [choiceSpacing[0]*(i+1)+self.choiceW*i, choiceSpacing[1]],
                        randomCardChoice["name"],
                        randomCardChoice["basePrice"],
                        randomCardChoice["col"],
                        randomCardChoice["id"]
                    )
            )

    def getDrawRect(self,offsetRect):
        return [self.backgroundRect[0]+offsetRect[0], self.backgroundRect[1]+offsetRect[1], offsetRect[2], offsetRect[3]]

    def swapStates(self):
        if not self.store and not self.closing:
            self.store = True

    def draw(self, window):
        if self.closing or self.store:
            drawRect(window, self.backgroundRect, self.bgCol)
            closeButtonDrawRect = self.getDrawRect(self.closeButtonRect)
            drawRect(window, closeButtonDrawRect, (255,0,0))
            for choice in self.choices:
                choice.draw(window, self)

    def openShop(self):
        if not (self.store or self.closing):
            self.store = True
            self.newCards()

    def update(self, dt):
        mouse = self.game.mouse
        waveManager = self.game.curr_world.entities["Manager"]["WaveManager"]
        if self.store or self.closing:
            player = self.game.curr_world.entities["Player"]["player"]
            if self.store:
                player.choicehovering = "none"
                for choice in self.choices:
                    choice.update(self.game.mouse, self, player)
                self.backgroundRect = rectLerp(self.backgroundRect,self.backgroundRectTarget,0.1)
            else:
                self.backgroundRect = rectLerp(self.backgroundRect,self.spawnPos,0.1)

                if abs(self.backgroundRect[1] - self.spawnPos[1]) <= 1:
                    self.closing = False
                    waveManager.newWave()

            # close button TODO: redo with new UI elements
            closeButtonDrawRect = self.getDrawRect(self.closeButtonRect)
            if AABBCollision(closeButtonDrawRect, [self.game.mouse.x,self.game.mouse.y,0,0]):
                if mouse.pressed[0]:
                    self.store = False
                    self.closing = True

