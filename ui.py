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
        return self.rect.translate(pygame.Vector2(root_rel_rect.x, root_rel_rect.y))

class UI_Root(Entity):
    def __init__(self, root_entity, relative_rect, fill_col, outline_col):
        self.rect = relative_rect
        self.root = root_entity
        self.elements = []
        self.isUI = True
        self.outline_col = outline_col
        self.fill_col = fill_col
        self.col = (self.fill_col, self.outline_col)

    def add_element(self, elem, priority="UI"):
        self.elements.append(elem)
        game.curr_scene.add_entity(elem, elem.__class__.__name__, priority)

    def update(self, dt):
        pass

    def get_relative_rect(self):
        root_rel_rect = self.root.rect
        return self.rect.translate(pygame.Vector2(root_rel_rect.x, root_rel_rect.y))
    
    def remove_self(self): # delete all leaves and branches as well
        if self.alive:
            game.remove_entity(self)
            self.alive = False
            for el in self.elements:
                el.remove_self()

    def draw(self, window):
        drawRect(window, self.rect.translate(pygame.Vector2(self.root.rect.x, self.root.rect.y)), self.col, 10)

class Text:
    def __init__(self, string, col, size):
        self.string = string
        self.col = col
        self.size = size

class Label(UI_Element):
    def __init__(self, root_entity, relative_rect, text):
        self.isUI = True
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
        self.isUI = True
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
        self.outlined = False

        self.onActionDelay = 0.1;
        self.onActionTimer = 0;

        self.disabled = False;

        self.shakeTimer = 0
        self.shake = pygame.Vector2()
        self.shakeIntensity = 10

    def toggle(self):
        self.disabled = not self.disabled;

    def update(self, dt):
        self.hovered = AABBCollision(self.get_relative_rect(), game.mouse.rect) if game.input_mode == "keyboard" else game.controller.get_selected_btn() == self

        self.highlightCol = self.highlightCol.lerp(self.baseHighlightCol, 0.1)
        self.drawingInflation = self.drawingInflation.lerp(pygame.Vector2(), 0.1)

        clicked = game.mouse.pressed[0] if game.input_mode == "keyboard" else game.controller.get_pressed("a")

        queue = game.curr_scene.UIPriority
        isTopOfQueue = queue[len(queue)-1] == self.uiTag if len(queue) > 0 else False
        if self.hovered and isTopOfQueue and not self.disabled:
            if clicked:
                self.onActionTimer = self.onActionDelay
                self.highlightCol = pygame.Vector3(120,120,120)
                self.drawingInflation = pygame.Vector2(-10,-10)
        else:
            self.hovered = False

        if self.onActionTimer > 0:
            self.onActionTimer -= dt

            if self.onActionTimer <= 0:
                if self.onAction(self) is False:
                    self.shakeTimer = 0.2

        if self.shakeTimer > 0:
            self.shakeTimer -= dt
            self.shake.x += random.randint(-self.shakeIntensity, self.shakeIntensity)
            self.shake.y += random.randint(-self.shakeIntensity, self.shakeIntensity)

        self.shake = self.shake.lerp(pygame.Vector2(0,0), 0.1)

    def draw_name(self, window):
        drawingRect = self.get_relative_rect().inflate(self.drawingInflation.x, self.drawingInflation.y)
        drawingRect.center = (drawingRect.center[0]+self.shake.x, drawingRect.center[1]+self.shake.y)
        drawText(window, self.text.string, self.text.col, drawingRect.center, round(self.text.size+self.drawingInflation.x/2), True)

    def draw(self, window):
        drawingRect = self.get_relative_rect().inflate(self.drawingInflation.x, self.drawingInflation.y)
        drawingRect.center = (drawingRect.center[0]+self.shake.x, drawingRect.center[1]+self.shake.y)
        if self.hovered or self.outlined:
            drawingRect = drawingRect.inflate(5,5)
            drawRect(window, drawingRect.inflate(10,10), self.highlightCol)
        drawRect(window, drawingRect, self.col)
        self.draw_name(window)

# so basically u create a class extending Menu then
# pass in a uiTag ie "mainmenu" and draw priority
# then implement add_elements where you can yknow add
# buttons and labels etc see a class in menus.py for examples
class Menu(Entity):
    def __init__(self, uiTag, priority, col_obj, do_instant_open = False):
        self.isUI = True
        w, h = game.W*0.6, game.H*0.7
        self.openRect = Rect(((W-w)/2,(H-h)/2),(w,h))
        self.closeRect = self.openRect.copy()
        self.closeRect.y = game.H
        self.rect = self.closeRect.copy()

        self.isOpen = False
        self.UIRoot = None
        self.uiTag = uiTag
        self.priority = priority
        self.do_instant_open = do_instant_open
        self.close_on_esc = False

        self.bgCol = col_obj[0]
        self.outline_col = col_obj[1]

    def create_centered_button(self, center, wh, bttnCol, txtObj, func):
        # params( (x, y), (w, h), Text(), onAction )
        rect = Rect((0,0),(wh))
        rect.center = center
        btn = Button(self.UIRoot, rect, bttnCol, txtObj, func)
        self.UIRoot.add_element(btn)
        return btn

    def add_elements(self):
        pass # this is the only thing u need to implement

    def close(self, elem):
        self.isOpen = False
        game.curr_scene.UIPriority.remove(self.uiTag)

    def lerp(self, targ_rect, t):
        vec1 = pygame.Vector2(self.rect.x, self.rect.y)
        vec2 = pygame.Vector2(targ_rect.x, targ_rect.y)
        vec3 = vec1.lerp(vec2, t)
        self.rect.x = vec3.x
        self.rect.y = vec3.y
    
    def change_rect_dimensions(self, w, h):
        self.rect = self.rect.inflate(w,h)
        self.openRect = self.openRect.inflate(w,h)
        self.closeRect = self.closeRect.inflate(w,h)

    def open(self):
        if not self.isOpen:
            game.curr_scene.UIPriority.append(self.uiTag)
            self.isOpen = True
            self.UIRoot = UI_Root(
                game.get_entity_by_id("bg"), self.rect,
                self.bgCol, self.outline_col
            )
            self.UIRoot.uiTag = self.uiTag
            game.curr_scene.add_entity(self.UIRoot, self.uiTag+"ui root", self.priority)
            self.add_elements()

    def handle_close_on_esc(self):
        close_input = game.key_pressed(pygame.K_ESCAPE) if game.input_mode == "keyboard" else game.controller.get_pressed("start") or game.controller.get_pressed("b")
        queue = game.curr_scene.UIPriority
        isTopOfQueue = queue[len(queue)-1] == self.uiTag if len(queue) > 0 else True
        if close_input and isTopOfQueue:
            if self.isOpen:
                self.close(self)
                return

    def update(self, dt):
        if self.close_on_esc:
            self.handle_close_on_esc()

        if self.isOpen:
            t = 1 if self.do_instant_open else 0.1
            self.lerp(self.openRect, t)
        else:
            if self.UIRoot is not None:
                t = 1 if self.do_instant_open else 0.3
                
                dist = abs(self.rect.y - self.closeRect.y)
                self.lerp(self.closeRect, t)
                if dist < 80: # arbitrary seems to work fine tho
                    self.UIRoot.remove_self()
                    self.UIRoot = None
    
    def draw(self, window):
        pass
    
