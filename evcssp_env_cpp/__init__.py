from gym.envs.registration import register

register(
    id='charging-hub-v6',
    entry_point='evcssp_env_cpp.envs:EvcsspManagerEnv_v6',
    max_episode_steps=999,
    reward_threshold=99,
)
