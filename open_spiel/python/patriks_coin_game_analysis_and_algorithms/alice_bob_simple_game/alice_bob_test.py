import pyspiel
from open_spiel.python import rl_environment
from open_spiel.python.algorithms import policy_gradient

game = pyspiel.load_game("alice_bob_guessing_game")
env = rl_environment.Environment(game)
agent = policy_gradient.PolicyGradient(
    session,
    player_id=0,
    info_state_size=env.observation_spec()["info_state"][0].shape[0],
    num_actions=env.action_spec()["num_actions"],
    loss_str="a2c",
    hidden_layers_sizes=(128,),
    batch_size=16,
    entropy_cost=0.01,
    critic_learning_rate=0.01,
    pi_learning_rate=0.001,
    num_critic_before_pi=8,
    additional_discount_factor=1.0,
    max_global_gradient_norm=None,
    optimizer_str="sgd")