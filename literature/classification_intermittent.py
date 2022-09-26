import io
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
import pandas as pd
import matplotlib.cm as cm
from PIL import Image
from io import BytesIO

save_path = """E:/2022json/"""
file_name = "teste"
completeName = os.path.join(save_path, file_name)

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
record_last_index_value = 0
sampling_frequency = 1e5
time_step = 1 / sampling_frequency
ki = 6.46
index = 0
index_aux = 0
path = '/jsonfiles/'
directory_contents = os.listdir(path)
print(directory_contents)
current_shapes = ["no voltage no fr", "no voltage", "dripping", "intermittent", "multijet",
                  "streamer onset"]



for i in directory_contents:
    res = re.search(current_shapes[3], i)
    if res == None:
        continue
    else:
        print(i)
        with open('C:/Users/hvvhl/PycharmProjects/pyco/jsonfiles/' + i) as json_file:
            data_dict = json.load(json_file)
            manual_shape = data_dict['config']['liquid']['actual measurement']['current shape manual']
            print("\nmanual shape:", manual_shape)
            current_comment = data_dict['config']['liquid']['actual measurement']['current comment']
            res = re.search("unstable", current_comment)
            electrical_conductivity = data_dict['config']['liquid']['actual measurement'][
                                          'electrical conductivity'] * 10  # ToDo: take off this *10 for the next measurements

            if index_aux == 0: # verifica
                name.append(data_dict['config']['liquid']['name'])
                index_aux = index_aux + 1
            else:
                exists = data_dict['config']['liquid']['name'] in name
                if exists:
                    print("index of this liquid: ")
                    print(index)
                    index = name.index(data_dict['config']['liquid']['name'])
                else:
                    print("index: ")
                    print(index)
                    name.append(data_dict['config']['liquid']['name'])
                    index_aux = index_aux + 1

                    stddev_value_array.append([]) # **
                    mean_value_array.append([]) # **
                    med_value_array.append([]) # **
                    flow_rate_chen_pui.append([])
                    flow_rate_actual_array.append([])
                    flow_rate_array.append([])
                    alpha_chen_pui.append([])
                    I_emitted_chen_pui.append([])
                    sjaak_verified.append([])
                    x_ganan_calvo.append([])
                    I_Ig_ganan_calvo.append([])
                    sjaak_std_mean_array.append([]) # **
                    sjaak_mean_median_array.append([]) # **
                    sjaak_verified_false.append([])
                    sjaak_verified_true.append([])
                    electrical_conductivity_array.append([])

                # flow_rate_actual = data_dict['config']['liquid']['actual measurement']['flow rate']
            index =index_aux -1
            min_fr_chen_pui = data_dict['config']['liquid']['actual measurement']['flow rate chen pui']
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
                flow_rate_actual = (data_dict['measurements'][i]['flow rate [m3/s]'])
                print("\nflow rate:", flow_rate_actual)

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
                    sjaak_std_mean = abs(stddev_value / mean_value)
                else:
                    sjaak_mean_median_array[index].append(0)
                print('sjaak_std_mean: ', sjaak_std_mean)
                sjaak_std_mean_array[index].append(sjaak_std_mean)
                if med_value != 0:
                    sjaak_mean_median = abs(mean_value / med_value)
                else:
                    sjaak_mean_median_array[index].append(0)
                    sjaak_avg_development_relaxation_ratios.append(0)

                print('sjaak_mean_median: ', sjaak_mean_median)
                sjaak_mean_median_array[index].append(sjaak_mean_median)
                if mean_value < 5 or mean_value == 5:
                    print("dripping mean < 5!")
                    if sjaak_std_mean > 2.5:
                        if sjaak_mean_median < 0.9 or sjaak_mean_median > 1.1:
                            if manual_shape == current_shapes[2]:  # dripping
                                print("dripping classified!")
                            else:
                                print("dripping not classified!")

                if mean_value > 5:
                    if sjaak_std_mean < 2.5 and med_value > 0:
                        if sjaak_mean_median < 0.9 or (sjaak_mean_median > 1.1):
                            print("Intermittent Sjaak")
                        if manual_shape == current_shapes[3]:  # Intermittent
                            print("Intermittent classified!")
                        else:
                            print("Intermittent not classified!")

                    if mean_value > 5 and med_value > 0:
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
                flow_rate_chen_pui[index].append(data_dict['measurements'][i]['flow rate [m3/s]'])
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

                datapoints = (data_dict['measurements'][i]['data [nA]'])
                data_points_np = np.array(datapoints)
                time_max = time_step * len(data_points_np)
                t = np.arange(0.0, time_max, time_step)  # time axes, time steps size is 1 / (sample frequences)

