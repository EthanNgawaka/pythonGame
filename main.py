from library import *

W = 800
H = 600
keys = [0]*512 #init keys to avoid index error (pygame has 512 keycodes) 
# to access the state of a key (true for down false for up) use "keys[pygame.KEYCODE]"
# eg) if keys[pygame.KEY_a]:
#         print("a down")

class Player:
    def __init__(self,x,y):
        w, h = 20,20
        self.r = w/2
        self.rect = (x,y,w,h)
        self.col = (255, 0, 0)

    def update(self, window):
        pass

    def draw(self, window):
        drawCircle(window,((self.rect[0],self.rect[1]),self.r),self.col)

player = Player(0,0)
def update(window):
    global keys
    player.update(window)

    keys = pygame.key.get_pressed()

def draw(window):
    drawRect(window, (0,0,W,H), (0,0,255))
    player.draw(window)


def main():
    window = init(W,H,"bingus 2.0")

    running = True
    while running:
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
