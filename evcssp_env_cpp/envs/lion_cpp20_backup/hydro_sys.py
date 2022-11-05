import math
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pyevstation import PoissonNumber, CarArriveRandom, RandomUtil


class Electrolyser(object):
    def __init__(self, mass_flow_max=10.63):
        self.R = 0.082
        self.T = 25
        self.p = 1
        self.v_H = None  # ml/min
        self.v_H_mol = None
        self.v_H_mass = None  # g/s
        self.max_gen_flow_speed = mass_flow_max
        self.v_M = self.R * (273 + self.T) / self.p  # L/mol
        self.R_i = 0.326
        self.e_rev = 1.476
        self.F = 96487
        self.get_power0(10)  # assume max produce rate 10 ml/min
        # noinspection PyTypeChecker
        self.cell_number = math.ceil(mass_flow_max / self.v_H_mass)
        print('cell_number', self.cell_number)
        self.power = None

    def get_power0(self, v_h):  # ml/min
        if v_h is not None:
            self.v_H = v_h
        v_H_L = (self.v_H / 1000) / 60  # L/s
        self.v_H_mol = v_H_L / self.v_M  # mol/s
        self.v_H_mass = self.v_H_mol * 2.02  # g/s
        self.power = (self.v_H * 2 * self.F / (self.v_M * 1000 * 60)) ** 2 * self.R_i + (
                self.v_H * 2 * self.F / (self.v_M * 1000 * 60)) * self.e_rev
        return self.power

    def get_power(self, v_H_mass):  # g/s
        # print('v_H_mass', v_H_mass)
        if self.cell_number == 0:
            return 0
        self.v_H_mass = v_H_mass / self.cell_number
        self.v_H_mol = self.v_H_mass / 2.02  # mol/s
        v_H_L = self.v_H_mol * self.v_M  # L/s
        self.v_H = v_H_L * 1000 * 60  # mL/min
        temp = self.v_H * 2 * self.F / (self.v_M * 1000 * 60)
        self.power = temp ** 2 * self.R_i + temp * self.e_rev
        self.power = self.cell_number * self.power / 1000  # kW
        return self.power

    def ele_reset(self):
        self.v_H_mass = None
        self.v_H_mol = None
        self.v_H = None
        self.power = None


class Compressor(object):
    def __init__(self):
        self.n_H2 = None  # (mol/s) 2.02 g/mole
        self.eta_c = 0.8
        self.alpha = 1.4
        self.R = 0.082
        self.T = 273 + 25  # K
        self.P_in = 1  # bar
        self.P_out = 200  # bar
        self.P_a = math.sqrt(self.P_in * self.P_out)  # bar
        self.W_c = None
        self.W_1 = None
        self.W_2 = None
        self.part1 = self.alpha / (self.alpha - 1)
        self.part2 = self.part1 * self.R * self.T
        self.part3 = (self.alpha - 1) / self.alpha

    def generate_W0(self):
        self.W_1 = self.part2 * (-1 + (self.P_a / self.P_in) ** self.part3)
        self.W_2 = self.part2 * (-1 + (self.P_out / self.P_a) ** self.part3)
        self.W_c = self.n_H2 * (self.W_1 + self.W_2) / self.eta_c

    def generate_W(self, m_H2):  # g/s
        self.n_H2 = m_H2 / 2.02
        self.generate_W0()
        return self.W_c / 1000  # unit:kW

    def cpr_reset(self):
        self.n_H2 = None
        self.W_c = None
        self.W_1 = None
        self.W_2 = None