plt.figure()
for j in range(index + 1):
    xlog = (np.log10(flow_rate_actual_array[j]))
    ylog = (np.log10(I_emitted_chen_pui[j]))
    slope, intercept = np.polyfit(flow_rate_actual_array[j], I_emitted_chen_pui[j], 1)
    plt.scatter(xlog, ylog, marker=">", label="Liquid %s elec.conductivity [SI] %s" % (name[j], str(electrical_conductivity_array[j][1])))
plt.xlabel('Q [m^3/s]')
plt.ylabel('I[nA]')
plt.title('I x Q ' + current_shapes[3])
plt.legend(loc='best')
plt.grid()
plt.savefig("C:/Users/hvvhl/PycharmProjects/pyco/plot_generated/ganancalvo_"+current_shapes[3]+".jpg", format='jpg', dpi=300)

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
plt.savefig("C:/Users/hvvhl/PycharmProjects/pyco/plot_generated/ganancalvo2_"+current_shapes[3]+".jpg", format='jpg', dpi=300)

values = ["column 1: sjaak_std_mean_array ]2.5", "column 2: sjaak_mean_median_array ]0.9,1.1["]
fig, axs = plt.subplots(index + 1)
data_red=[]
data_blue=[]
for j in range(index + 1):
    data_1 = np.array(sjaak_std_mean_array[j])
    data_2 = np.array(sjaak_mean_median_array[j]) #, 0.99, 0.9, 1.1))
    data_red.append([data_1, data_2])
    data = [data_1, data_2]
    axs[j].set(xlabel=values)
    axs[j].set_title(name[j])
    axs[j].boxplot(data, vert=False)
plt.savefig("C:/Users/hvvhl/PycharmProjects/pyco/plot_generated/boxplotsjaak_"+current_shapes[3]+".jpg", format='jpg', dpi=300)

## INTERMITTENT PLOTS
values = ["mean>5", "med>0"]
red_square = dict(markerfacecolor='r', marker='s')
fig, axs = plt.subplots(index + 1)

if current_shapes[3] == manual_shape:
    data = [sjaak_std_mean_array[0], sjaak_std_mean_array[1], sjaak_std_mean_array[2], sjaak_std_mean_array[3]]
    nameliquids = [name[0], name[1], name[2], name[3]]
    fig, ax1 = plt.subplots(figsize=(10, 6))
    bp = plt.boxplot(data, notch=0, sym='+', vert=0, whis=1.5,  widths=(0.7))
    plt.setp(bp['boxes'], color='black')
    plt.setp(bp['whiskers'], color='black')
    plt.setp(bp['fliers'], color='red', marker='+')
    ax1.spines['top'].set_visible(True)
    ax1.spines['right'].set_visible(True)
    ax1.spines['left'].set_visible(True)
    ax1.xaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
    ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
    ytickNames = plt.setp(ax1, yticklabels=nameliquids)
    ax1.axvspan(0, 0.5, facecolor='red', alpha=0.1)
    ax1.axvspan(2.5, 200, facecolor='red', alpha=0.1)
    ax1.axvspan(0.5, 2.5, facecolor='green', alpha=0.1)
    plt.axvline(x=2.5, color="green", linestyle="--")
    plt.xticks(fontsize=14)
    plt.setp(ytickNames, rotation=45, fontsize=12)
    ax1.set_title('Sjaak 0.5 < | deviation σ / avg | < 2.5 : '+current_shapes[3])
    plt.show()
    plt.savefig('C:/Users/hvvhl/PycharmProjects/pyco/plot_generated/Sjaakdeviation_avg' + current_shapes[3] + ".jpg",
                format='jpg', dpi=300)

    data = [mean_value_array[0], mean_value_array[1], mean_value_array[2], mean_value_array[3]]
    fig, ax1 = plt.subplots(figsize=(10, 6))
    bp = plt.boxplot(data, notch=0, sym='+', vert=0, whis=1.5, widths=(0.7), flierprops=red_square)
    ytickNames = plt.setp(ax1, yticklabels=nameliquids)
    ax1.axvspan(0, 5, facecolor='red', alpha=0.1)
    ax1.axvspan(5, 300, facecolor='green', alpha=0.1)
    plt.axvline(x=5, color="green", linestyle="--")
    plt.setp(ytickNames, rotation=45, fontsize=12)
    plt.xticks(fontsize=14)
    ax1.set_title('Sjaak | avg | > 5nA : ')
    ax1.set_ylabel('Different liquids')
    ax1.set_xlabel('Current [nA]'+current_shapes[3], fontsize=15)
    plt.show()
    plt.savefig('C:/Users/hvvhl/PycharmProjects/pyco/plot_generated/Current [nA]' + current_shapes[3] + ".jpg",
                format='jpg', dpi=300)

    data = [sjaak_mean_median_array[0], sjaak_mean_median_array[1], sjaak_mean_median_array[2], sjaak_mean_median_array[3]]
    fig, ax1 = plt.subplots(figsize=(10, 6))
    bp = plt.boxplot(data, notch=0, sym='+', vert=0, whis=1.5, flierprops=red_square, widths=(0.9))
    plt.setp(bp['boxes'], color='black')
    plt.setp(bp['whiskers'], color='black')
    plt.setp(bp['fliers'], color='red', marker='+')
    ax1.xaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
    ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
    ax1.spines['top'].set_visible(True)
    ax1.spines['right'].set_visible(True)
    ax1.spines['left'].set_visible(True)
    ytickNames = plt.setp(ax1, yticklabels=nameliquids)
    plt.axvline(x=0.9, color="green", linestyle="--")

    plt.axvline(x=1.1, color="green", linestyle="--")
    ax1.axvspan(0.0, 0.9, facecolor='green', alpha=0.1)
    ax1.axvspan(1.1, 4, facecolor='green', alpha=0.1)
    ax1.axvspan(0.9, 1.1, facecolor='red', alpha=0.1)
    plt.setp(ytickNames, rotation=45, fontsize=12)
    plt.xticks(fontsize=14)
    ax1.set_title('Sjaak |avg / median η| < 0.9 or |avg / median η| > 1.1 : '+current_shapes[3])
    plt.show()
    plt.savefig('Sjaakavg_media' + current_shapes[3] + ".jpg",
                format='jpg', dpi=300)

