import os
import sys
import pickle
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pyevstation import SlowChargeStation, FastChargeStation, Vector_float

file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '../data_file/price_data/price_after_MAD_96.pkl')

with open(file_name, 'rb') as fo:
    # price_mean = 22.578910431309936
    # price_std = 3.537822280277024
    mean_for_MAD = pickle.load(fo)


# from My_RL.Agent.Aggregator_Agent import TopAgent, MiddleAgent


class Aggregator(object):
    """电动汽车充电站运营商 EVCSSP

    EVCSSP

    Attributes:
        aggregator_time_hole (int): 运营商提供的时间
        station_list (list): 所管辖 EVCS 的列表
        station_type_list (list): 所管辖 EVCS 类型的列表
        station_number (int): 所管辖 EVCS 的数量
        evcssp_max_demand (float): 所有 EVCS 集合的最大负荷
        evcssp_min_demand (float): 所有 EVCS 集合的最小负荷
        evcssp_charge_power (float): 所有 EVCS 集合的当前负荷
        evcssp_charge_power_aim (float): 所有 EVCS 集合的当前目标负荷
        evcs_charge_power_aims (list): 各个EVCS的目标充电负荷
        evcssp_evs_objects (list): EVCS 对象形成的列表 ####
        flag_consult_top_agent (bool): 是否获取上层智能体动作
        flag_consult_middle_agent (bool): 是否获取下层智能体动作
        total_max_power(float): maximum power of the stations this aggregator owned
        price_constant(float): the recorded price data
        price(float): real_time_price_list
    """

    def __init__(self, station_list, station_type_list, constant_charging=False):
        """init

        详细描述：初始化

        Args:
             station_list (list): 输入 所管辖 EVCS 的列表
             station_type_list (list): 输入 所管辖 EVCS 类型的列表

        Returns:
            无
        """
        self.constant_charging = constant_charging
        self.wait = True
        # 电动汽车充电站运营商时间
        self.aggregator_time_hole = 0
        assert isinstance(station_list, list), 'Aggregator类的输入必须是一张元素为每个电动汽车充电站充电桩个数，元素个数为充电站个数的列表'
        assert len(station_list) == len(station_type_list), '电动汽车充电站车位数列表与类型数列表长度不一致'
        self.station_list = station_list
        self.station_type_list = station_type_list
        self.station_number = len(self.station_list)

        # 电网侧发布的电价
        self.price_constant = mean_for_MAD
        self.price = [] + mean_for_MAD
        self.price_max = max(self.price)
        self.price_min = min(self.price)

        # 最大最小充电负荷
        self.evcssp_max_demand = None
        self.evcssp_min_demand = None
        # 充电负荷
        self.evcssp_charge_power = None

        # 充电功率目标（上层的输出、下层的输入之一）
        self.evcssp_charge_power_aim = 0

        # 各个充电站的充电功率目标向量（下层的输出）
        self.evcs_charge_power_aims = None

        # 所管辖的EVS的列表
        self.evcssp_evs_objects = []
        self._make_evs_list()

        self.flag_consult_top_agent = False
        self.flag_consult_middle_agent = False

        # consult the maximum charging power
        self.total_max_power = 0
        for station in self.evcssp_evs_objects:
            self.total_max_power += station.transformer_limit

        self.consult_all_evcs_power()

    def consult_top_agent(self, top_charge_power):
        """获取上层智能体的输出结果

        详细描述：该函数被上层智能体调用，设置所有 EVCS的功率总和

        Args:
             top_charge_power (float): 上层智能体设置的目标充电功率
             self

        Returns:
            无
        """
        self.evcssp_charge_power_aim = top_charge_power
        self.flag_consult_top_agent = True
        pass

    def consult_middle_agent(self, middle_charge_power_input):
        """电动汽车充电站运营商状态迭代

        详细描述：该函数被下层智能体调用，下层智能体根据上层智能体给出的总功率目标，设置所有 EVCS各自的功率

        Args:
             middle_charge_power_input (np.ndarray): 目标充电功率(调整)列表
             self

        Returns:
            无
        """
        # 先检查上层智能体是否调用过 consult_top_agent函数
        assert self.flag_consult_top_agent is True, '在获取下层的动作结果前应该先获取上层的动作结果'

        middle_charge_power_list = list(middle_charge_power_input)

        assert isinstance(middle_charge_power_list, list), '下层智能体的输出应为列表'
        assert len(middle_charge_power_list) == self.station_number, '该列表的长度应与EVCS的数量相同'

        # 赋值每个EVCS充电目标
        self.evcs_charge_power_aims = middle_charge_power_list
        self.flag_consult_middle_agent = True
        pass

    def ag_step(self, simulate=False):
        """电动汽车充电站运营商状态迭代

        详细描述：调用该函数前应已经调用过函数 consult_top_agent以及 函数 consult_middle_agent，
                各个EVCS按目标执行充电，并最终返回各自的充电功率

        Args:
             simulate (bool): finally take action in one top agent time step
             self

        Returns:
            实际EVCSSP的总充电功率以及各EVCS的实际充电功率
        """
        assert self.flag_consult_top_agent is True, '在环境迭代前应该先获取上层的动作设置的目标'
        assert self.flag_consult_middle_agent is True, '在环境迭代前应该先获取下层的动作设置的目标'
        for power, station in zip(self.evcs_charge_power_aims, self.evcssp_evs_objects):
            power_clip = np.clip(power, station.min_power, station.max_power)

            if simulate:
                station.evs_step(power_clip, test=True)
            else:
                station.evs_step(power_clip)

        # 重置智能体是否访问标签，以便下次迭代使用
        if not simulate:
            # self.flag_consult_top_agent = False
            # print('self.price[-1]-1', self.price[-1])
            # update real time price
            self.price.append(mean_for_MAD[self.aggregator_time_hole])

            # update env time
            self.aggregator_time_hole += 1
            self.aggregator_time_hole %= 96

            # print('self.price[-1]', self.price[-1])

        self.flag_consult_middle_agent = False

        self.consult_all_evcs_power()

    def ag_reset(self):
        """电动汽车充电站运营商状态重置 every episode

        详细描述：reset station； 最大功率、充电功率、充电目标置0

        Args:
            self

        Returns:
            无
        """
        for station in self.evcssp_evs_objects:
            station.evs_reset()
        self.aggregator_time_hole = 0
        self.price = [] + mean_for_MAD
        # TODO:下面三个属性的操作
        self.evcssp_max_demand = None
        self.evcssp_min_demand = None
        self.evcssp_charge_power_aim = None
        self.consult_all_evcs_power()

    def _make_evs_list(self):
        """制作电动汽车充电站对象列表

        详细描述：若 station_type_list中的元素为 slow 则设置对象为慢充 EVCS；若元素为 fast 则设置对象为快充 EVCS

        Args:
            self

        Returns:
            无
        """
        for pile_number, evs_type in zip(self.station_list, self.station_type_list):
            if evs_type == 'slow':
                self.evcssp_evs_objects.append(
                    SlowChargeStation(pile_number, self.wait, self.constant_charging))
            elif evs_type == 'fast':
                self.evcssp_evs_objects.append(
                    FastChargeStation(pile_number, self.wait, self.constant_charging))
            else:
                raise ValueError('EVS类型列表中的元素必须是 fast 或者 slow')

    def consult_all_evcs_power(self):
        self.evcssp_charge_power = 0
        self.evcssp_max_demand = 0
        self.evcssp_min_demand = 0
        for station in self.evcssp_evs_objects:
            self.evcssp_charge_power += station.charge_power
            self.evcssp_max_demand += station.max_power
            self.evcssp_min_demand += station.min_power


