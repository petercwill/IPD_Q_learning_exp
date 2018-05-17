from IPD.game import GameHistory, Action, Game
import itertools as it
from IPD.player import Player


class Nice(Player):
    player_id = it.count()

    def __init__(self, order, name="Nice"):
        self.order = order
        self.memory = GameHistory(order)
        self.behavior = self.behavior_model()
        self.id = next(Nice.player_id)
        self.name = "%s_%s" % (name, self.id)
        self.score = 0
        self.count = 0
        self.payoff_history = []
        self.tournament_score = 0
        self.tournament_count = 0

    def behavior_model(self):
        behavior = {
            GameHistory(1, games=[(Action(1), Action(1))]): (1, 0),
            GameHistory(1, games=[(Action(1), Action(0))]): (1, 0),
            GameHistory(1, games=[(Action(0), Action(1))]): (1, 0),
            GameHistory(1, games=[(Action(0), Action(0))]): (1, 0)
        }
        return(behavior)
