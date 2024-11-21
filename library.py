import pygame
import copy
import pygame._sdl2 as pg_sdl2
import random
import math
import time
import cProfile, pstats, io
import sys

W = 1920 # default but not needed
H = 1080

clock = pygame.time.Clock()
maxFPS = 60

DEBUG = True

def profile(fnc):
    """A decorator that uses cProfile to profile a function"""
    def inner(*args, **kwargs):

        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner

# TODO implement this
def line_intersection_with_rect():
    pass

class Rect:
    def __init__(self, pos, dim):
        self.topleft = pygame.Vector2(pos)
        self.dimensions = pygame.Vector2(dim)

    def __getitem__(self, item):
        return [*self.topleft, *self.dimensions][item]

    def scale(self, sf_x, sf_y):
        # lin alg bullshit
        r = self.copy()
        t_vec = -r.center
        vertices = [
            r.topleft + t_vec,
            r.topleft+pygame.Vector2(r.w,0) + t_vec,
            r.topleft+pygame.Vector2(0,r.h) + t_vec,
            r.topleft+r.dimensions + t_vec,
        ]

        for i in vertices:
            i.x *= sf_x
            i.y *= sf_y
            i -= t_vec
        return Rect(vertices[0],vertices[3]-vertices[0])

    @property
    def center(self):
        return self.topleft + self.dimensions/2
    
    @center.setter
    def center(self, pos):
        self.topleft = pos - self.dimensions/2

    @property
    def x(self):
        return self.topleft.x

    @x.setter
    def x(self, x):
        self.topleft.x = x

    @property
    def y(self):
        return self.topleft.y

    @y.setter
    def y(self, y):
        self.topleft.y = y

    @property
    def w(self):
        return self.dimensions.x

    @w.setter
    def w(self, w):
        self.dimensions.x = w

    @property
    def h(self):
        return self.dimensions.y

    @h.setter
    def h(self, h):
        self.dimensions.y = h
    
    def move(self, vec):
        self.topleft += vec

    def translate(self, vec):
        new_rect = self.copy()
        new_rect.topleft += vec
        return new_rect

    def inflate(self, w, h):
        new_rect = self.copy()
        new_rect.x -= w/2
        new_rect.y -= h/2
        new_rect.w += w
        new_rect.h += h
        return new_rect

    def copy(self):
        return Rect(self.topleft,self.dimensions)

    def as_tuple(self):
        return (self.x, self.y, self.w, self.h)
    
    def __iter__(self):
        return iter((self.x, self.y, self.w, self.h))

# classes TODO( need to seperate these out )
class Mouse:
    def __init__(self):
        self.pressed = [False,False]
        self.down = [False,False]
        self.pos = pygame.Vector2()
        self.rect = pygame.Rect(0,0,0,0)

        self.moved_this_frame = False
        self.old_pos = pygame.Vector2()
    
    def update(self):
        self.old_pos = pygame.Vector2(self.pos)

        self.pressed = [False,False]
        mousePos = pygame.mouse.get_pos()
        self.pos.x = mousePos[0]
        self.pos.y = mousePos[1]
        self.rect = pygame.Rect(self.pos.x,self.pos.y,0,0)
        pressed = pygame.mouse.get_pressed(num_buttons=3)
        if pressed[0]:
            if self.down[0]:
                self.pressed[0] = False
            else:
                self.pressed[0] = True
            self.down[0] = True
        else:
            self.down[0] = False

        if pressed[1]:
            if self.down[1]:
                self.pressed[1] = False

            else:
                self.pressed[1] = True
            self.down[1] = True
        else:
            self.down[1] = False

        self.moved_this_frame = self.pos != self.old_pos


