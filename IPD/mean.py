from IPD.game import GameHistory, Action, Game
from IPD.player import Player
import itertools as it


class Mean(Player):
    player_id = it.count()

    def __init__(self, order, name="Mean"):
        self.order = order
        self.memory = GameHistory(order)
        self.behavior = self.behavior_model()
        self.id = next(Mean.player_id)
        self.name = "%s_%s" % (name, self.id)
        self.score = 0
        self.count = 0
        self.payoff_history = []
        self.tournament_score = 0
        self.tournament_count = 0

    def initial_moves(self):
        return(Action(0))

    def behavior_model(self):
        behavior = {
            GameHistory(1, games=[(Action(1), Action(1))]): (0, 1),
            GameHistory(1, games=[(Action(1), Action(0))]): (0, 1),
            GameHistory(1, games=[(Action(0), Action(1))]): (0, 1),
            GameHistory(1, games=[(Action(0), Action(0))]): (0, 1)
        }
        return(behavior)
