#include "open_spiel/games/patriks_coin_game/patriks_coin_game.h"

namespace open_spiel
{
  namespace patriks_coin_game
  {

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
        /*provides_observation_string=*/true,
        /*provides_observation_tensor=*/false,
        /*parameter_specification=*/{}};

    std::shared_ptr<const Game> Factory(const GameParameters &params)
    {
      return std::shared_ptr<const Game>(new PatriksCoinGame(params));
    }

    REGISTER_SPIEL_GAME(kGameType, Factory);

    PatriksCoinGameState::PatriksCoinGameState(std::shared_ptr<const Game> game)
        : State(game),
          current_round_(1),
          estimator_won_(false),
          coin_player_used_zero_(false),
          last_non_zero_choice_(0) {}

    Player PatriksCoinGameState::CurrentPlayer() const
    {
      return IsTerminal() ? kTerminalPlayerId : kSimultaneousPlayerId;
    }

    std::string PatriksCoinGameState::ActionToString(Player player, Action action_id) const
    {
      return "Player " + std::to_string(player) + " chose: " + std::to_string(action_id);
    }

    std::string PatriksCoinGameState::ToString() const
    {
      std::string str = "Game State:\n";
      str += "Current Round: " + std::to_string(current_round_) + "\n";
      str += "Coin Player Choices: ";
      for (int c : coin_player_choices_)
        str += std::to_string(c) + " ";
      str += "\nEstimator Guesses: ";
      for (int g : estimator_guesses_)
        str += std::to_string(g) + " ";
      str += "\n";
      return str;
    }

    bool PatriksCoinGameState::IsTerminal() const
    {
      return estimator_won_ || current_round_ > 3;
    }

    std::vector<double> PatriksCoinGameState::Returns() const
    {
      if (estimator_won_)
        return {-1.0, 1.0};
      else if (IsTerminal())
        return {1.0, -1.0};
      else
        return {0.0, 0.0};
    }

    std::string PatriksCoinGameState::InformationStateString(Player player) const
    {
      std::string info = "Round: " + std::to_string(current_round_) + "\n";
      if (player == 0)
      {
        info += "Coin Player Choices: ";
        for (int c : coin_player_choices_)
          info += std::to_string(c) + " ";
        info += "\nEstimator Guesses: ";
        for (int g : estimator_guesses_)
          info += std::to_string(g) + " ";
      }
      else if (player == 1)
      {
        info += "Estimator Guesses: ";
        for (int g : estimator_guesses_)
          info += std::to_string(g) + " ";
        info += "\nCoin Player Choices: ";
        for (int c : coin_player_choices_)
          info += std::to_string(c) + " ";
      }
      return info;
    }

    std::unique_ptr<State> PatriksCoinGameState::Clone() const
    {
      return std::unique_ptr<State>(new PatriksCoinGameState(*this));
    }

  std::vector<Action> PatriksCoinGameState::LegalActions(Player player) const {
    if (IsTerminal()) return {};

    if (player == 0) {  // Coin Player
      std::vector<Action> actions;
      int start = 1;

      // If it's the first round, start at 1
      if (current_round_ == 1) {
        start = 1;
      } else if (coin_player_used_zero_ && last_non_zero_choice_ > 0) {
        // After using zero, the player continues from the last non-zero choice
        start = last_non_zero_choice_ + 1;
      } else if (!coin_player_used_zero_) {
        // If 0 has not been used, start from the last non-zero choice + 1
        start = last_non_zero_choice_ + 1;
      }

      // Allow 5 if last choice was 5, otherwise allow from 'start' to 5
      for (int i = start; i <= 5; ++i) {
        actions.push_back(i);
      }

      // Add 0 as an option if it hasn't been used yet
      if (!coin_player_used_zero_) {
        actions.push_back(0);
      }

      return actions;
    } else if (player == 1) {  // Estimator
      return {0, 1, 2, 3, 4, 5};  // Estimator guesses from 0 to 5
    } else {
      SpielFatalError("Invalid player.");
    }
  }

    void PatriksCoinGameState::DoApplyActions(const std::vector<Action> &actions)
    {
      SPIEL_CHECK_EQ(actions.size(), 2);
      int coin_choice = actions[0];
      int estimator_guess = actions[1];

      // Update histories
      coin_player_choices_.push_back(coin_choice);
      estimator_guesses_.push_back(estimator_guess);

      // Check if the estimator has guessed correctly
      if (coin_choice == estimator_guess)
        estimator_won_ = true;

      if (coin_choice != 0)
      {
        if (current_round_ > 1 && last_non_zero_choice_ != 0 && coin_choice != 5)
          SPIEL_CHECK_GT(coin_choice, last_non_zero_choice_);
        last_non_zero_choice_ = coin_choice; // Update last non-zero choice
      }
      else
      {
        // If 0 is chosen, enforce it's only once
        SPIEL_CHECK_FALSE(coin_player_used_zero_);
        coin_player_used_zero_ = true;
      }

      current_round_++;
    }

    PatriksCoinGame::PatriksCoinGame(const GameParameters &params)
        : Game(kGameType, params) {}

    std::unique_ptr<State> PatriksCoinGame::NewInitialState() const
    {
      return std::unique_ptr<State>(new PatriksCoinGameState(shared_from_this()));
    }

  } // namespace patriks_coin_game
} // namespace open_spiel
