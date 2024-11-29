# train_dqn.py

import os
import numpy as np
import tensorflow.compat.v1 as tf
from absl import logging
import open_spiel.python.algorithms as algorithms
import open_spiel.python.rl_environment as rl_environment
from dqn import DQN  # Ensure dqn.py is in the same directory or PYTHONPATH

def main():
    # Initialize the OpenSpiel environment
    game_name = "patriks_coin_game"
    env = rl_environment.Environment(game_name)

    # Extract environment specifications
    num_players = env.num_players
    assert num_players == 2, "This implementation assumes a 2-player game."

    # Assuming DQN will control Player 0 and Player 1 is a fixed policy (e.g., random)
    # If you intend to have DQN for both players, consider multi-agent DQN

    # TensorFlow session
    with tf.Session() as session:
        # Get state and action sizes
        info_state_size = env.observation_spec()["info_state"][0].shape[0]
        num_actions = env.action_spec()["num_actions"]

        # Initialize DQN agent for Player 0
        agent0 = DQN(
            session=session,
            player_id=0,
            state_representation_size=info_state_size,
            num_actions=num_actions,
            hidden_layers_sizes=[128, 128],  # Example architecture
            replay_buffer_capacity=10000,
            batch_size=128,
            learning_rate=0.001,
            update_target_network_every=1000,
            learn_every=10,
            discount_factor=0.99,
            min_buffer_size_to_learn=1000,
            epsilon_start=1.0,
            epsilon_end=0.1,
            epsilon_decay_duration=int(1e6),
            optimizer_str="adam",
            loss_str="mse"
        )

        # Initialize DQN agent for Player 1 as a random agent or fixed policy
        # For simplicity, we'll use a random agent
        agent1 = algorithms.RandomAgent(player_id=1)

        # Initialize all variables
        session.run(tf.global_variables_initializer())

        # Optionally, load existing checkpoints
        checkpoint_dir = "checkpoints_patriks_coin_game"
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)
        if agent0.has_checkpoint(checkpoint_dir):
            agent0.restore(checkpoint_dir)
            print("Agent0 restored from checkpoint.")
        else:
            print("No checkpoint found. Starting fresh training.")

        num_iterations = 1000000
        for it in range(num_iterations):
            time_step = env.reset()
            while not time_step.last():
                # Get actions for each player
                current_player = time_step.current_player()
                if current_player == 0:
                    step_output = agent0.step(time_step, is_evaluation=False)
                    action0 = step_output.action
                elif current_player == 1:
                    # Random action for Player 1
                    action1 = agent1.step(time_step, is_evaluation=False).action
                else:
                    raise ValueError(f"Unexpected player id: {current_player}")

                # Apply actions; since it's a simultaneous game, collect all actions first
                if current_player == 0:
                    # Wait for Player 1's action
                    action = [action0, action1]
                elif current_player == 1:
                    action = [action0, action1]

                # Advance the environment with both actions
                time_step = env.step(action)

            # After episode ends, optionally log and save checkpoints
            if it % 1000 == 0:
                loss = agent0.loss
                print(f"Iteration {it}, Loss: {loss}")
                agent0.save(checkpoint_dir)

        # Save final model
        agent0.save(checkpoint_dir)
        print("Training completed and model saved.")

if __name__ == "__main__":
    main()