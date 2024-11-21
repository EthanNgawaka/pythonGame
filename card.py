from game import *

class Card(Entity):
    def __init__(self):
        self.rect = None#Rect((game.W,game.H),(128,128))
        self.player = game.get_entity_by_id("player")

    def update(self, dt):
        self.passive()

    def draw(self, window):
        pass

    def on_pickup(self): # triggered on pickup
        pass

    def passive(self): # triggered every frame
        pass
