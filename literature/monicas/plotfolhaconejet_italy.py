import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button
import json
import os
import matplotlib.pyplot as plt
from scipy import signal
from matplotlib.patches import Rectangle
import numpy as np
import re
import seaborn as sns
from scipy.stats import norm
import math
import pandas as pd
import matplotlib.cm as cm
from PIL import Image
from io import BytesIO

from scipy.stats import norm
data_index = 0
sampling_frequency = 1e5
time_step = 1 / sampling_frequency
#0 - 5000 hz

#absolute value: cumsum 0 -5000 hz
"""
make another plot 0 - 50k

we want to ccumulate until a certain point
we dont want the index - bc is DC

fft for cone jet is empty except for the dc frequency
"""
index = 0
index_aux = 0
path = "E:/2022JSONTESTSEG/"
#path = "E:/2022jsonauxethanol/"
#path = "C:/Users/hvvhl/Desktop/joao/EHDA_library/jsonfiles/"
directory_contents = os.listdir(path)

data = []

mean_div_max_variation_array = []
variance_div_deviation_array = []

voltage_PS_array = []
current_PS_array = []
spray_mode_array = []
mean_value_array = []
flow_rate_actual = 0
med_array = []
flow_rate_actual_array = []
flow_rate_array = []
stddev_array = []
fourier_peaks_array = []
maximum_variation_distance_array = []
rms_array = []
data_each_flow_rate = []
mean_each_flow_rate = []
electrical_conductivity_array = []
mean_array = []
tuple_mean_and_flowrate = []
data_array = []
name_list = []
sjaak_std_div_mean = []
sjaak_mean_div_median = []

plt.rcParams["figure.autolayout"] = True

def calculate_for_json_with_all_shapes(data_dict):
    # for i in range(10, 60):
    for i in range(0, len(data_dict['processing'])):
        # datapoints = (data_dict['measurements'][i]['data [nA]'])
        # data_points_np = np.array(datapoints)
        current_PS = data_dict['measurements'][i]['current PS']
        voltage_PS = data_dict['measurements'][i]['voltage']
        spray_mode = data_dict['measurements'][i]['spray mode']['Sjaak']
        mean = float(data_dict['processing'][i]['mean'])
        median = float(data_dict['processing'][i]['median'])

        if mean != 0.0 and median != 0.0:
            if current_PS != '0.0' and voltage_PS != '0.0' and spray_mode == 'cone jet ':
                if mean < 150 and float(voltage_PS) < 7350.0 :
                    flow_rate_actual = (data_dict['measurements'][i]['flow rate [m3/s]'])
                    # print(flow_rate_actual)
                    # data = (data_dict['measurements'][i]['data [nA]'])
                    deviation = (np.float64(data_dict['processing'][i]['deviation']))

                    # for each flow rate
                    voltage_PS_array.append(float(voltage_PS))
                    current_PS_array.append(current_PS)
                    flow_rate_actual_array.append(float(flow_rate_actual))
                    mean_value_array.append(float(mean))

                    sjaak_std_div_mean.append(deviation / mean)
                    sjaak_mean_div_median.append(mean / median)



for file in directory_contents:
    with open(path + file) as json_file:
        data_dict = json.load(json_file)
        name_liquid = data_dict['config']['liquid']['name']
        calculate_for_json_with_all_shapes(data_dict)
    """
    with open(path + filename) as json_file:
    """

# print(data[data_index])
# print(data[data_index+1])

#line, = plt.plot(x, data[data_index])
#y1 = np.cumsum(data[data_index])

flowrate = str(flow_rate_actual)
# Create the figure
"""fig, axs = plt.subplots(3)

axs[0].scatter(voltage_PS_array, mean_value_array, color="green", label="mean", marker='^')
axs[0].set_xlabel('V [V]')
axs[0].set_ylabel('nA')
axs[0].set_title('V x nA for cone jet mode using Sjaak classification for ' + name_liquid)
axs[0].xaxis.set_ticks(np.arange(0, 1.1e4, 5e2))


# ylog = (np.log10(sjaak_mean_div_median))
ylog = sjaak_mean_div_median
axs[1].scatter(voltage_PS_array, ylog, color="red", label="mean", marker= 'o')
axs[1].set_xlabel('V [V]')
axs[1].set_ylabel('mean/median ')
axs[1].set_title('V x mean/median for cone jet mode using Sjaak classification for ' + name_liquid)
axs[1].xaxis.set_ticks(np.arange(0, 1.1e4, 5e2))

# ylog = (np.log10(sjaak_std_div_mean))
ylog = sjaak_std_div_mean
axs[2].scatter(voltage_PS_array, ylog, color="blue", label="mean", marker= '*')
axs[2].set_xlabel('V [V]')
axs[2].set_ylabel('deviation/mean ')
axs[2].set_title('V x deviation/mean for cone jet mode using Sjaak classification for ' + name_liquid)
axs[2].xaxis.set_ticks(np.arange(0, 1.1e4, 5e2))"""


plt.figure()
plt.scatter(flow_rate_actual_array, voltage_PS_array, marker="*", color= 'lightseagreen')
# for i in range(len(ylog[j])):
# plt.scatter([pt[i] for pt in xlog], [pt[i] for pt in ylog], marker='o', label="liquid %s" % (name[j]), c=j)
plt.title('Plot Flow Rate x Voltage PS ' + name_liquid, fontsize=15)
plt.show()


array = [flow_rate_actual_array, voltage_PS_array]

df = pd.DataFrame(array).T
df.to_excel(excel_writer = "C:/Users/hvvhl/Desktop/joao/EHDA_library/plot_generated/flowrate_voltagePS"+name_liquid+".xlsx")