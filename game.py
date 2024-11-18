from library import *
import traceback

class Entity: 
    # informal interface ie python is cringe and doesnt have interfaces nor
    # abstract classes so just kinda hope you do it right
    def update(self, dt):
        print("please implement the UPDATE func uwu")
    def draw(self, window):
        print("please implement the DRAW func uwu")
    def init(self):
        # called once curr_scene exists, only used in niche cases
        self.initialized = True

    # well maybe its not too bad that its not an interface
    # cause this is usefule
    def remove_self(self):
        if self.alive:
            game.remove_entity(self)
            self.alive = False
    def set_id(self, id):
        self.id = id
        self.alive = True
        self.initialized = False
    def move(self, vec):
        try:
            self.rect.move(vec)
        except Exception as e:
            print(e)
            print(self.rect.topleft)
            print("rect doesnt exist for this entity! id: " + self.id)

class Scene:
    def __init__(self, reset_on_switch=True):
        self.entities = {}
        self.drawPriorityLookup = {}
        self.toAdd = []
        self.toRm = []
        self.UIPriority = []
        self.reset_on_switch = reset_on_switch
        self.initialized = False

    def get_sorted_draw_indices(self):
        sorted_list = list(self.drawPriorityLookup.keys()).copy()
        sorted_list.sort()
        return sorted_list
    
    def get_bottom_draw_priority(self):
        limst = self.get_sorted_draw_indices()
        if len(limst) == 0:
            return 0
        return limst[1] # returns second element because the first is the background

    def get_top_draw_priority(self):
        limst = self.get_sorted_draw_indices()
        if len(limst) == 0:
            return 0
        return limst[len(limst) - 1]
    
    def add_entity(self, entity, id, drawPriority = None):
        # queues the entity to be added next update call
        self.toAdd.append((entity, id, drawPriority))

    def init_entity(self, entity, ent_id, drawPriority = None):
        return self.actually_add_entity(entity, ent_id, drawPriority)

    def get_min_draw_priority(self):
        sorted_dps = self.get_sorted_draw_indices()
        last_dp = None
        for i in sorted_dps:
            if last_dp is not None:
                if abs(i - last_dp) > 1 and last_dp + 1 > 0:
                    return last_dp + 1
            last_dp = i

        if self.get_top_draw_priority() < 0:
            return 0

        return self.get_top_draw_priority()+1

    def actually_add_entity(self, entity, ent_id, drawPriority = None):
        # idk this seems a lil stupid but drawPriority dictates WHEN the
        # entity is drawn ie entity with 0 is drawn before 1 etc
        # PASS IN "UI" for ui elements that are not the root node
        id = ent_id
        while id in self.entities:
            id += str(random.randint(0,9))
        entity.set_id(id)
        self.entities[id] = entity

        if drawPriority == "bottom":
            dp = self.get_bottom_draw_priority() - 1
            self.drawPriorityLookup[dp] = id
            return

        if drawPriority is not None:
            dp = drawPriority
            if drawPriority == "UI":
                dp = self.get_top_draw_priority() + 1
                # so root node of UI will always be like 1000 or whatever so 
                # for leaves just make it so its drawn on top

            self.drawPriorityLookup[dp] = id
            return

        # if no drawPriority provided just draw next smallest one
        self.drawPriorityLookup[self.get_min_draw_priority()] = id

    def remove_entity(self, entity):
        self.toRm.append(entity.id)

    def handle_adding(self):
        for params in self.toAdd:
            self.actually_add_entity(params[0], params[1], params[2])
        self.toAdd = []

    def get_draw_priority_from_id(self, id):
        id_to_priority = {v: k for k, v in self.drawPriorityLookup.items()}
        return id_to_priority[id]
    
    def handle_removing(self):
        for id in self.toRm:
            try:
                del self.entities[id]
                del self.drawPriorityLookup[self.get_draw_priority_from_id(id)]
            except KeyError:
                print(id + " doesnt exist")
        self.toRm = []

    def update(self, dt):
        self.handle_adding()
        if not self.initialized:
            self.start_state = copy.deepcopy(self)
            self.initialized = True

        for [key, entity] in self.entities.items():
            if not entity.initialized:
                entity.init()
            if len(self.UIPriority) > 0:
                try:
                    topTag = self.UIPriority[len(self.UIPriority)-1]
                    if topTag == entity.uiTag or entity.isUI:
                        entity.update(dt)
                except AttributeError:
                    pass
                continue

            entity.update(dt)

        self.handle_removing()


    def draw(self, window):
        for priority in self.get_sorted_draw_indices():
            self.entities[self.drawPriorityLookup[priority]].draw(window)

    def cleanup(self):
        if self.reset_on_switch:
            return self.start_state
        return False

