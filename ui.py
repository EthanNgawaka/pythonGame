from game import *

class UI_Element(Entity):
    def remove_self(self): # delete all leaves and branches as well
        if self.alive:
            game.remove_entity(self)
            self.alive = False
            for el in game.get_entities_by_type(UI_Element):
                if el.root == self:
                    el.remove_self()

    def get_relative_rect(self):
        root_rel_rect = self.root.get_relative_rect()
        return self.rect.move(root_rel_rect.x, root_rel_rect.y)

class UI_Root(Entity):
    def __init__(self, root_entity, relative_rect, col):
        self.rect = relative_rect
        self.root = root_entity
        self.col = col
        self.elements = []
        self.isUI = True

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

class Label(UI_Element):
    def __init__(self, root_entity, relative_rect, text):
        # text is an obj:
        # {"string": string, "col": color, "size": size in pixels}
        self.rect = relative_rect
        self.root = root_entity
        self.text = text
        self.uiTag = self.root.uiTag

    def update(self, dt):
        pass
    def draw(self, window):
        drawingRect = self.get_relative_rect()
        drawText(window, self.text.string, self.text.col, drawingRect.center, self.text.size, True)


class Button(UI_Element):
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
        self.uiTag = self.root.uiTag

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

class MainMenu(Entity):
    def __init__(self):
        w, h = W*0.6, H*0.7
        self.openRect = pygame.Rect((W-w)/2,(H-h)/2,w,h)
        self.closeRect = pygame.Rect((W-w)/2,H*1.2,w,h)
        self.rect = self.closeRect.copy()
        self.isOpen = False
        self.UIRoot = None
        self.uiTag = "mainmenu"

    def add_elements(self):
        # exit button
        closeRect = pygame.Rect(0,0,self.rect.w/5,self.rect.h/5)
        closeRect.center = (self.rect.w/2, 4*self.rect.h/5)
        closeBtn = Button(
            self.UIRoot, closeRect,
            (255,0,0), Text("EXIT",(255,255,255),45),
            lambda e : pygame.quit()
        )
        resumeRect = pygame.Rect(0,0,self.rect.w/5,self.rect.h/5)
        resumeRect.center = (self.rect.w/2, self.rect.h/5)
        resumeBtn = Button(
            self.UIRoot, resumeRect,
            (125,125,125), Text("RESUME",(255,255,255),45),
            self.close
        )
        testRect = pygame.Rect(0,0,self.rect.w/3,self.rect.h/5)
        testRect.center = (self.rect.w/2, self.rect.h/2)
        testBtn = Button(
            self.UIRoot, testRect,
            (125,125,125), Text("Funny Button",(255,255,255),45),
            lambda e : print("ahhaha poopy")
        )
        self.UIRoot.add_element(testBtn)
        self.UIRoot.add_element(resumeBtn)
        self.UIRoot.add_element(closeBtn)

    def close(self, elem):
        self.isOpen = False
        game.curr_scene.UIPriority.remove("mainmenu")

    def lerp(self, targ_rect, t):
        vec1 = pygame.Vector2(self.rect.x, self.rect.y)
        vec2 = pygame.Vector2(targ_rect.x, targ_rect.y)
        vec3 = vec1.lerp(vec2, t)
        self.rect.x = vec3.x
        self.rect.y = vec3.y

    def open(self):
        if not self.isOpen:
            game.curr_scene.UIPriority.append("mainmenu")
            self.isOpen = True
            self.UIRoot = UI_Root(game.get_entity_by_id("bg"), self.rect, (255,0,255))
            self.UIRoot.uiTag = "mainmenu"
            game.curr_scene.add_entity(self.UIRoot, "main menu ui root", 100000)
            self.add_elements()
    
    def draw(self, window):
        pass
    
    def update(self, dt):
        if game.key_pressed(pygame.K_ESCAPE):
            if self.isOpen:
                self.close(self)
                return
            if self.UIRoot is None:
                self.open()
            return

        if self.isOpen:
            self.lerp(self.openRect, 0.1)
        else:
            if self.UIRoot is not None:
                dist = abs(self.rect.y - self.closeRect.y)
                self.lerp(self.closeRect, 0.1)
                if dist < 80: # arbitrary seems to work fine tho
                    self.UIRoot.remove_self()
                    self.UIRoot = None
