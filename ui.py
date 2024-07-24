from library import *

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
