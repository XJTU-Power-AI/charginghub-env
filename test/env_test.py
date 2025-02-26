import gym
import random
import numpy as np
import matplotlib.pyplot as plt
import pickle

seed_rand = False
if not seed_rand:
    random.seed(0)
    np.random.seed(0)

EVCS_list = [20, 25]
EVCS_type_list = ['fast', 'slow']
time_window = 1

hydro_prod_rate = 100  # default generate 430 m^3/h
hydro_init_soc = 0.2
hydro_store_vlt = 500 / 20  # default volume 5000 m^3
fcev_permeate = 0.01
max_fc_power = 100

use_lagrange = False

renew_fluctuate = 0.3 * 0

price_fluctuate = 0 * 30 / 100
hydro_loss = 0 * 2 / 100  # (2% -10%)

env_kwargs = {'station_list': EVCS_list, 'station_type_list': EVCS_type_list, 'constant_charging': False,
              'seed_rand': seed_rand, 'hydro_prod_rate': hydro_prod_rate, 'hydro_store_vlt': hydro_store_vlt,
              'init_soc': hydro_init_soc, 'fc_max_power': max_fc_power, 'fcev_permeate': fcev_permeate,
              'use_lagrange': use_lagrange, 'renew_fluctuate': renew_fluctuate, 'price_fluctuate': price_fluctuate, 'hydro_loss': hydro_loss}


if __name__ == '__main__':
    environment = gym.make('evcssp_env_cpp:charging-hub-v6', **env_kwargs)

    environment.reset()
    done = False

    while not done:
        s_, r, done, _ = environment.step(action=None)
