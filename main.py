import gym

env = gym.make('CartPole-v1')
num_episodes = 10

for episode in range(num_episodes):
    state = env.reset()
    done = False
    total_reward = 0

    while not done:
        # Вибір випадкової дії (для прикладу)
        action = env.action_space.sample()
        next_state, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        # Ваш код навчання/логіки тут
        total_reward += reward

        state = next_state

    print(f"Епізод {episode+1} завершено. Сумарна нагорода: {total_reward}")

env.close()