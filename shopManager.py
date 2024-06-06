from library import *

class shopManager:
    def __init__(self, screenW, screenH):
        self.choiceW = 150
        backgroundW = 900
        backgroundH = 600

        self.choices = [] #choice = {pos: (int,int), name: string, price: int}
        choiceSpacing = [(backgroundW - self.choiceW*3)/4, (backgroundH-self.choiceW)/2]
        for i in range(3):
            self.choices.append({
                "pos": [choiceSpacing[0]*(i+1)+self.choiceW*i, choiceSpacing[1]],
                "name": f"test{i}",
                "price": random.randint(0,1000)
            })
        print(self.choices)

        spacing = ((screenW-backgroundW)/2,(screenH-backgroundH)/2)
        self.backgroundRectTarget = [spacing[0], spacing[1], backgroundW, backgroundH]
        self.backgroundRect = [spacing[0], screenH + backgroundH, backgroundW, backgroundH]

    def draw(self, window):
        drawRect(window, self.backgroundRect, (55,55,55))
        for i in self.choices:
            pos = [self.backgroundRect[0]+i["pos"][0], self.backgroundRect[1]+i["pos"][1], self.choiceW, self.choiceW]
            drawRect(window, pos, (155,155,155)) 
            drawText(window, i["name"], (255,255,255), (pos[0]+pos[2]/2,pos[1]-50), 30, True)
            drawText(window, f"${i['price']}", (255,255,255), (pos[0]+pos[2]/2,pos[1]+pos[3]+50), 30, True)

    def update(self, dt):
        self.backgroundRect = rectLerp(self.backgroundRect,self.backgroundRectTarget,0.1)
