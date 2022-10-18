import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.signal import butter, lfilter
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import re
import math

import matplotlib.cm as cm

all_data = []
mean_value_array = []
med_value_array = []
flow_rate_chen_pui = []
flow_rate_actual_array = []
flow_rate_array = []
I_actual_array = []
stddev_value_array = []
alpha_chen_pui = []
I_emitted_chen_pui = []
sjaak_verified = []
sjaak_verified_false = 0
sjaak_verified_true = 0
x_ganan_calvo = []
I_Ig_ganan_calvo = []
sjaak_std_mean_array = []
sjaak_mean_median_array = []
sampling_frequency = 1e5
time_step = 1 / sampling_frequency
number_subplots = 5
ki = 6.46

path = '/E:/2022JSONTESTSEG/'
directory_contents = os.listdir(path)
print(directory_contents)
current_shapes = ["no voltage no fr", "no voltage", "dripping", "intermittent", "cone jet", "multijet", "streamer onset"]

for i in directory_contents:
    res = re.search("cone jet", i)
    if res == None:


        continue
    else:
        print(i)
        with open('C:/Users/hvvhl/PycharmProjects/pyco/jsonfiles/'+i) as json_file:
            data_dict = json.load(json_file)

            manual_shape = data_dict['config']['liquid']['actual measurement']['current shape manual']
            print("\nmanual shape:", manual_shape)

            current_comment = data_dict['config']['liquid']['actual measurement']['current comment']
            res = re.search("unstable", current_comment)

            if res == None:
                name = data_dict['config']['liquid']['name']

                # flow_rate_actual = data_dict['config']['liquid']['actual measurement']['flow rate']
                electrical_conductivity = data_dict['config']['liquid']['actual measurement']['electrical conductivity']*10 # ToDo: take off this *10 for the next measurements
                min_fr_chen_pui = data_dict['config']['liquid']['actual measurement']['flow rate chen pui']
                rho = data_dict['config']['liquid']['density']
                permitivity = data_dict['config']['liquid']['vacuum permitivity']

                print("\nconfig liquid:", data_dict['config']['liquid'])
                surface_tension = data_dict['config']['liquid']['surface tension']
                dielectric_const = data_dict['config']['liquid']['dielectric const']

                print("\nsurface tension:", surface_tension)
                print("\nelectrical conductivity:", electrical_conductivity)
                print("\ndieletric const:", dielectric_const)

                """number_subplots = len(data_dict['processing'])
                fig, axs = plt.subplots(number_subplots)"""

                for i in range(len(data_dict['processing'])):
                    flow_rate_actual = data_dict['measurements'][i]['flow rate [m3/s]']
                    #voltage_actual = data_dict['measurements'][i]['voltage']
                    print(i)
                    print("\nflow rate:", flow_rate_actual)

                    mean_value = np.float64(data_dict['processing'][i]['mean'])
                    med_value = np.float64(data_dict['processing'][i]['median'])
                    variance_value = np.float64(data_dict['processing'][i]['variance'])
                    stddev_value = np.float64(data_dict['processing'][i]['deviation'])
                    stddev_value_array.append(stddev_value)
                    rms_value = np.float64(data_dict['processing'][i]['rms'])

                    mean_value_array.append(mean_value)
                    med_value_array.append(med_value)
                    print('mean_value: ', mean_value)
                    if mean_value != 0:
                        sjaak_std_mean = (stddev_value / mean_value)
                    else:
                        sjaak_std_mean = 0
                    print('sjaak_std_mean: ', sjaak_std_mean)
                    sjaak_std_mean_array.append(sjaak_std_mean)
                    if med_value != 0:
                        sjaak_mean_median = (mean_value / med_value)
                    else:
                        sjaak_mean_median = 0
                        sjaak_avg_development_relaxation_ratios = 0
                    print('sjaak_mean_median: ', sjaak_mean_median)
                    sjaak_mean_median_array.append(sjaak_mean_median)
                    if mean_value < 0.5 or mean_value == 0.5:
                        print("dripping mean < 0.5!")
                        if sjaak_std_mean > 2.5:
                            if sjaak_mean_median < 0.9 or sjaak_mean_median > 1.1:
                                if manual_shape == current_shapes[2]:  # dripping
                                    print("dripping validate!")
                                else:
                                    print("dripping not validate!")
                    if sjaak_std_mean > 2.5 and med_value > 0:
                        if sjaak_mean_median < 0.9 or (sjaak_mean_median > 1.1):
                            print("Intermittent Sjaak")
                    """x = np.arange(0.0, 1.1, 0.01)
                    y1 = x * (0.9)
                    plt.fill_between(x, y1, 1.1)"""
                    if mean_value > 1 and med_value > 0:
                        if sjaak_mean_median > 0.9 or sjaak_mean_median < 1.1:
                            print("Cone jet Sjaak")
                            sjaak_verified.append(1)
                            sjaak_verified_true = sjaak_verified_true + 1
                        else:
                            sjaak_verified.append(0)
                            sjaak_verified_false = sjaak_verified_false + 1

                        if variance_value / stddev_value > 5 and variance_value / stddev_value < 20:
                            if mean_value - stddev_value < 30:
                                print("Cone jet Monica")
                        """if unstable:
                            if variance_value / stddev_value < 8:
                                print("Cone jet Unstable Monica ***** improve this****** ")"""
                    if mean_value > 100:
                        if mean_value - stddev_value > 30:
                            print("Multi-jet Monica 1 ")
                        if variance_value / stddev_value > 30:
                            print("Multi-jet Monica 2 ")
                        if sjaak_std_mean > 0.3 or sjaak_std_mean < 40:
                            print("Multi-jet Monica 3")

                    print("**************************************")
                    flow_rate_actual_array.append(flow_rate_actual)
                    flow_rate_chen_pui.append(data_dict['measurements'][i]['flow rate [m3/s]'])
                    #I_actual_array.append(voltage_actual * 0.0001)

                    if flow_rate_actual_array[i] == 0.0:
                        print("passei aq")
                        flow_rate_chen_pui[i] = 0
                    if electrical_conductivity == 0.0 or rho == 0.0:
                        flow_rate_chen_pui.append(0.0)
                    else:
                        flow_rate_chen_pui.append(np.array(
                            float(float(dielectric_const) ** 0.5) * float(permitivity) * float(surface_tension) / (
                                        float(rho) * float(electrical_conductivity))))

                    alpha_chen_pui_actual = (surface_tension * electrical_conductivity * flow_rate_actual / dielectric_const) ** (.5)
                    alpha_chen_pui.append(alpha_chen_pui_actual)

                    I_emitted_chen_pui.append(ki * dielectric_const ** (.25) * alpha_chen_pui_actual)

                    beta_ganan_calvo = dielectric_const / permitivity
                    alphap_ganan_calvo = (rho * electrical_conductivity * flow_rate_actual) / (surface_tension * permitivity)

                    if (alphap_ganan_calvo/(beta_ganan_calvo - 1)) < 1:
                        I_ganan_calvo = ((rho * electrical_conductivity**2 * flow_rate_actual**2)/((beta_ganan_calvo - 1)* permitivity)) ** (.5)
                        Ig_ganan_calvo = (surface_tension * electrical_conductivity * flow_rate_actual) ** .5

                        I_Ig_ganan_calvo.append(I_ganan_calvo/Ig_ganan_calvo)
                        x_ganan_calvo.append(alphap_ganan_calvo * ((beta_ganan_calvo - 1) ** -1))

                    datapoints = (data_dict['measurements'][i]['data [nA]'])
                    data_points_np = np.array(datapoints)

                    time_max = time_step * len(data_points_np)
                    t = np.arange(0.0, time_max, time_step)  # time axes, time steps size is 1 / (sample frequences)
            else:
                continue

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
            all_data.astype(int).plot.hist()
            
    """
"""plt.figure()
plt.plot(t, data_points_np)
axs[i].plot(t, mean_value)
# mean_value_plot = np.full(datapoints, mean_value)  # create a mean value line
# plt.plot(t, mean_value_plot)
plt.text(i, i, 'mean = ' + str(np.round(mean_value_array[i], 1)), fontsize=8, color='C1')
plt.xlabel('time [s]')
plt.ylabel('current (nA)')
plt.title('osci reading')
plt.grid()"""


"""for i in range(len(alpha_chen_pui)):
    print("%0.6f" % alpha_chen_pui[i])
