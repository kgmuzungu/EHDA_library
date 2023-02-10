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

mean_value_array = [[]]
med_value_array = [[]]
flow_rate_chen_pui = [[]]
flow_rate_actual_array = [[]]
flow_rate_array = [[]]
stddev_value_array = [[]]
alpha_chen_pui = [[]]
I_emitted_chen_pui = [[]]
sjaak_verified = [[]]
x_ganan_calvo = [[]]
I_Ig_ganan_calvo = [[]]
sjaak_std_mean_array = [[]]
sjaak_mean_median_array = [[]]
sjaak_verified_false = [[]]
sjaak_verified_true = [[]]
electrical_conductivity_array = [[]]
rho = [0]
electrical_conductivity = [0]
permitivity = [0]
surface_tension = [0]
dielectric_const = [0]
min_fr_chen_pui = [0]

name = []
slope = []
all_data = []
sjaak_std_mean = []
sjaak_avg_development_relaxation_ratios = []
sjaak_mean_median = []
"""beta_ganan_calvo = []
alphap_ganan_calvo = []
I_ganan_calvo = []
Ig_ganan_calvo = []"""

sampling_frequency = 1e5
time_step = 1 / sampling_frequency
ki = 6.46
index = 0
index_aux = 0
path = 'C:/Users/hvvhl/Desktop/joao/EHDA_library/jsonfiles/'
directory_contents = os.listdir(path)
print(directory_contents)
current_shapes = ["no voltage no fr", "no voltage", "dripping", "intermittent", "cone jet", "multijet",
                  "streamer onset"]