# DO NOT USE THIS VERSION
class HubAggregator(object):
    """电动汽车充电站运营商 EVCSSP

    EVCSSP

    Attributes:
        aggregator_time_hole (int): 运营商提供的时间
        station_list (list): 所管辖 EVCS 的列表
        station_type_list (list): 所管辖 EVCS 类型的列表
        station_number (int): 所管辖 EVCS 的数量
        evcssp_max_demand (float): 所有 EVCS 集合的最大负荷
        evcssp_min_demand (float): 所有 EVCS 集合的最小负荷
        evcssp_charge_power (float): 所有 EVCS 集合的当前负荷
        evcssp_charge_power_aim (float): 所有 EVCS 集合的当前目标负荷
        evcs_charge_power_aims (list): 各个EVCS的目标充电负荷
        evcssp_evs_objects (list): EVCS 对象形成的列表 ####
        flag_consult_middle_agent (bool): 是否获取智能体动作
        total_max_power(float): maximum power of the stations this aggregator owned
        price_constant(float): the recorded price data
        price(float): real_time_price_list
    """

    def __init__(self, station_list, station_type_list, constant_charging=False):
        """init

        详细描述：初始化

        Args:
             station_list (list): 输入 所管辖 EVCS 的列表
             station_type_list (list): 输入 所管辖 EVCS 类型的列表

        Returns:
            无
        """
        self.constant_charging = constant_charging
        self.wait = True
        # 电动汽车充电站运营商时间
        self.aggregator_time_hole = 0
        assert isinstance(station_list, list), 'Aggregator类的输入必须是一张元素为每个电动汽车充电站充电桩个数，元素个数为充电站个数的列表'
        assert len(station_list) == len(station_type_list), '电动汽车充电站车位数列表与类型数列表长度不一致'
        self.station_list = station_list
        self.station_type_list = station_type_list
        self.station_number = len(self.station_list)

        # 电网侧发布的电价
        self.price_constant = mean_for_MAD
        self.price = [] + mean_for_MAD
        self.price_max = max(self.price)
        self.price_min = min(self.price)

        # 最大最小充电负荷
        self.evcssp_max_demand = None
        self.evcssp_min_demand = None
        # 充电负荷
        self.evcssp_charge_power = None

        # 充电功率目标（上层的输出、下层的输入之一）
        self.evcssp_charge_power_aim = 0

        # 各个充电站的充电功率目标向量（下层的输出）
        self.evcs_charge_power_aims = None

        # 所管辖的EVS的列表
        self.evcssp_evs_objects = []
        self._make_evs_list()

        # self.flag_consult_top_agent = False
        self.flag_consult_middle_agent = False

        # consult the maximum charging power
        self.total_max_power = 0
        for station in self.evcssp_evs_objects:
            self.total_max_power += station.transformer_limit

        self.consult_all_evcs_power()

    def consult_middle_agent(self, middle_charge_power_input):
        """电动汽车充电站运营商状态迭代

        详细描述：该函数被下层智能体调用，下层智能体根据上层智能体给出的总功率目标，设置所有 EVCS各自的功率

        Args:
             middle_charge_power_input (np.ndarray): 目标充电功率(调整)列表
             self

        Returns:
            无
        """
        # # 先检查上层智能体是否调用过 consult_top_agent函数
        # assert self.flag_consult_top_agent is True, '在获取下层的动作结果前应该先获取上层的动作结果'

        middle_charge_power_list = list(middle_charge_power_input)

        assert isinstance(middle_charge_power_list, list), '下层智能体的输出应为列表'
        assert len(middle_charge_power_list) == self.station_number, '该列表的长度应与EVCS的数量相同'

        # 赋值每个EVCS充电目标
        self.evcs_charge_power_aims = middle_charge_power_list
        self.flag_consult_middle_agent = True
        pass

    def ag_step(self, simulate=False):
        """电动汽车充电站运营商状态迭代

        详细描述：调用该函数前应已经调用过函数 consult_middle_agent，
                各个EVCS按目标执行充电，并最终返回各自的充电功率

        Args:
             simulate (bool): finally take action in one top agent time step, namely lower agent can adjust action in one upper agent step
             self

        Returns:
            实际EVCSSP的总充电功率以及各EVCS的实际充电功率
        """
        assert simulate is False, 'simulation is not allowed in HubAggregator'
        assert self.flag_consult_middle_agent is True, '在环境迭代前应该先获取下层的动作设置的目标'
        for power, station in zip(self.evcs_charge_power_aims, self.evcssp_evs_objects):
            power_clip = np.clip(power, station.min_power, station.max_power)

            if simulate:
                pass
                station.evs_step(power_clip, test=True)
            else:
                station.evs_step(power_clip)

        # 重置智能体是否访问标签，以便下次迭代使用
        if not simulate:
            # update real time price
            self.price.append(mean_for_MAD[self.aggregator_time_hole])

            # update env time
            self.aggregator_time_hole += 1
            self.aggregator_time_hole %= 96

        self.flag_consult_middle_agent = False

        self.consult_all_evcs_power()

    def ag_reset(self):
        """电动汽车充电站运营商状态重置 every episode

        详细描述：reset station； 最大功率、充电功率、充电目标置0

        Args:
            self

        Returns:
            无
        """
        for station in self.evcssp_evs_objects:
            station.evs_reset()
        self.aggregator_time_hole = 0
        self.price = [] + mean_for_MAD

        self.evcssp_max_demand = None
        self.evcssp_min_demand = None
        self.evcssp_charge_power_aim = None
        self.consult_all_evcs_power()

    def _make_evs_list(self):
        """制作电动汽车充电站对象列表

        详细描述：若 station_type_list中的元素为 slow 则设置对象为慢充 EVCS；若元素为 fast 则设置对象为快充 EVCS

        Args:
            self

        Returns:
            无
        """
        for pile_number, evs_type in zip(self.station_list, self.station_type_list):
            if evs_type == 'slow':
                self.evcssp_evs_objects.append(
                    SlowChargeStation(pile_number, self.wait, self.constant_charging))
            elif evs_type == 'fast':
                self.evcssp_evs_objects.append(
                    FastChargeStation(pile_number, self.wait, self.constant_charging))
            else:
                raise ValueError('EVS type must be fast or slow')

    def consult_all_evcs_power(self):
        self.evcssp_charge_power = 0
        self.evcssp_max_demand = 0
        self.evcssp_min_demand = 0
        self.ag_car_number = []
        self.ag_flow_in_number = []
        self.ag_load_assigned = []
        for station in self.evcssp_evs_objects:
            self.evcssp_charge_power += station.charge_power
            self.evcssp_max_demand += station.max_power
            self.evcssp_min_demand += station.min_power
            self.ag_car_number.append(station.car_number)
            self.ag_flow_in_number.append(station.flow_in_number)
            self.ag_load_assigned.append(station.load_assigned)


