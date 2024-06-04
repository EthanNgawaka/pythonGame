from library import *

W = 800
H = 600
keys = [0]*512 #init keys to avoid index error (pygame has 512 keycodes) 
# to access the state of a key (true for down false for up) use "keys[pygame.KEYCODE]"
# eg) if keys[pygame.KEY_a]:
#         print("a down")

x = 0
y = 0
def update(window):
    global keys,x,y
    if keys[pygame.K_w]:
        y -= 1
    if keys[pygame.K_s]:
        y += 1
    if keys[pygame.K_a]:
        x -= 1
    if keys[pygame.K_d]:
        x += 1

    keys = pygame.key.get_pressed()

def draw(window):
    global x,y
    drawRect(window, (0,0,W,H), (0,0,255))

    temprect = (W/2, H/2, 100,100)
    drawRect(window, temprect, (0,0,0))

    check = AABBCollision((x,y,50,50), temprect)
    if check:
        x += check[0]
        y += check[1]
        drawRect(window, (x,y,50,50), (255,0,0))
    else:
        drawRect(window, (x,y,50,50), (0,255,0))

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

    print("beans 2")

if __name__ == "__main__":
    main()