# TODO( integrate with game class )
class Camera:
    def __init__(self, trackingEasing=0.1):
        self.pos = pygame.Vector2(0,0)
        self.target = pygame.Vector2(0,0)
        self.shakeTimer = 0
        self.shakeIntensity = 0
        self.trackingEasing = trackingEasing
        self.shakeEasing = 0.5
    
    def setTarget(self, targetVec):
        self.target = targetVec

    def shake(self, intensity=20, duration=0.2, shakeEasing=0.6):
        self.shakeTimer = duration
        #self.shakeIntensity = max(self.shakeIntensity, intensity)
        self.shakeIntensity = intensity
        self.shakeEasing = shakeEasing

    def getRect(self):
        return Rect((self.pos[0], self.pos[1]), (0, 0))

    def update(self, dt):
        self.pos = self.pos.lerp(self.target, self.trackingEasing)

        if self.shakeTimer > 0:
            self.shakeTimer -= dt
            shakeVec = pygame.Vector2()
            shakeVec.x = random.uniform(-1,1)*self.shakeIntensity
            shakeVec.y = random.uniform(-0.25,0.25)*self.shakeIntensity
            self.pos = self.pos.lerp(self.pos+shakeVec, self.shakeEasing)

camera = Camera()

# currently no support for multiple controllers it just uses the first one connected
# TODO redo this
class Controller:
    def __init__(self):
        self.joysticks = []
        self.LSTICK = pygame.Vector2()
        self.RSTICK = pygame.Vector2()
        self.RTRIGGER = 0
        self.A = 0
        self.B = 0
        self.X = 0
        self.Y = 0
        self.START = 0

        self.virtual_cursor = pygame.Rect((0,0),(0,0))
        self.virtual_cursor_index = [0,0]
        self.btn_matrix = []

        self.buttons = {"a":0, "b":1, "x":2, "y":3, "start":11, "rtrigger":0}
        self.connected = False

        self.deadzone_range = 0.1
        self.prev_btns = None
        self.prev_LSTICK = self.LSTICK.copy()
        self.prev_last_in_queue = None
        self.any_input = False
        self.input_timer = 0
        self.input_change = 0
        self.input_buffer = 0.75
        self.selected_btn = None

        # new controller idea
        """
        moving along x axis:
            find button closest with x axis priority and select it
        same for y
        WAYY simpler and none of this hacky shit
        
        dist = x^2 + y^3 for x pref
        dist = x^3 + y^2 for y pref
        """

    def get_pressed(self, key):
        return getattr(self, key.upper()) == 1

    def get_down(self, key):
        return getattr(self, key.upper()) > 0

    def check_controllers_connected(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                print("new controller added")
                joy = pygame.joystick.Joystick(event.device_index)
                self.joysticks.append(joy)

    def get_selected_btn(self):
        return self.selected_btn

    def get_closest_button(self, weights, buttons_to_check, pos):
        min_btn = None
        min_btn_dist = math.inf
        for btn in buttons_to_check:
            dist = math.pow(pos.x-btn.rect.center.x, weights[0]) + math.pow(pos.y-btn.rect.center.y, weights[1]) # weighted towards x
            if dist < min_btn_dist:
                min_btn = btn
                min_btn_dist = dist

        return min_btn

    def update_virtual_cursor(self, buttons):
        if self.LSTICK.length() <= 0:
            self.input_change = self.input_buffer
            self.input_timer = 0
        if self.input_timer <= 0 and self.LSTICK.length() > 0:
            if self.selected_btn is None:
                self.selected_btn = buttons[0]

            self.input_timer = self.input_change
            if abs(self.LSTICK.x) > abs(self.LSTICK.y):
                # moving in x dir
                if self.LSTICK.x > 0:
                    # +ve x dir
                    buttons_to_check = [btn for btn in buttons if btn.rect.center.x > self.selected_btn.rect.center.x]
                    if len(buttons_to_check) == 0:
                        # loop back around
                        return 
                    self.selected_btn = self.get_closest_button([2,2], buttons_to_check, self.selected_btn.rect.center)
                    return

                # -ve x dir
                buttons_to_check = [btn for btn in buttons if btn.rect.center.x < self.selected_btn.rect.center.x]
                if len(buttons_to_check) == 0:
                    # loop back around
                    return 
                self.selected_btn = self.get_closest_button([2,2], buttons_to_check, self.selected_btn.rect.center)
                return

            # moving in y dir
            if self.LSTICK.y > 0:
                # +ve y dir
                buttons_to_check = [btn for btn in buttons if btn.rect.center.y > self.selected_btn.rect.center.y]
                if len(buttons_to_check) == 0:
                    # loop back around
                    return 
                self.selected_btn = self.get_closest_button([2,2], buttons_to_check, self.selected_btn.rect.center)
                return

            # -ve y dir
            buttons_to_check = [btn for btn in buttons if btn.rect.center.y < self.selected_btn.rect.center.y]
            if len(buttons_to_check) == 0:
                # loop back around
                return 
            self.selected_btn = self.get_closest_button([2,2], buttons_to_check, self.selected_btn.rect.center)
            return

    def update(self, game, dt):
        if not self.connected:
            self.check_controllers_connected()
            if len(self.joysticks) > 0:
                self.connected = True
            return

        joy = self.joysticks[0]

        for btn in self.buttons:
            btn_num = self.buttons[btn]
            if joy.get_button(btn_num):
                setattr(self, btn.upper(), getattr(self,btn.upper())+1)
                continue

            setattr(self, btn.upper(), 0)

        """ rounded to 1 decimal to stop drifting? idk what best practice is
        self.LSTICK = [round(joy.get_axis(0), 1), round(joy.get_axis(1), 1)]
        self.RSTICK = [round(joy.get_axis(2), 1), round(joy.get_axis(3), 1)]
        """
        self.prev_LSTICK = self.LSTICK.copy()
        self.LSTICK = pygame.Vector2(joy.get_axis(0),joy.get_axis(1))
        self.RSTICK = pygame.Vector2(joy.get_axis(2),joy.get_axis(3))
        self.RTRIGGER = 1 if joy.get_axis(4) > -0.5 else 0 # just gets rid of the range cause i dont think thats very useful for this game
        if abs(self.LSTICK.x) < self.deadzone_range:
            self.LSTICK.x = 0
        if abs(self.LSTICK.y) < self.deadzone_range:
            self.LSTICK.y = 0
        if abs(self.RSTICK.x) < self.deadzone_range:
            self.RSTICK.x = 0
        if abs(self.RSTICK.y) < self.deadzone_range:
            self.RSTICK.y = 0

        queue = game.curr_scene.UIPriority
        if game.input_mode == "keyboard":
            a = self.LSTICK.length()
            b = self.RSTICK.length()
            c = self.A or self.B or self.X or self.Y or self.START
            if a or b or c:
                game.input_mode = "controller"
                if len(queue) > 0:
                    all_buttons = game.get_entities_by_id("Button")
                    last_in_queue = queue[len(queue)-1]
                    buttons = [btn for btn in all_buttons if btn.uiTag == last_in_queue and not btn.disabled]
                    self.selected_btn = buttons[0]
            return

        if len(queue) > 0:
            last_in_queue = queue[len(queue)-1]
            all_buttons = game.get_entities_by_id("Button")
            buttons = [btn for btn in all_buttons if btn.uiTag == last_in_queue and not btn.disabled]

            if self.selected_btn is None and len(buttons) > 0:
                self.selected_btn = buttons[0]

            self.update_virtual_cursor(buttons)

        if self.input_timer > 0:
            self.input_timer -= dt
            if self.input_timer <= 0:
                self.input_change = max(self.input_change/3, 0.05)



class Image:
    def __init__(self, src, x, y, w, h):
        self.rect = Rect((x,y),(w,h))
        self.img = pygame.image.load(src).convert()
        self.img.set_colorkey((0,255,0))
        self.sprite = pygame.Surface((self.img.get_width(),self.img.get_height()))
        self.sprite.blit(self.img, (0,0))
        self.rot = 0

    def __deepcopy__(self, memo):
        # so you cant "pickle" (serialize) pygame surfaces and self.img is a pygame surface so just override here and it just shallow copies
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.copy(v))
        return result


    def set_rotation(self, rot):
        self.rot = rot

    def draw_rotated_and_flipped(self, window, rect, horiz=False,vert=False, rot_around = pygame.Vector2()):
        self.rect = rect
        self.rect.topleft -= camera.pos
        scaledImage = pygame.transform.flip(pygame.transform.scale(self.img, tuple(self.rect.dimensions)),horiz,vert) # flip on this step
        scaledAndRotatedImage = pygame.transform.rotate(scaledImage, self.rot)

        centerPos = self.rect.center
        if rot_around[0] != 0 or rot_around[1] != 0:
            centerPos = (rot_around[0], rot_around[1])
        newRect = scaledAndRotatedImage.get_rect(center=centerPos)
        window.blit(scaledAndRotatedImage, newRect.topleft)

    def draw_flipped(self, window, rect, horiz=False,vert=False):
        self.rect = rect
        self.rect.topleft -= camera.pos
        window.blit(pygame.transform.flip(pygame.transform.scale(self.img, (self.rect.w, self.rect.h)), horiz, vert), (self.rect.x, self.rect.y))

    def draw(self, window, rect):
        self.rect = rect
        self.rect.topleft -= camera.pos
        window.blit(pygame.transform.scale(self.img, (self.rect.w, self.rect.h)), (self.rect.x, self.rect.y))
    
    def draw_rotated(self, window, rect, rot_around = pygame.Vector2()):
        self.rect = rect
        self.rect.topleft -= camera.pos
        scaledImage = pygame.transform.scale(self.img, tuple(self.rect.dimensions))
        scaledAndRotatedImage = pygame.transform.rotate(scaledImage, self.rot)

        centerPos = self.rect.center
        if rot_around[0] != 0 or rot_around[1] != 0:
            centerPos = (rot_around[0], rot_around[1])
        newRect = scaledAndRotatedImage.get_rect(center=centerPos)
        window.blit(scaledAndRotatedImage, newRect.topleft)

