from __future__ import division
import random as rand
import collections
from enum import Enum
import itertools as it
import math
import copy
import matplotlib.pylab as plt
from itertools import cycle
import numpy as np
from matplotlib import colors
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
        # return_string = ""
        # for num,item in enumerate(self.history):
        #     return_string += "%s:  %s \n"%(num,item)
        # return(return_string)
        return("%s" %self.history)



class Game(object):

    def __init__(self, p1, p2, rounds):
        p1.reset_behavior()
        p2.reset_behavior()
        self.p1 = p1
        self.p2 = p2
        self.rounds = rounds

    def play_one(self):
        print("\n ****NEW GAME**** \n")
        p1_action = self.p1.make_move()
        p2_action = self.p2.make_move()
        gs_1 = GameState(p1_action,p2_action)
        gs_2 = GameState(p2_action,p1_action)
        print("%s_%s VERSUS %s_%s" %(self.p1.name, self.p1.id, self.p2.name, self.p2.id))
        print("\t %s %s" %(self.p1, p1_action))
        print("\t %s %s" %(self.p2, p2_action))
        self.p1.update(gs_1, gs_1.p1_score)
        self.p2.update(gs_2, gs_2.p1_score)


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
        self.score_dict = {}
        self.avg_reward = []

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
        self.avg_reward.append(self.score / self.count)
        self.score_dict[self.count] = score

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
    player_id = it.count()
    def __init__(self, order, name="TitForTat"):
        self.order = order
        self.memory = GameHistory(order)
        self.score = 0
        self.behavior = self.behavior_model()
        self.name = name
        self.id = next(TitForTat.player_id)
        self.count = 0
        self.score_dict = {}
        self.avg_reward = []

    def behavior_model(self):
        behavior = {
            GameHistory(1, games=[GameState(Action(1), Action(1))]):(1,0),
            GameHistory(1, games=[GameState(Action(1), Action(0))]):(0,1),
            GameHistory(1, games=[GameState(Action(0), Action(1))]):(1,0),
            GameHistory(1, games=[GameState(Action(0), Action(0))]):(0,1)
        }
        return(behavior)


class StableCooperate(Player):
    player_id = it.count()
    def __init__(self, order, name="Nice"):
        self.order = order
        self.memory = GameHistory(order)
        self.score = 0
        self.behavior = self.behavior_model()
        self.name = name
        self.id = next(StableCooperate.player_id)
        self.count = 0
        self.score_dict = {}
        self.avg_reward = []

    def behavior_model(self):
        behavior = {
            GameHistory(1, games=[GameState(Action(1), Action(1))]):(1,0),
            GameHistory(1, games=[GameState(Action(1), Action(0))]):(1,0),
            GameHistory(1, games=[GameState(Action(0), Action(1))]):(1,0),
            GameHistory(1, games=[GameState(Action(0), Action(0))]):(1,0)
        }
        return(behavior)


class StableDefect(Player):
    player_id = it.count()
    def __init__(self, order, name="Mean"):
        self.order = order
        self.memory = GameHistory(order)
        self.score = 0
        self.behavior = self.behavior_model()
        self.name = name
        self.id = next(StableDefect.player_id)
        self.count = 0
        self.score_dict = {}
        self.avg_reward = []

    def initial_moves(self):
        return(Action(0))

    def behavior_model(self):
        behavior = {
            GameHistory(1, games=[GameState(Action(1), Action(1))]):(0,1),
            GameHistory(1, games=[GameState(Action(1), Action(0))]):(0,1),
            GameHistory(1, games=[GameState(Action(0), Action(1))]):(0,1),
            GameHistory(1, games=[GameState(Action(0), Action(0))]):(0,1)
        }
        return(behavior)


