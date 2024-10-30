from library import *
import traceback

class Entity: 
    # informal interface ie python is cringe and doesnt have interfaces nor
    # abstract classes so just kinda hope you do it right
    def update(self, dt):
        print("please implement the UPDATE func uwu")
    def draw(self, window):
        print("please implement the DRAW func uwu")

    # well maybe its not too bad that its not an interface
    # cause this is usefule
    def remove_self(self):
        game.remove_entity(self)
    def set_id(self, id):
        self.id = id

class Scene:
    def __init__(self):
        self.entities = {}
        self.drawPriorityLookup = {}
        self.toRm = []

    def get_sorted_draw_indices(self):
        sorted_list= list(self.drawPriorityLookup.keys()).copy()
        sorted_list.sort()
        return sorted_list
    
    def get_top_draw_priority(self):
        limst = self.get_sorted_draw_indices()
        return limst[len(limst) - 1]

    def add_entity(self, entity, id, drawPriority = None):
        # idk this seems a lil stupid but drawPriority dictates WHEN the
        # entity is drawn ie entity with 0 is drawn before 1 etc
        entity.set_id(id)
        self.entities[id] = entity
        if drawPriority is not None:
            self.drawPriorityLookup[drawPriority] = id
            return

        # if no drawPriority provided just draw on top of everything
        self.drawPriorityLookup[self.get_top_draw_priority() + 1] = id

    def remove_entity(self, entity):
        self.toRm.append(entity.id)
    
    def update(self, dt):
        for [key, entity] in self.entities.items():
            entity.update(dt)

    def draw(self, window):
        for priority in self.get_sorted_draw_indices():
            self.entities[self.drawPriorityLookup[priority]].draw(window)

        for id in self.toRm:
            del self.entities[id]
        self.toRm = []

    def cleanup(self):
        pass # idk if i even need this but called when scene is switching

class Game:
    def __init__(self):
        self.scenes = {}
        self.curr_scene = None
        self.mouse = Mouse()
        self.keys = [0] * 512
        self.oldKeys = self.keys
        # init keys to avoid index error (pygame has 512 keycodes)
        # im sure theres a better way to do this
        # eg) if game.keyDown(pygame.KEY_a):
        #         print("a down")
        #
        # eg) if game.keyPressed(pygame.key_s):
        #         print("s pressed")
        #
        # dif being that pressed only returns true on the first frame the key is pressed
    
    def get_entity_by_id(self, id):
        return self.curr_scene.entities[id]

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

    def switch_to_scene(self, id):
        if self.curr_scene is not None:
            self.curr_scene.cleanup()
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
        self.oldKeys = self.keys
        self.keys = pygame.key.get_pressed()

    def draw(self, window):
        try:
            self.curr_scene.draw(window)
        except Exception as e:
            print(traceback.format_exc())

# singleton game class for global access
game = Game()