class HyStore(object):
    # https: // ieeexplore.ieee.org / stamp / stamp.jsp?tp = & arnumber = 9265468
    def __init__(self, store_v=None, init_soc=0.1):
        self.density = 0.089 * (200 / 1)  # g/L
        # Hydrogen Storage Optimal Scheduling for Fuel Supply and Capacity - Based Demand Response Program Under Dynamic Hydrogen Pricing
        self.h_v_max = 5000 if store_v is None else store_v  # m^3
        self.capacity_temp = self.h_v_max * 1000  # L
        self.capacity_mass = self.density * self.capacity_temp  # g
        # print('self.capacity_mass', self.capacity_mass)
        self.capacity = init_soc * self.capacity_mass
        self.Store_SOC = init_soc
        self.init_soc_ = init_soc
        # print('self.capacity_mass', self.capacity_mass)

    def sty_step(self, mass_s_H2, hy_use=0):  # g/s
        temp_to_store = mass_s_H2 * 15 * 60
        # print('temp_to_store', temp_to_store)
        # print('hy_use', hy_use)
        self.capacity += temp_to_store

        upper_change = self.capacity_mass - self.capacity
        lower_change = self.capacity - 0.1 * self.capacity_mass
        lower_change = max(0, lower_change)
        assert lower_change >= 0
        assert upper_change >= 0

        temp_to_change = min(lower_change, hy_use)
        self.hy_use = temp_to_change
        self.not_meet = hy_use - temp_to_change

        self.capacity -= temp_to_change
        # print(111111111111111, self.capacity)
        # self.capacity = min(self.capacity, self.capacity_mass)
        # Hydrogen Storage Optimal Scheduling for Fuel Supply and Capacity - Based Demand Response Program Under Dynamic Hydrogen Pricing
        # self.capacity = max(self.capacity, self.capacity_mass * 0.1)
        self.Store_SOC = self.capacity / self.capacity_mass

    def sty_reset(self):
        self.capacity = self.init_soc_ * self.capacity_mass
        self.Store_SOC = self.init_soc_


# class HyFEVStation(object):
#     def __init__(self):
#         # hv property ; unit: g
#         # https: // www.fueleconomy.gov / feg / fcv_sbs.shtml (360/66)
#         self.capacity_mass = 5.45 * 1000
#         # station property
#         self.arrive_number = None
#         self.arrive_soc_ini_list = []
#         self.arrive_soc_tar_list = []
#         self.needed_soc_list = []
#         self.arrive_number_sum = 0
#         self.total_mass_need = None
#
#     def _hv_arrive(self, time):
#         self.arrive_number = PoissonNumber.hv_car_number_wrt_poisson(time)
#
#     def hvs_step(self, time):
#         self._hvs_reset()
#         self._hv_arrive(time)
#         self.arrive_number_sum += self.arrive_number
#         # print('self.arrive_number', self.arrive_number)
#         # print('self.arrive_number_sum', self.arrive_number_sum)
#         for _ in range(self.arrive_number):
#             self.arrive_soc_ini_list.append(CarArriveRandom.mk_soc())
#             self.arrive_soc_tar_list.append(RandomUtil.uniform_rand(80.0, 100.0, True))
#             self.needed_soc_list.append(
#                 (self.arrive_soc_tar_list[-1] - self.arrive_soc_ini_list[-1]) * 0.01 * self.capacity_mass)
#         self.total_mass_need = sum(self.needed_soc_list)
#
#     def _hvs_reset(self):
#         self.arrive_number = None
#         self.arrive_soc_ini_list = []
#         self.arrive_soc_tar_list = []
#         self.needed_soc_list = []
#         # self.arrive_number_sum = 0
#         self.total_mass_need = None


