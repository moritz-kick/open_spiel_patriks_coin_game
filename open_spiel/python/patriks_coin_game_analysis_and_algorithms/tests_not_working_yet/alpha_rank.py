#not working
import itertools
import numpy as np
from open_spiel.python.egt import alpharank
from typing import List, Tuple, Dict, Set

# Define the set of possible moves
MOVES = range(6)


# Coin Player strategies
PLAYER_STRATEGIES = [
    (0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 1, 5),
    (0, 2, 3), (0, 2, 4), (0, 2, 5),
    (0, 3, 4), (0, 3, 5),
    (0, 4, 5),
    (0, 5, 5),
    (1, 0, 2), (1, 0, 3), (1, 0, 4), (1, 0, 5),
    (1, 2, 0), (1, 2, 3), (1, 2, 4), (1, 2, 5),
    (1, 3, 0), (1, 3, 4), (1, 3, 5),
    (1, 4, 0), (1, 4, 5),
    (1, 5, 0), (1, 5, 5),
    (2, 0, 3), (2, 0, 4), (2, 0, 5),
    (2, 3, 0), (2, 3, 4), (2, 3, 5),
    (2, 4, 0), (2, 4, 5),
    (2, 5, 0), (2, 5, 5),
    (3, 0, 4), (3, 0, 5),
    (3, 4, 0), (3, 4, 5),
    (3, 5, 0), (3, 5, 5),
    (4, 0, 5),
    (4, 5, 0), (4, 5, 5),
    (5, 0, 5),
    (5, 5, 0), (5, 5, 5)
]

# Estimator strategies
ESTIMATOR_STRATEGIES = list(itertools.product(MOVES, repeat=3))

def simulate_game(player_strategy: Tuple[int, ...], estimator_guesses: Tuple[int, ...]) -> Tuple[int, int]:
    """Simulates a game and returns the outcome and the ending round."""
    for round_num, (player_move, estimator_guess) in enumerate(zip(player_strategy, estimator_guesses)):
        if player_move == estimator_guess:
            return -1, round_num + 1  # Estimator wins
    return 1, 3  # Player wins

# Initialize payoff matrices
num_p0_strategies = len(PLAYER_STRATEGIES)
num_p1_strategies = len(ESTIMATOR_STRATEGIES)

payoff_matrix_p0 = np.zeros((num_p0_strategies, num_p1_strategies))
payoff_matrix_p1 = np.zeros((num_p0_strategies, num_p1_strategies))

# Step 3: Populate payoff matrices
for i, p0_strategy in enumerate(PLAYER_STRATEGIES):
    for j, p1_strategy in enumerate(ESTIMATOR_STRATEGIES):
        outcome, end_round = simulate_game(p0_strategy, p1_strategy)
        payoff_matrix_p0[i, j] = outcome
        payoff_matrix_p1[i, j] = -outcome

# Step 4: Prepare payoff matrices
payoff_matrices = [payoff_matrix_p0, payoff_matrix_p1]

# Step 5: Run Alpha-Rank
from open_spiel.python.egt import alpharank

# Provide strategy labels
p0_strategy_labels = ['-'.join(map(str, s)) for s in PLAYER_STRATEGIES]
p1_strategy_labels = ['-'.join(map(str, s)) for s in ESTIMATOR_STRATEGIES]

alpharank_results = alpharank.compute(payoff_matrices)
rhos, rho_m, pi, _, _ = alpharank_results

# Print results
alpharank.print_results(payoff_matrices, False, pi=pi,
                        strat_labels=(p0_strategy_labels, p1_strategy_labels))