class Spritesheet:
    def __init__(self, rect, src, spriteSize, secsBetweenFrames, bounce=False): # ([x,y,w,h], filename, [spriteW, spriteH], fps)
        self.src = src
        self.rect = rect
        self.sprite_sheet = pygame.image.load(src)
        self.spriteW = spriteSize[0]
        self.spriteH = spriteSize[1]

        self.timer = 0
        self.secsBetweenFrames = secsBetweenFrames
        self.currFrame = 0
        self.bounce = bounce
        self.animationDir = 1

        self.state = ""
        self.states = {} #{"state_name":[frames, correspondingLine]}
        self.rotation = 0

    def rotate(self, rotation):
        self.rotation = rotation

    def __deepcopy__(self, memo):
        # so you cant "pickle" (serialize) pygame surfaces and self.img is a pygame surface so just override here and it just shallow copies
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.copy(v))
        return result

    def addState(self, state_name, correspondingLine, frames):
        self.states[state_name] = [frames, correspondingLine]
        self.state = state_name

    def setState(self, state_name, reset=True):
        if self.state != state_name:
            self.state = state_name
            self.currFrame = 0
            self.animationDir = 1

    def draw(self, rect, window, rotateAround=[0,0]):
        self.rect = rect
        self.rect.topleft -= camera.pos
        scaledImage = pygame.transform.scale(self.get_curr_sprite(), (self.rect[2], self.rect[3]))
        scaledAndRotatedImage = pygame.transform.rotate(scaledImage, self.rotation)

        centerPos = (self.rect[0]+self.rect[2]/2, self.rect[1]+self.rect[3]/2)
        if rotateAround[0] != 0 and rotateAround[1] != 0:
            centerPos = (rotateAround[0], rotateAround[1])

        newRect = scaledAndRotatedImage.get_rect(center=centerPos)

        window.blit(scaledAndRotatedImage, newRect.topleft)
        
    def update(self, dt):
        self.timer += dt
        if self.timer >= self.secsBetweenFrames:
            self.currFrame += self.animationDir
            self.timer = 0

            if self.bounce:
                if self.currFrame == 0 or self.currFrame >= self.states[self.state][0]-1:
                    self.animationDir*=-1
            else:
                if self.currFrame >= self.states[self.state][0]:
                    self.currFrame = 0

    def get_sprite(self, x, y):
        sprite = pygame.Surface((self.spriteW, self.spriteH))
        sprite.set_colorkey((0,255,0))
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, self.spriteW, self.spriteH))
        return sprite

    def get_curr_sprite(self):
        state = self.states[self.state]
        return self.get_sprite(self.currFrame*self.spriteW, state[1]*self.spriteH)