class HySystem(object):
    def __init__(self, hydro_prod_rate=None, hydro_store_vlt=None, init_soc=0.1, fcev_permeanbility=0.01):
        # test version
        # self.hvs = HyFEVStation()
        self.hvs = HyFCEVStation(fcev_permeanbility)
        self.cpr = Compressor()
        assert init_soc >= 0.1 and init_soc <= 1
        self.sty = HyStore(hydro_store_vlt, init_soc)  # default volume 5000 m^3
        # Hydrogen Storage Optimal Scheduling for Fuel Supply and Capacity - Based Demand Response Program Under Dynamic Hydrogen Pricing
        if hydro_prod_rate is None:
            self.F_h_max = 430  # m^3/h
        else:
            self.F_h_max = hydro_prod_rate
        self.v_h_max = 0.089 * self.F_h_max * 1000 / 3600  # 10.63 g/s
        self.ele = Electrolyser(self.v_h_max)
        self.hy_flow_speed = None  # g/s
        self.hy_flow_speed_15 = None  # g/15min
        self.ele_power = None
        self.cpr_power = None
        self.all_power_second = None
        self.all_power_15 = None
        self.sys_time = 0
        self.hy_sys_max_power = self.ele.get_power(self.v_h_max) + self.cpr.generate_W(self.v_h_max)
        self.hy_power_speed_list = [self.hy_step(0.01 * i, init=True) for i in range(101)]
        self.hy_power_speed_list.append(self.hy_power_speed_list[-1])
        self.hy_power_speed_list_input = [0.01 * i for i in range(101)]
        self.hy_power_speed_list_input.append(self.hy_power_speed_list_input[-1])
        self.hy_reset()

    def hy_step(self, gen_speed=None, init=None):  # (0~1) in 15min
        # print('gen_speed', gen_speed)
        assert self.sty.capacity >= 0 * self.sty.capacity_mass, "111"
        if gen_speed is not None:
            assert 0 <= gen_speed <= 1

        def hy_speed(gen_speed_input):  # 0~1 -> g/s
            return gen_speed_input * self.v_h_max

        self.hvs.hvs_step(self.sys_time)

        # todo: !!!!!
        assert self.sty.capacity >= 0 * self.sty.capacity_mass, "222"
        # to make sure that soc is lower than 1 and greater than 0.1
        # must_charge = max(0, self.hvs.total_mass_need - (self.sty.capacity - self.sty.capacity_mass * 0.1))
        # must_charge = min(must_charge, self.sty.capacity_mass - self.sty.capacity)
        must_charge = max(0, self.sty.capacity_mass * 0.1 - self.sty.capacity)
        upper_charge = max(self.sty.capacity_mass - self.sty.capacity, 0)

        if gen_speed is not None:
            # todo
            charge_temp = max(min(hy_speed(gen_speed) * (15 * 60), upper_charge), must_charge)
            self.hy_flow_speed = charge_temp / (15 * 60)

        else:
            self.hy_flow_speed = max(min(self.hvs.total_mass_need, upper_charge), must_charge) / (15 * 60)

        self.hy_flow_speed = min(self.hy_flow_speed, self.v_h_max)
        self.hy_flow_speed_15 = 15 * 60 * self.hy_flow_speed

        self.ele_power = self.ele.get_power(self.hy_flow_speed)  # kW
        self.cpr_power = self.cpr.generate_W(self.hy_flow_speed)  # kW

        self.sty.sty_step(self.hy_flow_speed, self.hvs.total_mass_need)

        self.all_power_second = self.ele_power + self.cpr_power
        self.all_power_15 = self.all_power_second * 15 * 60
        self.sys_time += 1
        self.sys_time %= 96
        if init is not None:
            return self.all_power_second

    def hy_reset(self):
        self.hvs.hvs_reset()
        self.cpr.cpr_reset()
        self.sty.sty_reset()
        self.ele.ele_reset()
        self.hy_flow_speed = None  # g/s
        self.hy_flow_speed_15 = None  # g/15min
        self.ele_power = None
        self.cpr_power = None
        self.all_power_second = None
        self.all_power_15 = None
        self.sys_time = 0


