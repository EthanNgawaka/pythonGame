from library import *
from enemies import *

W = 800
H = 600
keys = [0] * 512  #init keys to avoid index error (pygame has 512 keycodes)
# to access the state of a key (true for down false for up) use "keys[pygame.KEYCODE]"
# eg) if keys[pygame.KEY_a]:
#         print("a down")


class Player:

    def __init__(self, x, y):
        w, h = 40, 40
        self.r = w / 2
        self.rect = [x, y, w, h]  # position = self.rect[0], self.rect[1]
        self.col = (155, 155, 155)
        self.vel = [0, 0]
        self.speed = 5000

    def physics(self, dt):
        self.rect[0] += self.vel[0]*dt
        self.rect[1] += self.vel[1]*dt
        self.vel[0] *= 0.9
        self.vel[1] *= 0.9

    def input(self, dt):
        dir = [0, 0]  # moveVector
        if keys[pygame.K_w]:
            dir[1] += -1
        if keys[pygame.K_s]:
            dir[1] += 1
        if keys[pygame.K_a]:
            dir[0] += -1
        if keys[pygame.K_d]:
            dir[0] += 1
        SF = math.sqrt(dir[0]**2 + dir[1]**2)
        if SF != 0:
            self.vel[0] += self.speed * dt * dir[0] / SF
            self.vel[1] += self.speed * dt * dir[1] / SF
        # find magnitude (scale factor) (sqrt(x^2+y^2))
        # add (speed * dir)/magnitude

    def update(self, window, dt):
        self.input(dt)
        self.physics(dt)

    def draw(self, window):
        drawCircle(window, ((self.rect[0]+self.r, self.rect[1]+self.r), self.r), self.col)


player = Player(0,0)
testEnemy = BasicEnemy(110,110)


def update(window, dt):
    global keys
    player.update(window, dt)
    testEnemy.update(window, player.rect, dt)

    keys = pygame.key.get_pressed()


def draw(window, dt):
    drawRect(window, (0, 0, W, H), (0, 0, 255))
    player.draw(window)
    testEnemy.draw(window)

maxFPS = 60
clock = pygame.time.Clock()

def main():
    window = init(W, H, "bingus 2.0")

    running = True
    while running:  # main game loop
        dt = clock.tick(maxFPS) / 1000.0
        print(1/dt)
        update(window, dt)
        draw(window, dt)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if keys[pygame.K_ESCAPE]:
            running = False

    print("Done")


if __name__ == "__main__":
    main()
