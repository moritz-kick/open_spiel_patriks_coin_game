#ifndef OPEN_SPIEL_GAMES_PATRIKS_COIN_GAME_H_
#define OPEN_SPIEL_GAMES_PATRIKS_COIN_GAME_H_

#include <memory>
#include <string>
#include <vector>
#include "open_spiel/spiel.h"

namespace open_spiel {
namespace patriks_coin_game {

class PatriksCoinGame;

/**
 * @brief Represents the state of Patrik's Coin Game.
 */
class PatriksCoinGameState : public State {
 public:
  explicit PatriksCoinGameState(std::shared_ptr<const Game> game);

  // Override methods from the State base class.
  Player CurrentPlayer() const override;
  std::string ActionToString(Player player, Action action_id) const override;
  std::string ToString() const override;
  bool IsTerminal() const override;
  std::vector<double> Returns() const override;
  std::vector<double> Rewards() const override;
  std::string InformationStateString(Player player) const override;
  void InformationStateTensor(Player player, std::vector<float>* values) const override;
  std::unique_ptr<State> Clone() const override;

  std::vector<Action> LegalActions() const override;
  std::vector<Action> LegalActions(Player player) const override;

 protected:
  void DoApplyAction(Action action) override;
  void DoApplyActions(const std::vector<Action>& actions) override;

 private:
  int num_rounds_played_;
  std::vector<int> coin_player_choices_;
  std::vector<int> estimator_guesses_;
  bool estimator_won_;
  bool coin_player_used_zero_;
  int last_non_zero_choice_;
};

/**
 * @brief Defines the game Patrik's Coin Game.
 */
class PatriksCoinGame : public Game {
 public:
  explicit PatriksCoinGame(const GameParameters& params);
  int NumDistinctActions() const override { return 6; }
  std::unique_ptr<State> NewInitialState() const override;
  int NumPlayers() const override { return 2; }
  double MinUtility() const override { return -1; }
  double MaxUtility() const override { return 1; }
  int MaxGameLength() const override { return 6; }  // 3 rounds * 2 actions per round
  absl::optional<double> UtilitySum() const override { return 0.0; }
};

}  // namespace patriks_coin_game
}  // namespace open_spiel

#endif  // OPEN_SPIEL_GAMES_PATRIKS_COIN_GAME_H_