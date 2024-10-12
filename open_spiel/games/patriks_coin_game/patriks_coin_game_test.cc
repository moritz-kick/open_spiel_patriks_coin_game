#include "open_spiel/spiel.h"
#include "open_spiel/tests/basic_tests.h"
#include <iostream>

namespace open_spiel {
namespace patriks_coin_game {
namespace {

// Alias for testing namespace
namespace testing = open_spiel::testing;

void BasicPatriksCoinGameTests() {
  // Load the game and run basic OpenSpiel tests
  testing::LoadGameTest("patriks_coin_game");
  testing::RandomSimTest(*LoadGame("patriks_coin_game"), 50);

  // Specific tests for Patrik's Coin Game
  auto game = LoadGame("patriks_coin_game");
  auto state = game->NewInitialState();

  // Check that initial legal actions are correct for each player
  std::cout << "Checking legal actions for each player..." << std::endl;
  auto coin_player_actions = state->LegalActions(0);  // Coin Player
  auto estimator_actions = state->LegalActions(1);  // Estimator
  SPIEL_CHECK_TRUE(std::is_sorted(coin_player_actions.begin(), coin_player_actions.end()));
  SPIEL_CHECK_TRUE(std::is_sorted(estimator_actions.begin(), estimator_actions.end()));

  // Simulate moves and print game state after each round
  std::cout << "Simulating game moves..." << std::endl;
  while (!state->IsTerminal()) {
    // Ensure the game is in a simultaneous-move state
    Player current_player = state->CurrentPlayer();
    SPIEL_CHECK_EQ(current_player, kSimultaneousPlayerId);

    // Collect actions from both players
    std::vector<Action> joint_actions;
    for (Player player = 0; player < game->NumPlayers(); ++player) {
      auto legal_actions = state->LegalActions(player);
      SPIEL_CHECK_FALSE(legal_actions.empty());
      Action action = legal_actions[0];  // Choose the first legal action
      joint_actions.push_back(action);
      std::cout << "Player " << player << " chooses action: " << action << std::endl;
    }

    // Apply both actions simultaneously
    state->ApplyActions(joint_actions);
    std::cout << state->ToString() << std::endl;
  }

  // Check terminal state and ensure returns are correctly calculated
  SPIEL_CHECK_TRUE(state->IsTerminal());
  std::vector<double> returns = state->Returns();
  SPIEL_CHECK_EQ(returns.size(), 2);

  // Verifying returns align with the win/loss rules
  if (returns[0] == 1.0) {
    SPIEL_CHECK_FLOAT_EQ(returns[1], -1.0);
  } else if (returns[0] == -1.0) {
    SPIEL_CHECK_FLOAT_EQ(returns[1], 1.0);
  } else {
    SPIEL_CHECK_FLOAT_EQ(returns[0], 0.0);
    SPIEL_CHECK_FLOAT_EQ(returns[1], 0.0);
  }



  std::cout << "All tests passed for Patrik's Coin Game!" << std::endl;
}

}  // namespace
}  // namespace patriks_coin_game
}  // namespace open_spiel

int main(int argc, char** argv) {
  open_spiel::patriks_coin_game::BasicPatriksCoinGameTests();
}