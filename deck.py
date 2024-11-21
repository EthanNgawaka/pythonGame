from game import *
from passives import *
from actives import *

class Deck(Entity):
    def __init__(self, player):
        self.player = player;
        self.cards = [];

    def add_card(self, card):
        card.on_pickup()
        self.cards.append(card)

    def actives(self):
        return [c for c in self.cards if isinstance(c, ActiveCard)]

    def update(self, dt):
        pass

    def draw(self, window):
        pass

