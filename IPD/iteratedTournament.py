from IPD.game import GameHistory, Action, Game
import random as rand
import itertools as it
import numpy as np
import logging
import pickle
import matplotlib.pylab as plt


class IteratedTournament(object):
    def __init__(
        self,
        tournament,
        iterations,
        scores_output_fp=None
    ):
        self.tournament = tournament
        self.iterations = iterations
        self.scores_output_fp = scores_output_fp

    def run(self):
            n_players = len(self.tournament.players)
            n_games = self.tournament.rounds
            avg_score_mat = np.zeros((n_players, self.iterations, n_games))
            division_array = np.arange(1, self.tournament.rounds+1)

            for tourn_idx in range(self.iterations):
                logging.info("New Tournament")
                self.tournament.run()
                self.tournament.report_results()

                if self.scores_output_fp:
                    for player_idx in range(n_players):
                        scores = np.array(
                            self.tournament.players[player_idx].payoff_history
                            )
                        avg_scores = np.divide(
                            np.cumsum(scores),
                            np.arange(1, n_games+1)
                        )

                        avg_score_mat[player_idx][tourn_idx] = avg_scores

                pickle.dump(
                    avg_score_mat,
                    open(self.scores_output_fp, 'wb')
                    )

            self.report_results(avg_score_mat)

    def report_results(self, avg_score_mat):

        n_games = self.tournament.rounds
        avg_scores = np.mean(
            avg_score_mat[:, :, -1]*n_games,
            axis=1
        )

        std_scores = np.std(
            avg_score_mat[:, :, -1]*n_games,
            axis=1
        )

        for player_score_pair in sorted(
            zip(avg_scores, std_scores, self.tournament.players),
            reverse=True
        ):

            print("%s \t %s \t %s" % (
                player_score_pair[2],
                player_score_pair[0],
                player_score_pair[1]
                )
            )

    def make_avg_plot(self):
        avg_score_mat = pickle.load(open(self.scores_output_fp, 'rb'))
        n_players, n_tournaments, n_games = avg_score_mat.shape
        fig, ax = plt.subplots()

        color = iter(plt.cm.rainbow(np.linspace(0, 1, n_players)))

        for player_idx in range(n_players):
            c = next(color)
            avg_scores = avg_score_mat[player_idx]
            means = np.mean(avg_scores, axis=0)
            std_devs = np.std(avg_scores, axis=0)
            means_low = means - std_devs
            means_high = means + std_devs
            iterations = np.arange(n_games)

            ax.plot(
                iterations,
                means,
                color=c,
                label='%s' % self.tournament.players[player_idx],
                ls="--"
                )

            ax.fill_between(
                iterations,
                means_low,
                means_high,
                facecolor=c,
                alpha=0.5)

            ax.legend(loc='upper right')
            ax.set_xlabel('n')
            ax.set_ylabel('Average Score Per Game')
            ax.set_ylim([0, 5])
            ax.title.set_text('%s trial Avg.' % n_tournaments)
            ax.grid()

        plt.show()