for i in directory_contents:
    res = re.search("cone jet", i)
    if res == None:
        continue
    else:
        print(i)
        with open(path + i) as json_file:
            data_dict = json.load(json_file)
            manual_shape = data_dict['config']['liquid']['actual measurement']['current shape manual']
            print("\nmanual shape:", manual_shape)
            current_comment = data_dict['config']['liquid']['actual measurement']['current comment']
            res = re.search("unstable", current_comment)
            electrical_conductivity = data_dict['config']['liquid']['actual measurement'][
                                          'electrical conductivity'] * 10  # ToDo: take off this *10 for the next measurements

            if res == None:
                if index_aux == 0:
                    name.append(data_dict['config']['liquid']['name'])

                    index_aux = index_aux + 1
                else:
                    exists = data_dict['config']['liquid']['name'] in name
                    if exists:
                        print("index of this liquid: ")
                        print(index)
                        record_last_index_value = index
                        index = name.index(data_dict['config']['liquid']['name'])
                    else:
                        print("index: ")
                        print(index)
                        index = record_last_index_value
                        index_aux = index_aux + 1
                        name.append(data_dict['config']['liquid']['name'])

                        stddev_value_array.append([])
                        mean_value_array.append([])
                        med_value_array.append([])
                        flow_rate_chen_pui.append([])
                        flow_rate_actual_array.append([])
                        flow_rate_array.append([])
                        stddev_value_array.append([])
                        alpha_chen_pui.append([])
                        I_emitted_chen_pui.append([])
                        sjaak_verified.append([])
                        x_ganan_calvo.append([])
                        I_Ig_ganan_calvo.append([])
                        sjaak_std_mean_array.append([])
                        sjaak_mean_median_array.append([])
                        sjaak_verified_false.append([])
                        sjaak_verified_true.append([])
                        electrical_conductivity_array.append([])

                # flow_rate_actual = data_dict['config']['liquid']['actual measurement']['flow_rate']

                min_fr_chen_pui = data_dict['config']['liquid']['actual measurement']['flow_rate chen pui']
                rho = data_dict['config']['liquid']['density']
                permitivity = data_dict['config']['liquid']['vacuum permitivity']
                density = data_dict['config']['liquid']['density']

                print("\nconfig liquid:", data_dict['config']['liquid'])
                surface_tension = data_dict['config']['liquid']['surface tension']
                dielectric_const = data_dict['config']['liquid']['dielectric const']

                print("\nsurface tension:", surface_tension)
                print("\nelectrical conductivity:", electrical_conductivity)
                print("\ndieletric const:", dielectric_const)

                """number_subplots = len(data_dict['processing'])
                fig, axs = plt.subplots(number_subplots)"""

                for i in range(len(data_dict['processing'])):
                    # voltage_actual = data_dict['measurements'][i]['voltage']
                    print(i)
                    flow_rate_actual = (data_dict['measurements'][i]['flow_rate'])
                    print("\nflow_rate:", flow_rate_actual)

                    mean_value = (np.float64(data_dict['processing'][i]['mean']))
                    med_value = (np.float64(data_dict['processing'][i]['median']))
                    variance_value = (np.float64(data_dict['processing'][i]['variance']))
                    stddev_value = (np.float64(data_dict['processing'][i]['deviation']))
                    rms_value = (np.float64(data_dict['processing'][i]['rms']))

                    stddev_value_array[index].append(stddev_value)
                    mean_value_array[index].append(mean_value)
                    med_value_array[index].append(med_value)
                    electrical_conductivity_array[index].append(electrical_conductivity)

                    print('mean_value: ', mean_value)
                    if mean_value != 0:
                        sjaak_std_mean = (stddev_value / mean_value)
                    else:
                        sjaak_std_mean.append(0)
                    print('sjaak_std_mean: ', sjaak_std_mean)
                    sjaak_std_mean_array[index].append(sjaak_std_mean)
                    if med_value != 0:
                        sjaak_mean_median = (mean_value / med_value)
                    else:
                        sjaak_mean_median.append(0)
                        sjaak_avg_development_relaxation_ratios.append(0)

                    print('sjaak_mean_median: ', sjaak_mean_median)
                    sjaak_mean_median_array[index].append(sjaak_mean_median)
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
                            sjaak_verified[index].append(1)
                            sjaak_verified_true[index].append(1)
                        else:
                            sjaak_verified[index].append(0)
                            sjaak_verified_false[index].append(1)
                        if mean_value - stddev_value > 30:
                            print("cone-jet Monica 1 ")
                        if sjaak_std_mean > 0.3 or sjaak_std_mean < 40:
                            print("cone-jet Monica 3")

                        if variance_value / stddev_value > 5 and variance_value / stddev_value < 20:
                            if mean_value - stddev_value < 30:
                                print("Cone jet Monica")
                        """if unstable:
                            if variance_value / stddev_value < 8:
                                print("Cone jet Unstable Monica ***** improve this****** ")"""
                    if mean_value > 100:
                        if variance_value / stddev_value > 30:
                            print("Multi-jet Monica 2 ")
                    print("**************************************")


                    flow_rate_actual_array[index].append(flow_rate_actual)
                    flow_rate_chen_pui[index].append(data_dict['measurements'][i]['flow_rate'])
                    # I_actual_array.append(voltage_actual * 0.0001)
                    if flow_rate_actual_array[index][i] == 0.0:
                        print("passei aq")
                    if electrical_conductivity == 0.0 or rho == 0.0:
                        flow_rate_chen_pui[index].append(0.0)
                    else:
                        flow_rate_chen_pui[index].append(np.array(
                            float((dielectric_const) ** 0.5) * (permitivity) * (surface_tension) / (
                                    (rho) * (electrical_conductivity))))

                    alpha_chen_pui_actual = (
                            (surface_tension * electrical_conductivity * flow_rate_actual / dielectric_const) ** (
                        .5))
                    alpha_chen_pui[index].append(alpha_chen_pui_actual)
                    I_emitted_chen_pui[index].append(ki * dielectric_const ** (.25) * alpha_chen_pui_actual)

                    beta_ganan_calvo = (dielectric_const / permitivity)
                    alphap_ganan_calvo = ((rho * electrical_conductivity * flow_rate_actual) / (
                            surface_tension * permitivity))

                    if (alphap_ganan_calvo / (beta_ganan_calvo - 1)) < 1:
                        I_ganan_calvo = (((density * electrical_conductivity ** 2 * flow_rate_actual ** 2) / (
                                (beta_ganan_calvo - 1) * permitivity)) ** (.5))
                        Ig_ganan_calvo = ((surface_tension * electrical_conductivity * flow_rate_actual) ** .5)

                        I_Ig_ganan_calvo[index].append(I_ganan_calvo / Ig_ganan_calvo)
                        x_ganan_calvo[index].append(alphap_ganan_calvo * ((beta_ganan_calvo - 1) ** -1))

                    datapoints = (data_dict['measurements'][i]['current'])
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

