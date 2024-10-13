import pyspiel
import json
import os
import matplotlib.pyplot as plt

def run_cfr_and_save_policy(num_iterations=5000, verbose=True):
    """
    Runs the CFR algorithm on the Patrik's Coin Game and saves the average policy.

    Parameters:
    - num_iterations (int): Number of CFR iterations.
    - verbose (bool): If True, prints progress every 100 iterations.

    Returns:
    - average_policy (Policy): The average policy after CFR.
    """
    # Load your game
    game = pyspiel.load_game("patriks_coin_game")
    
    # Wrap the game to make it turn-based (if not already)
    sequential_game = pyspiel.convert_to_turn_based(game)
    
    # Initialize CFR Solver
    cfr_solver = pyspiel.CFRSolver(sequential_game)
    
    # Initialize a nested dictionary to store action probabilities for all players
    num_players = sequential_game.num_players()
    action_prob_history = {
        player: {f"Action(id={i}, player={player})": [] for i in range(sequential_game.action_size(player))}
        for player in range(num_players)
    }

    
    for i in range(1, num_iterations + 1):
        cfr_solver.evaluate_and_update_policy()
    
        # Get the current average policy
        current_policy = cfr_solver.average_policy()
    
        # Traverse the initial state to get action probabilities for all players
        initial_state = sequential_game.new_initial_state()
        
        # Function to traverse states and collect action probabilities
        def traverse_collect(state):
            if state.is_terminal():
                return
            
            player = state.current_player()
            if player == pyspiel.PlayerId.TERMINAL:
                return
            
            action_probs = current_policy.action_probabilities(state)
            for action, prob in action_probs.items():
                action_name = sequential_game.action_to_string(player, action)
                key = f"Action(id={action}, player={player})"
                if key in action_prob_history[player]:
                    action_prob_history[player][key].append(prob)
                else:
                    # Handle unexpected actions if any
                    action_prob_history[player][key] = [prob]
            
            for action in state.legal_actions():
                child_state = state.child(action)
                traverse_collect(child_state)
        
        traverse_collect(initial_state)
    
        if verbose and (i % 100 == 0 or i == 1):
            print(f"Iteration {i} completed")
    
    # Save the action probability history to JSON
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, "../data")
    os.makedirs(output_dir, exist_ok=True)
    history_path = os.path.join(output_dir, "action_prob_history_all_players.json")
    
    with open(history_path, "w") as f:
        json.dump(action_prob_history, f, indent=4)
    
    print(f"Action probability history saved to {history_path}")
    
    # Return the average policy for further use
    return cfr_solver.average_policy()
