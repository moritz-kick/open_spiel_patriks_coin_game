#ifndef OPEN_SPIEL_GAMES_PATRIKS_COIN_GAME_H_
#define OPEN_SPIEL_GAMES_PATRIKS_COIN_GAME_H_

#include <memory>
#include <string>
#include <vector>
#include "open_spiel/spiel.h"

namespace open_spiel {
namespace patriks_coin_game {

class PatriksCoinGame;

class PatriksCoinGameState : public State {
 public:
  explicit PatriksCoinGameState(std::shared_ptr<const Game> game);

  Player CurrentPlayer() const override;
  std::string ActionToString(Player player, Action action_id) const override;
  std::string ToString() const override;
  bool IsTerminal() const override;
  std::vector<double> Returns() const override;
  std::string InformationStateString(Player player) const override;
  std::unique_ptr<State> Clone() const override;
  std::vector<Action> LegalActions() const override;
  std::vector<Action> LegalActions(Player player) const;

 protected:
  void DoApplyActions(const std::vector<Action>& actions) override;

 private:
  int current_round_;
  std::vector<int> coin_player_choices_;
  std::vector<int> estimator_guesses_;
  bool estimator_won_;
  bool coin_player_used_zero_;
  int last_non_zero_choice_;
};

class PatriksCoinGame : public Game {
 public:
  explicit PatriksCoinGame(const GameParameters& params);
  int NumDistinctActions() const override { return 6; }
  std::unique_ptr<State> NewInitialState() const override;
  int NumPlayers() const override { return 2; }
  double MinUtility() const override { return -1; }
  double MaxUtility() const override { return 1; }
  int MaxGameLength() const override { return 3; }
};

}  // namespace patriks_coin_game
}  // namespace open_spiel

#endif  // OPEN_SPIEL_GAMES_PATRIKS_COIN_GAME_H_