plt.figure()
plt.plot(t, data_points_np)
axs[i].plot(t, mean_value[index])
# mean_value_plot = np.full(datapoints, mean_value)  # create a mean value line
# plt.plot(t, mean_value_plot)
for i in range(len([index])):
    plt.text(i, i, 'mean = ' + str(np.round(mean_value_array[index][i], 1)), fontsize=8, color='C1')
plt.xlabel('time [s]')
plt.ylabel('current (nA)')
plt.title('osci reading')
plt.grid()
"""
plt.figure()
colors = cm.rainbow(np.linspace(0, 1, index + 1))
for j in range(index + 1):
    slope, intercept = np.polyfit(alpha_chen_pui[j], I_emitted_chen_pui[j], 1)
    # for i in range(len(I_emitted_chen_pui[j])):
    plt.scatter(alpha_chen_pui[j], I_emitted_chen_pui[j], label="liquid %s %s" % (name[j], slope))
    # plt.scatter([pt[i] for pt in alpha_chen_pui], [pt[i] for pt in I_emitted_chen_pui], label='slope %s' % slope)
# plt.scatter(alpha_chen_pui[index], I_emitted_chen_pui, marker="D", label="EG")
plt.xlabel('alpha')
plt.ylabel('I emitted [nA]')
plt.legend(loc='best')
plt.title('Chen n Pui')

plt.figure()
x = np.linspace(0, 0.000000005)
for j in range(index + 1):
    plt.scatter(alpha_chen_pui[j], I_emitted_chen_pui[j], label="liquid %s %s" % (name[j], slope), zorder=1)
    slope, intercept = np.polyfit(alpha_chen_pui[j], I_emitted_chen_pui[j], 1)
    plt.ylim(0, 0.0000001)
    plt.xlim(0, 0.000000005)
    # plt.scatter([pt[i] for pt in alpha_chen_pui], [pt[i] for pt in I_emitted_chen_pui], label='slope %s' % slope)
    # for j in range(index + 1):
    """    
    slope, intercept = np.polyfit(alpha_chen_pui[j], I_emitted_chen_pui[j], 1)
    plt.scatter(alpha_chen_pui[j], I_emitted_chen_pui[j], label="liquid %s %s" % (name[j], slope), zorder=1)
    """
    # for i in range(len(I_emitted_chen_pui[j])):
    if name[j] == "ethanol pure":
        slope = 10.5
        intercept = (0.0000000000, 0.0000000000) #, (0.1, 0.01)
        # y = slope * x
        # plt.plot(x, y, zorder=2)
        plt.axline(intercept, slope=slope, zorder=2, linestyle="--" )
    if name[j] == "ethyleneglycol" or name[j] == "ethylene glycol +1 drop nitric acid":
        intercept = (0.0000000000, 0.000000000)#, (0.007, 0.1)
        slope = 14.2
        #y = slope * x + intercept
        #plt.plot(x, y, zorder=2)
        plt.axline(intercept, slope=slope, zorder=2, color='orange', linestyle=":")
    if name[j] == "water60alcohol40":
        intercept = (0.00000001, 0.00000007)#, (0.1, 0.007)
        slope = 12.82
        #y = slope * x + intercept
        plt.axline(intercept, slope=slope, zorder=2, color='green', linestyle="--")
        # plt.axline(intercept, slope=slope, zorder=2)
        # plt.axline(intercept, slope=12.82, color='y')
        # plt.scatter([pt[i] for pt in alpha_chen_pui], [pt[i] for pt in I_emitted_chen_pui], label='slope %s' % slope)
        # plt.scatter(alpha_chen_pui[index], I_emitted_chen_pui, marker="D", label="EG")
    plt.xlabel('alpha')
    plt.ylabel('I emitted [nA]')
    plt.legend(loc='best')
    plt.title('Chen n Pui combined')

plt.figure()
# plt.errorbar(flow_rate_actual_array, I_emitted_chen_pui, yerr=stddev_value_array,  marker='^', label="EG")
for j in range(index + 1):
    xlog = (np.log10(flow_rate_actual_array[j]))
    ylog = (np.log10(I_emitted_chen_pui[j]))
    slope, intercept = np.polyfit(flow_rate_actual_array[j], I_emitted_chen_pui[j], 1)
    plt.scatter(xlog, ylog, marker=">", label="liquid %s %s" % (name[j], str(electrical_conductivity_array[j][1])))
    # for i in range(len(I_emitted_chen_pui[j])):
    # plt.scatter([pt[i] for pt in flow_rate_actual_array], [pt[i] for pt in I_emitted_chen_pui], marker="*", label="EG")
plt.xlabel('Q [m^3/s]')
plt.ylabel('I[nA]')
plt.title('I x Q')
plt.legend(loc='best')
plt.grid()

plt.figure()
# plt.loglog(x_ganan_calvo, I_Ig_ganan_calvo, '--r', linewidth=2, label='liquid')
for j in range(index + 1):
    xlog = (np.log10(x_ganan_calvo[j]))
    ylog = (np.log10(I_Ig_ganan_calvo[j]))
    plt.scatter(xlog, ylog, marker="*", label="liquid %s" % (name[j]))
    # for i in range(len(ylog[j])):
    # plt.scatter([pt[i] for pt in xlog], [pt[i] for pt in ylog], marker='o', label="liquid %s" % (name[j]), c=j)
    plt.title('Ganan calvo on log scale', fontsize=15)

plt.xlabel('log(x)', fontsize=13)
plt.ylabel('log(y)', fontsize=13)
plt.legend(loc='best')

values = ["column 1: sjaak_std_mean_array ]2.5", "column 2: sjaak_mean_median_array ]0.9,1.1[", " column 3: mean_value_array ]1", "column 4: med_value_array ]0"]
fig, axs = plt.subplots(index + 1)
for j in range(index + 1):
    data_1 = np.array(sjaak_std_mean_array[j])
    data_2 = np.array(sjaak_mean_median_array[j]) #, 0.99, 0.9, 1.1))
    data_3 = np.array(mean_value_array[j])  # , stddev_value_array[j])
    data_4 = np.array(med_value_array[j])
    #data_reference_std_mean = np.concatenate(1.25, 2.5, 0)
    """    data_reference_mean_median = np.concatenate(spread, center, flier_high, flier_low)
    data_reference_mean_median = np.concatenate(spread, center, flier_high, flier_low)
    data_reference_med_value = np.concatenate(spread, center, flier_high, flier_low)"""
    data = [data_1, data_2, data_3, data_4]
    axs[index].set(xlabel=values)
    axs[j].set_title(name[j])
    axs[j].boxplot(data, vert=True)

values = ["mean_value_array ]1", "med_value_array ]0"]
red_square = dict(markerfacecolor='r', marker='s')
fig, axs = plt.subplots(index + 1)
for j in range(index + 1):
    data_3 = np.array(mean_value_array[j])  # , stddev_value_array[j])
    data_4 = np.array(med_value_array[j])

    """    data_reference_mean_median = np.concatenate(spread, center, flier_high, flier_low)
    data_reference_mean_median = np.concatenate(spread, center, flier_high, flier_low)
    data_reference_med_value = np.concatenate(spread, center, flier_high, flier_low)"""
    data = [data_3, data_4]
    axs[index].set(xlabel=values)
    axs[j].set_title(name[j])
    axs[j].boxplot(data, vert=False, flierprops=red_square)

    #fig1, ax1 = plt.subplots()

plt.figure()
x0 = [[]]
fig, axs = plt.subplots(index + 1)
for j in range(index + 1):
    for i in range(len(sjaak_std_mean_array[j])):
        x0[j].append(i)
    colors = 'black'
    axs[j].scatter(x0[j], sjaak_std_mean_array[j], c=colors, marker='^', label="sjaak_std_mean_array %s" % (name[j]))
    # plt.scatter([pt[i] for pt in x0[j]], [pt[i] for pt in sjaak_std_mean_array[j]], c=colors, marker='^')
    # sjaak_std_mean
    axs[j].axhline(2.5, color=colors, lw=2, alpha=0.5)
    axs[j].legend(loc='best')

    colors = 'green'
    # for i in range(len(sjaak_mean_median_array[j])):
    # plt.scatter([pt[i] for pt in x0], [pt[i] for pt in sjaak_mean_median_array[j]], c=colors, marker="s")
    axs[j].scatter(x0[j], sjaak_mean_median_array[j], c=colors, marker="s", label="sjaak_mean_median_array %s" % (name[j]))
    # sjaak_mean_median
    axs[j].axhline(0.9, color=colors, lw=2, alpha=0.5)
    axs[j].axhline(1.1, color=colors, lw=2, alpha=0.5)
    axs[j].legend(loc='best')

    colors = 'blue'
    # for i in range(len(mean_value_array[j])):
    axs[j].scatter(x0[j], mean_value_array[j], c=colors, marker=">", label="mean_value_array %s" % (name[j]))
    # plt.scatter([pt[i] for pt in x0[j]], [pt[i] for pt in mean_value_array[j]], c=colors, marker=">")
    # mean_sjaak
    axs[j].axhline(1, color=colors, lw=2, alpha=0.5)
    axs[j].legend(loc='best')

    colors = 'yellow'
    # for i in range(len(med_value_array[j])):
    axs[j].scatter(x0[j], med_value_array[j], c=colors, marker="<", label="med_value_array %s" % (name[j]))
    # plt.scatter([pt[i] for pt in x0[j]], [pt[i] for pt in med_value_array[j]], c=colors, marker="<")
    # med_value
    axs[j].axhline(0, color=colors, lw=2, alpha=0.5)
    x0.append([])
    axs[j].legend(loc='best')

# monica classification
# (mean_value - stddev_value) > 30:
plt.figure()
colors = ['Red', 'Lime']
labels = ['Sjaak classified false', 'Sjaak classified true']
"""
for j in range(index + 1):
    zero_els = len(sjaak_verified[j]) - np.count_nonzero(sjaak_verified[j])
    # np.count_nonzero(sjaak_verified[j] == 0)
    one_els = np.count_nonzero(sjaak_verified[j] == 1)
    x = [zero_els, one_els]
"""
fig, axs = plt.subplots(index + 1)
for j in range(index + 1):
    # subplot(j + 1, 1, j + 1)
    nbins = [0, 1]
    bars = ["0/False" + name[j], "1/True" + name[j]]
    sjaak_verified_true_aux = (np.ones(len(sjaak_verified_true[j])))
    sjaak_verified_false_aux = (np.zeros(len(sjaak_verified_false[j])))
    x = [sjaak_verified_false_aux, sjaak_verified_true_aux]
    axs[j].hist(x, nbins, density=True, histtype='bar', color=colors, label=labels)
    axs[j].grid(axis='y', alpha=0.75)
    axs[j].set(xlabel=bars, ylabel=nbins, title='%s' % name[j])

"""
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
 """
"""
for i in range(len(alpha_chen_pui)):
    print("%0.6f" % alpha_chen_pui[i])
for i in range(len(I_emitted_chen_pui)):
    print("%0.6f" % I_emitted_chen_pui[i])
"""
