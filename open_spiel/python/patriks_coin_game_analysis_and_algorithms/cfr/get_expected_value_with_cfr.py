import pyspiel
import json
import os
from itertools import product

# Load your game
game = pyspiel.load_game("patriks_coin_game")

# Wrap the game to make it sequential
sequential_game = pyspiel.convert_to_turn_based(game)

# Initialize CFR Solver
cfr_solver = pyspiel.CFRSolver(sequential_game)
num_iterations = 1000

# Run CFR for num_iterations
for i in range(num_iterations):
    cfr_solver.evaluate_and_update_policy()
    if i % 100 == 0:
        print(f"Iteration {i}")

# Get the average policy
average_policy = cfr_solver.average_policy()

# Now compute the expected value for both players under the average policy
def expected_value(state, policy):
    """Recursively compute expected value from state under policy."""
    if state.is_terminal():
        returns = state.returns()
        return returns
    elif state.is_chance_node():
        outcomes = state.chance_outcomes()
        expected_returns = [0.0] * state.num_players()
        for action, prob in outcomes:
            child_state = state.child(action)
            child_returns = expected_value(child_state, policy)
            for i in range(state.num_players()):
                expected_returns[i] += prob * child_returns[i]
        return expected_returns
    elif state.is_simultaneous_node():
        # Handle simultaneous move nodes
        action_probabilities = []
        legal_actions_list = []
        for player in range(state.num_players()):
            info_state = state.information_state_string(player)
            action_probs = policy.action_probabilities(info_state)
            action_probabilities.append(action_probs)
            legal_actions_list.append(list(action_probs.keys()))
        expected_returns = [0.0] * state.num_players()
        # Iterate over all possible joint actions
        for joint_actions in product(*legal_actions_list):
            joint_prob = 1.0
            for idx, action in enumerate(joint_actions):
                joint_prob *= action_probabilities[idx][action]
            child_state = state.child(joint_actions)
            child_returns = expected_value(child_state, policy)
            for i in range(state.num_players()):
                expected_returns[i] += joint_prob * child_returns[i]
        return expected_returns
    else:
        current_player = state.current_player()
        action_probs = policy.action_probabilities(state)
        expected_returns = [0.0] * state.num_players()
        for action, prob in action_probs.items():
            child_state = state.child(action)
            child_returns = expected_value(child_state, policy)
            for i in range(state.num_players()):
                expected_returns[i] += prob * child_returns[i]
        return expected_returns

root_state = sequential_game.new_initial_state()
expected_returns = expected_value(root_state, average_policy)
print("Expected returns:", expected_returns)

# Collect the policies
def traverse_and_collect_policies(state, policy, policies):
    if state.is_terminal():
        return
    elif state.is_chance_node():
        for action, _ in state.chance_outcomes():
            child_state = state.child(action)
            traverse_and_collect_policies(child_state, policy, policies)
    elif state.is_simultaneous_node():
        for player in range(state.num_players()):
            info_state = state.information_state_string(player)
            if info_state not in policies:
                action_probs = policy.action_probabilities(info_state)
                action_probs_serializable = {str(action): prob for action, prob in action_probs.items()}
                policies[info_state] = action_probs_serializable
        legal_actions_list = []
        for player in range(state.num_players()):
            legal_actions_list.append(state.legal_actions(player))
        for joint_actions in product(*legal_actions_list):
            child_state = state.child(joint_actions)
            traverse_and_collect_policies(child_state, policy, policies)
    else:
        current_player = state.current_player()
        info_state = state.information_state_string(current_player)
        if info_state not in policies:
            action_probs = policy.action_probabilities(state)
            action_probs_serializable = {str(action): prob for action, prob in action_probs.items()}
            policies[info_state] = action_probs_serializable
        for action in state.legal_actions():
            child_state = state.child(action)
            traverse_and_collect_policies(child_state, policy, policies)

policies = {}
traverse_and_collect_policies(root_state, average_policy, policies)

# Save outputs
current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, "../data")
os.makedirs(output_dir, exist_ok=True)
expected_value_path = os.path.join(output_dir, "expected_value.json")
game_policy_path = os.path.join(output_dir, "game_policy.json")

# Save expected returns
with open(expected_value_path, 'w') as f:
    json.dump({'expected_returns': expected_returns}, f)

# Save policies
with open(game_policy_path, 'w') as f:
    json.dump(policies, f)