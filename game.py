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
        self.draw_on_top = False
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
    
    def add_entity(self, entity, id, drawPriority = 3):
        # queues the entity to be added next update call
        self.toAdd.append((entity, id, drawPriority))

    def init_entity(self, entity, ent_id, drawPriority = 3):
        return self.actually_add_entity(entity, ent_id, drawPriority)

    def actually_add_entity(self, entity, ent_id, drawPriority = 3):
        id = ent_id
        while id in self.entities:
            id += str(random.randint(0,9))

        entity.set_id(id)
        self.entities[id] = entity

        # create drawPriority if needed
        if drawPriority in self.drawPriorityLookup:
            self.drawPriorityLookup[drawPriority].append(id)
            return
        self.drawPriorityLookup[drawPriority] = [id]

    def remove_entity(self, entity):
        self.toRm.append(entity.id)

    def handle_adding(self):
        for params in self.toAdd:
            self.actually_add_entity(params[0], params[1], params[2])
        self.toAdd = []

    def get_draw_priority_from_id(self, id):
        for draw_layer in self.drawPriorityLookup:
            if id in self.drawPriorityLookup[draw_layer]:
                return draw_layer

        return None
    
    def handle_removing(self):
        for id in self.toRm:
            try:
                del self.entities[id]
                self.drawPriorityLookup[self.get_draw_priority_from_id(id)].remove(id)
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
        top_layer = []
        for priority in self.get_sorted_draw_indices():
            ent_ids = self.drawPriorityLookup[priority]
            for id in ent_ids:
                self.entities[id].draw(window)

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
        self.sfx = SFX()

        self.oldKeys = self.keys
        self.input_mode = "keyboard"

        self.window = None
        self.display = None
        self.ctx = None
        self.quad_buffer = None
        self.W = 0
        self.H = 0
        self.transition_timer = 0
        self.trans_time = 1
        self.time_speed = 1.0
        self.slow_down_timer = 0
        self.slow_down_targ = 1
        self.pixelSize = 1 # idk if 2 looks good or shit
        self.rgbOffsetBase = 0.0008
        self.rgbOffset = self.rgbOffsetBase
        self.CURVATURE = 0.05

        self.abberate_targ = 0
        self.abberate_timer = 0
        # init keys to avoid index error (pygame has 512 keycodes)
        # im sure theres a better way to do this
        # eg) if game.keyDown(pygame.KEY_a):
        #         print("a down")
        #
        # eg) if game.keyPressed(pygame.key_s):
        #         print("s pressed")
        #
        # dif being that pressed only returns true on the first frame the key is pressed
        self.vert_shader = """
            #version 330 core

            in vec2 vert;
            in vec2 texcoord;
            out vec2 uvs;
            out vec2 viewPos;

            void main(){
                uvs = texcoord;
                viewPos = vert;
                gl_Position = vec4(vert, 0.0, 1.0);
            }
        """
        self.frag_shader = """
            #version 330 core

            uniform sampler2D tex;
            uniform float pixelSize;
            uniform float curvature;
            uniform float rgbOffset; // (0 to 1)
            uniform float t;

            const float scanlineIntensity = 0.1;  // (0.0 to 1.0)
            const float scanlineFrequency = 90;  // (lower = more lines)
            const float FREQ = scanlineFrequency * 2.0 * 3.14159;

            in vec2 uvs;
            in vec2 viewPos;
            out vec4 f_color;

            vec2 apply_distortion(vec2 coord){
                float x = viewPos.x;
                float y = viewPos.y;
                float r = sqrt(x*x + y*y);

                coord.x += x * curvature * r;
                coord.y += y * curvature * r/10;

                return coord;
            }

            float createScanLines(vec2 coord){
                float scanline = (1.0 - scanlineIntensity*(sin(FREQ * viewPos.y + 3.14159*t)*0.5 + 0.5));
                return scanline;
            }

            vec4 applyRGBFringe(vec2 coord){
                vec2 redCoord = coord + vec2(rgbOffset, 0.0);
                vec2 greenCoord = coord;
                vec2 blueCoord = coord - vec2(rgbOffset, 0.0);

                vec4 red = texture(tex, redCoord);
                vec4 green = texture(tex, greenCoord);
                vec4 blue = texture(tex, blueCoord);

                return vec4(red.r, green.g, blue.b, 1.0);
            }

            void main(){
                vec2 scaled_coords = apply_distortion(uvs) * textureSize(tex, 0);

                scaled_coords = floor(scaled_coords / pixelSize) * pixelSize;
                scaled_coords = scaled_coords / textureSize(tex, 0);

                if(scaled_coords.x < 0.0 || scaled_coords.x > 1.0){
                    f_color = vec4(0,0,0, 1.0);
                }else{
                    vec3 rgb = applyRGBFringe(scaled_coords).rgb;
                    float scanLineEff = createScanLines(viewPos);
                    f_color = vec4(rgb * (scanLineEff), 1.0);
                }
            }
        """

    def slow_down_time(self, speed, length):
        self.slow_down_timer = length
        self.slow_down_targ = speed

    def abberate(self, amnt, length):
        self.abberate_targ = amnt
        self.abberate_timer = length

    def close(self, btn):
        pygame.quit()
        sys.exit()

    def surf_to_tex(self,surf):
        tex = self.ctx.texture(surf.get_size(), 4)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = "BGRA"
        tex.write(surf.get_view('1'))

        return tex

    def convert_to_uv(self,pos):
        return (2*pos[0]/W - 1, -(2*pos[1]/H - 1)) # negate y cause uv uses cart
    
    def init_sounds(self):
        self.sfx.create_sound("hit", "./assets/audio/hit.wav")
        self.sfx.create_sound("shot", "./assets/audio/shot.wav")
        self.sfx.create_sound("bug_hit", "./assets/audio/bug_hit.wav")
        self.sfx.create_sound("bug_die", "./assets/audio/bug_die.wav")
        self.sfx.create_sound("frag_pickup", "./assets/audio/frag_pickup.wav")

        self.sfx.create_sound("click", "./assets/audio/click.wav")
        self.sfx.create_sound("select", "./assets/audio/select.wav")
        self.sfx.create_sound("slide", "./assets/audio/slide.wav")

    def init_window(self, caption):
        self.W, self.H, self.window, self.display = init_pygame(caption)

        # open gl stuff for shaders
        self.ctx = moderngl.create_context()
        self.quad_buffer = self.ctx.buffer(data=array('f', [
            # pos.x, pos.y, uv.x, uv.y
            -1.0, 1.0, 0.0, 0.0, # top left
            1.0, 1.0, 1.0, 0.0, # top right
            -1.0, -1.0, 0.0, 1.0, # bot left
            1.0, -1.0, 1.0, 1.0, # bot right
        ]))

        self.program = self.ctx.program(vertex_shader=self.vert_shader, fragment_shader=self.frag_shader)
        self.render_obj = self.ctx.vertex_array(self.program, [(self.quad_buffer, '2f 2f', 'vert', 'texcoord')])

    def change_resolution(self, new_w, new_h):
        # not really working yet
        # need to make it actually scale the screen but idk
        # what to use as a base resolution
        #self.window = pygame.display.set_mode((new_w,new_h))
        #self.W = new_w
        #self.H = new_h
        pass
    
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

    def does_entity_exist(self, ent):
        for [k,e] in self.curr_scene.entities.items():
            if e == ent:
                return True
        return False

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
        return out

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
            w = self.W
            h = self.H * l/2
            drawRect(self.window, Rect((0,0),(w,h*1.1)), (0,0,0))
            drawRect(self.window, Rect((0,self.H-h*1.1),(w,h*1.1)), (0,0,0))
            frame_tex = self.surf_to_tex(self.window)
            frame_tex.use(0)
            self.program['tex'] = 0
            self.program['pixelSize'] = self.pixelSize
            self.program['curvature'] = self.CURVATURE

            self.render_obj.render(mode=moderngl.TRIANGLE_STRIP)

            pygame.display.flip()
            frame_tex.release()

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

    def update(self, dt, real_dt):
        if self.slow_down_timer > 0:
            self.time_speed = lerp(self.time_speed, self.slow_down_targ, 0.1)
            self.slow_down_timer -= real_dt
        else:
            self.time_speed = lerp(self.time_speed, 1, 0.1)

        if self.abberate_timer > 0:
            self.rgbOffset = lerp(self.rgbOffset, self.abberate_targ, 0.1)
            self.abberate_timer -= real_dt
        else:
            self.rgbOffset = lerp(self.rgbOffset, self.rgbOffsetBase, 0.1)

        try:
            self.curr_scene.update(dt)
        except Exception as e:
            print(traceback.format_exc())

        # updating input stuff
        self.mouse.update(self)
        self.controller.update(self, dt)
        self.oldKeys = self.keys
        self.keys = pygame.key.get_pressed()
        camera.update(dt)

        if 1 in self.keys or self.mouse.moved_this_frame:
            self.input_mode = "keyboard"

        if self.transition_timer > 0:
            self.transition_timer -= dt

    #@profile
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
            l = self.transition_lerp(t)
            w = self.W
            h = self.H * l/2
            drawRect(self.window, Rect((0,0),(w,h*1.1)), (0,0,0))
            drawRect(self.window, Rect((0,self.H-h*1.1),(w,h*1.1)), (0,0,0))

# singleton game class for global access
game = Game()
