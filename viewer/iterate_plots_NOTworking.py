import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button
import json
import os
import matplotlib.pyplot as plt
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

index = 0
index_aux = 0
path = "E:/2022JSONCORRECT/"
# path = "C:/Users/hvvhl/PycharmProjects/pyco/jsonfiles/"
filename = "stepsetup7ethyleneglycol_all shapes_1.11112e-09m3_s.json"

#filename = "stepsetup7ethyleneglycol_all shapes_1.194454e-09m3_s.json"
directory_contents = os.listdir(path)

data = []

mean_div_max_variation_array = []
variance_div_deviation_array = []

voltage_PS_array = []
current_PS_array = []
spray_mode_array = []
mean_value_array = []

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

def calculate_for_json_with_all_shapes(data_dict, index):
    # for i in range(10, 60):
    for i in range(len(data_dict['processing'])):
        # datapoints = (data_dict['measurements'][i]['data [nA]'])
        # data_points_np = np.array(datapoints)
        current_PS = (data_dict['measurements'][i]['current PS'])
        voltage_PS = data_dict['measurements'][i]['voltage']
        spray_mode = data_dict['measurements'][i]['spray mode']

        if current_PS != 0.0 and voltage_PS != 0.0:
            flow_rate_actual = (data_dict['measurements'][i]['flow rate [m3/s]'])
            mean_value = (np.float64(data_dict['processing'][i]['mean']))
            med_value = (np.float64(data_dict['processing'][i]['median']))
            rms_value = (np.float64(data_dict['processing'][i]['rms']))
            variance_value = (np.float64(data_dict['processing'][i]['variance']))
            stddev_value = (np.float64(data_dict['processing'][i]['deviation']))
            maximum_variation_distance = (np.float64(data_dict['processing'][i]['maximum variation distance']))
            mean_div_max_variation_array.append(mean_value / maximum_variation_distance)
            variance_div_deviation_array.append(variance_value / stddev_value)
            data = (data_dict['measurements'][i]['data [nA]'])
            # for each liquid
            voltage_PS_array.append(voltage_PS)
            current_PS_array.append(current_PS)
            mean_array.append(mean_value)
            med_array.append(med_value)
            flow_rate_actual_array.append(flow_rate_actual)
            spray_mode_array.append(spray_mode)
            rms_array.append(rms_value)
            data_array.append(data)
            stddev_array.append(stddev_value)


with open(path + filename) as json_file:
    data_dict = json.load(json_file)
    name_liquid = data_dict['config']['liquid']['name']
    # analyse only step and ethyleneglycol for now
    calculate_for_json_with_all_shapes(data_dict, 0)


data = np.array(data_array)
data_len = len(data)
data_size = data.size

data_info = str(data_index) + ": mean=" + str(round(mean_array[data_index], 2)) + \
    " rms=" + str(round(rms_array[data_index], 2)) + \
    " current PS=" + str(round(float(current_PS_array[data_index]), 10)) + \
    " voltage PS=" + str(round(float(voltage_PS_array[data_index]), 5)) + \
    " std deviation=" + str(round(stddev_array[data_index],2)) + \
    " median=" + str(round(med_array[data_index],2)) + \
    " spray mode=" + str(spray_mode_array[data_index])


# print(data[data_index])
# print(data[data_index+1])

# Create the figure
fig, ax = plt.subplots(2)

#line, = plt.plot(x, data[data_index])
line, = ax[0].plot(np.arange(0, len(data[data_index]) * time_step, time_step), data[data_index])

fourier_transform = np.fft.fft(data[data_index])
freq = np.fft.fftfreq(data[data_index].size, d=time_step)
line2, = ax[1].plot(freq[0:500], abs(fourier_transform[0:500]))

# line2, = ax[1].plot(np.arange(0, len(data[data_index]) * time_step, time_step), data[data_index])
"""line, = ax[0].plot(x, data[data_index], lw=2)
line2, = ax[1].plot(data_array[data_index], lw=2)
"""

ax[0].set_xlabel('Time [s]')
ax[0].set_ylabel('Current (nA)')
ax[0].yaxis.set_ticks([-1e2, 0, 1e2, 2e2])
#ax[0].yaxis.set_ticks([-3e2, -2e2, -1e2, 0, 1e2, 2e2, 3e2, 4e2, 5e2, 6e2, 7e2, 8e2, 9e2, 1e3])

ax[1].set_xlabel('Frequency [Hz]')
ax[1].set_ylabel('Magnitude ')
ax[1].yaxis.set_ticks([0, 1e5, 2e5, 3e5, 4e5, 5e5, 6e5, 7e5, 8e5, 9e5, 1e6])
# adjust the main plot to make room for the sliders
plt.subplots_adjust(left=0.25, bottom=0.25)
# plt.text(0.65, 0.5, "teste", fontdict=None)

# The function to be called anytime the button is pressed

def update(val):
    line.set_ydata(data[val])
    fourier_transform = np.fft.fft(data[val])
    line2.set_ydata(abs(fourier_transform[0:500]))

    t = plt.text(0.0, 2,   str(val) + ": mean=" + str(round(mean_array[val], 2)) + \
        " rms=" + str(round(rms_array[val], 2)) + \
        " current PS=" + str(round(float(current_PS_array[data_index]), 10)) + \
        " voltage PS=" + str(round(float(voltage_PS_array[data_index]), 5)) + \
        " std deviation=" + str(round(stddev_array[val], 2)) + \
        " median=" + str(round(med_array[val],2)) + \
        " spray mode=" + str(spray_mode_array[val]))
    t.set_bbox(dict(facecolor='white'))
    fig.canvas.draw_idle()


# Create `matplotlib.widgets.Button`
nextax = plt.axes([0.7, 0.025, 0.1, 0.04])  # position of button
button_next = Button(nextax, 'next', hovercolor='0.975')
#prevax = plt.axes([0.3, 0.025, 0.1, 0.04])  # position of button
prevax = plt.axes([0.2, 0.025, 0.1, 0.04])  # position of button
button_prev = Button(prevax, 'prev', hovercolor='0.975')

t = plt.text(0.0, 2, (data_info))
t.set_bbox(dict(facecolor='white'))


def next(event):
    print("function NEXT: ## " + str(event))
    global data_index
    global data_len
    data_index = (data_index + 1) % data_len
    update(data_index)


def prev(event):
    print("function PREV: ## " + str(event))
    global data_index
    global data_len
    data_index = (data_index - 1) % data_len
    update(data_index)



button_prev.on_clicked(prev)
button_next.on_clicked(next)
plt.show()