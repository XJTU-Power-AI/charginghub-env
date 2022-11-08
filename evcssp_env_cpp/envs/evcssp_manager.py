import os
import sys
import gym
import random
import copy
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
print(os.path.dirname(os.path.abspath(__file__)))
from lion_cpp20.Aggregator_Simple import HubAggregator_v2
from lion_cpp20.hydro_sys import HySystem, HFC
from lion_cpp20.renewable import ReNew
from lion_cpp20.pyevstation import Change_Use_Seed, Get_Car_Flow_Dir

Get_Car_Flow_Dir(os.path.dirname(os.path.abspath(__file__))+"/lion_cpp20/SCP_Base/")

class EvcsspManagerEnv_v1(gym.Env):
    metadata = {
        "render.modes": ["human", "rgb_array"],
        "video.frames_per_second": 30
    }

    def __init__(self, station_list, station_type_list, constant_charging=False, hydro_prod_rate=None,
                 hydro_store_vlt=None, init_soc=None, fc_max_power=None, fcev_permeate=0.01, seed_rand=True,
                 use_lagrange=False):
        Change_Use_Seed(seed_rand)
        print("this env is v1 for charging hub with fuel cell")
        print("init hydrogen storage init soc is", init_soc)
        self.price_noise = OU_Noise(size=1, seed=1, theta=.1, sigma=0.005)
        self.me = None
        self.simulate = False

        self.hydro_prod_rate = hydro_prod_rate
        self.fcev_permeate = fcev_permeate
        self.init_soc = init_soc

        assert len(station_list) == len(station_type_list) == 2
        self.env_aggregator = HubAggregator_v2(station_list, station_type_list, constant_charging)
        self.hy_sys = HySystem(hydro_prod_rate=hydro_prod_rate, hydro_store_vlt=hydro_store_vlt, init_soc=init_soc,
                               fcev_permeanbility=self.fcev_permeate)
        self.hy_init_soc = self.hy_sys.sty.init_soc_
        self.hfc = HFC(hy_system=self.hy_sys, cell_number_=fc_max_power)
        self.renew = ReNew()
        self.price_count = 0

        self.price_mean = np.mean(self.env_aggregator.price_constant)
        self.price_std = np.std(self.env_aggregator.price_constant)

        obs_price = (np.array(self.env_aggregator.price_constant) - self.price_mean) / self.price_std

        # state
        self.min_time = -1.0
        self.max_time = 1.0
        self.real_time_max = 96

        self.min_price = min(obs_price)
        self.max_price = max(obs_price)

        self.min_power = -1.0
        self.max_power = 1.0

        self.min_line = 0
        self.max_line = 2

        self.min_hy_soc = 0
        self.max_hy_soc = 1

        self.min_pv_power = 0
        self.max_pv_power = 1

        self.min_wd_power = 0
        self.max_wd_power = 1

        # action
        self.min_action = -1.0
        self.max_action = 1.0

        min_list = [self.min_time, self.min_price]
        max_list = [self.max_time, self.max_price]

        print("pile number 0", self.env_aggregator.pile_number[0])
        print("pile number 1", self.env_aggregator.pile_number[1])

        real_station_number = 1

        if self.env_aggregator.pile_number[1] == 0 or self.env_aggregator.pile_number[0] == 0:
            min_list += [self.min_power, self.min_power, self.min_power, self.min_line]
            max_list += [self.max_power, self.max_power, self.max_power, self.max_line]
        else:
            real_station_number = 2
            for _ in range(self.env_aggregator.station_number):  # substation_number is 2
                min_list += [self.min_power, self.min_power, self.min_power, self.min_line]
                max_list += [self.max_power, self.max_power, self.max_power, self.max_line]

        min_list += [self.min_hy_soc, self.min_pv_power, self.min_wd_power]
        max_list += [self.max_hy_soc, self.max_pv_power, self.max_wd_power]

        self.low_state = np.array(
            min_list,
            dtype=np.float32
        )
        self.high_state = np.array(
            max_list,
            dtype=np.float32
        )

        self.viewer = None

        self.action_space = spaces.Box(
            low=self.min_action,
            high=self.max_action,
            shape=(sum(self.env_aggregator.pile_number) + 2,),
            dtype=np.float32
        )
        self.observation_space = spaces.Box(
            low=self.low_state,
            high=self.high_state,
            dtype=np.float32
        )
        self.seed()
        self.reset()
        self.real_state = None
        self.np_random = None
        self.state = None

        self.use_lagrangian = use_lagrange
        self.lagrangian_factor = 1
        self.penalty = 0
        self.total_hy_use = 0

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        if self.simulate:
            time_real_next = self.real_state[0]
        else:
            time_real_next = self.real_state[0] + 1

        ############  renewable add here   ###############  begin
        re_new_power = self.re_wd_power + self.re_pv_power
        ############  renewable add here   ###############  end

        if action is None:
            action = np.append(np.ones(sum(self.env_aggregator.pile_number)), [0, 0])
        assert len(action) == sum(self.env_aggregator.pile_number) + 2
        action_real = self.action_to_real(action)
        # noinspection PyAttributeOutsideInit
        self.action_real = action_real

        self.env_aggregator.consult_middle_agent(action_real[:-2])

        self.env_aggregator.ag_step(simulate=False)

        charging_power = sum(self.env_aggregator.evcssp_charge_power_list)

        hy_power_limit = max(0, 2000 + re_new_power - charging_power)

        self.hy_act = -1
        self.gen_hy = False
        limit = 0.5

        debug = False
        # debug = True
        if debug:
            pass
        else:
            if self.hy_sys.hy_power_speed_list[math.ceil(action_real[-1] * 100)] > hy_power_limit:
                act_limit = None
                for ind, power in zip(range(len(self.hy_sys.hy_power_speed_list)), self.hy_sys.hy_power_speed_list):
                    if power >= hy_power_limit:
                        act_limit = self.hy_sys.hy_power_speed_list_input[ind - 1]
                        break
                if act_limit is None:
                    act_limit = self.hy_sys.hy_power_speed_list_input[- 1]
                self.hy_sys.hy_step(act_limit)
                if self.hy_sys.hy_flow_speed > limit:
                    self.gen_hy = True
                self.hy_act = act_limit
            else:
                self.hy_sys.hy_step(action_real[-1])
                if self.hy_sys.hy_flow_speed > limit:
                    self.gen_hy = True
                self.hy_act = action_real[-1]

        ############  renewable add here   ###############  begin
        self.re_hy_gen = self.hy_sys.hy_flow_speed_15
        hydrogen_power = self.hy_sys.all_power_second
        self.re_hydrogen_power_init = hydrogen_power

        ev_power_sum = charging_power
        ev_power_list = self.env_aggregator.evcssp_charge_power_list
        if sum(self.env_aggregator.evcssp_charge_power_list) > 0:
            fc_rate = charging_power / sum(self.env_aggregator.evcssp_charge_power_list)
            assert 0 <= fc_rate <= 1
            ev_power_list = [fc_rate * charge_power for charge_power in self.env_aggregator.evcssp_charge_power_list]

        used_renew = 0
        if re_new_power >= hydrogen_power:
            re_new_power -= hydrogen_power
            used_renew += hydrogen_power
            hydrogen_power = 0

            temp = ev_power_sum
            ev_power_sum = max(0, ev_power_sum - re_new_power)
            used_renew += temp - ev_power_sum
            if sum(ev_power_list) > 0:
                rate = ev_power_sum / sum(ev_power_list)
                assert 0 <= rate <= 1
                ev_power_list = [rate * ev_p for ev_p in ev_power_list]
        else:
            hydrogen_power -= re_new_power
            used_renew = re_new_power
        ############  renewable add here   ###############  end;  output: hydrogen_power ev_power_sum ev_power_list
        self.re_ev_power_list = ev_power_list
        self.re_used_renew = used_renew

        ############  fuel cell add here   ###############  begin
        if debug or self.gen_hy:
            _, fc_power = self.hfc.use_cell(0, ev_power_sum)
        else:
            _, fc_power = self.hfc.use_cell(self.hfc.cell_number * float(action_real[-2]), ev_power_sum)
        ev_power_sum -= fc_power
        self.fc_power = fc_power
        if sum(ev_power_list) > 0:
            rate_ = ev_power_sum / sum(ev_power_list)
            ev_power_list = [rate_ * power for power in ev_power_list]
        hy_loss = -6 / 1000 * self.hfc.hy_to_use
        self.re_hy_for_fc = self.hfc.hy_to_use
        ############  fuel cell add here   ###############  end

        self.real_charging_power = ev_power_sum

        self.re_hydrogen_power = hydrogen_power
        self.re_ev_power_sum = ev_power_sum

        ############  to_calculate_income ###########
        real_price_dollar = self.real_state[1] / 4  # kW*15min

        # https://greencarjournal.com/electric-cars/what-does-public-charging-cost/
        # $0.21 slow     $0.42 fast
        income_evs_fast = 0.42 / 4 * self.env_aggregator.evcssp_charge_power_list[0] - real_price_dollar * \
                          ev_power_list[0]
        income_evs_slow = 0.21 / 4 * self.env_aggregator.evcssp_charge_power_list[1] - real_price_dollar * \
                          ev_power_list[1]
        income_evs = income_evs_fast + income_evs_slow
        self.re_income_evs_cost = - real_price_dollar * (ev_power_list[0] + ev_power_list[1])
        income_evs_serve = 0.8 * sum(self.env_aggregator.ag_flow_in_number)

        self.re_income_evs_cost_list = [- real_price_dollar * ev_power_list[0], - real_price_dollar * ev_power_list[1]]
        self.re_income_evs_list = [0.42 / 4 * self.env_aggregator.evcssp_charge_power_list[0],
                                   0.21 / 4 * self.env_aggregator.evcssp_charge_power_list[1]]
        self.re_income_evs_serve = income_evs_serve

        # https://www.sgh2energy.com/economics
        income_hys = 6 / 1000 * self.hy_sys.sty.hy_use
        not_meet_loss = -10 / 1000 * self.hy_sys.sty.not_meet

        hy_cost = -real_price_dollar * hydrogen_power

        self.mass_need = self.hy_sys.hvs.total_mass_need
        self.mass_support = self.hy_sys.sty.hy_use

        self.all_power_15 = self.hy_sys.all_power_15

        self.re_price_dollar = real_price_dollar

        self.re_income_evs_list = [income_evs_fast, income_evs_slow]

        self.re_income_evs = income_evs

        self.re_income_hys = income_hys
        self.re_hy_cost = hy_cost

        reward = float(
            (income_hys + income_evs + income_evs_serve + hy_cost + 1 * hy_loss + not_meet_loss) / 50)
        self.acumulate_reward += reward

        ################
        self.income = income_hys + income_evs + income_evs_serve + hy_cost
        self.not_meet_loss = not_meet_loss
        ################

        done = bool(
            time_real_next >= self.real_time_max
        )

        self.total_hy_use += self.hy_sys.sty.hy_use

        if done:
            if self.use_lagrangian:
                temp_deviation = (self.hy_sys.sty.Store_SOC - self.hy_init_soc) * self.hy_sys.sty.capacity_mass / 1000
            else:
                temp_deviation = abs(
                    self.hy_sys.sty.Store_SOC - self.hy_init_soc) * self.hy_sys.sty.capacity_mass / 1000
            temp_deviation = temp_deviation / 0.2
            print("reward", self.acumulate_reward)
            print("SOC", temp_deviation)
            print("SOC_init is ", self.hy_init_soc)
            print("SOC_end is ", self.hy_sys.sty.Store_SOC)
            self.test_penalty = abs(temp_deviation)
            self.penalty = temp_deviation * self.lagrangian_factor
            if self.use_lagrangian:
                reward -= self.penalty
            else:
                reward -= self.test_penalty
        self.deviation = abs(self.hy_sys.sty.Store_SOC - self.hy_init_soc)

        time_real_next = time_real_next % self.real_time_max

        self.make_state(time=time_real_next)
        return self.state, reward, done, {}

    def reset(self):
        self.acumulate_reward = 0
        self.renew.renew_reset()
        self.env_aggregator.ag_reset()
        self.hy_sys.hy_reset()
        self.make_state(time=0)
        self.price_count = 0
        self.lagrangian_factor = 1
        self.penalty = 0
        self.total_hy_use = 0
        return np.array(self.state)

    def state_norm(self):
        k = 2 * np.pi / 96
        time_norm = np.sin(k * self.real_state[0])
        price_norm = (self.real_state[1] - self.price_mean) / self.price_std
        norm_state_list = [time_norm, price_norm]

        station_num_temp = 0
        for station in self.env_aggregator.evcssp_evs_objects:
            if station.charge_number > 0:
                norm_station_list = self.norm(self.real_state[4 * station_num_temp + 2:4 * station_num_temp + 2 + 3],
                                              station.transformer_limit)

                norm_station_list += self.norm_non_negative(
                    self.real_state[4 * station_num_temp + 2 + 3:4 * station_num_temp + 2 + 4], 5)
                norm_state_list += norm_station_list
                station_num_temp += 1

        assert station_num_temp >= 1, "A station must have fast pile or slow pile!"

        # add normalized hy soc
        norm_state_list.append(self.real_state[-3])

        # add normalized pv power
        max_pv_power = 42 * self.scale_pv
        norm_state_list.append(self.real_state[-2] / max_pv_power)

        # add normalized wd power
        max_wd_power = 92 * self.scale_wd
        norm_state_list.append(self.real_state[-1] / max_wd_power)

        assert len(norm_state_list) == len(self.real_state), "state length error"
        self.state = np.array(norm_state_list)

    def render(self, mode="human"):
        pass

    def close(self):
        pass

    def make_state(self, time):
        # to make real state as well as normed state

        ################# renewable add here #################
        self.scale_pv = 5
        self.scale_wd = 1
        self.re_pv_power = self.renew.get_pv_power(int(time)) * self.scale_pv
        self.re_wd_power = self.renew.get_wd_power(int(time)) * self.scale_wd
        ################# renewable add here #################

        ################# price add here #################
        if self.price_count % 4 == 0:
            price_next = float(self.price_noise.sample())
            self.price_next = price_next
            price_next += self.env_aggregator.price[-1]
        else:
            price_next = self.env_aggregator.price[-1] + self.price_next
        self.price_count += 1
        ################# price add here #################
        assert time == self.env_aggregator.aggregator_time_hole == self.hy_sys.sys_time, "time inconsistent"
        real_state_list = [time, price_next]

        for station in self.env_aggregator.evcssp_evs_objects:
            if station.charge_number > 0:
                real_state_list += [station.min_power, station.charge_power, station.max_power, station.line]
        real_state_list.append(self.hy_sys.sty.Store_SOC)
        real_state_list.append(self.re_pv_power)
        real_state_list.append(self.re_wd_power)

        self.real_state = np.array(real_state_list)
        self.state_norm()

    def norm(self, my_input, max_range):
        self.me = None
        half_range = max_range / 2
        return list((np.array(my_input) - half_range) / half_range)

    def norm_non_negative(self, my_input, max_range):
        self.me = None
        return list(np.array(my_input) / max_range)

    def action_to_real(self, action):
        action_1 = action[:-2]
        real_action = (np.array(action_1) + 1) / 2
        real_actions = []
        for act in real_action:
            if act >= 0.5:
                real_actions.append(1.0)
            else:
                real_actions.append(0.0)
        if action[-1] is not None:
            real_actions.append((action[-1] + 1) / 2)
        else:
            real_actions.append(action[-1])

        if action[-2] is not None:
            real_actions.append((action[-2] + 1) / 2)
        else:
            real_actions.append(action[-2])
        return np.array(real_actions)

    def show_situation(self):
        for station in self.env_aggregator.evcssp_evs_objects:
            station.print_situation()


# noinspection PyPep8Naming,DuplicatedCode,PyNoneFunctionAssignment
class OU_Noise(object):

    def __init__(self, size, seed, mu=0., theta=0.15, sigma=0.2):
        self.mu = mu * np.ones(size)
        self.theta = theta
        self.sigma = sigma
        self.seed = random.seed(seed)
        self.state = None
        self.reset()

    def reset(self):
        self.state = copy.copy(self.mu)

    def sample(self):
        dx = self.theta * (self.mu - self.state) + self.sigma * np.array(
            [np.random.normal() for _ in range(len(self.state))])
        self.state += dx
        return self.state


if __name__ == '__main__':
    pass




