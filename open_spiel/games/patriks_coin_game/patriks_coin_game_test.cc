#include "open_spiel/spiel.h"
#include "open_spiel/tests/basic_tests.h"

namespace open_spiel {
namespace patriks_coin_game {
namespace {

namespace testing = open_spiel::testing;

void BasicPatriksCoinGameTests() {
  testing::LoadGameTest("patriks_coin_game");
  testing::RandomSimTest(*LoadGame("patriks_coin_game"), 50);

  auto game = LoadGame("patriks_coin_game");
  auto state = game->NewInitialState();

  // Simulate moves and print game state after each round.
  while (!state->IsTerminal()) {
    Player player = state->CurrentPlayer();
    auto legal_actions = state->LegalActions();
    Action action = legal_actions[0];
    state->ApplyAction(action);
    std::cout << state->ToString() << std::endl;
  }

  // Check terminal state
  SPIEL_CHECK_TRUE(state->IsTerminal());
  std::vector<double> returns = state->Returns();
  SPIEL_CHECK_EQ(returns.size(), 2);
}

}  // namespace
}  // namespace patriks_coin_game
}  // namespace open_spiel

int main(int argc, char** argv) {
  open_spiel::patriks_coin_game::BasicPatriksCoinGameTests();
}
