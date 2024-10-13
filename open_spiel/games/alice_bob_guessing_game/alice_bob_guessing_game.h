#ifndef OPEN_SPIEL_GAMES_ALICE_BOB_GUESSING_GAME_H_
#define OPEN_SPIEL_GAMES_ALICE_BOB_GUESSING_GAME_H_

#include <memory>
#include <string>
#include <vector>
#include "open_spiel/spiel.h"

namespace open_spiel {
namespace alice_bob_guessing_game {

class AliceBobGuessingGame;

class AliceBobGuessingGameState : public State {
 public:
  explicit AliceBobGuessingGameState(std::shared_ptr<const Game> game);

  Player CurrentPlayer() const override;
  std::vector<Action> LegalActions() const override;
  std::vector<Action> LegalActions(Player player) const override;
  std::string ActionToString(Player player, Action action_id) const override;
  void ObservationAsNormalizedVector(Player player,
                                     std::vector<double>* values) const override;

  std::string ToString() const override;
  bool IsTerminal() const override;
  std::vector<double> Returns() const override;
  std::string InformationStateString(Player player) const override;
  std::unique_ptr<State> Clone() const override;

 protected:
  void DoApplyAction(Action action_id) override;
  void DoApplyActions(const std::vector<Action>& actions) override;

 private:
  int current_stage_;  // 1 or 2
  bool bob_won_;
  bool alice_won_;
  std::vector<Action> alice_actions_;
  std::vector<Action> bob_actions_;
};

class AliceBobGuessingGame : public Game {
 public:
  explicit AliceBobGuessingGame(const GameParameters& params);
  int NumDistinctActions() const override { return 7; }
  std::unique_ptr<State> NewInitialState() const override;
  int NumPlayers() const override { return 2; }
  double MinUtility() const override { return -1; }
  double MaxUtility() const override { return 1; }
  int MaxGameLength() const override { return 2; }
  absl::optional<double> UtilitySum() const override { return 0.0; }
};

}  // namespace alice_bob_guessing_game
}  // namespace open_spiel

#endif  // OPEN_SPIEL_GAMES_ALICE_BOB_GUESSING_GAME_H_