from library import *
llc = True
class shopManager:
    def __init__(self, screenW, screenH):
        self.choiceW = 150
        backgroundW = 900
        backgroundH = 600

        self.choices = [] #choice = {pos: (int,int), name: string, price: int}
        choiceSpacing = [(backgroundW - self.choiceW*3)/4, (backgroundH-self.choiceW)/2]
        
        self.choices.append({
            "pos": [choiceSpacing[0]*(-0.6)+self.choiceW*1, choiceSpacing[1]],
            "name": "test1",
            "price": random.randint(0,1000)
        })
        self.choices.append({
            "pos": [choiceSpacing[0]*(0.6)+self.choiceW*2, choiceSpacing[1]],
            "name": "test2",
            "price": random.randint(0,1000)
        })
        self.choices.append({
            "pos": [choiceSpacing[0]*(1.6)+self.choiceW*3, choiceSpacing[1]],
            "name": "test3",
            "price": random.randint(0,1000)
        })

        spacing = ((screenW-backgroundW)/2,(screenH-backgroundH)/2)
        self.backgroundRectTarget = [spacing[0], spacing[1], backgroundW, backgroundH]
        self.b1 = [spacing[0], screenH + backgroundH, backgroundW, backgroundH]
        self.backgroundRect = [spacing[0], screenH + backgroundH, backgroundW, backgroundH]
        self.backgroundRect2 = [self.backgroundRect[0], self.backgroundRect[1], 50, 50]
        self.store = True

    def draw(self, window):
        self.backgroundRect2[0] = self.backgroundRect[0] + 850
        self.backgroundRect2[1] = self.backgroundRect[1]
        drawRect(window, self.backgroundRect, (55,55,55))
        drawRect(window, self.backgroundRect2, (255,0,0))
        for i in self.choices:
            pos = [self.backgroundRect[0]+i["pos"][0], self.backgroundRect[1]+i["pos"][1], self.choiceW, self.choiceW]
            drawRect(window, pos, (155,155,155))
            drawText(window, i["name"], (255,255,255), (pos[0]+pos[2]/2,pos[1]-50), 30, True)
            drawText(window, f"${i['price']}", (255,255,255), (pos[0]+pos[2]/2,pos[1]+pos[3]+50), 30, True)
            mx, my = pygame.mouse.get_pos()
            rect1 = pos
            rect2 = (mx,my,0,0)
            if AABBCollision(self.backgroundRect2,rect2):
                global llc
                if pygame.mouse.get_pressed(num_buttons=3)[0] == True:
                    self.store = False

            if AABBCollision(rect1,rect2):
                global llc
                if pygame.mouse.get_pressed(num_buttons=3)[0] == True:
                    
                    if mx < 650 and llc == False:
                        print("1")
                        llc = True
                    elif mx > 950 and llc == False:
                        print("3")
                        llc = True
                    elif mx > 650 and mx < 950 and llc == False:
                        print("2")
                        llc = True
                else:
                    llc = False
                    


    def update(self, dt):
        if self.store == True:
            self.backgroundRect = rectLerp(self.backgroundRect,self.backgroundRectTarget,0.1)
        else:
            self.backgroundRect = rectLerp(self.backgroundRect,self.b1,0.1)

