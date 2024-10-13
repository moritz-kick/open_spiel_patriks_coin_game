import pyspiel
import json
import os
import matplotlib.pyplot as plt

def run_cfr_and_save_history():
    # Load your game
    game = pyspiel.load_game("patriks_coin_game")
    
    # Wrap the game to make it sequential
    sequential_game = pyspiel.convert_to_turn_based(game)
    
    # Initialize CFR Solver
    cfr_solver = pyspiel.CFRSolver(sequential_game)
    num_iterations = 5000  # As per your requirement
    
    # Initialize a dictionary to store action probabilities over iterations
    action_prob_history = {f"Action(id={i}, player=0)": [] for i in range(6)}  # Corrected action names
    
    for i in range(1, num_iterations + 1):
        cfr_solver.evaluate_and_update_policy()
    
        # Get the current average policy
        current_policy = cfr_solver.average_policy()
    
        # Traverse the initial state to get action probabilities
        initial_state = sequential_game.new_initial_state()
        player = initial_state.current_player()
        action_probs = current_policy.action_probabilities(initial_state)
    
        # Store the probabilities
        for action, prob in action_probs.items():
            action_name = sequential_game.action_to_string(player, action)
            if action_name in action_prob_history:
                action_prob_history[action_name].append(prob)
            else:
                # Handle unexpected actions if any
                action_prob_history[action_name] = [prob]
    
        if i % 10 == 0 or i == 1:
            print(f"Iteration {i} completed")
    
    # Save the action probability history to JSON
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, "../data")
    os.makedirs(output_dir, exist_ok=True)
    history_path = os.path.join(output_dir, "action_prob_history.json")
    
    with open(history_path, "w") as f:
        json.dump(action_prob_history, f, indent=4)
    
    print(f"Action probability history saved to {history_path}")
    
    # Optionally, save the game tree results as before

if __name__ == "__main__":
    run_cfr_and_save_history()