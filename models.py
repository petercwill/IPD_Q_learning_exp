from __future__ import division
import random as rand
import collections
from enum import Enum
import itertools as it

class Action(Enum):
    Cooperate = 1
    Defect = 0


class GameState():

    def __init__(self, p1_action, p2_action):
        self.p1_action = p1_action
        self.p2_action = p2_action
        self.score_game()

    def score_game(self):
        if(self.p1_action.value == 1 and self.p2_action.value == 1):
            self.p1_score = 3
            self.p2_score = 3

        elif(self.p1_action.value == 1 and self.p2_action.value == 0):
            self.p1_score = 0
            self.p2_score = 5

        elif(self.p1_action.value == 0 and self.p2_action.value == 1):
            self.p1_score = 5
            self.p2_score = 0

        else:
            self.p1_score = 1
            self.p2_score = 1

    def __key(self):
        return (self.p1_action, self.p2_action)

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        return("(%s, %s)" %(self.p1_action, self.p2_action))

    def __repr__(self):
        return("(%s, %s)" %(self.p1_action, self.p2_action))


class GameHistory(object):

    def __init__(self, order, **kwargs):
        games = self.history = kwargs.get('games', None)
        if(games):
            assert(len(games) == order), "length of games parameter must equal order: %r, %r" %(len(games), order)
            self.history = collections.deque(games, order)
        else:
            self.history = kwargs.get('games', collections.deque([], order))

    def add_game(self, gameState):
        self.history.append(gameState)

    def __key(self):
        return (tuple([(g.p1_action, g.p2_action) for g in self.history]))

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        return("%s" %self.history)

    def __repr__(self):
        return("%s" %self.history)


class Game(object):

    def __init__(self, p1, p2, rounds):
        p1.reset_behavior()
        p2.reset_behavior()
        self.p1 = p1
        self.p2 = p2
        self.rounds = rounds

    def play_one(self):
        p1_action = self.p1.make_move()
        p2_action = self.p2.make_move()
        gs_1 = GameState(p1_action,p2_action)
        gs_2 = GameState(p2_action,p1_action)
        self.p1.update(gs_1, gs_1.p1_score)
        self.p2.update(gs_2, gs_2.p1_score)
        print("%s_%s VERSUS %s_%s" %(self.p1.name, self.p1.id, self.p2.name, self.p2.id))
        print("\t %s %s" %(self.p1, p1_action))
        print("\t %s %s" %(self.p2, p2_action))


    def play_all(self):
        for i in range(self.rounds):
            self.play_one()


class Player(object):
    player_id = it.count()
    def __init__(self, order, name="defalt"):
        self.order = order
        self.memory = GameHistory(order)
        self.score = 0
        self.behavior = self.behavior_model()
        self.name = name
        self.id = next(Player.player_id)
        self.count = 0

    def behavior_model(self):
        behavior = {}
        for action_tupple in it.product(
            it.product([Action(1), Action(0)], repeat=2),
            repeat=self.order
        ):
            gh = GameHistory(self.order)
            for tup in action_tupple:
                gh.add_game(GameState(*tup))
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

    def update_memory(self, gameState):
        self.memory.add_game(gameState)

    def update_behavior(self, gameState):
        pass

    def update_score(self, score):
        self.score += score

    def update(self, gameState, score):
        self.update_memory(gameState)
        self.update_behavior(gameState)
        self.update_score(score)

    def reset_behavior(self):
        self.memory = GameHistory(self.order)
        self.behavior = self.behavior_model()

    def __str__(self):
        return("%s_Player_%s: %s" %(self.name,self.id,self.score))


class TitForTat(Player):
    #Fix this
    player_id = it.count()
    def __init__(self, order, name="TitForTat"):
        self.order = order
        self.memory = GameHistory(order)
        self.score = 0
        self.behavior = self.behavior_model()
        self.name = name
        self.id = next(TitForTat.player_id)
        self.count = 0

    def behavior_model(self):
        behavior = {
            GameHistory(1, games=[GameState(Action(1), Action(1))]):(1,0),
            GameHistory(1, games=[GameState(Action(1), Action(0))]):(0,1),
            GameHistory(1, games=[GameState(Action(0), Action(1))]):(1,0),
            GameHistory(1, games=[GameState(Action(0), Action(0))]):(0,1)
        }
        return(behavior)


class Tournament(object):
    def __init__(self, players):
        self.players = players

    def run_tournament(self):
        for (p1,p2) in it.combinations(self.players, r=2):
            Game(p1,p2,200).play_all()

    def report_results(self):
        for p in sorted(self.players, key=lambda p: p.score, reverse=True):
            print("%s \t %s" %(p,p.count))

def main():
    players = [Player(order=1) for i in range(50)]
    tit_for_tat_player = [TitForTat(order=1, name="Tit_For_Tat") for i in range(2)]
    players = players+tit_for_tat_player
    # p1 = Player(order=1)
    # p2 = Player(order=1)
    # g = Game(p1,p2,20)
    # g.play_all()
    # print(p1.score)
    # print(p2.score)
    t = Tournament(players)
    t.run_tournament()
    t.report_results()

if __name__ == '__main__':
    main()
