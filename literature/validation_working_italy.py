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

data_index = 0
sampling_frequency = 1e5
time_step = 1 / sampling_frequency

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
Ig_ganan_calvo = []

we want to ccumulate until a certain point
we dont want the index - bc is DC

088-1236860

fft for cone jet is empty except for the dc frequency
"""
ki = 6.46
index = 0
index_aux = 0
path = 'E:/2022JSONCORRECT/'
directory_contents = os.listdir(path)
print(directory_contents)
current_shapes = ["no voltage no fr", "no voltage", "dripping", "intermittent", "cone jet", "multijet",
                  "streamer onset"]

record_last_index_value = 0
def calculate_for_json_with_all_shapes(data_dict, index):
    # for i in range(10, 60):
    rho = data_dict['config']['liquid']['density']
    permitivity = data_dict['config']['liquid']['vacuum permitivity']
    density = data_dict['config']['liquid']['density']
    electrical_conductivity = data_dict['config']['liquid']['electrical conductivity']
    print("\nconfig liquid:", data_dict['config']['liquid'])
    surface_tension = data_dict['config']['liquid']['surface tension']
    dielectric_const = data_dict['config']['liquid']['dielectric const']
    electrical_conductivity_array[index].append(electrical_conductivity)

    for i in range(0, len(data_dict['processing'])):
        # datapoints = (data_dict['measurements'][i]['data [nA]'])
        # data_points_np = np.array(datapoints)
        current_PS = data_dict['measurements'][i]['current PS']
        voltage_PS = data_dict['measurements'][i]['voltage']
        spray_mode = data_dict['measurements'][i]['spray mode']['Sjaak']
        mean = float(data_dict['processing'][i]['mean'])
        median = float(data_dict['processing'][i]['median'])

        if mean != 0.0 and median != 0.0 and electrical_conductivity != 0.0 and rho != 0.0:
            if current_PS != '0.0' and voltage_PS != '0.0' and spray_mode == 'cone jet ' and mean > 10:
                if mean < 150 and float(voltage_PS) < 7500.0 and float(voltage_PS) > 4000.0:
                    flow_rate_actual = (data_dict['measurements'][i]['flow rate [m3/s]'])
                    # print(flow_rate_actual)
                    # data = (data_dict['measurements'][i]['data [nA]'])
                    deviation = (np.float64(data_dict['processing'][i]['deviation']))
                    # for each flow rate
                    """
                    voltage_PS_array.append(float(voltage_PS))
                    current_PS_array.append(current_PS)
                    flow_rate_actual_array.append(float(flow_rate_actual))
                    mean_value_array.append(float(mean))
    
                    sjaak_std_div_mean.append(deviation / mean)
                    sjaak_mean_div_median.append(mean / median)"""

                    flow_rate_actual_array[index].append(flow_rate_actual)
                    flow_rate_chen_pui[index].append(data_dict['measurements'][i]['flow rate [m3/s]'])
                    flow_rate_chen_pui[index].append(np.array(
                        float((dielectric_const) ** 0.5) * (permitivity) * (surface_tension) / (
                                (rho) * (electrical_conductivity))))

                    alpha_chen_pui_actual = (surface_tension * electrical_conductivity * flow_rate_actual / dielectric_const) ** (
                        .5)
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


for i in directory_contents:
    print(path + i)
    with open(path + i) as json_file:
        try:
            data_dict = json.load(json_file)
        except OSError as err:
            print("OS error: {0}".format(err))
        except ValueError:
            print("Could not convert data to an json.")
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise

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
                index = index_aux
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
        # flow_rate_actual = data_dict['config']['liquid']['actual measurement']['flow rate']

        calculate_for_json_with_all_shapes(data_dict , index)

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
        intercept =  (0.1, 0.01)
        # intercept = (0.1*1e-7, 1*1e-6)
        # intercept = (1e-7, 1e-6) #, (0.1, 0.01)
        #plt.axline(intercept, slope=slope, zorder=2, linestyle="--" )
    if name[j] == "ethyleneglycol" or name[j] == "ethylene glycol +1 drop nitric acid":
        intercept = (0.5e-7, 0.5*1e-6)
        # intercept = (0.7e-7, 1e-6) #, (0.007, 0.1)
        slope = 14.2
        plt.axline(intercept, slope=slope, zorder=2, color='orange', linestyle=":")

    if name[j] == "water60alcohol40":
        # intercept = (0.2e-7, 1e-6) #, (0.1, 0.007)
        intercept = (0.2*1e-7, 0.2*1e-6)
        slope = 12.82
        plt.axline(intercept, slope=slope, zorder=2, color='green', linestyle="--")

    plt.xlabel('alpha')
    plt.ylabel('I emitted [nA]')
    plt.legend(loc='best')
    plt.title('Chen n Pui combined')

plt.figure()
# plt.errorbar(flow_rate_actual_array, I_emitted_chen_pui, yerr=stddev_value_array,  marker='^', label="EG")
"""0881236860
for j in range(index + 1):
    xlog = (np.log10(flow_rate_actual_array[j]))
    ylog = (np.log10(I_emitted_chen_pui[j]))
    slope, intercept = np.polyfit(flow_rate_actual_array[j], I_emitted_chen_pui[j], 1)
    plt.scatter(xlog, ylog, marker=">", label="liquid %s %s" % (name[j], str(electrical_conductivity_array[j][0])))

plt.xlabel('Q [m^3/s]')
plt.ylabel('I[nA]')
plt.title('I x Q')
plt.legend(loc='best')
plt.grid()

plt.figure()"""
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