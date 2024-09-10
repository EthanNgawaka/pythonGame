from world import *
import traceback

class Game:
    def __init__(self):
        self.currScene = None
        self.scenes = {}

        self.curr_world = None

        self.switchingTo = None

        self.transitionTimerMax = 1 # seconds
        self.transitionTimer = self.transitionTimerMax

        self.pause = 0
        self.loadingPauseLength = 0.3 # seconds

        #input
        self.keys = [0] * 512
        self.mouse = Mouse()
        self.camera = Camera()

    def add_scene(self, scene):
        self.scenes[scene.name] = scene

    def actually_switch_scenes(self, name):
        try:
            self.scenes[self.currScene].exit()
        except Exception as e: # this is fine, just means currScene is null
            print("no scene to call exit()")

        self.currScene = name

        try:
            self.scenes[self.currScene].enter()
        except Exception as e:
            traceback.print_exc()

        self.curr_world = self.scenes[self.currScene].world
        self.switchingTo = None

    def switch_scenes(self, nameOfNewScene):
        self.transitionTimer = self.transitionTimerMax
        self.switchingTo = nameOfNewScene

    def update(self, dt):
        if self.transitionTimer <= self.transitionTimerMax*0.5:
            if self.switchingTo:
                # pause and start loading scene before finishing trasnsition
                self.pause = self.loadingPauseLength
                self.actually_switch_scenes(self.switchingTo)

            try:
                self.scenes[self.currScene].update(dt) # update if exists
            except Exception as e:
                print(f"scene with name: {self.currScene} does not exist!")
                traceback.print_exc()

        elif self.pause <= 0:
            self.transitionTimer -= dt
        else:
            self.pause -= dt

    def draw(self, window):
        #draw transition

        if self.transitionTimer <= self.transitionTimerMax*0.5:
            try:
                self.scenes[self.currScene].draw(window) # draw if exists
            except Exception as e:
                print(f"scene with name: {self.currScene} does not exist!")
                traceback.print_exc()

class Scene:
    def __init__(self, name, startingEntities, collisionRules, gameRef):
        self.startingEntities = startingEntities
        self.collisionRules = collisionRules
        self.name = name
        self.world = None
        self.game = gameRef

    def enter(self):
        try:
            self.world = World(self.game, self.collisionRules, self.startingEntities)
        except Exception as e:
            print(f"world is None for scene with name: {self.name} @ enter")
            traceback.print_exc()
    
    def update(self, dt):
        try:
            self.world.update(dt)
        except Exception as e:
            print(f"world is None for scene with name: {self.name} @ update")
            traceback.print_exc()


    def draw(self, window):
        try:
            self.world.draw(window)
        except Exception as e:
            print(f"world is None for scene with name: {self.name} @ draw")
            traceback.print_exc()

    def exit():
        print("exiting scene: " + self.name)
