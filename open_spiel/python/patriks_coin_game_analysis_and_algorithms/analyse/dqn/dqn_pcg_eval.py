import os
import numpy as np
import tensorflow.compat.v1 as tf
import open_spiel.python.rl_environment as rl_environment
from dqn import DQN
import open_spiel.python.algorithms as algorithms

def main():
    game_name = "patriks_coin_game"
    env = rl_environment.Environment(game_name)

    with tf.Session() as session:
        info_state_size = env.observation_spec()["info_state"][0].shape[0]
        num_actions = env.action_spec()["num_actions"]

        agent0 = DQN(
            session=session,
            player_id=0,
            state_representation_size=info_state_size,
            num_actions=num_actions,
            hidden_layers_sizes=[128, 128],
            replay_buffer_capacity=10000,
            batch_size=128,
            learning_rate=0.001,
            update_target_network_every=1000,
            learn_every=10,
            discount_factor=0.99,
            min_buffer_size_to_learn=1000,
            epsilon_start=0.0,  # No exploration during evaluation
            epsilon_end=0.0,
            epsilon_decay_duration=0,
            optimizer_str="adam",
            loss_str="mse"
        )

        checkpoint_dir = "checkpoints_patriks_coin_game"
        agent0.restore(checkpoint_dir)
        print("Agent0 restored from checkpoint.")

        agent1 = algorithms.RandomAgent(player_id=1)

        num_episodes = 1000
        win_count = 0
        loss_count = 0
        draw_count = 0

        for ep in range(num_episodes):
            time_step = env.reset()
            while not time_step.last():
                # Player 0 (DQN) action
                step_output0 = agent0.step(time_step, is_evaluation=True)
                action0 = step_output0.action

                # Player 1 (Random) action
                step_output1 = agent1.step(time_step, is_evaluation=True)
                action1 = step_output1.action

                # Apply both actions
                action = [action0, action1]
                time_step = env.step(action)

            # Check the outcome
            returns = time_step.rewards
            if returns[0] > returns[1]:
                win_count += 1
            elif returns[0] < returns[1]:
                loss_count += 1
            else:
                draw_count += 1

        print(f"Out of {num_episodes} episodes:")
        print(f"Wins: {win_count}")
        print(f"Losses: {loss_count}")
        print(f"Draws: {draw_count}")

if __name__ == "__main__":
    main()