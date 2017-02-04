import random as rand
import collections
from enum import Enum
import logging


class Action(Enum):
    Cooperate = 1
    Defect = 0


class GameHistory(object):

    def __init__(self, order, **kwargs):
        games = kwargs.get('games', None)
        if(games):
            try:
                assert(len(games) == order), "length of games" \
                    "parameter must equal order: %s, %s" % (len(games), order)
            except AssertionError:
                log.exception(
                    "length of games parameter must equal order: %s, %s"
                    % (len(games), order)
                    )
            self.history = collections.deque(games, order)
        else:
            self.history = kwargs.get('games', collections.deque([], order))

    def add_game(self, p1_action, p2_action):
        self.history.append((p1_action, p2_action))

    def __key(self):
        return tuple(self.history)

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        return self.__repr__()

    def __repr__(self):

        def string_conversion(action_tuple):
            if action_tuple == (Action(1), Action(1)):
                return "(C,C)"
            if action_tuple == (Action(0), Action(1)):
                return "(D,C)"
            if action_tuple == (Action(1), Action(0)):
                return "(C,D)"
            if action_tuple == (Action(0), Action(0)):
                return "(D,D)"
            else:
                raise ValueError("bad action tuple")

        return("["+",".join(list(map(string_conversion, self.history)))+"]")


class Game(object):

    def __init__(self, p1, p2, rounds, convergence=None):
        p1.reset_behavior()
        p1.position = "P1"
        p2.reset_behavior()
        p2.position = "P2"
        self.p1 = p1
        self.p2 = p2
        self.rounds = rounds
        self.convergence = convergence
        logging.info(" Starting New Game")
        logging.info(" P1 %s" % self.p1)
        logging.info(" P2 %s" % self.p2)

    def score_game(self, action_1, action_2):
        if(action_1 == 1 and action_2 == 1):
            p1_score = 3
            p2_score = 3

        elif(action_1 == 1 and action_2 == 0):
            p1_score = 0
            p2_score = 5

        elif(action_1 == 0 and action_2 == 1):
            p1_score = 5
            p2_score = 0

        elif(action_1 == 0 and action_2 == 0):
            p1_score = 1
            p2_score = 1

        return (p1_score, p2_score)

    def play_one(self):
        logging.info(
            " Iteration %s:  P1 Score %s, P2 Score %s"
            % (self.p1.count, self.p1.score, self.p2.score)
            )
        p1_action = self.p1.make_move()
        p2_action = self.p2.make_move()
        (p1_reward, p2_reward) = self.score_game(
            p1_action.value,
            p2_action.value
            )
        logging.debug("   P1 %s, %s" % (p1_action, p1_reward))
        logging.debug("   P2 %s, %s" % (p2_action, p2_reward))
        self.p1.update(p1_action, p2_action, p1_reward)
        self.p2.update(p2_action, p1_action, p2_reward)
        return (p1_reward, p2_reward)

    def play_all_with_convergance(self):
        prev_move = None
        convergence_count = 0
        while (
            self.p1.count < self.rounds and
                convergence_count < self.convergence
        ):
            move = self.play_one()
            if move == prev_move:
                convergence_count += 1
            else:
                prev_move = move
                convergence_count = 0

            if(counter > self.convergence):
                logging.info(
                    "stopped play after %s consecutive moves"
                    % counter
                    )

    def play_all_wo_convergance(self):
        for i in range(self.rounds):
            self.play_one()

    def run_game(self):
        if self.convergence:
            self.play_all_with_convergance()
        else:
            self.play_all_wo_convergance()
