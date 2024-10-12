import pyspiel
import json
import os

# Load your game
game = pyspiel.load_game("patriks_coin_game")

# Wrap the game to make it sequential
sequential_game = pyspiel.convert_to_turn_based(game)

# Initialize CFR Solver
cfr_solver = pyspiel.CFRSolver(sequential_game)
num_iterations = 1000

# Initialize a dictionary to store action probabilities over iterations
action_prob_history = {f"Player 0 chose: {i}": [] for i in range(6)}  # Assuming 6 choices: 0-5

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

    if i % 100 == 0 or i == 1:
        print(f"Iteration {i} completed")

# Get the average policy after CFR
average_policy = cfr_solver.average_policy()

# Prepare data structure to save results as a list of states
results = []

# Initialize a set to keep track of visited information states
visited_states = set()

# Function to parse info_state string into the desired dictionary format
def parse_info_state(info_state):
    parsed_info = {}
    for line in info_state.split('\n'):
        key, value = line.split(':', 1)
        key, value = key.strip(), value.strip()

        if key == "Current player":
            parsed_info["player"] = int(value)
        elif key == "Round":
            parsed_info["round"] = int(value)
        elif key == "Estimator Guesses":
            parsed_info["estimator_guesses"] = tuple(map(int, value.split())) if value else ()
        elif key == "Coin Player Choices":
            parsed_info["coin_player_choices"] = tuple(map(int, value.split())) if value else ()
    return parsed_info

# Modified traverse function with duplicate prevention
def traverse(state, average_policy, depth=0):
    if state.is_terminal():
        return

    # Parse the info state
    player = state.current_player()
    info_state = state.information_state_string(player)

    # Check if this state has already been visited
    if info_state in visited_states:
        return  # Skip to prevent duplication

    # Mark this state as visited
    visited_states.add(info_state)

    info_state_dict = parse_info_state(info_state)

    # Add depth to the parsed information
    info_state_dict["depth"] = depth

    # Get action probabilities for the state
    action_probs = average_policy.action_probabilities(state)

    # Prepare data for saving
    state_data = {
        **info_state_dict,  # include parsed info state details with depth
        "actions": {state.action_to_string(player, action): prob for action, prob in action_probs.items()}
    }

    # Append state data to the results list
    results.append(state_data)

    # Traverse legal actions
    for action in state.legal_actions():
        cloned_state = state.clone()
        cloned_state.apply_action(action)
        traverse(cloned_state, average_policy, depth + 1)

# Start traversing from the initial state
initial_state = sequential_game.new_initial_state()
traverse(initial_state, average_policy)

# Get absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define output path
output_dir = os.path.join(current_dir, "../data")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "game_tree_results.json")

# Save results to JSON
with open(output_path, "w") as f:
    json.dump(results, f, indent=4)

print(f"Game tree results saved to {output_path}")