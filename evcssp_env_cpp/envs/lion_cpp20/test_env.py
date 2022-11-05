import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print(1111111111111)
from pystation import SlowChargeStation, FastChargeStation, Vector_float

# TS.evs_step(TS.max_power)
# # print(TS.max_power)


sc = SlowChargeStation(5)
sc.evs_reset()

day = 1
car_number_list = [[] for _ in range(day)]

action = Vector_float()
action_original = [1.0, 1.0, 1.0, 1.0, 1.0]
for it in action_original:
    action.append(it)

for i in range(96 * day):
    if (i // 96) != ((i - 1) // 96):
        sc.evs_reset()
    # sc.calculate_output()
    print(11111111111111, sc.max_power)
    sc.evs_step(action)
    car_number_list[i // 96].append(sc.car_number)
