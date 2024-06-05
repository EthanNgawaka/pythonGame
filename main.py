from library import *

W = 800
H = 600
keys = [0] * 512  #init keys to avoid index error (pygame has 512 keycodes)
# to access the state of a key (true for down false for up) use "keys[pygame.KEYCODE]"
# eg) if keys[pygame.KEY_a]:
#         print("a down")


class Player:

    def __init__(self, x, y):
        w, h = 20, 20
        self.r = w / 2
        self.rect = [x, y, w, h]  # position = self.rect[0], self.rect[1]
        self.col = (155, 155, 155)
        self.vel = [0, 0]
        self.speed = 0.1

    def physics(self):
        self.rect[0] += self.vel[0]
        self.rect[1] += self.vel[1]
        self.vel[0] *= 0.9
        self.vel[1] *= 0.9
        pass

    def input(self):
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
            self.vel[0] += self.speed * dir[0] / SF
            self.vel[1] += self.speed * dir[1] / SF
        # find magnitude (scale factor) (sqrt(x^2+y^2))
        # add (speed * dir)/magnitude

    def update(self, window):
        self.input()
        self.physics()

    def draw(self, window):
        drawCircle(window, ((self.rect[0]+self.r, self.rect[1]+self.r), self.r), self.col)


player = Player(0,0)


def update(window):
    global keys
    player.update(window)

    keys = pygame.key.get_pressed()


def draw(window):
    drawRect(window, (0, 0, W, H), (0, 0, 255))
    player.draw(window)


def main():
    window = init(W, H, "bingus 2.0")

    running = True
    while running:  # main game loop
        update(window)
        draw(window)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if keys[pygame.K_ESCAPE]:
            running = False

    print("Done")


if __name__ == "__main__":
    main()
