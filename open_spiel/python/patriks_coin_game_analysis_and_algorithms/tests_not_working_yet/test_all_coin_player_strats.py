import pyspiel

def run_test_sequence(game, sequence):
    state = game.new_initial_state()
    for i, coin_choice in enumerate(sequence):
        if state.is_terminal():
            print(f"Game ended before sequence completed at round {i + 1}. Game state:\n{state}")
            return False
        legal_actions = state.legal_actions(0)  # Legal actions for the Coin Player
        if coin_choice not in legal_actions:
            print(f"Test Failed: Action {coin_choice} is not legal in round {i + 1}")
            print(f"Legal actions: {legal_actions}")
            return False
        # Set Estimator's guess to a value not equal to the Coin Player's choice
        estimator_guess = (coin_choice + 1) % 6  # Ensure estimator_guess != coin_choice
        if estimator_guess == coin_choice:
            estimator_guess = (coin_choice + 2) % 6
        state.apply_actions([coin_choice, estimator_guess])
    print(f"Test Passed for sequence {sequence}")
    return True

def main():
    game = pyspiel.load_game("patriks_coin_game")
    # List of all valid sequences
    valid_sequences = [
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
    for sequence in valid_sequences:
        if not run_test_sequence(game, sequence):
            print(f"Failed on sequence {sequence}")
            break

if __name__ == "__main__":
    main()