# noinspection DuplicatedCode
class HyFCEVStation(object):
    def __init__(self, permeate=0.01):
        # hv property ; unit: g

        # # https://www.fueleconomy.gov/feg/fcv_sbs.shtml (360/66) (360/68)
        # # self.capacity_mass = 5.45 * 1000
        # #self.capacity_volume = (360 / 68) * 4.54609188 / 1000

        # https://en.wikipedia.org/wiki/Hyundai_Nexo
        self.capacity_mass = 6.3 * 1000  # g
        self.capacity_volume = 156 / 1000  # m^3
        self.max_pressure = 70  # Mpa

        print(self.capacity_mass)
        print(self.capacity_volume * 1000)

        # Impact of hydrogen SAE J2601 fueling methods on fueling time of light-duty fuel cell electric vehicles
        self.APRR_top_off = 7.2  # Mpa/min (0,5]MPa
        self.APRR_norm_val = 18.5  # Mpa/min (5,70]MPa

        self.lookup_table = [[0.50, 5.00, 10.0, 15.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0],
                             [87.4, 81.0, 86.8, 86.1, 85.4, 83.8, 82.2, 80.4, 78.5, 76.1]]

        # station property
        self.arrive_number = None
        self.arrive_soc_ini_list = []
        self.arrive_pressure_ini_list = []
        self.needed_time_list = []
        self.needed_hy_list = []
        self.arrive_number_sum = 0
        self.serve_number_sum = 0
        self.total_mass_need = None
        self.line = 0
        self.num = 0

        self.possible_in = 0.3
        self.permeability = permeate  # 0.01 by default

    def _hv_arrive(self, time):
        self.arrive_number = PoissonNumber.hv_car_number_wrt_poisson(time, self.possible_in, self.permeability)

    def hvs_step(self, time):
        time_interval = 15
        self._hvs_interval_reset()
        self._hv_arrive(time)
        self.arrive_number_sum += self.arrive_number
        for _ in range(self.arrive_number):
            self.arrive_soc_ini_list.append(CarArriveRandom.mk_soc())  # 0 - 100
            if self.arrive_soc_ini_list[-1] < 0.5: self.arrive_soc_ini_list[-1] = 0.5
            self.arrive_pressure_ini_list.append(self._soc_to_pressure(self.arrive_soc_ini_list[-1] * 0.01))
            needed_time, needed_mass = self._init_pressure_to_needed_time_and_mass(
                self.arrive_pressure_ini_list[-1])
            self.needed_time_list.append(needed_time)
            self.needed_hy_list.append(needed_mass)
        total_time_needed_for_this_time_interval = sum(self.needed_time_list)

        if total_time_needed_for_this_time_interval > time_interval:
            flag = True
            for i in range(self.arrive_number - 1):
                i += 1
                if sum(self.needed_time_list[:-i]) <= time_interval and flag:
                    self.line = i
                    self.num = len(self.needed_time_list[:-i])
                    flag = False
                    break
            self.total_mass_need = sum(self.needed_hy_list)
            self.needed_time_list = self.needed_time_list[self.num:]
            self.needed_hy_list = self.needed_hy_list[self.num:]
        else:
            self.total_mass_need = sum(self.needed_hy_list)
            self.line = 0
            self.num = len(self.needed_time_list)
            self.needed_hy_list = []
            self.needed_time_list = []

    def _hvs_interval_reset(self):
        self.arrive_number = None
        self.arrive_soc_ini_list = []
        self.arrive_pressure_ini_list = []
        self.total_mass_need = None
        self.num = 0

    def hvs_reset(self):
        self._hvs_interval_reset()
        self.needed_hy_list = []
        self.needed_time_list = []
        self.line = 0
        self.arrive_number_sum = 0
        self.serve_number_sum = 0

    def _soc_to_pressure(self, soc):  # (0~1)
        assert soc >= 0
        assert soc <= 1
        p_pressure = soc * self.max_pressure
        return p_pressure

    def _init_pressure_to_needed_time_and_mass(self, pressure_init):
        if pressure_init < 5:
            assert 69 - pressure_init > 0, "top off error!"
            time_need = (69 - pressure_init) / self.APRR_norm_val + (87.4 - 69) / self.APRR_top_off
            target_pressure = self.__init_to_target_pressure(pressure_init)
            mass_need = self.__pressure_to_mass(target_pressure) - self.__pressure_to_mass(pressure_init)
            return time_need, mass_need
        target_pressure = self.__init_to_target_pressure(pressure_init)
        APRR = self.__init_to_target_ramp_rate(pressure_init)
        assert target_pressure >= 0
        assert APRR >= 0
        time_need = (target_pressure - pressure_init) / APRR
        mass_need = self.__pressure_to_mass(target_pressure) - self.__pressure_to_mass(pressure_init)
        return time_need, mass_need

    # def __top_off(self, pressure_init):
    #     assert 69 - pressure_init > 0, "top off error!"
    #     time_need = (69 - pressure_init) / self.APRR_norm_val + (87.4 - 69) / self.APRR_top_off
    #     target_pressure = self.__init_to_target_pressure(pressure_init)
    #     mass_need = self.__pressure_to_mass(target_pressure) - self.__pressure_to_mass(pressure_init)
    #     return time_need, mass_need

    def __init_to_target_ramp_rate(self, pressure):
        if pressure < 5:
            return self.APRR_top_off
        elif 5 <= pressure < 70:
            return self.APRR_norm_val
        else:
            return 0

    def __init_to_target_pressure(self, pressure):
        if pressure < self.lookup_table[0][1]:
            return self.lookup_table[1][0]
        elif self.lookup_table[0][1] <= pressure < self.lookup_table[0][2]:
            return (self.lookup_table[1][2] - self.lookup_table[1][1]) / (
                    self.lookup_table[0][2] - self.lookup_table[0][1]) * (pressure - self.lookup_table[0][1]) + \
                   self.lookup_table[1][1]
        elif self.lookup_table[0][1 + 1] <= pressure < self.lookup_table[0][2 + 1]:
            a = 1
            return (self.lookup_table[1][2 + a] - self.lookup_table[1][1 + a]) / (
                    self.lookup_table[0][2 + a] - self.lookup_table[0][1 + a]) * (
                           pressure - self.lookup_table[0][1 + a]) + \
                   self.lookup_table[1][1 + a]
        elif self.lookup_table[0][1 + 2] <= pressure < self.lookup_table[0][2 + 2]:
            a = 2
            return (self.lookup_table[1][2 + a] - self.lookup_table[1][1 + a]) / (
                    self.lookup_table[0][2 + a] - self.lookup_table[0][1 + a]) * (
                           pressure - self.lookup_table[0][1 + a]) + \
                   self.lookup_table[1][1 + a]
        elif self.lookup_table[0][1 + 3] <= pressure < self.lookup_table[0][2 + 3]:
            a = 3
            return (self.lookup_table[1][2 + a] - self.lookup_table[1][1 + a]) / (
                    self.lookup_table[0][2 + a] - self.lookup_table[0][1 + a]) * (
                           pressure - self.lookup_table[0][1 + a]) + \
                   self.lookup_table[1][1 + a]
        elif self.lookup_table[0][1 + 4] <= pressure < self.lookup_table[0][2 + 4]:
            a = 4
            return (self.lookup_table[1][2 + a] - self.lookup_table[1][1 + a]) / (
                    self.lookup_table[0][2 + a] - self.lookup_table[0][1 + a]) * (
                           pressure - self.lookup_table[0][1 + a]) + \
                   self.lookup_table[1][1 + a]
        elif self.lookup_table[0][1 + 5] <= pressure < self.lookup_table[0][2 + 5]:
            a = 5
            return (self.lookup_table[1][2 + a] - self.lookup_table[1][1 + a]) / (
                    self.lookup_table[0][2 + a] - self.lookup_table[0][1 + a]) * (
                           pressure - self.lookup_table[0][1 + a]) + \
                   self.lookup_table[1][1 + a]
        elif self.lookup_table[0][1 + 6] <= pressure < self.lookup_table[0][2 + 6]:
            a = 6
            return (self.lookup_table[1][2 + a] - self.lookup_table[1][1 + a]) / (
                    self.lookup_table[0][2 + a] - self.lookup_table[0][1 + a]) * (
                           pressure - self.lookup_table[0][1 + a]) + \
                   self.lookup_table[1][1 + a]
        elif self.lookup_table[0][1 + 7] <= pressure <= self.lookup_table[0][2 + 7]:
            a = 7
            return (self.lookup_table[1][2 + a] - self.lookup_table[1][1 + a]) / (
                    self.lookup_table[0][2 + a] - self.lookup_table[0][1 + a]) * (
                           pressure - self.lookup_table[0][1 + a]) + \
                   self.lookup_table[1][1 + a]
        else:
            return pressure

    def __pressure_to_mass(self, pressure):
        return self.capacity_mass * (pressure / self.max_pressure)


