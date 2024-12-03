import json
import os
import matplotlib.pyplot as plt

def plot_cfr_action_evolution(history_json_path, output_plot_path):
    """
    Plots the evolution of action probabilities over CFR iterations.

    Parameters:
    - history_json_path (str): Path to the action_prob_history.json file.
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

    # Ensure that all actions have the same number of iterations
    num_iterations = None
    for action, probs in action_prob_history.items():
        if num_iterations is None:
            num_iterations = len(probs)
        elif len(probs) != num_iterations:
            print(f"Error: Action '{action}' has a different number of iterations.")
            return

    if num_iterations is None:
        print("Error: No action probabilities found in the JSON.")
        return

    iterations = list(range(1, num_iterations + 1))

    plt.figure(figsize=(12, 8))

    # Plot each action's probability over iterations
    for action, probs in action_prob_history.items():
        plt.plot(iterations, probs, label=action)

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

if __name__ == "__main__":
    # Define the paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    history_json_path = os.path.join(current_dir, "../data2/action_prob_history.json")
    output_plot_path = os.path.join(current_dir, "../plots/action_prob_evolution2.png")

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_plot_path), exist_ok=True)

    # Generate the plot
    plot_cfr_action_evolution(history_json_path, output_plot_path)