def calculate_expected_utilities(average_policy):
    """
    Traverses the game tree using the average policy to calculate expected utilities for both players.

    Parameters:
    - average_policy (Policy): The average policy obtained from CFR.

    Returns:
    - expected_utility_player_0 (float): Expected utility for Player 0.
    - expected_utility_player_1 (float): Expected utility for Player 1.
    """
    # Load your game
    game = pyspiel.load_game("patriks_coin_game")
    
    # Wrap the game to make it turn-based (if not already)
    sequential_game = pyspiel.convert_to_turn_based(game)
    
    initial_state = sequential_game.new_initial_state()
    
    expected_utility_player_0 = 0.0
    expected_utility_player_1 = 0.0
    
    # Initialize a set to keep track of visited information states
    visited_states = set()
    
    # Prepare data structure to save results as a list of states
    results = []
    
    # Function to parse info_state string into the desired dictionary format
    def parse_info_state(info_state):
        parsed_info = {}
        for line in info_state.split('\n'):
            if not line.strip():
                continue  # Skip empty lines
            try:
                key, value = line.split(':', 1)
                key, value = key.strip(), value.strip()
            except ValueError:
                # Handle lines that do not contain a colon
                continue
    
            if key == "player":
                parsed_info["player"] = int(value)
            elif key == "round":
                parsed_info["round"] = int(value)
            elif key == "estimator_guesses":
                parsed_info["estimator_guesses"] = tuple(map(int, value.split())) if value else ()
            elif key == "coin_player_choices":
                parsed_info["coin_player_choices"] = tuple(map(int, value.split())) if value else ()
            elif key == "depth":
                parsed_info["depth"] = int(value)
        return parsed_info
    
    # Recursive traversal function
    def traverse(state, probability=1.0, utility_player_0=0.0, utility_player_1=0.0, depth=0):
        nonlocal expected_utility_player_0, expected_utility_player_1
        
        if state.is_terminal():
            returns = state.returns()
            # Assuming returns[0] is for Player 0 and returns[1] for Player 1
            expected_utility_player_0 += probability * returns[0]
            expected_utility_player_1 += probability * returns[1]
            return
        
        player = state.current_player()
        if player == pyspiel.PlayerId.TERMINAL:
            return
        
        info_state = state.information_state_string(player)
        
        # Check if this state has already been visited with the same path
        # To prevent infinite recursion in cyclic games
        state_id = (info_state, depth)
        if state_id in visited_states:
            return
        visited_states.add(state_id)
        
        # Parse the info state
        info_state_dict = parse_info_state(info_state)
        info_state_dict["depth"] = depth
        
        # Get action probabilities from the average policy
        action_probs = average_policy.action_probabilities(state)
        
        # Prepare data for saving (optional)
        state_data = {
            **info_state_dict,  # include parsed info state details with depth
            "actions": {sequential_game.action_to_string(player, action): prob for action, prob in action_probs.items()}
        }
        results.append(state_data)
        
        # Traverse each action
        for action, prob in action_probs.items():
            cloned_state = state.clone()
            cloned_state.apply_action(action)
            traverse(cloned_state, probability * prob, utility_player_0, utility_player_1, depth + 1)
    
    traverse(initial_state)
    
    # Save the complete game tree with parsed information states
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, "../data")
    os.makedirs(output_dir, exist_ok=True)
    tree_output_path = os.path.join(output_dir, "complete_game_tree_results.json")
    
    with open(tree_output_path, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"Complete game tree results saved to {tree_output_path}")
    
    return expected_utility_player_0, expected_utility_player_1

def plot_cfr_action_evolution(history_json_path, output_plot_path):
    """
    Plots the evolution of action probabilities over CFR iterations.

    Parameters:
    - history_json_path (str): Path to the action_prob_history_all_players.json file.
    - output_plot_path (str): Path where the plot image will be saved.
    """
    # Load the action probability history from JSON
    try:
        with open(history_json_path, "r") as f:
            action_prob_history = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {history_json_path} does not exist.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file {history_json_path} is not a valid JSON.")
        return

    # Determine the number of iterations from one of the actions
    num_iterations = None
    for player, actions in action_prob_history.items():
        for action, probs in actions.items():
            num_iterations = len(probs)
            break
        if num_iterations is not None:
            break

    if num_iterations is None:
        print("Error: No action probabilities found in the JSON.")
        return

    iterations = list(range(1, num_iterations + 1))

    plt.figure(figsize=(14, 10))

    # Assign different colors for different players
    colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown']
    color_map = {}
    color_idx = 0

    for player, actions in action_prob_history.items():
        for action, probs in actions.items():
            action_label = f"P{player}: {action}"
            if action_label not in color_map:
                color_map[action_label] = colors[color_idx % len(colors)]
                color_idx += 1
            plt.plot(iterations, probs, label=action_label, color=color_map[action_label])

    plt.xscale('log')
    plt.xlabel("Iterations")
    plt.ylabel("Probability")
    plt.title("Evolution of Action Probabilities over CFR Iterations")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the plot to the specified path
    plt.savefig(output_plot_path)
    plt.close()
    print(f"Plot saved to {output_plot_path}")

def main():
    # Step 1: Run CFR and obtain the average policy
    average_policy = run_cfr_and_save_policy(num_iterations=5000, verbose=True)
    
    # Step 2: Calculate expected utilities for both players
    expected_utility_player_0, expected_utility_player_1 = calculate_expected_utilities(average_policy)
    
    print(f"Expected Utility for Player 0: {expected_utility_player_0}")
    print(f"Expected Utility for Player 1: {expected_utility_player_1}")
    
    # Step 3: Plot the evolution of action probabilities
    current_dir = os.path.dirname(os.path.abspath(__file__))
    history_json_path = os.path.join(current_dir, "../data/action_prob_history_all_players.json")
    output_plot_path = os.path.join(current_dir, "../plots/action_prob_evolution_all_players.png")
    
    os.makedirs(os.path.dirname(output_plot_path), exist_ok=True)
    
    plot_cfr_action_evolution(history_json_path, output_plot_path)

if __name__ == "__main__":
    main()
