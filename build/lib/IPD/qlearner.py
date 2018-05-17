from IPD.game import GameHistory, Action, Game
import itertools as it
from IPD.player import Player
import logging
import math
import random as rn


class QLearner(Player):

    player_id = it.count()

    def __init__(
        self,
        order,
        annealing_constant_a=5,
        annealing_constant_b=.999,
        alpha=.2,
        gamma=.95,
        name="QLearner"
    ):

        self.order = order
        self.memory = GameHistory(order)
        self.behavior = None
        self.id = next(QLearner.player_id)
        self.score = 0
        self.name = "%s_%s" % (name, self.id)
        self.count = 0
        self.QLookup = {}
        self.annealing_constant_a = annealing_constant_a
        self.annealing_constant_b = annealing_constant_b
        self.t = 0
        self.alpha = alpha
        self.gamma = gamma
        self.payoff_history = []
        self.tournament_score = 0
        self.tournament_count = 0
        self.c_prob_list = []

    def string_convert_lookupTable(self):
        return_string = ""
        for k, v in self.QLookup.items():
            s = "\n\t%s : (%.2f, %.2f)" % (k, v[0], v[1])
            return_string += s
        return return_string

    def make_move(self):
        logging.debug(
            "   %s lookup table %s"
            % (self.position, self.string_convert_lookupTable())
            )
        logging.debug("   %s memory %s" % (self.position, self.memory))

        self.count += 1
        self.t = (
            self.annealing_constant_a *
            self.annealing_constant_b**self.count
            )
        (Q_coop, Q_defect) = self.QLookup.get(self.memory, (0, 0))
        action = self.explore(Q_coop, Q_defect)
        return(action)

    def explore(self, Q_coop, Q_defect):

        if self.t >= .001:
            try:
                p_coop = 1/(1 + math.exp((Q_defect - Q_coop)/self.t))
                self.c_prob_list.append(p_coop)
                logging.debug(
                    "   %s t = %s, Q_coop = %s, Q_defect = %s, p_coop = %s"
                    % (self.position, self.t, Q_coop, Q_defect, p_coop)
                    )
                act = Action(1) if rn.random() <= p_coop else Action(0)
                return act

            except (OverflowError, ZeroDivisionError) as e:
                logging.exception(e)
                pass

        logging.debug("   Exploration Period Expired")
        logging.debug(
            "   %s t = %s, Q_coop = %s, Q_defect = %s"
            % (self.position, self.t, Q_coop, Q_defect)
            )
        if Q_coop >= Q_defect:
            act = Action(1)
            self.c_prob_list.append(1)
        else:
            act = Action(0)
            self.c_prob_list.append(0)
        return act

    def update_behavior(self, p1_action, p2_action, reward):
        if len(self.memory.history) < self.order:
            return

        s = copy.deepcopy(self.memory)
        self.update_memory(p1_action, p2_action)
        s_prime = self.memory
        idx = p1_action.value  # 0 defect, 1 cooperate
        q_update = self.alpha*(
            reward + self.gamma*max(
                self.QLookup.get(s_prime, (0, 0))
                ) - self.QLookup.get(s, (0, 0))[idx]
        )

        q_0, q_1 = self.QLookup.get(s, (0, 0))
        if idx:
            self.QLookup[s] = (q_0, q_1 + q_update)

        else:
            self.QLookup[s] = (q_0 + q_update, q_1)

    def update(self, p1_action, p2_action, score):
        self.update_behavior(p1_action, p2_action, score)
        self.update_score(score)

    def reset_behavior(self):
        self.memory = GameHistory(self.order)
        self.QLookup = {}
        self.behavior = self.behavior_model()
        self.count = 0
        self.score = 0
        self.payoff_history = []

    def __str__(self):
        return "%s order = %s, gamma = %s" % (
            self.name,
            self.order,
            self.gamma
            )