class QLearner(Player):

    player_id = it.count()
    def __init__(
        self,
        order,
        annealing_constant_a=5,
        annealing_constant_b=.999,
        alpha=.2,
        gamma=.1,
        name="QLearner"
    ):

        self.order = order
        self.memory = GameHistory(order)
        self.score = 0
        self.behavior = None
        self.name = name
        self.id = next(QLearner.player_id)
        self.count = 0
        self.QLookup = {}
        self.annealing_constant_a = annealing_constant_a
        self.annealing_constant_b = annealing_constant_b
        self.t = 0
        self.alpha = alpha
        self.gamma = gamma
        self.score_dict = {}
        self.avg_reward = []


    def make_move(self):
        self.count += 1
        self.t = self.annealing_constant_a * self.annealing_constant_b**self.count
        Q_s_coop = self.get_Q_value(self.memory, Action(1))
        Q_s_defect = self.get_Q_value(self.memory, Action(0))
        print("Q_coop: %s, Q_s_defect: %s" %(Q_s_coop, Q_s_defect))
        if self.t > .05:
            action = self.explore(Q_s_coop, Q_s_defect)
        else:
            if(Q_s_coop >= Q_s_defect):
                action = Action(1)
            else:
                action = Action(0)

        return(action)


    def explore(self, Q_coop, Q_defect):
        try:
            p_coop = 1/(1 + math.exp((Q_defect - Q_coop)/self.t))
            print("t: %s" %self.t)
            print("prob coop: %s" %p_coop)
            if rand.random() < p_coop:
                action = Action(1)
            else:
                action = Action(0)

        except OverflowError:
            print("OVERFLOW")
            if(Q_coop >= Q_defect):
                action = Action(1)
            else:
                action = Action(0)

        return(action)





    def get_Q_value(self, state, action):
        #print("Looking for (%s, %s) in %s" %(state, action, self.QLookup))
        if (state, action) in self.QLookup:
            return(self.QLookup[(state, action)])
        else:
            return(0)

    def update_behavior(self, gamestate, reward):
        s = copy.deepcopy(self.memory)
        if(len(s.history)) >= self.order:
            s_prime = copy.deepcopy(s)
            #print("S: %s" %s)
            #print("S_Prime: %s" %s_prime)
            s_prime.add_game(gamestate)
            # print("t: %s" %self.t)
            # print("S: %s" %s)
            # print("S_prime: %s" %s_prime)
            # print("S_prime for Coop: %s" %self.get_Q_value(s_prime, Action(1)))
            # print("S_prime for Defect: %s" %self.get_Q_value(s_prime, Action(0)))
            #print("S: %s" %s)
            #print("S_Prime: %s" %s_prime)
            a = gamestate.p1_action
            q_update = self.alpha*(
                reward + self.gamma*max(
                    self.get_Q_value(s_prime, Action(1)),
                    self.get_Q_value(s_prime, Action(0))
                    ) - self.get_Q_value(s, a)
            )
            if (s,a) in self.QLookup:
                print("state IN Q_lookup")
                self.QLookup[(s, a)] += q_update
            else:
                print("state NOT IN Q_lookup")
                self.QLookup[(s, a)] = q_update

            # print("UPDATED %s, %s with %s" %(s,a, q_update))
            #self.QLookup[(s, a)] = q_update
        else:
            pass

    def update(self, gameState, score):
        self.update_behavior(gameState, score)
        self.update_memory(gameState)
        self.update_score(score)

    def reset_behavior(self):
        self.memory = GameHistory(self.order)
        self.QLookup = {}


class Tournament(object):
    def __init__(self, players, rounds):
        self.players = players
        self.rounds = rounds

    def run_tournament(self):
        for (p1,p2) in it.combinations(self.players, r=2):
            Game(p1,p2,self.rounds).play_all()

    def report_results(self):
        for p in sorted(self.players, key=lambda p: p.score, reverse=True):
            print("%s \t %s" %(p,p.count))

    def plot_average_scores(self):
        fig, ax = plt.subplots()
        lines = ["-", "--", "-."]
        linecycler = cycle(lines)
        for p in self.players:

            y = p.avg_reward
            x = [i for i in range(len(y))]
            ax.plot(
                x,
                y,
                label = p.name,
                lw=3.0,
                ls=next(linecycler)
            )
        plt.legend()
        plt.show()

    def plot_score_heatmap(self, player):
        cols = {-1:'grey', 0:'black',1:'blue',3:'green',5:'red'}
        scores = np.array([i for i in player.score_dict.values()])
        n = math.ceil(len(scores)**.5)
        filler_size = (n**2) - len(scores)
        filler = np.array(filler_size*[-1])
        square_array = np.concatenate((scores,filler))
        square_array = square_array.reshape((n,n))
        cvr = colors.ColorConverter()
        tmp = sorted(cols.keys())
        cols_rgb = [cvr.to_rgb(cols[k]) for k in tmp]
        intervals = np.array(tmp + [tmp[-1]+1]) - 0.5
        cmap, norm = colors.from_levels_and_colors(intervals,cols_rgb)
        plt.pcolor(square_array,cmap = cmap, norm = norm)
        # plt.imshow(square_array, cmap="hot", interpolation='nearest')
        # print(square_array)
        plt.colorbar()
        plt.show()


def main():
    default_players = [Player(order=1) for i in range(2)]
    #default_players = []
    tit_for_tat_players = [TitForTat(order=1, name="Tit_For_Tat") for i in range(1)]
    q_players = [QLearner(order=4, name="Q_Learner", gamma=.95, alpha=.2, annealing_constant_b=.5) for i in range(1)]
    mean_players = [StableDefect(order=1, name="Mean") for i in range(1)]
    nice_players = [StableCooperate(order=1, name="Nice") for i in range(2)]
    players = q_players+tit_for_tat_players
    # p1 = Player(order=1)
    # p2 = Player(order=1)
    # g = Game(p1,p2,20)
    # g.play_all()
    # print(p1.score)
    # print(p2.score)
    t = Tournament(players,1000)
    t.run_tournament()
    t.report_results()
    #t.plot_average_scores()
    t.plot_score_heatmap(t.players[0])

if __name__ == '__main__':
    main()
