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

mean_value_array = []
med_value_array = []
flow_rate_chen_pui = [[]]
flow_rate_actual_array = [[]]
flow_rate_array = [[]]
stddev_value_array = [[]]
fourier_peaks_array = [[]]
maximum_variation_distance_array = [[]]

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

sjaak_std_mean_array_total = []
sjaak_mean_median_array_total = []
mean_div_max_variation_array = []
variance_div_deviation_array = []
height_div_pos_array = []
pos_array = []
height_array = []
mean_freq_array = []
freq_values = []
mean_freq_values = []
variance_value_array = []
med_value_array = []
record_last_index_value = 0
sampling_frequency = 1e5
time_step = 1 / sampling_frequency
ki = 6.46
index = 0
index_aux = 0
# path = 'C:/Users/hvvhl/Desktop/joao/EHDA_library/jsonfiles'
path = 'E:/2021json/'
directory_contents = os.listdir(path)
print(directory_contents)
current_shapes = ["no voltage no fr", "no voltage", "dripping", "intermittent", "cone jet", "multijet", "streamer onset"]
# 0no voltage no fr/1no voltage/2dripping/3intermittent/4cone jet/5multijet/6streamer onset"]

for i in directory_contents:
    res = re.search(current_shapes[3], i)
    if res == None:
        continue
    else:
        print(i)
        with open(path + i) as json_file:
            data_dict = json.load(json_file)
            manual_shape = data_dict['config']['liquid']['actual measurement']['current shape manual']
            current_comment = data_dict['config']['liquid']['actual measurement']['current comment']
            res = re.search("unstable", current_comment)
            electrical_conductivity = data_dict['config']['liquid']['actual measurement'][
                                          'electrical conductivity'] * 10
            print("\nmanual shape:", manual_shape)

            if res == None:
                if index_aux == 0:  # verify
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
                        stddev_value_array.append([])
                        flow_rate_chen_pui.append([])
                        flow_rate_actual_array.append([])
                        flow_rate_array.append([])
                        fourier_peaks_array.append([])
                        maximum_variation_distance_array.append([])
                        electrical_conductivity_array.append([])
                        sjaak_std_mean_array.append([])
                        sjaak_mean_median_array.append([])

                    # flow_rate_actual = data_dict['config']['liquid']['actual measurement']['flow rate']
                index =index_aux -1
                min_fr_chen_pui = data_dict['config']['liquid']['actual measurement']['flow rate chen pui']
                rho = data_dict['config']['liquid']['density']
                permitivity = data_dict['config']['liquid']['vacuum permitivity']
                density = data_dict['config']['liquid']['density']
                surface_tension = data_dict['config']['liquid']['surface tension']
                dielectric_const = data_dict['config']['liquid']['dielectric const']

                """
                print("\nconfig liquid:", data_dict['config']['liquid'])
                print("\nsurface tension:", surface_tension)
                print("\nelectrical conductivity:", electrical_conductivity)
                print("\ndieletric const:", dielectric_const)
                """

                """
                number_subplots = len(data_dict['processing'])
                fig, axs = plt.subplots(number_subplots)"""

                for i in range(len(data_dict['processing'])):
                    # voltage_actual = data_dict['measurements'][i]['voltage']
                    print(i)
                    flow_rate_actual = (data_dict['measurements'][i]['flow rate [m3/s]'])
                    mean_value = (np.float64(data_dict['processing'][i]['mean']))
                    med_value = (np.float64(data_dict['processing'][i]['median']))
                    variance_value = (np.float64(data_dict['processing'][i]['variance']))


                    stddev_value = (np.float64(data_dict['processing'][i]['deviation']))
                    rms_value = (np.float64(data_dict['processing'][i]['rms']))
                    maximum_variation_distance = (np.float64(data_dict['processing'][i]['maximum variation distance']))
                    mean_div_max_variation_array.append(mean_value/maximum_variation_distance)
                    variance_div_deviation_array.append(variance_value/stddev_value)

                    print("mean/maximum variation distance: %f" % (mean_value/maximum_variation_distance))
                    print("variance/deviation: %f " % (variance_value/stddev_value))
                    """for j in range(len(data_dict['processing'][i]['freq'])):
                        print(np.float64(data_dict['processing'][i]['freq'][j]))"""
                    for j in range(len(data_dict['processing'][i]['freq'])):
                        #print(np.mean(data_dict['processing'][i]['freq'][j]))
                        freq_values.append(np.mean(data_dict['processing'][i]['freq'][j]))

                    for j in range(len(data_dict['processing'][i]['fourier peaks'])):
                        if type(data_dict['processing'][i]['fourier peaks'][j])==str:
                            print(data_dict['processing'][i]['fourier peaks'][j])
                        else:
                            print("peak height: %f,  peak pos: %f" % (data_dict['processing'][i]['fourier peaks'][j][0], data_dict['processing'][i]['fourier peaks'][j][1]))
                            if data_dict['processing'][i]['fourier peaks'][j][1] !=0:
                                print("peak height/position: %f " % (data_dict['processing'][i]['fourier peaks'][j][0]/data_dict['processing'][i]['fourier peaks'][j][1]))
                                height_div_pos_array.append(data_dict['processing'][i]['fourier peaks'][j][0]/data_dict['processing'][i]['fourier peaks'][j][1])
                                height_array.append(data_dict['processing'][i]['fourier peaks'][j][0])
                                pos_array.append(data_dict['processing'][i]['fourier peaks'][j][1])


                            #print(np.float64(data_dict['processing'][i]['fourier peaks'][j]))

                    stddev_value_array.append(stddev_value)
                    mean_value_array.append(mean_value)
                    med_value_array.append(med_value)
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

                    print('sjaak_mean_median: ', sjaak_mean_median)
                    sjaak_mean_median_array[index].append(sjaak_mean_median)

                    sjaak_std_mean_array_total.append(sjaak_std_mean)
                    sjaak_mean_median_array_total.append(sjaak_mean_median)
                    variance_value_array.append(variance_value)
                    med_value_array.append(med_value)
                    if mean_value > 100:
                        if variance_value / stddev_value > 30:
                            print("Multi-jet Monica 2 ")
                    print("**************************************")

            else:
                continue

print(manual_shape)

print("mean height_div_pos_array %f, max %f" % (np.mean(height_div_pos_array), max(height_div_pos_array)))
print("mean pos_array %f max position %f" % (np.mean(pos_array), max(pos_array)))
print("mean height_array  %f, max height %f" % (np.mean(height_array), max(height_array)))
print("mean height/mean position  %f, max height/max position %f" % ( np.mean(height_array)/np.mean(pos_array) , max(height_array)/max(pos_array)))

print("mean freq_values %f, max freq  %f" % (np.mean(freq_values), max(freq_values)))
print("mean div_max_variation_array %f, max %f" % (np.mean(mean_div_max_variation_array), max(mean_div_max_variation_array)))

print("max variation %f" % max(variance_value_array))
print("max mean %f" % max(mean_value_array))
print("max median %f" % max(med_value_array))

print(" mean variance_div_deviation_array %f , max %f " % (np.mean(variance_div_deviation_array), max(variance_div_deviation_array)))
print("mean sjaak_std_mean_array %f max %f" % (np.mean(sjaak_std_mean_array_total), max(sjaak_std_mean_array_total)))
print("mean sjaak_mean_median_array %f max %f" % (np.mean(sjaak_mean_median_array_total), max(sjaak_mean_median_array_total)))