# init funcs
def init(caption):
    pygame.init()
    pygame.joystick.init()
    display_info = pygame.display.Info()

    W = display_info.current_w
    H = display_info.current_h

    window = pygame.display.set_mode((W,H), pygame.FULLSCREEN | pygame.DOUBLEBUF)#, flags=pygame.SCALED | pygame.HIDDEN)

    #SCALE = (display_info.current_w/windowW, display_info.current_h/windowH)
    #nativeWindow = pg_sdl2.Window.from_display_module()
    #nativeWindow.size = (windowW * SCALE[0], windowH * SCALE[1])
    #nativeWindow.position = pg_sdl2.WINDOWPOS_CENTERED
    #nativeWindow.show()

    #pygame.display.toggle_fullscreen()
    pygame.display.set_caption(caption)
    return (W,H,window)

# misc math funcs
def vec_angle_to(A, B):
    AtoB = B - A
    return math.atan2(AtoB.y, AtoB.x)
def degs_to_rads(degs):
    return math.pi*degs/180
def rads_to_degs(rads):
    return 180*rads/math.pi
def lerp(i, j, t):
    return i * (1-t) + j*t
def AABBCollision(rect1, rect2): # rect = (x,y,w,h) returns min trans vec if true
    # actual aabb logic, never done it in a list b4 thought itd look neater
    checks = [
        (rect1[0]+rect1[2] >= rect2[0]), (rect1[0] <= rect2[0]+rect2[2]),
        (rect1[1]+rect1[3] >= rect2[1]), (rect1[1] <= rect2[1] + rect2[3])
    ]
    for check in checks:
        if not check:
            return False

    ytv21 = rect2[1] - (rect1[1]+rect1[3])
    ytv12 = (rect2[1]+rect2[3]) - rect1[1]

    xtv21 = rect2[0] - (rect1[0]+rect1[2])
    xtv12 = (rect2[0]+rect2[2]) - rect1[0] 
    
    ytv = ytv21 if abs(ytv21) < abs(ytv12) else ytv12
    xtv = xtv21 if abs(xtv21) < abs(xtv12) else xtv12
    
    mtv = (xtv,0) if abs(xtv) < abs(ytv) else (0,ytv)
    return mtv

