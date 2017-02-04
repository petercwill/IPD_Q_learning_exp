import IPD

q_v_q = IPD.tournament.Tournament(
    [
        IPD.qlearner.QLearner(
            order=10,
            name="QLearner",
            gamma=.9,
            alpha=.2,
            annealing_constant_a=50,
            annealing_constant_b=.999
        ),
        IPD.qlearner.QLearner(
            order=2,
            name="QLearner",
            gamma=.9,
            alpha=.2,
            annealing_constant_a=50,
            annealing_constant_b=.99
        )
    ],
    10000
)

q_v_t = IPD.tournament.Tournament(
    [
        IPD.qlearner.QLearner(
            order=4,
            name="QLearner",
            gamma=.5,
            alpha=.2,
            annealing_constant_a=20,
            annealing_constant_b=.9999
        ),
        IPD.tft.TitForTat(order=1)
    ],
    20
)

iterT = IPD.iteratedTournament.IteratedTournament(q_v_q, 10, "scores_out.txt")

iterT.run()
iterT.make_avg_plot()
