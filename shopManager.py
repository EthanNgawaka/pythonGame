from library import *

class Choice:
    def __init__(self, choiceSpacing, name, price, col):
        self.choiceW = 150
        self.rect = [choiceSpacing[0], choiceSpacing[1], self.choiceW, self.choiceW]
        self.col = col
        self.name = name
        self.price = price

    def draw(self, window, parent):
        pos = parent.getDrawRect(self.rect)
        drawRect(window, pos, (155,155,155))
        drawText(window, self.name, (255,255,255), (pos[0]+pos[2]/2,pos[1]-50), 30, True)
        drawText(window, f"${self.price}", (255,255,255), (pos[0]+pos[2]/2,pos[1]+pos[3]+50), 30, True)

    def update(self, mouse, parent):
        pos = parent.getDrawRect(self.rect)
        if AABBCollision(pos, [mouse.x,mouse.y,0,0]):
            if mouse.pressed[0]:
                print(self.name)
                pass # run ability func from parent and delete self
        
speedUp = 0
atkSpeedUp = 0
dmgup = 0
maxHealthUp = 0
bulletSpeedUp = 0
activeCooldownUp = 0
choicesText = ["speedUp","atkSpeedUp","dmgup","maxHealthUp","bulletSpeedUp","activeCooldownUp"]
choicesVars = [speedUp,atkSpeedUp,dmgup,maxHealthUp,bulletSpeedUp,activeCooldownUp]
choicesCols = [(0,255,255),(150,0,255),(255,0,0),(255,100,0),(50,50,50),(0,0,255)]

class shopManager:
    def __init__(self, screenW, screenH):
        self.choiceW = 150
        self.a = random.randint(0,5)
        self.b = random.randint(0,5)
        self.c = random.randint(0,5)
        backgroundW = 900
        backgroundH = 600
        self.bgCol = (55,55,55)

        self.choices = [] 
        choiceSpacing = [(backgroundW - self.choiceW*3)/4, (backgroundH-self.choiceW)/2]
        
        for i in range(3):
            self.choices.append(Choice([choiceSpacing[0]*(i+1)+self.choiceW*i, choiceSpacing[1]], f"test{i}", random.randint(0,100), (255,255,0)))

        spacing = ((screenW-backgroundW)/2,(screenH-backgroundH)/2)
        self.backgroundRectTarget = [spacing[0], spacing[1], backgroundW, backgroundH]
        self.backgroundRect = [spacing[0], screenH + backgroundH, backgroundW, backgroundH]
        self.spawnPos = self.backgroundRect
        self.closeButtonRect = [backgroundW-50, 0, 50, 50]
        self.store = False
        self.closing = False

    def getDrawRect(self,offsetRect):
        return [self.backgroundRect[0]+offsetRect[0], self.backgroundRect[1]+offsetRect[1], offsetRect[2], offsetRect[3]]

    def swapStates(self):
        if not self.store and not self.closing:
            self.store = True

    def draw(self, window):
        drawRect(window, self.backgroundRect, self.bgCol)
        closeButtonDrawRect = self.getDrawRect(self.closeButtonRect)
        drawRect(window, closeButtonDrawRect, (255,0,0))
        for choice in self.choices:
            choice.draw(window, self)

    def update(self, dt, mouse):
        for choice in self.choices:
            choice.update(mouse, self)
        if self.store:
            self.backgroundRect = rectLerp(self.backgroundRect,self.backgroundRectTarget,0.1)
        else:
            self.backgroundRect = rectLerp(self.backgroundRect,self.spawnPos,0.1)

        closeButtonDrawRect = self.getDrawRect(self.closeButtonRect)
        if AABBCollision(closeButtonDrawRect, [mouse.x,mouse.y,0,0]):
            if mouse.pressed[0]:
                self.store = False
                self.closing = True

