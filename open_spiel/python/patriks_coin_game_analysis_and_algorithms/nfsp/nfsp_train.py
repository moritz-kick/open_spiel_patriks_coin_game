import os
import json
import numpy as np
import tensorflow.compat.v1 as tf
import pyspiel

from open_spiel.python import rl_agent
from open_spiel.python.algorithms import nfsp
from open_spiel.python.algorithms import exploitability
from open_spiel.python import rl_environment
from open_spiel.python.simple_nets import MLP
from absl import app, flags, logging

FLAGS = flags.FLAGS

flags.DEFINE_integer("num_train_episodes", int(3e6),
                     "Number of training episodes.")
flags.DEFINE_integer("eval_every", 10000,
                     "Episode frequency at which the agents are evaluated.")
flags.DEFINE_list("hidden_layers_sizes", ["128"],
                  "Number of hidden units in the avg-net and Q-net.")
flags.DEFINE_integer("replay_buffer_capacity", int(2e5),
                     "Size of the replay buffer.")
flags.DEFINE_integer("reservoir_buffer_capacity", int(2e6),
                     "Size of the reservoir buffer.")
flags.DEFINE_float("anticipatory_param", 0.1,
                   "Prob of using the rl best response as episode policy.")
flags.DEFINE_string("output_dir", "../data",
                    "Directory to save the game tree results.")


class NFSPPolicies(pyspiel.Policy):
    """Joint policy to be evaluated."""

    def __init__(self, env, nfsp_policies, mode):
        game = env.game
        player_ids = list(range(game.num_players()))
        super(NFSPPolicies, self).__init__(game, player_ids)
        self._policies = nfsp_policies
        self._mode = mode
        self._obs = {"info_state": [None for _ in player_ids],
                    "legal_actions": [None for _ in player_ids],
                    "current_player": None}

    def action_probabilities(self, state, player_id=None):
        if state.is_terminal():
            return {}
        if player_id is None:
            player_id = state.current_player()
        if player_id == pyspiel.PlayerId.CHANCE:
            return {}
        
        self._obs["current_player"] = player_id
        self._obs["info_state"][player_id] = state.information_state_tensor(player_id)
        self._obs["legal_actions"][player_id] = state.legal_actions(player_id)

        # Create a dummy TimeStep object
        timestep = rl_environment.TimeStep(
            step_type=None,
            reward=None,
            discount=None,
            observations=self._obs
        )

        with self._policies[player_id].temp_mode_as(nfsp.MODE.average_policy):
            agent_output = self._policies[player_id].step(timestep, is_evaluation=True)
            action_probs = agent_output.probs

        prob_dict = {}
        legal_actions = state.legal_actions(player_id)
        for action in legal_actions:
            prob_dict[state.action_to_string(player_id, action)] = float(action_probs[action])
        return prob_dict


def main(unused_argv):
    # Initialize the environment
    game_name = "patriks_coin_game"
    num_players = 2
    env_configs = {"players": num_players}
    env = rl_environment.Environment(game_name, **env_configs)

    info_state_size = env.observation_spec()["info_state"][0]
    num_actions = env.action_spec()["num_actions"]

    hidden_layers_sizes = [int(l) for l in FLAGS.hidden_layers_sizes]

    # NFSP Agent Parameters
    agent_kwargs = {
        "replay_buffer_capacity": FLAGS.replay_buffer_capacity,
        "epsilon_decay_duration": FLAGS.num_train_episodes,
        "epsilon_start": 0.06,
        "epsilon_end": 0.001,
    }

    # Create TensorFlow session
    with tf.Session() as sess:
        # Initialize NFSP agents
        agents = [
            nfsp.NFSP(sess, player_id, info_state_size, num_actions,
                      hidden_layers_sizes, FLAGS.reservoir_buffer_capacity,
                      FLAGS.anticipatory_param,
                      **agent_kwargs) for player_id in range(num_players)
        ]

        # Initialize policies for evaluation
        expl_policies_avg = NFSPPolicies(env, agents, nfsp.MODE.average_policy)

        sess.run(tf.global_variables_initializer())

        # Training Loop
        for episode in range(1, FLAGS.num_train_episodes + 1):
            time_step = env.reset()
            while not time_step.last():
                player_id = time_step.observations["current_player"]
                agent_output = agents[player_id].step(time_step)
                actions = [agent_output.action]
                time_step = env.step(actions)

            # Episode is over, inform agents
            for agent in agents:
                agent.step(time_step)

            # Periodically evaluate and log progress
            if episode % FLAGS.eval_every == 0 or episode == 1:
                losses = [agent.loss for agent in agents]
                logging.info("Episode %d: Losses: %s", episode, losses)
                expl = exploitability.exploitability(env.game, expl_policies_avg)
                logging.info("Episode %d: Exploitability AVG %s", episode, expl)
                logging.info("_____________________________________________")

        # After training, traverse the game tree and save action probabilities
        logging.info("Training completed. Traversing the game tree to collect action probabilities.")

        results = []

        def parse_info_state(info_state_str):
            parsed_info = {}
            for line in info_state_str.split('\n'):
                if ':' not in line:
                    continue
                key, value = line.split(':', 1)
                key, value = key.strip(), value.strip()

                if key == "Round":
                    parsed_info["round"] = int(value)
                elif key == "Coin Player Choices":
                    parsed_info["coin_player_choices"] = tuple(map(int, value.split())) if value else ()
                elif key == "Estimator Guesses":
                    parsed_info["estimator_guesses"] = tuple(map(int, value.split())) if value else ()
            return parsed_info

        def traverse(state, policy, depth=0):
            if state.is_terminal():
                return

            player = state.current_player()
            info_state_str = state.information_state_string(player)
            info_state = parse_info_state(info_state_str)
            info_state["depth"] = depth

            action_probs = policy.action_probabilities(state)

            state_data = {
                **info_state,
                "actions": action_probs
            }

            results.append(state_data)

            for action in state.legal_actions():
                cloned_state = state.clone()
                cloned_state.apply_action(action)
                traverse(cloned_state, policy, depth + 1)

        # Start traversal from the initial state
        initial_state = env.game.new_initial_state()
        traverse(initial_state, expl_policies_avg)

        # Ensure output directory exists
        os.makedirs(FLAGS.output_dir, exist_ok=True)
        output_path = os.path.join(FLAGS.output_dir, "nfsp_game_tree_results.json")

        # Save results to JSON
        with open(output_path, "w") as f:
            json.dump(results, f, indent=4)

        logging.info(f"Game tree results saved to {output_path}")


if __name__ == "__main__":
    app.run(main)