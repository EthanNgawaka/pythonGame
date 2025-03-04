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
        return self.rect.translate(Vec2(root_rel_rect.x, root_rel_rect.y))

class UI_Root(Entity):
    def __init__(self, root_entity, relative_rect, fill_col, outline_col):
        self.rect = relative_rect
        self.root = root_entity
        self.elements = []
        self.isUI = True
        self.outline_col = outline_col
        self.fill_col = fill_col
        self.col = (self.fill_col, self.outline_col)

    def add_element(self, elem, priority=6):
        self.elements.append(elem)
        id = elem.__class__.__name__
        game.curr_scene.add_entity(elem, id, priority)

    def update(self, dt):
        pass

    def get_relative_rect(self):
        root_rel_rect = self.root.rect
        return self.rect.translate(Vec2(root_rel_rect.x, root_rel_rect.y))
    
    def remove_self(self): # delete all leaves and branches as well
        if self.alive:
            game.remove_entity(self)
            self.alive = False
            for el in self.elements:
                el.remove_self()

    def draw(self, window):
        drawRect(window, self.rect.translate(Vec2(self.root.rect.x, self.root.rect.y)), self.col, 10)

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
        drawText(window, self.text.string, self.text.col, drawingRect.center, self.text.size, True, True)

class Dialogue(Entity):
    def __init__(self, textList):
        self.isUI = True
        w, h = game.W*0.8, game.H*0.25
        self.rect = Rect(((W-w)/2,H - h*1.25),(w,h))

        self.isOpen = False
        self.UIRoot = None
        self.uiTag = "dialogueBox"
        self.priority = 6
        self.close_on_esc = False

        self.text = textList
        self.listIndex = 0
        self.textIndex = 0
        self.displayText = ""

        self.textTimer = 0
        self.textSpeed = 0.02
        self.waiting_for_input = False

        size = 35
        self.textBox = TextBox(self.displayText, self.rect, size, [size*2, size, 10])

    def init(self):
        super().init()
        self.open()

    def add_elements(self):
        pass # this is the only thing u need to implement

    def close(self, elem):
        self.isOpen = False
        game.curr_scene.UIPriority.remove(self.uiTag)
    
    def open(self):
        if not self.isOpen:
            game.curr_scene.UIPriority.append(self.uiTag)
            self.isOpen = True
            self.add_elements()

    def update(self, dt):
        queue = game.curr_scene.UIPriority
        isTopOfQueue = queue[len(queue)-1] == self.uiTag if len(queue) > 0 else False
        if not isTopOfQueue:
            return
        if not self.isOpen:
            self.UIRoot.remove_self()
            self.UIRoot = None

        if game.key_pressed(pygame.K_SPACE):
            if self.waiting_for_input :
                self.textBox.empty_string()
                self.textIndex = 0
                self.listIndex += 1
                self.waiting_for_input = False
                if self.listIndex >= len(self.text):
                    self.remove_self()
                    return
            else:
                for char in self.text[self.listIndex][self.textIndex:]:
                    self.textBox.add_to_string(char)
                self.waiting_for_input = True

        self.textTimer += dt
        self.textBox.textSpeed = self.textSpeed
        if self.textTimer > self.textSpeed and not self.waiting_for_input:
            self.textTimer = 0
            self.textBox.add_to_string(self.text[self.listIndex][self.textIndex])
            self.textIndex+=1
            if self.textIndex >= len(self.text[self.listIndex]):
                self.waiting_for_input = True


        self.textBox.update(dt)

    def drawText(self, window):
        size = 35
        self.textBox.draw(window)
    
    def draw(self, window):
        drawRect(window, self.rect, (128,0,128))
        self.drawText(window)

