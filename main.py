import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import pathlib
import csv

motors_path = "data/motors.csv"
motors_df = pd.read_csv(motors_path)
prop_array = []
props = []
motors_array = []
watts_array = []
prop_apc_lines_array = []
prop_apc_array = []
propellers_array = []
prop_rpm = []
prop_rpm_array = []
potencias = []
potencias_array = []
pwr_list = []
thrust_list = []
pwr_list_array = []
v_list = []
decay_coeff_array = []
output = [
    ["Motor", "Propeller", "Static Thrust", "Decay Coeff"]
]

output_path = "data/output.csv"

k = 0

for i in range(len(motors_df)):
    potencia = motors_df.loc[i, 'W']
    Prop_motor = motors_df.loc[i, 'Prop']
    motor = motors_df.loc[i, 'Motor']
    try:
        prop_apc = pd.read_csv(f'data/propellers/{Prop_motor}.csv')
    except Exception:
        print(f'hélice {Prop_motor} nao encontrada!')
        continue

    prop_apc = prop_apc.groupby('RPM')

    pwr_list = []
    v_list = []
    thrust_list = []
    pwr_list_array = []
    v_list_array = []
    thrust_list_array = []

    for rpm, grupo in prop_apc:
        pwr = grupo['PWR'].tolist()
        thrust = grupo['Thrust'].tolist()
        v = grupo['V'].tolist()
        pwr_list.append(pwr)
        v_list.append(v)
        thrust_list.append(thrust)
    pwr_list_array.append(pwr_list)
    v_list_array.append(v_list)
    thrust_list_array.append(thrust_list)

    for p in range(len(pwr_list_array[0])):
        try:
            if potencia - 8 < (float(pwr_list_array[0][p][-1]) * 745.7) < potencia + 8:
                thrust_calculus = thrust_list_array[0][p]
                v_calculus = v_list_array[0][p]
                decay_coeff = (float(thrust_calculus[-1]) - float(thrust_calculus[0])) / (float(v_calculus[-1]) - float(v_calculus[0]))

                output.append(
                    [f"{motor}", f"{Prop_motor}", f"{(float(thrust_list_array[0][p][0]) * 4.448)}", f"{decay_coeff}"]
                )
        except Exception:
            pass

with open(output_path, mode='w', newline='') as arquivo_csv:
    escritor_csv = csv.writer(arquivo_csv)

    for linha in output:
        escritor_csv.writerow(linha)
