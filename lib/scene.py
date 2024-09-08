class Game:
    def __init__(self):
        self.currScene = None
        self.scenes = {}

        self.switchingTo = None

        self.transitionTimerMax = 1 # seconds
        self.transitionTimer = self.transitionTimerMax

        self.pause = 0
        self.loadingPauseLength = 0.3 # seconds

    def add_scene(self, scene):
        self.scenes[scene.name] = scene

    def actually_switch_scenes(self, name):
        try:
            self.scenes[self.currScene].exit()
        except Exception as e: # this is fine, just means currScene is null
            print(e)

        self.currScene = name

        try:
            self.scenes[self.currScene].enter()
        except Exception as e:
            print(e)

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
                print(e)
        elif self.pause <= 0:
            self.transitionTimer -= dt
        else:
            self.pause -= dt

    def draw(self):
        #draw transition

        try:
            self.scenes[self.currScene].draw() # draw if exists
        except Exception as e:
            print(e)

class Scene:
    def __init__(self, name, startingEntities, collisionRules):
        self.startingEntities = startingEntities
        self.name = name
        self.world = None

    def enter(self):
        self.world = World(collisionRules, startingEntities)
    
    def update(self, dt):
        self.world.update(dt)

    def draw(self):
        self.world.draw()

    def exit():
        print("exiting scene: " + self.name)