class Slider(UI_Element):
    def __init__(self, root_entity, relative_rect, starting_value, bounds, rect_col, circle_col, value_to_update, round, sig_figs):
        self.isUI = True
        self.root = root_entity
        self.uiTag = self.root.uiTag

        self.rect = relative_rect

        self.rect_col = rect_col
        self.circle_col = circle_col

        self.curr_value = starting_value
        self.min_value = bounds[0]
        self.max_value = bounds[1]
        self.value_to_update = value_to_update
        self.sig_figs = sig_figs

        self.baseHighlightCol = pygame.Vector3(255,255,255)
        self.highlightCol = self.baseHighlightCol
        self.drawingInflation = Vec2()

        self.outlined = False
        self.highlight = True
        self.disabled = False
        self.hovered = False

        self.shakeTimer = 0
        self.shake = Vec2()
        self.shakeIntensity = 10

        self.drawingRect = None

        self.prev_hovered = False
        self.prev_clicked = False
        self.down = False
        self.round = round

    def toggle(self):
        self.disabled = not self.disabled

    def update_value(self):
        new_pos = game.mouse.pos.x - self.get_relative_rect().x
        dist_along = max(self.min_value, min(self.rect.w, new_pos))
        new_val = (self.max_value * dist_along/self.rect.w) + self.min_value
        self.curr_value = round(new_val) if self.round else new_val

        setattr(self.value_to_update[0], self.value_to_update[1], self.curr_value)

    def update(self, dt):
        circle_pos = (self.get_relative_rect().center)+Vec2(-self.rect.w/2 + self.rect.w*(self.curr_value-self.min_value)/self.max_value, 0)
        r = 20
        self.hovered_over_circle = (game.mouse.pos - circle_pos).length() < r
        self.hovered = AABBCollision(self.get_relative_rect(), game.mouse.rect) or self.hovered_over_circle

        self.highlightCol = self.highlightCol.lerp(self.baseHighlightCol, 0.1)
        self.drawingInflation = self.drawingInflation.lerp(Vec2(), 0.1)

        clicked = game.mouse.down[0]

        queue = game.curr_scene.UIPriority
        isTopOfQueue = queue[len(queue)-1] == self.uiTag if len(queue) > 0 else False
        if (((self.hovered and not self.prev_clicked) or (self.down and self.prev_clicked))) and isTopOfQueue and not self.disabled:
            if not self.prev_hovered:
                game.sfx.select.play()
                self.prev_hovered = True
            if clicked:
                if not self.prev_clicked:
                    game.sfx.click.play()

                self.down = True
                self.highlightCol = pygame.Vector3(120,120,120)
        else:
            self.hovered = False
            self.prev_hovered = False
        if not clicked:
            self.down = False

        self.prev_clicked = clicked

        if self.down:
            self.update_value()

        if self.shakeTimer > 0:
            self.shakeTimer -= dt
            self.shake.x += random.randint(-self.shakeIntensity, self.shakeIntensity)
            self.shake.y += random.randint(-self.shakeIntensity, self.shakeIntensity)

        self.shake = self.shake.lerp(Vec2(0,0), 0.1)

    def draw(self, window):
        self.drawingRect = self.get_relative_rect()
        if self.drawingInflation.length() > 0:
            self.drawingRect = self.drawingRect.inflate(self.drawingInflation.x, self.drawingInflation.y)

        self.drawingRect.center = (self.drawingRect.center[0]+self.shake.x, self.drawingRect.center[1]+self.shake.y)
        drawRect(window, self.drawingRect.inflate(*self.drawingInflation).inflate(10,10), self.highlightCol)
        drawRect(window, self.drawingRect, self.rect_col)

        if (self.hovered or self.outlined or self.down) and self.highlight:
            white_surf = create_colored_surf(rect_to_surf(self.drawingRect), 80, self.baseHighlightCol)
            window.blit(white_surf, (self.drawingRect.topleft.x, self.drawingRect.topleft.y))

        circle_pos = (self.get_relative_rect().center)+Vec2(-self.rect.w/2 + self.rect.w*(self.curr_value-self.min_value)/self.max_value, 0)
        r = 20
        if self.hovered:
            r = 25
        if self.down:
            r = 15
        drawCircle(window, (circle_pos, r), "white")
        drawCircle(window, (circle_pos, r*3/5), self.circle_col)
        drawText(window, str(round(self.curr_value, self.sig_figs)), "white", circle_pos + Vec2(0, 50), 25, True, True)

        drawText(window, str(self.min_value), "white", self.get_relative_rect().topleft - Vec2(0, 25), 25, True, True)
        drawText(window, str(self.max_value), "white", self.get_relative_rect().topright - Vec2(0, 25), 25, True, True)

