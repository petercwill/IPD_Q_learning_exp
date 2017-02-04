from IPD.game import GameHistory, Action, Game
import random as rand
import itertools as it
import copy
import numpy as np
import collections
import math
from matplotlib import colors
import matplotlib.pylab as plt
import matplotlib.animation as animation


class Tournament(object):
    def __init__(self, players, rounds, convergence=None):
        self.players = players
        self.rounds = rounds
        self.convergence = convergence

    def run(self):

        inds = [i for i in range(len(self.players))]
        rand.shuffle(inds)
        for p in self.players:
            p.tournament_score = 0
            p.tournament_count = 0

        for (ind_1, ind_2) in it.combinations(inds, r=2):
            p1 = self.players[ind_1]
            p2 = self.players[ind_2]
            g = Game(p1, p2, self.rounds, self.convergence)
            g.run_game()
            p1.tournament_count += p1.count
            p1.tournament_score += p1.score
            p2.tournament_count += p2.count
            p2.tournament_score += p2.score

    def report_results(self):
        pos = 1
        d = {}
        for p in sorted(
            self.players,
            key=lambda p: p.tournament_score,
            reverse=True
        ):

            print(
                "%s \t %s \t %s" % (p, p.tournament_score, p.tournament_count)
            )

            d[p.name] = (pos, p.tournament_score)
            pos += 1
        return(d)

    def plot_score_heatmap(self, player1, player2):

        scores = np.array(player1.payoff_history)
        scores_cnt = collections.Counter(scores)

        if len(scores > 40000):
            scores = scores[-40000:]

        n = math.ceil(len(scores)**.5)
        filler_size = (n**2) - len(scores)
        filler = np.array(filler_size*[-1])
        square_array = np.concatenate((scores, filler))
        square_array = square_array.reshape((n, n))
        print("1")
        cols_rgb = [
            (255/256, 65/256, 65/256),
            (255/256, 255/256, 65/256),
            (65/256, 255/256, 65/256),
            (65/256, 65/256, 255/256)
            ]

        tmp = [0, 1, 3, 5]
        intervals = np.array(tmp + [tmp[-1]+1]) - 0.5
        cmap, norm = colors.from_levels_and_colors(intervals, cols_rgb)
        fig, ax = plt.subplots()

        heatmap = ax.pcolor(
            square_array,
            cmap=cmap,
            norm=norm,
            edgecolors='k',
            linewidths=.25
            )

        cbar = plt.colorbar(heatmap)
        print("2")
        cbar.ax.get_yaxis().set_ticks([])
        for j, lab in enumerate(['$S$', '$P$', '$R$', '$T$']):
            cbar.ax.text(.5, (2 * j + 1) / 8.0, lab, ha='center', va='center')
        for j, score in enumerate(tmp):
            cbar.ax.text(
                .5, (2 * j + 1) / 8.0,
                "\t n = %s" % scores_cnt.get(score),
                va='center'
            )
        cbar.ax.get_yaxis().labelpad = 15
        cbar.ax.set_ylabel('Payoff', rotation=270)
        plt.title(
            "Payoff History"
            "\n\t Player 1: %s"
            "\n\t Player 2: %s" % (player1, player2))
        plt.show()

    def plot_p_coop(self):
        assert(len(self.players) == 2), "Only works for 2-player tournaments"

        def reduce_array(a, n=10):
            reduce_size = math.floor(len(a)/n)
            avg_array = np.zeros(reduce_size)
            for i in range(reduce_size):
                avg_array[i] = np.sum(a[i*n:(i+1)*n]) / 10

            return (avg_array)

        fig, ax = plt.subplots()
        p1 = self.players[0]
        p2 = self.players[1]
        x = reduce_array(p1.c_prob_list)
        y = reduce_array(p2.c_prob_list)
        ax.set_ylim([-.05, 1.05])
        ax.set_xlim([-.05, 1.05])
        ax.set_aspect(1)
        norm = colors.Normalize(0, 1)
        cmap = plt.cm.ScalarMappable(norm=norm, cmap="jet")
        max_num = len(x)

        def init():
            return []

        def animate(i):
            xy = (x[i], y[i])

            return ax.add_patch(
                plt.Circle(xy, 0.01, color=cmap.to_rgba(i/max_num))
                ),

        ani = animation.FuncAnimation(
            fig,
            animate,
            init_func=init,
            frames=len(x)-1,
            blit=True
            )

        FFwriter = animation.FFMpegWriter(
            fps=round(max_num / 60),
            extra_args=['-vcodec', 'h264', '-pix_fmt', 'yuv420p']
            )
        ani.save('basic_animation.mp4', writer=FFwriter)

    def plot_p_coop_2(self):
        assert(len(self.players) == 2), "Only works for 2-player tournaments"

        def moving_average(a, n=3):
            ret = np.cumsum(a, dtype=float)
            ret[n:] = ret[n:] - ret[:-n]
            return ret[n - 1:] / n

        p1 = self.players[0]
        p2 = self.players[1]
        x = p1.c_prob_list
        y = p2.c_prob_list
        # x = moving_average(p1.c_prob_list,1)
        # y = moving_average(p2.c_prob_list,1)
        labels = [str(i) for i in range(len(x))]

        fig, ax = plt.subplots()
        # ax.scatter(
        #     x,
        #     y,
        #     marker="o",
        #     c="blue",
        #     facecolors="white",
        #     edgecolors="blue",
        #     label = p1.name,
        #     lw=3.0
        # )
        ax.set_ylim([-.05, 1.05])
        ax.set_xlim([-.05, 1.05])
        # line, = ax.plot(x,y)
        norm = colors.Normalize(0, 1)
        cmap = plt.cm.ScalarMappable(norm=norm, cmap="jet")
        max_num = len(x)
        print(max_num)

        class CProbPlot(object):
            def __init__(self):
                self.num = 0
                self.ax = ax

            def step(self, kwargs):
                print(self.num)
                self.num += 1
                new_segment = matplotlib.lines.Line2D(
                    x[self.num-2:self.num],
                    y[self.num-2:self.num]
                    )
                new_segment.set_color(cmap.to_rgba(self.num/max_num))
                xy = (x[self.num-1], y[self.num-1])
                new_patch = matplotlib.patches.Circle(
                    xy,
                    radius=.01,
                    color=cmap.to_rgba(self.num/max_num)
                    )
                # self.ax.add_line(new_segment)
                self.ax.add_patch(new_patch)
                return self.ax.plot()

        p_plot = CProbPlot()
        ani = animation.FuncAnimation(
            fig,
            p_plot.step,
            frames=len(x)-1,
            blit=True
            )
        FFwriter = animation.FFMpegWriter(
            fps=60,
            extra_args=['-vcodec', 'h264', '-pix_fmt', 'yuv420p']
            )
        ani.save('basic_animation.mp4', writer=FFwriter)
        # ani.save('basic_animation.mp4', extra_args=['-vcodec', 'libxvid'], fps=round(max_num / 60))
        # plt.show()


        # def init():
        #     line.set_data([],[])
        #     return line,
        #
        # def update(num, x, y, line):
        #     line.set_data(x[:num], y[:num])
        #     c = cmap.to_rgba(num/max_num)
        #     line.set_color(c)
        #     return line,
        #
        # ani = animation.FuncAnimation(fig, update, init_func=init, frames=len(x), fargs=[x, y, line],interval=25, blit=False)

        # for label,x,y in zip(labels, x,y):
        #     plt.annotate(
        #         label,
        #         xy = (x,y), xytext = (-20,20),
        #         textcoords = 'offset points', ha = 'right', va = 'bottom',
        #         bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.99)
        #     )
        # plt.legend()
        # plt.show()