# so i didnt realise font drawing was SO FUCKING EXPENSIVE
# create a new img to blit every frame is real bad but
# improves by about 4x with caching
# a font img is uniquely determined by its string, col and size
# if exists use it if not create it and add it to cached fonts
cached_fonts = {}
def drawWrappedText(window, string, col, size, rect, pad = [0,0,0], center=False):
    # pad = [x, y, line padding]
    # if wrap is given its a rect defining the place the text will be drawn,
    # in this case, if drawAtCenter, each line will be centered
    # (think of centering a line in word doc)
    # but it will still be inside of the rect
    font = pygame.font.SysFont("Arial",size)
    wrap = rect
    w_pad = pad[0]
    h_pad = pad[1]
    line_pad = pad[2]
    line_h = pygame.font.Font.size(font, "Tg")[1]
    max_w = wrap[2] - w_pad
    words = string.split(" ")
    lines = []
    curr_line = []
    for word in words:
        curr_line.append(word)
        font_dim = pygame.font.Font.size(font, " ".join(curr_line))
        if font_dim[0] > max_w or word == "|":
            overflow = curr_line[-1:]
            curr_line = curr_line[:-1]
            lines.append(" ".join(curr_line).strip())
            if word == "|":
                curr_line = []
                continue
            curr_line = overflow
    lines.append(" ".join(curr_line).strip())

    if center:
        for i in range(len(lines)):
            draw_pos = wrap.center.copy()
            draw_pos.y = wrap.y
            draw_pos.y += h_pad + (i) * (line_h + line_pad)
            drawText(window, lines[i], col, draw_pos, size, True) 
        return

    for i in range(len(lines)):
        draw_pos = wrap.topleft.copy()
        draw_pos.x += w_pad/2
        draw_pos.y += h_pad + (i) * (line_h + line_pad)
        drawText(window, lines[i], col, draw_pos, size, False) 

    return

