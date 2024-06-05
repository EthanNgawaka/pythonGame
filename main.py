from library import *

W = 800
H = 600
keys = [0]*512 #init keys to avoid index error (pygame has 512 keycodes) 
# to access the state of a key (true for down false for up) use "keys[pygame.KEYCODE]"
# eg) if keys[pygame.KEY_a]:
#         print("a down")

def update(window):
    global keys

    keys = pygame.key.get_pressed()

def draw(window):
    drawRect(window, (0,0,W,H), (0,0,255))


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