class HFC(object):
    def __init__(self, hy_system, cell_number_=None):
        # cell_power 0.6kW ~ 1.0kW
        # https://link.springer.com/content/pdf/10.1007%2F978-1-84800-340-8.pdf
        # self.fuel_cell_power = [0.6000, 1.000]  # power  kW
        # self.consumption_rate = [0.0100, 0.016]  # consumption rate  g/s
        # set multiple fuel cell number
        if cell_number_ is None:
            self.cell_number = 100 * 1
        else:
            self.cell_number = cell_number_
        # hy system storage
        self.hy_store = hy_system.sty

    # 0 ~ 100kW
    def use_cell(self, fc_power, charging_p):  # from power to consumption rate  kW -> g in 15 min
        # 1kW*s = 1kJ    1kW*15 min = 900 kJ
        # 1 kg H^2 -> (lower heating value) 119.96MJ    1 g -> 119.6 kJ
        # https://www.energy.gov/sites/prod/files/2016/06/f32/fcto_fuel_cells_comparison_chart_apr2016.pdf
        # 60% efficiency 1kW *15min 900/0.6 kJ=1500kJ -> 1500/119.6 g
        # 1kW -> 1500/119.6 g ()
        if fc_power > self.cell_number:
            fc_power = self.cell_number
        elif fc_power < 0:
            fc_power = 0
        elif fc_power > charging_p:
            fc_power = charging_p
        hy_to_use = fc_power * 1500 / 119.6

        hy_to_use = min(self.hy_store.capacity, hy_to_use)
        self.hy_to_use = hy_to_use
        true_power = hy_to_use * 119.6 / 1500
        true_power = max(0, fc_power)

        self.hy_store.capacity -= hy_to_use

        return hy_to_use, true_power


if __name__ == '__main__':
    pass