# drawing funcs
def drawText(window, string, col, in_pos, size, drawAtCenter=False):
    pos = in_pos - camera.pos
    if (string, col, size) in cached_fonts:
        img = cached_fonts[(string, col, size)]
    else:
        font = pygame.font.SysFont("Arial",size)
        img = font.render(string, True, col)
        cached_fonts[(string, col, size)] = img

    drawPos = pos

    if drawAtCenter:
        textRect = img.get_rect()
        textRect.center = drawPos
        window.blit(img, textRect)
    else:
        window.blit(img, drawPos)

def drawRect(window, in_rect, col_obj, outline_thickness=0, ignore_camera=False):
    rect = in_rect
    # col = (R, G, B, [A])
    # col_obj = (fill_col, outline_col)
    # can just pass fill_col if outline_thickness is left as 0
    # so it turns out creating a new surface a million times a frame is kinda ass soooo
    # back to basics

    col = col_obj
    out_col = None
    if outline_thickness > 0:
        col = col_obj[1]
        out_col = col_obj[0]

    if len(col) == 4 and col[3]/255 < 1: # alpha is provided
        # while creating a new surface constantly is bad
        # for an alpha it is still necessary so IF there is a transparent object then
        # do the surface version
        s = pygame.Surface((rect[2], rect[3]))
        s.set_alpha(col[3])
        s.fill((col[0],col[1],col[2]))

        if outline_thickness > 0:
            s.fill((out_col[0],out_col[1],out_col[2]), s.get_rect().inflate(-outline_thickness, -outline_thickness))

        window.blit(s, (rect[0]-camera.pos.x, rect[1]-camera.pos.y))
        return
        
    # just draw the goddamn rectangle
    draw_rect = rect.copy()
    if not ignore_camera:
        try:
            draw_rect.topleft -= camera.pos
        except AttributeError:
            draw_rect[0] -= camera.pos.x
            draw_rect[1] -= camera.pos.y
    try:
        pygame.draw.rect(window, col, rect)
        if outline_thickness > 0:
            pygame.draw.rect(window, out_col, draw_rect, outline_thickness)
    except TypeError:
        pygame.draw.rect(window, col, draw_rect.as_tuple())
        if outline_thickness > 0:
            pygame.draw.rect(window, out_col, draw_rect.as_tuple(), outline_thickness)

def drawCircle(window, in_circle, col): # circle = (center, radius)
    circle = in_circle
    circle[0][0] -= camera.pos.x
    circle[0][1] -= camera.pos.y
    pygame.draw.circle(window, col, circle[0], circle[1])