class Game:
    def __init__(self):
        self.scenes = {}
        self.curr_scene = None
        self.mouse = Mouse()
        self.keys = [0] * 512
        self.controller = Controller()
        self.oldKeys = self.keys
        self.input_mode = "keyboard"

        self.window = None
        self.W = 0
        self.H = 0
        self.transition_timer = 0
        self.trans_time = 1
        self.time_speed = 1.0
        # init keys to avoid index error (pygame has 512 keycodes)
        # im sure theres a better way to do this
        # eg) if game.keyDown(pygame.KEY_a):
        #         print("a down")
        #
        # eg) if game.keyPressed(pygame.key_s):
        #         print("s pressed")
        #
        # dif being that pressed only returns true on the first frame the key is pressed

    def close(self, btn):
        pygame.quit()
        sys.exit()

    def init_window(self, caption):
        self.W, self.H, self.window = init(caption)

    def change_resolution(self, new_w, new_h):
        # not really working yet
        # need to make it actually scale the screen but idk
        # what to use as a base resolution
        self.window = pygame.display.set_mode((new_w,new_h))
        self.W = new_w
        self.H = new_h
    
    def get_entity_by_id(self, id):
        try:
            return self.curr_scene.entities[id]
        except KeyError as e:
            print("no entity of id: " + id)
            return False

    def get_entities_by_id(self, string_contained_by_id):
        # returns a list of entities that have an id that contains the provided string
        out = []
        for k, e in self.curr_scene.entities.items():
            if string_contained_by_id in e.id:
                out.append(e)
        return out

    def get_entities_by_type(self, class_type):
        out = []
        for k, e in self.curr_scene.entities.items():
            if isinstance(e, class_type):
                out.append(e)
        return out

    def key_down(self, keyCode):
        return self.keys[keyCode]

    def key_pressed(self, keyCode):
        # if down this frame but not the last
        return self.keys[keyCode] and not self.oldKeys[keyCode]

    def transition_lerp(self, x):
        if x > 0.5:
            out = (math.sqrt(1-math.pow(-2*x+2,2))+1)/2
        else:
            out = (1-math.sqrt(1-math.pow(2*x,2)))/2
        return out*self.W

    def remove_entity(self, entity):
        self.curr_scene.remove_entity(entity)

    def remove_scene(self, id):
        # remove scene if its not the curr one
        if self.curr_scene == self.scenes[id]:
            print("Cant remove scene youre currently in idiot")
            return

        self.curr_scene = self.scenes[id]

    def add_scene(self, scene, id):
        self.scenes[id] = scene

    def switch_to_scene(self, id, do_transition=True):
        while self.transition_timer <= self.trans_time and do_transition:
            dt = clock.tick(maxFPS)/1000
            self.transition_timer += dt
            t = self.transition_timer/self.trans_time
            l = self.transition_lerp(t)
            drawRect(game.window, [0,0,l,self.H], (0,0,0))
            pygame.display.flip()

        if self.curr_scene is not None:
            reset = self.curr_scene.cleanup()
            if reset:
                old_id = None
                for [s_id,s] in self.scenes.items():
                    if s == self.curr_scene:
                        old_id = s_id
                self.scenes[old_id] = copy.deepcopy(reset)
        try:
            self.curr_scene = self.scenes[id]
        except Exception as e:
            print("Scene is not in scenes list! maybe you forgot to add it?")

    def update(self, dt):
        try:
            self.curr_scene.update(dt)
        except Exception as e:
            print(traceback.format_exc())

        # updating input stuff
        self.mouse.update()
        self.controller.update(self, dt)
        self.oldKeys = self.keys
        self.keys = pygame.key.get_pressed()

        if 1 in self.keys:
            self.input_mode = "keyboard"

        if self.transition_timer > 0:
            self.transition_timer -= dt

    def draw(self, window):
        if not pygame.get_init():
            print(pygame.get_init())
            return
        try:
            self.curr_scene.draw(window)
        except Exception as e:
            print(traceback.format_exc())

        if self.transition_timer > 0:
            t = self.transition_timer/self.trans_time
            drawRect(game.window, [0,0,self.transition_lerp(t),self.H], (0,0,0))


# singleton game class for global access
game = Game()