fig, axs = plt.subplots(index + 1)
values = ["  1: mean>5", " 2: med>0"]
for j in range(index + 1):
    data_3 = np.array(mean_value_array[j])  # , stddev_value_array[j])
    data_4 = np.array(med_value_array[j])
    data = [data_3, data_4]
    data_blue.append([data_3, data_4])
    axs[j].set(xlabel=values)
    axs[j].set_title(name[j])
    axs[j].boxplot(data, vert=False)

red_square = dict(markerfacecolor='r', marker='s')
blue_square = dict(markerfacecolor='b', marker='s')
for j in range(index + 1):
    fig, ax1 = plt.subplots()
    x0 = []
    color = 'tab:green'
    for i in range(len(data_red[j][0])):
        x0.append(i)
    ax1.set_xlabel(" -> x axis: %s measurements. each measurement has 50k data points." % name[j])
    ax1.set_ylabel(" mean>5 ", color=color)
    ax1.scatter(x0, data_blue[j][0], color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    x1 = []
    for i in range(len(data_red[j][1])):
        x1.append(i)
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:purple'
    ax2.set_ylabel(' med>0 ', color=color)  # we already handled the x-label with ax1
    ax2.scatter(x1, data_blue[j][1], color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    plt.savefig("C:/Users/hvvhl/PycharmProjects/pyco/plot_generated/plot_mean_med"+str(name[j])+current_shapes[3]+".svg", format='svg', dpi=300)

for j in range(index + 1):
    fig, ax1 = plt.subplots()
    x0 = []
    color = 'tab:red'
    for i in range(len(data_red[j][0])):
        x0.append(i)
    ax1.set_xlabel("-> x axis: %s measurements. each measurement has 50k data points. " % name[j])
    ax1.set_ylabel(" 0.5 < deviation/mean < 2.5 ", color=color)
    ax1.scatter(x0, data_red[j][0], color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    x1 = []
    for i in range(len(data_red[j][1])):
        x1.append(i)
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel(' mean/median < 0.9 || mean/median > 1.1 ', color=color)  # we already handled the x-label with ax1
    ax2.scatter(x1, data_red[j][1], color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    plt.savefig("C:/Users/hvvhl/PycharmProjects/pyco/plot_generated/plot_sjaak_std_mean_mean_median"+current_shapes[3]+str(name[j])+".svg", format='svg', dpi=300)


fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()
values = ["mean > 5", "med > 0"]
red_square = dict(markerfacecolor='r', marker='s')
fig, axs = plt.subplots(index + 1)
for j in range(index + 1):
    data_3 = np.array(mean_value_array[j])  # , stddev_value_array[j])
    data_4 = np.array(med_value_array[j])
    data = [data_3, data_4]
    axs[index].set(xlabel=values)
    axs[j].set_title(name[j])
    axs[j].boxplot(data, vert=False, flierprops=red_square)
plt.savefig("C:/Users/hvvhl/PycharmProjects/pyco/plot_generated/mean_med"+current_shapes[3]+".svg", format='svg', dpi=300)

plt.show()
for j in range(index + 1):
    zero_els = len(sjaak_verified[j]) - np.count_nonzero(sjaak_verified[j])
    one_els = np.count_nonzero(sjaak_verified[j] == 1)
    x = [zero_els, one_els]