for i in range(len(I_emitted_chen_pui)):
    print("%0.6f" % I_emitted_chen_pui[i])"""

plt.figure()
plt.scatter(alpha_chen_pui, I_emitted_chen_pui,  marker="D", label="EG")
plt.xlabel('alpha')
plt.ylabel('I emitted [nA]')
plt.title('Chen n Pui')

plt.figure()
#plt.errorbar(flow_rate_actual_array, I_emitted_chen_pui, yerr=stddev_value_array,  marker='^', label="EG")
plt.scatter(flow_rate_actual_array, I_emitted_chen_pui,  marker="*", label="EG")
plt.xlabel('Q [m^3/s]')
plt.ylabel('I[nA]')
plt.title('I x Q ')

plt.figure()
#plt.loglog(x_ganan_calvo, I_Ig_ganan_calvo, '--r', linewidth=2, label='liquid')
plt.grid()
xlog = np.log10(x_ganan_calvo)
ylog = np.log10(I_Ig_ganan_calvo)
plt.scatter(xlog, ylog,  marker='o', label="EG")
plt.title('Ganan calvo on log scale', fontsize=15)
plt.xlabel('log(x)', fontsize=13)
plt.ylabel('log(y)', fontsize=13)

plt.figure()
x0 = []
for i in range(len(sjaak_std_mean_array)):
    x0.append(i)
values = ["sjaak_std_mean_array", "sjaak_mean_median_array", "mean_value_array", "med_value_array"]
colors = 'black'
plt.scatter(x0, sjaak_std_mean_array, c=colors, marker='^')
# sjaak_std_mean
plt.axhline(2.5, color=colors, lw=2, alpha=0.5)

colors = 'green'
plt.scatter(x0, sjaak_mean_median_array, c=colors, marker="s")
# sjaak_mean_median
plt.axhline(0.9, color=colors, lw=2, alpha=0.5)
plt.axhline(1.1, color=colors, lw=2, alpha=0.5)

colors = 'blue'
plt.scatter(x0, mean_value_array, c=colors, marker=">")
# mean_sjaak
plt.axhline(1, color=colors, lw=2, alpha=0.5)

colors='yellow'
plt.scatter(x0, med_value_array, c=colors, marker="<")
# med_value
plt.axhline(0, color=colors, lw=2, alpha=0.5)

# monica classification
# (mean_value - stddev_value) > 30:
"""plt.axline(30, color=color, lw=2, alpha=0.5)
# monica std_mean
plt.axline(0.3, color=, lw=2, alpha=0.5)
plt.axline(40, color=, lw=2, alpha=0.5)
"""

colors = ['Red', 'Lime']
labels = ['Sjaak classified false', 'Sjaak classified true']
nbins = [0, 1]
sjaak_verified_true = np.ones(sjaak_verified_true)
sjaak_verified_false = np.zeros(sjaak_verified_false)
x = [sjaak_verified_false, sjaak_verified_true]
plt.figure()
plt.hist(x, nbins, density=True, histtype='bar', color=colors, label=labels)
plt.xticks((0,1))
plt.title('Histogram classification Sjaak')
plt.show()


"""plt.figure()
categories = ['sjaak_std_mean', 'sjaak_mean_median', 'mean_value', 'med_value']
N = len(categories)
values = [sjaak_std_mean, sjaak_mean_median, mean_value, med_value]
values += values[:1]
angles = [n/float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]
plt.polar(angles, values)
plt.xticks(angles[:-1], categories)
plt.yticks([-1, 0, 1, 2, 3, 4, 5], color="grey")
plt.ylim(-1,5)
plt.show()
"""