# DO NOT USE THIS VERSION
class HubAggregator_v2_old(object):
    """电动汽车充电站运营商 EVCSSP

    EVCSSP

    Attributes:
        aggregator_time_hole (int): 运营商提供的时间
        station_list (list): 所管辖 EVCS 的列表
        station_type_list (list): 所管辖 EVCS 类型的列表
        station_number (int): 所管辖 EVCS 的数量
        evcssp_max_demand (float): 所有 EVCS 集合的最大负荷
        evcssp_min_demand (float): 所有 EVCS 集合的最小负荷
        evcssp_charge_power (float): 所有 EVCS 集合的当前负荷
        evcssp_charge_power_aim (float): 所有 EVCS 集合的当前目标负荷
        evcs_charge_power_aims_on_off (list): EVCS 各 pile 充电状态
        evcssp_evs_objects (list): EVCS 对象形成的列表 ####
        flag_consult_middle_agent (bool): 是否获取智能体动作
        total_max_power(float): maximum power of the stations this aggregator owned
        price_constant(float): the recorded price data
        price(float): real_time_price_list
    """

    def __init__(self, station_list, station_type_list, constant_charging=False):
        """init

        详细描述：初始化

        Args:
             station_list (list): 输入 所管辖 EVCS 的列表
             station_type_list (list): 输入 所管辖 EVCS 类型的列表

        Returns:
            无
        """
        self.constant_charging = constant_charging
        self.wait = True
        # 电动汽车充电站运营商时间
        self.aggregator_time_hole = 0
        assert isinstance(station_list, list), 'Aggregator类的输入必须是一张元素为每个电动汽车充电站充电桩个数，元素个数为充电站个数的列表'
        assert len(station_list) == len(station_type_list) == 1, '电动汽车充电站车位数列表与类型数列表长度不一致'
        self.station_list = station_list
        self.station_type_list = station_type_list
        self.station_number = len(self.station_list)
        self.pile_number = self.station_list[0]

        # 电网侧发布的电价
        self.price_constant = mean_for_MAD
        self.price = [] + mean_for_MAD
        self.price_max = max(self.price)
        self.price_min = min(self.price)

        # 最大最小充电负荷
        self.evcssp_max_demand = None
        self.evcssp_min_demand = None
        # 充电负荷
        self.evcssp_charge_power = None

        # 充电功率目标（上层的输出、下层的输入之一）
        self.evcssp_charge_power_aim = 0

        # 各个充电站的充电功率目标向量（下层的输出）
        self.evcs_charge_power_aims_on_off = None

        # 所管辖的EVS的列表
        self.evcssp_evs_objects = []  # only has one charging hub in this class
        self._make_evs_list()

        # self.flag_consult_top_agent = False
        self.flag_consult_middle_agent = False

        # consult the maximum charging power
        self.total_max_power = 0
        for station in self.evcssp_evs_objects:
            self.total_max_power += station.transformer_limit

        self.consult_all_evcs_power()

    def consult_middle_agent(self, charging_or_not_list):
        """电动汽车充电站运营商状态迭代

        详细描述：该函数被下层智能体调用，下层智能体根据上层智能体给出的总功率目标，设置所有 EVCS各自的功率

        Args:
             middle_charge_power_input (np.ndarray): 目标充电功率(调整)列表
             self

        Returns:
            无
        """
        # # 先检查上层智能体是否调用过 consult_top_agent函数
        # assert self.flag_consult_top_agent is True, '在获取下层的动作结果前应该先获取上层的动作结果'

        # print(3333343434343, len(charging_or_not_list))
        charging_or_not_list = list(charging_or_not_list)

        assert isinstance(charging_or_not_list, list), '下层智能体的输出应为列表'
        assert len(charging_or_not_list) == self.pile_number, '该列表的长度应与EVCS的数量相同'

        # 赋值每个EVCS充电目标
        self.evcs_charge_power_aims_on_off = charging_or_not_list
        self.flag_consult_middle_agent = True
        pass

    def ag_step(self, simulate=False):
        """电动汽车充电站运营商状态迭代

        详细描述：调用该函数前应已经调用过函数 consult_middle_agent，
                各个EVCS按目标执行充电，并最终返回各自的充电功率

        Args:
             simulate (bool): finally take action in one top agent time step, namely lower agent can adjust action in one upper agent step
             self

        Returns:
            实际EVCSSP的总充电功率以及各EVCS的实际充电功率
        """
        assert simulate is False, 'simulation is not allowed in HubAggregator'
        assert self.flag_consult_middle_agent is True, '在环境迭代前应该先获取下层的动作设置的目标'

        assign_actions = Vector_float()
        for it in self.evcs_charge_power_aims_on_off:
            assign_actions.append(it)

        self.evcssp_evs_objects[0].evs_step(assign_actions)  # assign actions for only one charging hub

        # 重置智能体是否访问标签，以便下次迭代使用
        if not simulate:
            # update real time price
            self.price.append(mean_for_MAD[self.aggregator_time_hole])

            # update env time
            self.aggregator_time_hole += 1
            self.aggregator_time_hole %= 96

        self.flag_consult_middle_agent = False

        self.consult_all_evcs_power()

    def ag_reset(self):
        """电动汽车充电站运营商状态重置 every episode

        详细描述：reset station； 最大功率、充电功率、充电目标置0

        Args:
            self

        Returns:
            无
        """
        for station in self.evcssp_evs_objects:
            station.evs_reset()
        self.aggregator_time_hole = 0
        self.price = [] + mean_for_MAD

        self.evcssp_max_demand = None
        self.evcssp_min_demand = None
        self.evcssp_charge_power_aim = None
        self.consult_all_evcs_power()

    def _make_evs_list(self):
        """制作电动汽车充电站对象列表

        详细描述：若 station_type_list中的元素为 slow 则设置对象为慢充 EVCS；若元素为 fast 则设置对象为快充 EVCS

        Args:
            self

        Returns:
            无
        """
        for pile_number, evs_type in zip(self.station_list, self.station_type_list):
            if evs_type == 'slow':
                self.evcssp_evs_objects.append(
                    SlowChargeStation(pile_number, self.wait, self.constant_charging))
            elif evs_type == 'fast':
                self.evcssp_evs_objects.append(
                    FastChargeStation(pile_number, self.wait, self.constant_charging))
            else:
                raise ValueError('EVS type must be fast or slow')

    def consult_all_evcs_power(self):
        self.evcssp_charge_power = 0
        self.evcssp_max_demand = 0
        self.evcssp_min_demand = 0
        self.ag_car_number = []
        self.ag_flow_in_number = []
        self.ag_load_assigned = []
        for station in self.evcssp_evs_objects:
            self.evcssp_charge_power += station.charge_power
            self.evcssp_max_demand += station.max_power
            self.evcssp_min_demand += station.min_power
            self.ag_car_number.append(station.car_number)
            flow_in_number_list = [i for i in station.flow_in_number]
            self.ag_flow_in_number.append(flow_in_number_list[-1])
            self.ag_load_assigned.append(station.load_assigned)


