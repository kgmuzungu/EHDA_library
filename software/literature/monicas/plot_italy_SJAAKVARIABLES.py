import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import itertools
import math
font = {'weight' : 'bold',
        'size' : 18}

plt.rc('font', **font)

data_index = 0
sampling_frequency = 1e5
time_step = 1 / sampling_frequency
#0 - 5000 hz

index = 0
index_aux = 0
# path = "E:/2022jsonauxethanol/"
#path = "E:/summer22water60alcohol40/"
#path = "E:/summer22propanol/"
path = "E:/summer22ethanol/"
#path = "E:/summer22propanol/"
#path = "C:/Users/hvvhl/Desktop/joao/EHDA_library/jsonfiles/"
directory_contents = os.listdir(path)
#directory_contents = "stepsetup92propanol_all shapes_1.94446e-08m3_s.json"
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

plot_markers = itertools.cycle((',', '+', '^', 'o', '*', '>', '2', '1', '<', '3', '+', 's', '4'))
plot_colors = itertools.cycle(('orange', 'firebrick', 'hotpink', 'aqua', 'purple', 'red', 'yellowgreen', 'lightseagreen', 'blueviolet', 'darkcyan', 'green', 'black'))
plot_lines = []

def calculate_for_json_with_all_shapes(data_dict):
    # for i in range(10, 60):
    global flow_rate_actual_array
    flow_rate_actual = (data_dict['measurements'][10]['flow_rate'])
    print(flow_rate_actual)
    #flow_rate_actual_array.append(str(round(float(flow_rate_actual), 2)) + "[m3/s]")
    flow_rate_actual_array.append(str(flow_rate_actual)+ "[m3/s]")

    for i in range(0, len(data_dict['processing'])):
        # datapoints = (data_dict['measurements'][i]['current'])
        # data_points_np = np.array(datapoints)
        current_PS = data_dict['measurements'][i]['current_PS']
        voltage_PS = data_dict['measurements'][i]['voltage']
        spray_mode = data_dict['measurements'][i]['spray mode']['Sjaak']
        mean = float(data_dict['processing'][i]['mean'])
        median = float(data_dict['processing'][i]['median'])
        deviation = (float(data_dict['processing'][i]['deviation']))
        if mean != 0.0 and median != 0.0:
            if current_PS != '0.0' and voltage_PS != '0.0':  # and spray_mode == 'cone jet ':
                # if mean_value < 150 and float(voltage_PS) < 7000.0 and float(voltage_PS) > 4000.0:
                # print(flow_rate_actual)
                # data = (data_dict['measurements'][i]['current'])
                # for each flow_rate
                voltage_PS_array.append(float(voltage_PS))
                current_PS_array.append(current_PS)
                mean_value_array.append(float(mean))
                sjaak_std_div_mean.append(deviation / mean)
                sjaak_mean_div_median.append(mean / median)
fig, axs = plt.subplots()
axs.set_xlabel('V [V]')
#axs.set_ylabel('Mean [nA]')
#axs.set_ylabel('Mean/Median [-]')
axs.set_ylabel('Standard deviation/Mean [-]')
axs.xaxis.set_ticks(np.arange(0, 1.1e4, 5e2))

for file in directory_contents:
    with open(path + file) as json_file:
        data_dict = json.load(json_file)
        name_liquid = data_dict['config']['liquid']['name']
        calculate_for_json_with_all_shapes(data_dict)
        axs.legend(plot_lines, flow_rate_actual_array, loc='best')

        #axs.set_title('Voltage x Mean for ' + name_liquid )
        #axs.set_title('Voltage x Mean/Median for ' + name_liquid + ' - STEP')
        axs.set_title('Voltage x Standard deviation/Mean for ' + name_liquid )
        #plot_lines.append(axs.scatter(voltage_PS_array, mean_value_array, c=next(plot_colors), marker=next(plot_markers)))
        #plot_lines.append(axs.scatter(voltage_PS_array, (sjaak_mean_div_median), c=next(plot_colors), marker=next(plot_markers)))
        plot_lines.append(axs.scatter(voltage_PS_array, sjaak_std_div_mean, c=next(plot_colors), marker=next(plot_markers)))

        voltage_PS_array = []
        current_PS_array = []
        mean_value_array = []
        sjaak_std_div_mean = []
        sjaak_mean_div_median = []

#axs.legend(plot_lines, flow_rate_actual_array, loc='upper left')

#plt.savefig("C:/Users/hvvhl/Desktop/joao/EHDA_library/plot_generated/sjaak_mean" + name_liquid + ".jpg", format='jpg', dpi=300)

#plt.savefig('C:/Users/hvvhl/Desktop/joao/EHDA_library/plot_generated/sjaak_std_div_mean' + name_liquid + ".tiff", format='tiff', dpi=300)
#plt.savefig("C:/Users/hvvhl/Desktop/joao/EHDA_library/plot_generated/sjaak_std_div_mean" + name_liquid + ".jpg", format='jpg', dpi=300)
#plt.savefig('C:/Users/hvvhl/Desktop/joao/EHDA_library/plot_generated/logdeviation_div_meanXvoltage' + name_liquid[3] + ".jpg", format='jpg', dpi=300)
#plt.savefig('C:/Users/hvvhl/Desktop/joao/EHDA_library/plot_generated/logmean_div_medianXvoltage_' + name_liquid[3] + ".jpg", format='jpg', dpi=300)
plt.show()







