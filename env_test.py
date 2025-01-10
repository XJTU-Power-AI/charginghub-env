import gym
import matplotlib.pyplot as plt
import pickle

EVCS_list = [20, 25]
EVCS_type_list = ['fast', 'slow']

hydro_prod_rate = 100  # default generate 430 m^3/h
hydro_store_vlt = 500 / 20  # default volume 5000 m^3
hydro_init_soc = 0.5
max_fc_power = 100
fcev_permeate = 0.01
use_lagrange = False
env_kwargs = {'station_list': EVCS_list, 'station_type_list': EVCS_type_list, 'constant_charging': False,
              'seed_rand': False, 'hydro_prod_rate': hydro_prod_rate, 'hydro_store_vlt': hydro_store_vlt,
              'init_soc': hydro_init_soc, 'fc_max_power': max_fc_power, 'fcev_permeate': fcev_permeate,
              'use_lagrange': use_lagrange}


if __name__ == '__main__':
    environment = gym.make('evcssp_env_cpp:charging-hub-v1', **env_kwargs)

    environment.reset()
    done = False

    while not done:
        s_, r, done, _ = environment.step(action=None)
