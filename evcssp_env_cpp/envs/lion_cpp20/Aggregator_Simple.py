import os
import sys
import pickle
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pyevstation import SlowChargeStation, FastChargeStation, Vector_float

file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '../data_file/price_data/price_after_MAD_96.pkl')

with open(file_name, 'rb') as fo:
    mean_for_MAD = pickle.load(fo)


class HubAggregator_v2(object):

    def __init__(self, station_list, station_type_list, constant_charging=False):
        self.constant_charging = constant_charging
        self.wait = True

        self.aggregator_time_hole = 0
        assert isinstance(station_list, list), 'station_list must be a list of pile numbers'
        assert len(station_list) == len(station_type_list) == 2, 'station_type_list must have the same length of station_list'
        self.station_list = station_list
        self.station_type_list = station_type_list
        self.station_number = 2
        self.pile_number = station_list

        self.price_constant = mean_for_MAD
        self.price = [] + mean_for_MAD
        self.price_max = max(self.price)
        self.price_min = min(self.price)

        self.evcssp_max_demand = None
        self.evcssp_min_demand = None
        self.evcssp_charge_power = None
        self.evcs_charge_power_aims_on_off = None

        self.evcssp_evs_objects = []  # only has one charging hub in this class
        self._make_evs_list()

        self.flag_consult_middle_agent = False

        # consult the maximum charging power
        self.total_max_power = 0
        for station in self.evcssp_evs_objects:
            self.total_max_power += station.transformer_limit

        self.consult_all_evcs_power()

    def consult_middle_agent(self, charging_or_not_list):
        charging_or_not_list = list(charging_or_not_list)

        assert isinstance(charging_or_not_list, list), 'action output should be a list'
        assert len(charging_or_not_list) == sum(self.pile_number), 'length of charging_or_not_list must equal to pile number'

        self.evcs_charge_power_aims_on_off = charging_or_not_list
        self.flag_consult_middle_agent = True

    def ag_step(self, simulate=False):
        assert simulate is False, 'simulation is not allowed in HubAggregator'
        assert self.flag_consult_middle_agent is True, 'charging action should be accessed before env iteration'

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

        if not simulate:
            # update real time price
            self.price.append(mean_for_MAD[self.aggregator_time_hole])

            # update env time
            self.aggregator_time_hole += 1
            self.aggregator_time_hole %= 96

        self.flag_consult_middle_agent = False

        self.consult_all_evcs_power()

    def ag_reset(self):
        for station in self.evcssp_evs_objects:
            station.evs_reset()
        self.aggregator_time_hole = 0
        self.price = [] + mean_for_MAD

        self.evcssp_max_demand = None
        self.evcssp_min_demand = None
        self.consult_all_evcs_power()

    def _make_evs_list(self):
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
    pass
