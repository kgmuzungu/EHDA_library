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
path = "E:/2022JSONCORRECT/"
#path = "C:/Users/hvvhl/PycharmProjects/pyco/jsonfiles/"
filename = "rampsetup7ethyleneglycol_all shapes_1.222232e-09m3_s.json"

#filename = "rampsetup7ethyleneglycol_CONE JET REGION_1.222232e-09m3_s.json"
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

plt.rcParams["figure.autolayout"] = True

def calculate_for_json_with_all_shapes(data_dict, index):
    global flow_rate_actual
    # for i in range(10, 60):
    for i in range(3, len(data_dict['processing'])):
        # datapoints = (data_dict['measurements'][i]['data [nA]'])
        # data_points_np = np.array(datapoints)
        current_PS = (data_dict['measurements'][i]['current PS'])
        voltage_PS = data_dict['measurements'][i]['voltage']
        spray_mode = data_dict['measurements'][i]['spray mode']['Sjaak']

        if current_PS != 0.0 and voltage_PS != 0.0:
            flow_rate_actual = (data_dict['measurements'][i]['flow rate [m3/s]'])
            mean_value = (np.float64(data_dict['processing'][i]['mean']))
            med_value = (np.float64(data_dict['processing'][i]['median']))
            rms_value = (np.float64(data_dict['processing'][i]['rms']))
            variance_value = (np.float64(data_dict['processing'][i]['variance']))
            stddev_value = (np.float64(data_dict['processing'][i]['deviation']))
            maximum_variation_distance = (np.float64(data_dict['processing'][i]['maximum variation distance']))
            mean_div_max_variation_array.append(mean_value / maximum_variation_distance)

            data = (data_dict['measurements'][i]['data [nA]'])
            # for each liquid
            voltage_PS_array.append(float(voltage_PS))
            current_PS_array.append(float(current_PS))
            mean_array.append(float(mean_value))
            med_array.append(med_value)
            flow_rate_actual_array.append(flow_rate_actual)
            spray_mode_array.append(spray_mode)
            rms_array.append(rms_value)
            data_array.append(data)
            stddev_array.append(stddev_value)


"""for file in directory_contents:
    with open(path + file) as json_file:"""
with open(path + filename) as json_file:
    data_dict = json.load(json_file)
    name_liquid = data_dict['config']['liquid']['name']
    # analyse only step and ethyleneglycol for now
    calculate_for_json_with_all_shapes(data_dict, 0)


data = np.array(data_array)
mean = np.array(mean_array)

data_len = len(data)
data_size = data.size
t = np.arange(0.01, 50000, 0.01)

# print(data[data_index])
# print(data[data_index+1])

#line, = plt.plot(x, data[data_index])
#y1 = np.cumsum(data[data_index])

flowrate = str(flow_rate_actual)
# Create the figure
plt.subplot(211)
plt.title(name_liquid + ", Q [m3/s]: " + flowrate)
plt.plot(np.arange(0, len(data[data_index]) * time_step, time_step), data[data_index])
#plt.boxplot(data[data_index], sym='+', vert=1, whis=1.5,  widths=(0.7))

plt.subplot(212)
# plt.boxplot(mean, vert=False)
#plt.scatter(voltage_PS_array, mean, color="blue", label="mean")
new_list = []
for item in current_PS_array:
    new_list.append(float(item))
array1 = np.array(new_list)
X = np.multiply(array1, 1e6)
color = 'tab:red'

plt.plot(mean_array, voltage_PS_array, color="red", label="mean")
plt.tick_params(axis='y', labelcolor=color)
color = 'tab:blue'
#plt.plot(voltage_PS_array, X, color=color, label="current PS")
#plt.legend(('tab:red', 'tab:blue'), ('mean', 'damped'), loc='upper right', shadow=True)

# plt.scatter(np.arange(0, len(mean) * time_step, time_step), mean)
plt.show()

# plt.boxplot(data[data_index])
# plt.boxplot(mean)
"""
fourier_transform = np.fft.fft(data[data_index])
freq = np.fft.fftfreq(data[data_index].size, d=time_step)
plt.plot(freq[0:500], abs(fourier_transform[0:500]))
y1 = np.cumsum(abs(fourier_transform[0:500]))
plt.plot(freq[0:500], y1)
fig, ax1 = plt.subplots()
new_list = []
for item in current_PS_array:
    new_list.append(float(item))


array1 = np.array(new_list)
X = np.multiply(array1, 1e6)

color = 'tab:red'
ax1.set_xlabel('Voltage PS  [V]')
ax1.set_ylabel('Current Tie Pie [nA]', color=color)
ax1.plot(voltage_PS_array, mean_array, color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
color = 'tab:blue'
ax2.set_ylabel('Current PS [nA]', color=color)  # we already handled the x-label with ax1
ax2.plot(voltage_PS_array, X, color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()

"""

#line4, = ax[4].signal.welch(data[data_index], sampling_frequency, nperseg=1000)

# line2, = ax[1].plot(np.arange(0, len(data[data_index]) * time_step, time_step), data[data_index])
"""line, = ax[0].plot(x, data[data_index], lw=2)
line2, = ax[1].plot(data_array[data_index], lw=2)
"""

"""ax[4].set_xlabel('Frequency [Hz]')
ax[4].set_ylabel('PSD V**2/Hz')"""

# adjust the main plot to make room for the sliders
plt.subplots_adjust(left=0.25, bottom=0.25)
# plt.text(0.65, 0.5, "teste", fontdict=None)

plt.show()


plt.plot(mean_array, voltage_PS_array, color="red", label="mean")
plt.xlabel("mean")
plt.ylabel("voltage")