class HubAggregator_v2(object):
    """电动汽车充电站运营商 EVCSSP

    EVCSSP

    Attributes:
        aggregator_time_hole (int): 运营商提供的时间
        station_list (list): 所管辖 EVCS 的列表
        station_type_list (list): 所管辖 EVCS 类型的列表
        station_number (int): 所管辖 EVCS 的数量
        evcssp_max_demand (float): 所有 EVCS 集合的最大负荷
        evcssp_min_demand (float): 所有 EVCS 集合的最小负荷
        evcssp_charge_power (float): 所有 EVCS 集合的当前负荷
        evcs_charge_power_aims_on_off (list): EVCS 各 pile 充电状态
        evcssp_evs_objects (list): EVCS 对象形成的列表 ####
        flag_consult_middle_agent (bool): 是否获取智能体动作
        total_max_power(float): maximum power of the stations this aggregator owned
        price_constant(float): the recorded price data
        price(float): real_time_price_list
    """

    def __init__(self, station_list, station_type_list, constant_charging=False):
        """init

        详细描述：初始化

        Args:
             station_list (list): 输入 所管辖 EVCS 的列表
             station_type_list (list): 输入 所管辖 EVCS 类型的列表

        Returns:
            无
        """
        self.constant_charging = constant_charging
        self.wait = True
        # 电动汽车充电站运营商时间
        self.aggregator_time_hole = 0
        assert isinstance(station_list, list), 'Aggregator类的输入必须是一张元素为每个电动汽车充电站充电桩个数，元素个数为充电站个数的列表'
        assert len(station_list) == len(station_type_list) == 2, '电动汽车充电站车位数列表与类型数列表长度不一致'
        self.station_list = station_list
        self.station_type_list = station_type_list
        self.station_number = 2
        self.pile_number = station_list

        # 电网侧发布的电价
        self.price_constant = mean_for_MAD
        self.price = [] + mean_for_MAD
        self.price_max = max(self.price)
        self.price_min = min(self.price)

        # 最大最小充电负荷
        self.evcssp_max_demand = None
        self.evcssp_min_demand = None
        # 充电负荷
        self.evcssp_charge_power = None

        # 各个充电站的充电功率目标向量（下层的输出）
        self.evcs_charge_power_aims_on_off = None

        # 所管辖的EVS的列表
        self.evcssp_evs_objects = []  # only has one charging hub in this class
        self._make_evs_list()

        # self.flag_consult_top_agent = False
        self.flag_consult_middle_agent = False

        # consult the maximum charging power
        self.total_max_power = 0
        for station in self.evcssp_evs_objects:
            self.total_max_power += station.transformer_limit

        self.consult_all_evcs_power()

    def consult_middle_agent(self, charging_or_not_list):
        """电动汽车充电站运营商状态迭代

        详细描述：该函数被下层智能体调用，下层智能体根据上层智能体给出的总功率目标，设置所有 EVCS各自的功率

        Args:
             middle_charge_power_input (np.ndarray): 目标充电功率(调整)列表
             self

        Returns:
            无
        """
        # # 先检查上层智能体是否调用过 consult_top_agent函数
        # assert self.flag_consult_top_agent is True, '在获取下层的动作结果前应该先获取上层的动作结果'

        charging_or_not_list = list(charging_or_not_list)

        assert isinstance(charging_or_not_list, list), 'action的输出应为列表'
        assert len(charging_or_not_list) == sum(self.pile_number), '该二维列表的长度应与EVCS的数量相同'

        # 赋值每个EVCS充电目标
        self.evcs_charge_power_aims_on_off = charging_or_not_list
        self.flag_consult_middle_agent = True

    def ag_step(self, simulate=False):
        """电动汽车充电站运营商状态迭代

        详细描述：调用该函数前应已经调用过函数 consult_middle_agent，
                各个EVCS按目标执行充电，并最终返回各自的充电功率

        Args:
             simulate (bool): finally take action in one top agent time step, namely lower agent can adjust action in one upper agent step
             self

        Returns:
            实际EVCSSP的总充电功率以及各EVCS的实际充电功率
        """
        assert simulate is False, 'simulation is not allowed in HubAggregator'
        assert self.flag_consult_middle_agent is True, '在环境迭代前应该先获取充电动作'

        assign_actions_slow = Vector_float()
        assign_actions_fast = Vector_float()
        # assign_actions = [assign_actions_slow, assign_actions_fast]

        for ind, it in zip(range(len(self.evcs_charge_power_aims_on_off)), self.evcs_charge_power_aims_on_off):
            if ind < self.pile_number[0]:
                assign_actions_slow.append(it)
            else:
                assign_actions_fast.append(it)

        self.evcssp_evs_objects[0].evs_step(assign_actions_slow)  # assign actions charging hub
        self.evcssp_evs_objects[1].evs_step(assign_actions_fast)  # assign actions charging hub

        # 重置智能体是否访问标签，以便下次迭代使用
        if not simulate:
            # update real time price
            self.price.append(mean_for_MAD[self.aggregator_time_hole])

            # update env time
            self.aggregator_time_hole += 1
            self.aggregator_time_hole %= 96

        self.flag_consult_middle_agent = False

        self.consult_all_evcs_power()

    def ag_reset(self):
        """电动汽车充电站运营商状态重置 every episode

        详细描述：reset station； 最大功率、充电功率、充电目标置0

        Args:
            self

        Returns:
            无
        """
        for station in self.evcssp_evs_objects:
            station.evs_reset()
        self.aggregator_time_hole = 0
        self.price = [] + mean_for_MAD

        self.evcssp_max_demand = None
        self.evcssp_min_demand = None
        self.consult_all_evcs_power()

    def _make_evs_list(self):
        """制作电动汽车充电站对象列表

        详细描述：若 station_type_list中的元素为 slow 则设置对象为慢充 EVCS；若元素为 fast 则设置对象为快充 EVCS

        Args:
            self

        Returns:
            无
        """
        for pile_number, evs_type in zip(self.station_list, self.station_type_list):
            if evs_type == 'slow':
                self.evcssp_evs_objects.append(
                    SlowChargeStation(pile_number, self.wait, self.constant_charging))
            elif evs_type == 'fast':
                self.evcssp_evs_objects.append(
                    FastChargeStation(pile_number, self.wait, self.constant_charging))
            else:
                raise ValueError('EVS type must be fast or slow')

    def consult_all_evcs_power(self):
        self.evcssp_charge_power = 0
        self.evcssp_charge_power_list = []
        self.evcssp_max_demand = 0
        self.evcssp_min_demand = 0
        self.ag_car_number = []
        self.ag_flow_in_number = []
        self.ag_full = []
        for station in self.evcssp_evs_objects:
            self.evcssp_charge_power_list.append(station.charge_power)
            self.evcssp_charge_power += station.charge_power
            self.evcssp_max_demand += station.max_power
            self.evcssp_min_demand += station.min_power
            self.ag_car_number.append(station.car_number)
            self.ag_full.append(True if station.car_number >= station.charge_number else False)
            flow_in_number_list = [i for i in station.flow_in_number]
            self.ag_flow_in_number.append(flow_in_number_list[-1])


if __name__ == '__main__':
    # EVCS_list = [5, 20, 15, 20, 5]
    # EVCS_type_list = ['fast', 'fast', 'slow', 'fast', 'fast']
    # agg = Aggregator(EVCS_list, EVCS_type_list)
    print(1)
    pass
