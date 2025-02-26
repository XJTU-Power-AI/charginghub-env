import os
import sys
import pickle
import random
import copy
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '../data_file/pv_power_100.pkl')
with open(file_name, 'rb') as fo:
    pv_power_data = pickle.load(fo)

file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '../data_file/wd_power_150.pkl')
with open(file_name, 'rb') as fo:
    wd_power_data = pickle.load(fo)


class ReNew:
    def __init__(self, renew_fluctuate=0):
        def rand_gen(start, end):
            def wrapper():
                f = random.randint(start, end)
                return f

            return wrapper

        self.rand_int_pv = rand_gen(0, len(pv_power_data) - 1)
        self.rand_int_wd = rand_gen(0, len(wd_power_data) - 1)
        self.pv_day = None
        self.wd_day = None
        self.pv_noise = OU_Noise(size=1, seed=1, theta=.01, sigma=1.)
        self.wd_noise = OU_Noise(size=1, seed=1, theta=.01, sigma=1.5)
        self.renew_fluctuate = renew_fluctuate

    def get_pv_power(self, time):
        temp = pv_power_data[self.pv_day][time]
        if temp > 0 and self.pv_day % 2 == 0:
            temp += float(self.pv_noise.sample()) * (1 + self.renew_fluctuate)
        pv_power = max(0, temp)
        return pv_power

    def get_wd_power(self, time):
        temp = wd_power_data[self.wd_day][time]
        temp += float(self.wd_noise.sample()) * (1 + self.renew_fluctuate)
        wd_power = max(0, temp)
        return wd_power

    def renew_reset(self):
        self.pv_day = self.rand_int_pv()
        self.wd_day = self.rand_int_wd()


class OU_Noise(object):
    """Ornstein-Uhlenbeck process."""

    def __init__(self, size, seed, mu=0., theta=0.15, sigma=0.2):
        self.mu = mu * np.ones(size)
        self.theta = theta
        self.sigma = sigma
        self.seed = random.seed(seed)
        self.state = None
        self.reset()

    def reset(self):
        """Reset the internal state (= noise) to mean (mu)."""
        self.state = copy.copy(self.mu)

    def sample(self):
        """Update internal state and return it as a noise sample."""
        dx = self.theta * (self.mu - self.state) + self.sigma * np.array(
            [np.random.normal() for _ in range(len(self.state))])
        self.state += dx
        return self.state


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    rn = ReNew()
    for _ in range(50):
        rn.renew_reset()
        # one_day_data = []
        # for i in range(96):
        #     one_day_data.append(rn.get_wd_power(i))
        # plt.plot(one_day_data)
        # plt.show()