class Button(UI_Element):
    def __init__(self, root_entity, relative_rect, col, text, onAction):
        # text is an obj:
        # {"string": string, "col": color, "size": size in pixels}
        self.isUI = True
        self.rect = relative_rect
        self.root = root_entity
        self.col = col
        self.text = text
        self.text.string = self.text.string.upper()
        self.onAction = onAction
        self.hovered = False
        self.baseHighlightCol = pygame.Vector3(255,255,255)
        self.highlightCol = self.baseHighlightCol
        self.drawingInflation = Vec2()
        self.uiTag = self.root.uiTag
        self.outlined = False
        self.highlight = True

        self.prev_hovered = False

        self.onActionDelay = 0.1;
        self.onActionTimer = 0;

        self.disabled = False;

        self.shakeTimer = 0
        self.shake = Vec2()
        self.shakeIntensity = 10

        self.drawingRect = None

    def toggle(self):
        self.disabled = not self.disabled;

    def update(self, dt):
        self.hovered = AABBCollision(self.get_relative_rect(), game.mouse.rect) if game.input_mode == "keyboard" else game.controller.get_selected_btn() == self

        self.highlightCol = self.highlightCol.lerp(self.baseHighlightCol, 0.1)
        self.drawingInflation = self.drawingInflation.lerp(Vec2(), 0.1)

        clicked = game.mouse.pressed[0] if game.input_mode == "keyboard" else game.controller.get_pressed("a")

        queue = game.curr_scene.UIPriority
        isTopOfQueue = queue[len(queue)-1] == self.uiTag if len(queue) > 0 else False
        if self.hovered and isTopOfQueue and not self.disabled:
            if not self.prev_hovered:
                game.sfx.select.play()
                self.prev_hovered = True
            if clicked:
                game.sfx.click.play()
                self.onActionTimer = self.onActionDelay
                self.highlightCol = pygame.Vector3(120,120,120)
                self.drawingInflation = Vec2(-10,-10)
        else:
            self.hovered = False
            self.prev_hovered = False

        if self.onActionTimer > 0:
            self.onActionTimer -= dt

            if self.onActionTimer <= 0:
                if self.onAction(self) is False:
                    self.shakeTimer = 0.2

        if self.shakeTimer > 0:
            self.shakeTimer -= dt
            self.shake.x += random.randint(-self.shakeIntensity, self.shakeIntensity)
            self.shake.y += random.randint(-self.shakeIntensity, self.shakeIntensity)

        self.shake = self.shake.lerp(Vec2(0,0), 0.1)

    def draw_name(self, window):
        drawText(window, self.text.string, self.text.col, self.drawingRect.center, round(self.text.size+self.drawingInflation.x/2), True, True)

    def draw(self, window):
        self.drawingRect = self.get_relative_rect()
        if self.drawingInflation.length() > 0:
            self.drawingRect = self.drawingRect.inflate(self.drawingInflation.x, self.drawingInflation.y)

        self.drawingRect.center = (self.drawingRect.center[0]+self.shake.x, self.drawingRect.center[1]+self.shake.y)
        if self.hovered or self.outlined:
            if self.onActionTimer <= 0:
                self.drawingInflation = self.drawingInflation.lerp(Vec2(10,10), 0.1)
            drawRect(window, self.drawingRect.inflate(*self.drawingInflation).inflate(10,10), self.highlightCol)
        drawRect(window, self.drawingRect, self.col)
        self.draw_name(window)

        if (self.hovered or self.outlined) and self.highlight:
            white_surf = create_colored_surf(rect_to_surf(self.drawingRect), 80, self.baseHighlightCol)
            window.blit(white_surf, (self.drawingRect.topleft.x, self.drawingRect.topleft.y))

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
        self.closeRect.y = 1.1*game.H
        self.rect = self.closeRect.copy()

        self.isOpen = False
        self.UIRoot = None
        self.uiTag = uiTag
        self.priority = priority
        self.do_instant_open = do_instant_open
        self.close_on_esc = False

        self.bgCol = col_obj[0]
        self.outline_col = col_obj[1]

    def create_centered_slider(self, center, w, startingValue, maxValue, value_to_update, round=False, sig_figs=2, layer=6):
        # params( (x, y), (w, h), Text(), (class ref, "name_of_var") )
        rect = Rect((0,0),([w, 20]))
        rect.center = center
        slider = Slider(self.UIRoot, rect, startingValue, maxValue, (0,0,0), (0,0,0), value_to_update, round, sig_figs)
        self.UIRoot.add_element(slider, layer)
        return slider

    def create_centered_button(self, center, wh, bttnCol, txtObj, func, layer=6):
        # params( (x, y), (w, h), Text(), onAction )
        rect = Rect((0,0),(wh))
        rect.center = center
        btn = Button(self.UIRoot, rect, bttnCol, txtObj, func)
        self.UIRoot.add_element(btn, layer)
        return btn

    def add_elements(self):
        pass # this is the only thing u need to implement

    def close(self, elem):
        self.isOpen = False
        game.curr_scene.UIPriority.remove(self.uiTag)

    def lerp(self, targ_rect, t):
        vec1 = Vec2(self.rect.x, self.rect.y)
        vec2 = Vec2(targ_rect.x, targ_rect.y)
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
                if dist < 10: # arbitrary seems to work fine tho
                    self.UIRoot.remove_self()
                    self.UIRoot = None
    
    def draw(self, window):
        pass
    
