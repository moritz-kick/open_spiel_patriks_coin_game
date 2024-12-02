#include "open_spiel/games/patriks_coin_game/patriks_coin_game.h"

#include <algorithm>  // For std::sort

namespace open_spiel {
namespace patriks_coin_game {

const GameType kGameType{
    /*short_name=*/"patriks_coin_game",
    /*long_name=*/"Patrik's Coin Game",
    GameType::Dynamics::kSimultaneous,
    GameType::ChanceMode::kDeterministic,
    GameType::Information::kImperfectInformation,
    GameType::Utility::kZeroSum,
    GameType::RewardModel::kTerminal,
    /*max_num_players=*/2,
    /*min_num_players=*/2,
    /*provides_information_state_string=*/true,
    /*provides_information_state_tensor=*/false,
    /*provides_observation_string=*/false,
    /*provides_observation_tensor=*/false,
    /*parameter_specification=*/{}};

// Factory function to create a new instance of the game.
std::shared_ptr<const Game> Factory(const GameParameters& params) {
  return std::shared_ptr<const Game>(new PatriksCoinGame(params));
}

// Register the game with OpenSpiel.
REGISTER_SPIEL_GAME(kGameType, Factory);

// Constructor for PatriksCoinGameState.
PatriksCoinGameState::PatriksCoinGameState(std::shared_ptr<const Game> game)
    : State(game),
      num_rounds_played_(0),
      estimator_won_(false),
      coin_player_used_zero_(false),
      last_non_zero_choice_(0) {}

// Determine the current player. Returns terminal player if the game is over.
Player PatriksCoinGameState::CurrentPlayer() const {
  return IsTerminal() ? kTerminalPlayerId : kSimultaneousPlayerId;
}

// Get legal actions for the current player.
std::vector<Action> PatriksCoinGameState::LegalActions() const {
  return LegalActions(CurrentPlayer());
}

// Get legal actions for a specific player.
std::vector<Action> PatriksCoinGameState::LegalActions(Player player) const {
  if (IsTerminal()) return {};

  if (player == 0) {  // Coin Player
    std::vector<Action> actions;
    int start = 1;

    // Determine start based on the game state
    if (num_rounds_played_ == 0) {
      start = 1;
    } else {
      if (last_non_zero_choice_ == 5) {
        start = 5;  // Allow 5 again
      } else {
        start = last_non_zero_choice_ + 1;
      }
    }

    // Add 0 as an option if it hasn't been used yet
    if (!coin_player_used_zero_) {
      actions.push_back(0);
    }

    // Allow choices from 'start' to 5
    for (int i = start; i <= 5; ++i) {
      actions.push_back(i);
    }

    // Ensure the actions are sorted
    std::sort(actions.begin(), actions.end());

    return actions;
  } else if (player == 1) {  // Estimator
    return {0, 1, 2, 3, 4, 5};  // Estimator guesses from 0 to 5
  } else {
    SpielFatalError("Invalid player.");
  }
}

void PatriksCoinGameState::DoApplyAction(Action action) {
  // Since this is a simultaneous-move game, this method should not be called.
  SpielFatalError("DoApplyAction should not be called in a simultaneous-move game.");
}

// Apply actions for both players simultaneously.
void PatriksCoinGameState::DoApplyActions(const std::vector<Action>& actions) {
  SPIEL_CHECK_EQ(actions.size(), 2);
  int coin_choice = actions[0];
  int estimator_guess = actions[1];

  // Update histories
  coin_player_choices_.push_back(coin_choice);
  estimator_guesses_.push_back(estimator_guess);

  // Check if the estimator has guessed correctly
  if (coin_choice == estimator_guess)
    estimator_won_ = true;

  if (coin_choice != 0) {
    if (num_rounds_played_ > 0 && last_non_zero_choice_ != 0 && coin_choice != 5)
      SPIEL_CHECK_GT(coin_choice, last_non_zero_choice_);
    last_non_zero_choice_ = coin_choice;  // Update last non-zero choice
  } else {
    // If 0 is chosen, enforce it's only once
    SPIEL_CHECK_FALSE(coin_player_used_zero_);
    coin_player_used_zero_ = true;
  }

  num_rounds_played_++;  // Increment after actions are applied
}

// Convert an action to a string representation.
std::string PatriksCoinGameState::ActionToString(Player player, Action action_id) const {
  return "Player " + std::to_string(player) + " chose: " + std::to_string(action_id);
}

// Convert the current state to a string representation.
std::string PatriksCoinGameState::ToString() const {
  std::string str = "Game State:\n";
  str += "Current Round: " + std::to_string(num_rounds_played_ + 1) + "\n";
  str += "Coin Player Choices: ";
  for (int c : coin_player_choices_)
    str += std::to_string(c) + " ";
  str += "\nEstimator Guesses: ";
  for (int g : estimator_guesses_)
    str += std::to_string(g) + " ";
  str += "\n";
  return str;
}

// Check if the game has reached a terminal state.
bool PatriksCoinGameState::IsTerminal() const {
  return estimator_won_ || num_rounds_played_ >= 3;
}

// Get the returns for each player at a terminal state.
std::vector<double> PatriksCoinGameState::Returns() const {
  std::vector<double> returns;
  if (estimator_won_) {
    returns = {-1, 1};
  } else if (IsTerminal()) {
    returns = {1, -1};
  } else {
    returns = {0, 0};
  }
  return returns;
}

// Get the rewards for each player at the current state.
std::vector<double> PatriksCoinGameState::Rewards() const {
  std::vector<double> rewards;
  if (IsTerminal()) {
    rewards = Returns();
  } else {
    rewards = std::vector<double>(NumPlayers(), 0);
  }
  std::cout << "Rewards called: " << rewards[0] << ", " << rewards[1] << std::endl;
  return rewards;
}

// Get the information state string for a player.
std::string PatriksCoinGameState::InformationStateString(Player player) const {
  if (player < 0 || player >= NumPlayers()) {
    SpielFatalError("Player index out of bounds: player >= 0 and player < NumPlayers().");
  }
  std::string info = "Round: " + std::to_string(num_rounds_played_ + 1) + "\n";
  if (player == 0) {
    info += "Coin Player Choices: ";
    for (int c : coin_player_choices_)
      info += std::to_string(c) + " ";
    info += "\nEstimator Guesses: ";
    for (int g : estimator_guesses_)
      info += std::to_string(g) + " ";
  } else if (player == 1) {
    info += "Estimator Guesses: ";
    for (int g : estimator_guesses_)
      info += std::to_string(g) + " ";
    info += "\nCoin Player Choices: ";
    for (int c : coin_player_choices_)
      info += std::to_string(c) + " ";
  }
  return info;
}

// Clone the current state.
std::unique_ptr<State> PatriksCoinGameState::Clone() const {
  return std::unique_ptr<State>(new PatriksCoinGameState(*this));
}

// Constructor for PatriksCoinGame.
PatriksCoinGame::PatriksCoinGame(const GameParameters& params)
    : Game(kGameType, params) {}

// Create a new initial state for the game.
std::unique_ptr<State> PatriksCoinGame::NewInitialState() const {
  return std::unique_ptr<State>(new PatriksCoinGameState(shared_from_this()));
}

}  // namespace patriks_coin_game
}  // namespace open_spiel