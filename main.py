import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import pathlib
import csv
from scipy.interpolate import interp1d

output = [
    ["Motor", "Propeller", "Static Thrust", "Decay Coeff", "Mass", "Voltage"]
]

def create_polynom(x, y, degree):
    coeffs = np.polyfit(x, y, degree)
    return coeffs

def numero_mais_proximo(lista, alvo):
    if not lista:
        raise ValueError("A lista não pode estar vazia")

    numero_mais_proximo = lista[0]
    diferenca_mais_proxima = abs(float(alvo) - float(lista[0]))

    for numero in lista[1:]:
        diferenca_atual = abs(float(alvo) - float(numero))
        if diferenca_atual < diferenca_mais_proxima:
            numero_mais_proximo = numero
            diferenca_mais_proxima = diferenca_atual

    return numero_mais_proximo


motors_path = "data/motors.csv"
motors_dataframe = pd.read_csv(motors_path)

for index, row in motors_dataframe.iterrows():

    # print (f'Índice: {index}, '
    #       f'Motor: {row["Motor"]}, '
    #       f'Hélice: {row["Prop"]}, '
    #       f'Tensão: {row["U"]}, '
    #       f'Potência: {row["W"]}, '
    #       f'Massa: {row["Mass"]}')

    potencia_motor = row["W"] / 745.7

    prop_motor_df = row["Prop"]

    prop_datasheet = pd.read_csv(f'data/propellers/{prop_motor_df}.csv')

    last_pwr = prop_datasheet.groupby('RPM')['PWR'].first().reset_index()
    last_pwr['RPM'] = pd.to_numeric(last_pwr['RPM'], errors='coerce').astype(pd.Int64Dtype(), errors='ignore')
    last_pwr = last_pwr.sort_values(by='RPM').reset_index().drop(columns=['index'])
    last_pwr.dropna(subset=['RPM'], inplace=True)

    potencia_eq = float(numero_mais_proximo(last_pwr['PWR'].tolist(), potencia_motor))

    if abs((float(potencia_motor) * 745.7) - (potencia_eq * 745.7)) <= 50:
        index = last_pwr['PWR'].tolist().index(numero_mais_proximo(last_pwr['PWR'].tolist(), potencia_eq))
        rpm = last_pwr['RPM'][index]

        #print(rpm)
        prop_datasheet['RPM'] = pd.to_numeric(prop_datasheet['RPM'], errors='coerce')

        data_to_calculate = prop_datasheet[prop_datasheet['RPM'] == rpm]

        thrust_array = [float(valor) * 4.448 for valor in
                        data_to_calculate['Thrust'].tolist()]  # Lista de empuxo em Newton
        velocity_array = [float(valor) / 2.237 for valor in
                          data_to_calculate['V'].tolist()]  # Lista de velocidade em m/s

        static_thrust = thrust_array[0]

        coeffs = create_polynom(velocity_array, thrust_array, 1)
        decay_coeff = coeffs[0]

        output.append(
            [row["Motor"], row["Prop"], static_thrust, decay_coeff, row["Mass"], row["U"]]
        )

    else:
        if (float(potencia_motor) * 745.7) - (potencia_eq * 745.7) > 0:
            # todo: potencia_motor e potencia_motor - 1
            index_1 = last_pwr['PWR'].tolist().index(numero_mais_proximo(last_pwr['PWR'].tolist(), potencia_eq))
            index_0 = index_1 - 1
            rpm_1 = last_pwr['RPM'][index_1]
            rpm_0 = last_pwr['RPM'][index_0]

            prop_datasheet['RPM'] = pd.to_numeric(prop_datasheet['RPM'], errors='coerce')

            data_interp_1 = prop_datasheet[prop_datasheet['RPM'] == rpm_1]
            data_interp_0 = prop_datasheet[prop_datasheet['RPM'] == rpm_0]

            velocity_array_0 = [float(valor) / 2.237 for valor in data_interp_0['V'].tolist()]
            velocity_array_1 = [float(valor) / 2.237 for valor in data_interp_1['V'].tolist()]

            thrust_0 = [float(valor) * 4.448 for valor in data_interp_0['Thrust'].tolist()]
            thrust_1 = [float(valor) * 4.448 for valor in data_interp_1['Thrust'].tolist()]

            coeffs_0 = create_polynom(velocity_array_0, thrust_0, 1)
            coeffs_1 = create_polynom(velocity_array_1, thrust_1, 1)

            decay_coeff = (coeffs_0[0] + coeffs_1[0]) / 2

            static_thrust = (thrust_0[0] + thrust_1[0]) / 2

            output.append(
                [row["Motor"], row["Prop"], static_thrust, decay_coeff, row["Mass"], row["U"]]
            )

        elif (float(potencia_motor) * 745.7) - (potencia_eq * 745.7) < 0:
            # todo: potencia_motor e potencia_motor + 1
            index_0 = last_pwr['PWR'].tolist().index(numero_mais_proximo(last_pwr['PWR'].tolist(), potencia_eq))
            index_1 = index_0 + 1

            if index_1 in last_pwr['RPM'].index:
                rpm_0 = last_pwr['RPM'][index_0]
                rpm_1 = last_pwr['RPM'][index_1]

                prop_datasheet['RPM'] = pd.to_numeric(prop_datasheet['RPM'], errors='coerce')

                data_interp_0 = prop_datasheet[prop_datasheet['RPM'] == rpm_0]
                data_interp_1 = prop_datasheet[prop_datasheet['RPM'] == rpm_1]

                velocity_array_0 = [float(valor) / 2.237 for valor in data_interp_0['V'].tolist()]
                velocity_array_1 = [float(valor) / 2.237 for valor in data_interp_1['V'].tolist()]

                thrust_0 = [float(valor) * 4.448 for valor in data_interp_0['Thrust'].tolist()]
                thrust_1 = [float(valor) * 4.448 for valor in data_interp_1['Thrust'].tolist()]

                coeffs_0 = create_polynom(velocity_array_0, thrust_0, 1)
                coeffs_1 = create_polynom(velocity_array_1, thrust_1, 1)

                decay_coeff = (coeffs_0[0] + coeffs_1[0]) / 2

                static_thrust = (thrust_0[0] + thrust_1[0]) / 2

                output.append(
                    [row["Motor"], row["Prop"], static_thrust, decay_coeff, row["Mass"], row["U"]]
                )

            else:
                index_1 = index_0 - 1
                rpm_1 = last_pwr['RPM'][index_0]
                rpm_0 = last_pwr['RPM'][index_1]

                prop_datasheet['RPM'] = pd.to_numeric(prop_datasheet['RPM'], errors='coerce')

                data_interp_0 = prop_datasheet[prop_datasheet['RPM'] == rpm_0]
                data_interp_1 = prop_datasheet[prop_datasheet['RPM'] == rpm_1]

                velocity_array_0 = [float(valor) / 2.237 for valor in data_interp_0['V'].tolist()]
                velocity_array_1 = [float(valor) / 2.237 for valor in data_interp_1['V'].tolist()]

                thrust_0 = [float(valor) * 4.448 for valor in data_interp_0['Thrust'].tolist()]
                thrust_1 = [float(valor) * 4.448 for valor in data_interp_1['Thrust'].tolist()]

                coeffs_0 = create_polynom(velocity_array_0, thrust_0, 1)
                coeffs_1 = create_polynom(velocity_array_1, thrust_1, 1)

                decay_coeff = (coeffs_0[0] + coeffs_1[0]) / 2

                static_thrust = (thrust_0[0] + thrust_1[0]) / 2

                output.append(
                    [row["Motor"], row["Prop"], static_thrust, decay_coeff, row["Mass"], row["U"]]
                )


output_path = f"data/outputteste.csv"

with open(output_path, mode='w', newline='') as arquivo_csv:
    escritor_csv = csv.writer(arquivo_csv)

    for linha in output:
        escritor_csv.writerow(linha)
