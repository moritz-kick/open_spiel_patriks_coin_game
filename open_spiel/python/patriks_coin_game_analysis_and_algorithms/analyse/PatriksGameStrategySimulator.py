import random
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd

strategies = [
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

class PatriksGame:
    def __init__(self):
        self.coins = [0, 1, 2, 3, 4, 5]
    def rand(self, min, max):
        return random.randint(min, max)
    def play_rule_based(self):
        round1 = self.rand(0, 5)
        is_zero = (round1 == 0)
        is_five = (round1 == 5)
        if is_zero:
            round2 = self.rand(1, 5)
        elif is_five:
            round2 = self.rand(0, 1) * 5
        else:
            round2 = self.rand(0, 5)
            while round2 <= round1 and round2 != 0:
                round2 = self.rand(0, 5)
        is_zero = (round1 == 0 or round2 == 0)
        is_five = (round1 == 5 or round2 == 5)
            
        if is_five and is_zero:
            round3 = 5
        elif is_five and not is_zero:
            round3 = self.rand(0, 1) * 5
        elif is_zero:
            round3 = self.rand(1, 5)
            last_non_zero = max(round1, round2)
            while round3 <= last_non_zero:
                round3 = self.rand(0, 5)
        else:
            round3 = self.rand(0, 5)
            while round3 <= round2 and round3 != 0:
                round3 = self.rand(0, 5)
        return [round1, round2, round3]

def play_games(num_games):
    game = PatriksGame()
    strategy_counts = {strategy: 0 for strategy in strategies}
    
    for _ in tqdm(range(num_games), desc="Simulating games"):
        result = tuple(game.play_rule_based())
        if result in strategy_counts:
            strategy_counts[result] += 1
    
    return strategy_counts

def verify_strategies(num_games=1000):
    strategy_counts = play_games(num_games)
    
    all_strategies_occurred = all(count > 0 for count in strategy_counts.values())
    
    total_games = sum(strategy_counts.values())
    probabilities = {strategy: count / total_games for strategy, count in strategy_counts.items()}
    
    return all_strategies_occurred, probabilities

def calculate_probabilities(num_games=1000000):
    return play_games(num_games)

def plot_probabilities(probabilities):
    total_games = sum(probabilities.values())
    probabilities = {strategy: count / total_games for strategy, count in probabilities.items()}
    
    strategies_sorted = sorted(probabilities, key=probabilities.get, reverse=True)
    probs_sorted = [probabilities[s] for s in strategies_sorted]
    
    plt.figure(figsize=(15, 10))
    plt.bar(range(len(probs_sorted)), probs_sorted)
    plt.xlabel('Strategies')
    plt.ylabel('Probability')
    plt.title('Probabilities of Strategies in Patrik\'s Game')
    plt.xticks(range(len(probs_sorted)), [str(s) for s in strategies_sorted], rotation=90)
    plt.tight_layout()
    plt.savefig('strategy_probabilities.png')
    plt.close()

    # save probabilities to pd dataframe
    df = pd.DataFrame()
    df['Strategy'] = strategies_sorted
    df['Probability'] = probs_sorted
    df.to_csv('strategy_probabilities.csv', index=False)


if __name__ == '__main__':
    print("Verifying strategies...")
    all_occurred, initial_probs = verify_strategies()
    print(f"All strategies occurred: {all_occurred}")
    
    print("\nCalculating exact probabilities...")
    accurate_probs = calculate_probabilities()
    
    print("\nPlotting the probabilities...")
    plot_probabilities(accurate_probs)
    
    print("Done! Results have been saved in 'strategy_probabilities.png'.")