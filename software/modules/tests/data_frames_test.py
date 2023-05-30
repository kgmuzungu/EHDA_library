import pandas as pd
import matplotlib.pyplot as plt
import json
from scipy import stats
import numpy as np
from scipy.signal import butter, lfilter

all_data = []
mean_value_array = []
flow_rate_chen_pui = []
alpha_chen_pui = []
I_emitted_chen_pui = []

def read_print_json(liquid):
    # Opening JSON file
    with open('test.json') as json_file:
        data_dict = json.load(json_file)
        print("Type:", type(data_dict))

        print("\nconfig liquid:", data_dict['config']['liquid'])
        surface_tension = data_dict['config']['liquid']['surface tension']
        dieletric_const = data_dict['config']['liquid']['dieletric cons']
        electrical_conductivity = data_dict['config']['liquid']['electrical conductivity']
        print("\nflow_rate:", data_dict['measurements'][0]['flow_rate'])
        print("\nsurface tension:", surface_tension)
        print("\nelectrical conductivity:", electrical_conductivity)
        print("\ndieletric const:", dieletric_const)

        for i in range(len(data_dict['processing'])):
            mean_value = np.float64(data_dict['processing'][i]['mean'])
            print("\nprocessing_mean:", mean_value)
            mean_value_array.append(mean_value)
            print(type(mean_value))

        for i in range(len(data_dict['measurements'])):
            flow_rate_chen_pui.append(data_dict['measurements'][i]['flow_rate'])
            if flow_rate_chen_pui[i] == 0.0:
                print("passei aq")
                flow_rate_chen_pui[i] = i

            alpha_chen_pui.append((surface_tension * electrical_conductivity * flow_rate_chen_pui[i] / dieletric_const) ** (.5))

            datapoints = (data_dict['measurements'][i]['data'])
            data_points_np = np.array(datapoints)
            print("\nmeasurements:", data_points_np)

            time_max = time_step * len(data_points_np)
            t = np.arange(0.0, time_max, time_step)  # time axes, time steps size is 1 / (sample frequences)

            # mean_value_plot = np.full(datapoints, mean_value)  # create a mean value line
            axs[i].plot(t, data_points_np)
            # axs[i].plot(t, mean_value_plot)
            fig.text(i, i, 'mean = ' + str(np.round(mean_value_array[i], 1)), fontsize=8, color='C1')
            axs[i].set(xlabel='time [s]', ylabel='current (nA)', title='osci reading')
            axs[i].grid()

            axs[i+2].hist(datapoints, density=True)
            axs[i+2].set(xlabel='values', ylabel='quantity', title='Histogram')

            ki = 6.46
            I_emitted_chen_pui.append(ki * dieletric_const ** (.25) * alpha_chen_pui[i] ** (.5))
            # x_chen_pui = np.arange(0.0, alpha_chen_pui+10)  # time axes, time steps size is 1 / (sample frequences)
            # y_chen_pui = np.arange(0.0, I_emitted+10)


            # *********************** CONE JET ************************

            """
            I_cone_jet_chen_pui = (self.ki * (self.κ) ** .25 * (self.γ * self.k_electrical_conductivity * self.q_flow_rate / self.κ) ** .5)

            b = i_actual / ((self.γ * self.k_electrical_conductivity * self.q_flow_rate) ** .5)
            I_hartman = b * ((self.γ * self.k_electrical_conductivity * self.q_flow_rate) ** .5)
            """

            # min_flow_rate = (self.k ** 0.5) * self.permitivity0 * self.γ / (self.rho * self.k_electrical_conductivity)
        """        
        time_max = time_step * len(datapoints)
        t = np.arange(0.0, time_max, time_step)  # time axes, time steps size is 1 / (sample frequences)

        mean_value_plot = np.full(datapoints, mean_value)  # create a mean value line
        axs[0].plot(t, datapoints)
        axs[0].plot(t, mean_value_plot)
        fig.text(0.01, 0.01, 'mean = ' + str(np.round(mean_value, 1)), fontsize=16, color='C1')
        axs[0].set(xlabel='time [s]', ylabel='current (nA)', title='osci reading')
        axs[0].grid()

        cutoff_freq_normalized = 1500 / (0.5 * sampling_frequency)  # in Hz
        b, a = butter(6, Wn=cutoff_freq_normalized, btype='low',
                      analog=False)  # first argument is the order of the filter
        data_filtered = lfilter(b, a, datapoints)
        axs[1].plot(t, data_filtered)
        axs[1].set(xlabel='time', ylabel='nA', title='LP filtered')
        axs[1].grid()"""

    """    
    f = open(liquid + ".json")
    json_object_as_dict = json.load(f)
    print(json_object_as_dict)
    print(type(json_object_as_dict))
    # Iterating through the json list
    for i in json_object_as_dict['config']:
        print(i.setup)
    for i in json_object_as_dict['measurements']:
        jsonData = i.data
        all_data.append(jsonData)
        all_data.astype(int).plot.hist()"""

number_subplots = 5
fig, axs = plt.subplots(number_subplots)

sampling_frequency = 1e5
time_step = 1 / sampling_frequency

read_print_json('teste')
for i in range(len(alpha_chen_pui)):
    print("%0.6f" % alpha_chen_pui[i])
for i in range(len(I_emitted_chen_pui)):
    print("%0.6f" % I_emitted_chen_pui[i])
axs[4].scatter(alpha_chen_pui, I_emitted_chen_pui)
axs[4].set(xlabel='alpha', ylabel='I emitted [nA]', title='Chen n Pui')