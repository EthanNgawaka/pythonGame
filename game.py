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
        if self.alive:
            game.remove_entity(self)
            self.alive = False
    def set_id(self, id):
        self.id = id
        self.alive = True
    def move(self, vec):
        try:
            self.rect = self.rect.move(vec)
        except Exception as e:
            print("rect doesnt exist for this entity! id: " + self.id)

class Scene:
    def __init__(self):
        self.entities = {}
        self.drawPriorityLookup = {}
        self.toAdd = []
        self.toRm = []

    def get_sorted_draw_indices(self):
        sorted_list = list(self.drawPriorityLookup.keys()).copy()
        sorted_list.sort()
        return sorted_list
    
    def get_top_draw_priority(self):
        limst = self.get_sorted_draw_indices()
        return limst[len(limst) - 1]
    
    def add_entity(self, entity, id, drawPriority = None):
        # queues the entity to be added next update call
        self.toAdd.append((entity, id, drawPriority))

    def init_entity(self, entity, ent_id, drawPriority = None):
        self.actually_add_entity(entity, ent_id, drawPriority)

    def get_min_draw_priority(self):
        sorted_dps = self.get_sorted_draw_indices()
        last_dp = None
        for i in sorted_dps:
            if last_dp is not None:
                if abs(i - last_dp) > 1:
                    return last_dp + 1
            last_dp = i

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

        for [key, entity] in self.entities.items():
            entity.update(dt)

        self.handle_removing()


    def draw(self, window):
        for priority in self.get_sorted_draw_indices():
            self.entities[self.drawPriorityLookup[priority]].draw(window)

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
        try:
            return self.curr_scene.entities[id]
        except KeyError as e:
            print("no entity of id: " + id)

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
