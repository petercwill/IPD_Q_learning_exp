from IPD.game import GameHistory, Action, Game
import random as rand
import itertools as it


class Player(object):
    player_id = it.count()

    def __init__(self, order, name="defalt"):
        self.order = order
        self.memory = GameHistory(order)
        self.behavior = self.behavior_model()
        self.id = next(Player.player_id)
        self.name = "%s_%s" % (name, self.id)
        self.score = 0
        self.count = 0
        self.payoff_history = []
        self.tournament_score = 0
        self.tournament_count = 0

    def behavior_model(self):
        behavior = {}
        for action_tupple in it.product(
            it.product([Action(1), Action(0)], repeat=2),
            repeat=self.order
        ):
            gh = GameHistory(self.order)
            for tup in action_tupple:
                gh.add_game(*tup)
            behavior[gh] = (.5, .5)
        return(behavior)

    def initial_moves(self):
        return(Action(1))

    def make_move(self):
        self.count += 1
        if len(self.memory.history) < self.order:
            return(self.initial_moves())
        else:
            p_coop, p_defect = self.behavior[self.memory]
            if rand.random() < p_coop:
                return(Action(1))
            else:
                return(Action(0))

    def update_memory(self, p1_action, p2_action):
        self.memory.add_game(p1_action, p2_action)

    def update_behavior(self, p1_action, p2_action):
        pass

    def update_score(self, score):
        self.payoff_history.append(score)
        self.score += score

    def update(self, p1_action, p2_action, score):
        self.update_memory(p1_action, p2_action)
        self.update_behavior(p1_action, p2_action)
        self.update_score(score)

    def reset_behavior(self):
        self.memory = GameHistory(self.order)
        self.behavior = self.behavior_model()
        self.count = 0
        self.score = 0
        self.payoff_history = []

    def __str__(self):
        return self.name
