from game import *

class UI_Root(Entity):
    def __init__(self, root_entity, relative_rect, col):
        self.rect = relative_rect
        self.root = root_entity
        self.col = col
        self.elements = []

    def add_element(self, elem):
        self.elements.append(elem)
        game.curr_scene.add_entity(elem, "button", "UI")

    def update(self, dt):
        pass

    def get_relative_rect(self):
        root_rel_rect = self.root.rect
        return self.rect.move(root_rel_rect.x, root_rel_rect.y)
    
    def remove_self(self): # delete all leaves and branches as well
        if self.alive:
            game.remove_entity(self)
            self.alive = False
            for el in self.elements:
                el.remove_self()

    def draw(self, window):
        drawRect(window, self.rect.move(self.root.rect.x, self.root.rect.y), self.col)

class Text:
    def __init__(self, string, col, size):
        self.string = string
        self.col = col
        self.size = size

class Button(Entity):
    def __init__(self, root_entity, relative_rect, col, text, onAction):
        # text is an obj:
        # {"string": string, "col": color, "size": size in pixels}
        self.rect = relative_rect
        self.root = root_entity
        self.col = col
        self.text = text
        self.onAction = onAction
        self.hovered = False
        self.baseHighlightCol = pygame.Vector3(255,255,255)
        self.highlightCol = self.baseHighlightCol
        self.drawingInflation = pygame.Vector2()
    def get_relative_rect(self):
        root_rel_rect = self.root.get_relative_rect()
        return self.rect.move(root_rel_rect.x, root_rel_rect.y)

    def update(self, dt):
        self.hovered = False
        self.highlightCol = self.highlightCol.lerp(self.baseHighlightCol, 0.1)
        self.drawingInflation = self.drawingInflation.lerp(pygame.Vector2(), 0.1)

        if AABBCollision(self.get_relative_rect(), game.mouse.rect):
            self.hovered = True
            if game.mouse.pressed[0]:
                self.onAction(self)
                self.highlightCol = pygame.Vector3(120,120,120)
                self.drawingInflation = pygame.Vector2(-10,-10)

    def draw(self, window):
        drawingRect = self.get_relative_rect().inflate(self.drawingInflation.x, self.drawingInflation.y)
        if self.hovered:
            drawingRect = drawingRect.inflate(5,5)
            drawRect(window, drawingRect.inflate(10,10), self.highlightCol)
        drawRect(window, drawingRect, self.col)
        drawText(window, self.text.string, self.text.col, drawingRect.center, round(self.text.size+self.drawingInflation.x/2), True)
