import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import pathlib

motors_path = "data/motors.csv"
motors_df = pd.read_csv(motors_path)
prop_array = []
motors_array = []
watts_array = []
i = 0

for row in motors_df:
    for line in motors_df[row]:
        if i == 0:
            motors_array.append(line)
        elif i == 1:
            prop_array.append(line)
        else:
            watts_array.append(line)
    i += 1

print(motors_array)
# print(motors_df["W"])
# print(motors_df["Motor"])
