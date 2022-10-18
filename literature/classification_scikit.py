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

from sklearn.cluster import kmeans_plusplus
from sklearn.datasets import make_blobs
""""
https://scikit-learn.org/stable/auto_examples/cluster/plot_mean_shift.html#sphx-glr-auto-examples-cluster-plot-mean-shift-py


"""

from sklearn import linear_model
import io
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker
from scipy import stats
from scipy.signal import butter, lfilter
from scipy.stats import norm

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

mean_value_array = []
med_value_array = []
flow_rate_chen_pui = [[]]
flow_rate_actual_array = [[]]
flow_rate_array = [[]]
stddev_value_array = [[]]
fourier_peaks_array = [[]]
maximum_variation_distance_array = [[]]
data_each_shape = [[]]
mean_each_shape = [[]]
sjaak_verified = [[]]
x_ganan_calvo = [[]]
I_Ig_ganan_calvo = [[]]
sjaak_std_mean_array = [[]]
sjaak_mean_median_array = [[]]
sjaak_verified_false = [[]]
sjaak_verified_true = [[]]
electrical_conductivity_array = [[]]
mean_histogram = [[]]

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
# path = 'C:/Users/hvvhl/PycharmProjects/pyco/jsonfiles'

path = 'E:/2022json/'
directory_contents = os.listdir(path)
print(directory_contents)
colors = ["#4EACC5", "#FF9C34", "#4E9A06", "m", 'red', 'blue']
#colors = ['red', 'blue', 'yellow', 'green', 'black']
n_samples = 50000
n_components = 4


def calculate_peaks(self, data):
    quantity_max_data = 0
    max_data = max(data)
    for i in range(0, int(len(data))):
        if data[i] == max_data:
            quantity_max_data = quantity_max_data + 1
    percentage_max = (quantity_max_data / 50000) * 100
    print(max_data)
    print(quantity_max_data)
    print(percentage_max)
    print("*************")
    return max_data, quantity_max_data, percentage_max

def calculate_for_every_shape(shape):
    """
    mean_value_array_aux = []

    for i in range(0, 5):
        mean_value = (np.float64(data_dict['processing'][i]['mean']))
        mean_value_array_aux.append(mean_value)

    global colors, index_aux
    plt.figure()
    plt.hist(mean_value_array_aux, color=colors[index_aux - 1])
    plt.xlabel('Current [nA]')
    plt.ylabel('Values /  Datapoints ')
    plt.title('Mean histogram of the shape ' + shape + ' of the liquid '  + name_liquid)
    """
    print(shape)
    X=[]
    for i in range(0, 3):
        # for i in range(len(data_dict['processing'])):
        # voltage_actual = data_dict['measurements'][i]['voltage']

        datapoints = (data_dict['measurements'][i]['data [nA]'])
        X.append(datapoints)
        Y = [0., 1., 2., 3.]
        reg = linear_model.BayesianRidge()
        reg.fit(X, Y)

    for i in range(1, 2):
        datapoints = (data_dict['measurements'][i]['data [nA]'])
        data_points_np = np.array(datapoints)
        print(i)
        flow_rate_actual = (data_dict['measurements'][i]['flow rate [m3/s]'])
        mean_value = (np.float64(data_dict['processing'][i]['mean']))
        med_value = (np.float64(data_dict['processing'][i]['median']))
        variance_value = (np.float64(data_dict['processing'][i]['variance']))

        stddev_value = (np.float64(data_dict['processing'][i]['deviation']))
        rms_value = (np.float64(data_dict['processing'][i]['rms']))
        maximum_variation_distance = (np.float64(data_dict['processing'][i]['maximum variation distance']))
        mean_div_max_variation_array.append(mean_value / maximum_variation_distance)
        variance_div_deviation_array.append(variance_value / stddev_value)

        print("mean/maximum variation distance: %f" % (mean_value / maximum_variation_distance))
        print("variance/deviation: %f " % (variance_value / stddev_value))
        """for j in range(len(data_dict['processing'][i]['freq'])):
            print(np.float64(data_dict['processing'][i]['freq'][j]))"""
        for j in range(len(data_dict['processing'][i]['freq'])):
            # print(np.mean(data_dict['processing'][i]['freq'][j]))
            freq_values.append(np.mean(data_dict['processing'][i]['freq'][j]))

        for j in range(len(data_dict['processing'][i]['fourier peaks'])):
            if type(data_dict['processing'][i]['fourier peaks'][j]) == str:
                print(data_dict['processing'][i]['fourier peaks'][j])
            else:
                print("peak height: %f,  peak pos: %f" % (
                    data_dict['processing'][i]['fourier peaks'][j][0],
                    data_dict['processing'][i]['fourier peaks'][j][1]))
                if data_dict['processing'][i]['fourier peaks'][j][1] != 0:
                    print("peak height/position: %f " % (data_dict['processing'][i]['fourier peaks'][j][0] /
                                                         data_dict['processing'][i]['fourier peaks'][j][1]))
                    height_div_pos_array.append(data_dict['processing'][i]['fourier peaks'][j][0] /
                                                data_dict['processing'][i]['fourier peaks'][j][1])
                    height_array.append(data_dict['processing'][i]['fourier peaks'][j][0])
                    pos_array.append(data_dict['processing'][i]['fourier peaks'][j][1])

                # print(np.float64(data_dict['processing'][i]['fourier peaks'][j]))

        stddev_value_array.append(stddev_value)
        mean_value_array.append(mean_value)
        med_value_array.append(med_value)
        electrical_conductivity_array[index_aux - 1].append(electrical_conductivity)
        mean_each_shape[index_aux - 1].append(mean_value)
        data_each_shape[index_aux - 1].append(datapoints)
        flow_rate_actual_array[index_aux - 1].append(flow_rate_actual)
        print('mean_value: ', mean_value)
        if mean_value != 0:
            sjaak_std_mean = abs(stddev_value / mean_value)
        else:
            sjaak_mean_median_array[index].append(0)
        print('sjaak_std_mean: ', sjaak_std_mean)
        sjaak_std_mean_array[index_aux - 1].append(sjaak_std_mean)
        if med_value != 0:
            sjaak_mean_median = abs(mean_value / med_value)
        else:
            sjaak_mean_median = 0
            sjaak_mean_median_array[index_aux - 1].append(0)

        sjaak_mean_median_array[index_aux - 1].append(sjaak_mean_median)
        print('sjaak_mean_median: ', sjaak_mean_median)

        sjaak_std_mean_array_total.append(sjaak_std_mean)
        sjaak_mean_median_array_total.append(sjaak_mean_median)
        variance_value_array.append(variance_value)
        med_value_array.append(med_value)
        reg = linear_model.RidgeCV(alphas=[0.1, 1.0, 10.0])


        if mean_value > 100:
            if variance_value / stddev_value > 30:
                print("Multi-jet Monica 2 ")

        """        print("mean height_div_pos_array %f, max %f" % (
            np.mean(height_div_pos_array), max(height_div_pos_array)))
        print("mean pos_array %f max position %f" % (np.mean(pos_array), max(pos_array)))
        print("mean height_array  %f, max height %f" % (np.mean(height_array), max(height_array)))
        print("mean height/mean position  %f, max height/max position %f" % (
            np.mean(height_array) / np.mean(pos_array), max(height_array) / max(pos_array)))

        print("mean freq_values %f, max freq  %f" % (np.mean(freq_values), max(freq_values)))
        print("mean div_max_variation_array %f, max %f" % (
            np.mean(mean_div_max_variation_array), max(mean_div_max_variation_array)))

        print("max variation %f" % max(variance_value_array))
        print("max mean %f" % max(mean_value_array))
        print("max median %f" % max(med_value_array))

        print(" mean variance_div_deviation_array %f , max %f " % (
            np.mean(variance_div_deviation_array), max(variance_div_deviation_array)))
        print("mean sjaak_std_mean_array %f max %f" % (
            np.mean(sjaak_std_mean_array_total), max(sjaak_std_mean_array_total)))
        print("mean sjaak_mean_median_array %f max %f" % (
            np.mean(sjaak_mean_median_array_total), max(sjaak_mean_median_array_total)))
        print("**************************************")
        print("**************************************")"""


current_shapes = ["dripping", "intermittent", "cone jet", "multijet",
                  "streamer onset"]
for m in range(0, 4):
    print(current_shapes[m])
# 0no voltage no fr/1no voltage/2dripping/3intermittent/4cone jet/5multijet/6streamer onset"]
for i in directory_contents:
    for m in range(0, 4):
        res = re.search(current_shapes[m], i)
        if res:
            break
    res_setup9 = re.search("setup9", i)
    if res is None and res_setup9 is None:
        continue
    if res and res_setup9:
        print(i)
        with open(path + i) as json_file:
            data_dict = json.load(json_file)
            name_liquid = data_dict['config']['liquid']['name']
            manual_shape = data_dict['config']['liquid']['actual measurement']['current shape manual']
            current_comment = data_dict['config']['liquid']['actual measurement']['current comment']
            res_comment = re.search("unstable", current_comment)  # not unstable
            res_liquid = re.search("ethyleneglycol", name_liquid)

            electrical_conductivity = data_dict['config']['liquid']['actual measurement'][
                'electrical conductivity']
            flow_rate_actual = (data_dict['measurements'][0]['flow rate [m3/s]'])

            if res_comment is None and res_liquid is None:
                continue
            else:
                if manual_shape == "dripping" or manual_shape == "intermittent" or manual_shape == "cone jet" or manual_shape == "multijet" and flow_rate_actual== 2.5000200000000003e-10:
                    if index_aux == 0 :  # verify first
                        name.append(manual_shape)
                        index_aux = index_aux + 1
                        calculate_for_every_shape(manual_shape)


                    else:
                        exists = data_dict['config']['liquid']['actual measurement']['current shape manual'] in name
                        if exists:
                            index = name.index(manual_shape)
                            """print("index of this shape: ")
                            print(index)"""
                        else:
                            name.append(manual_shape)
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
                            data_each_shape.append([])
                            mean_each_shape.append([])
                            mean_histogram.append([])
                            # flow_rate_actual = data_dict['config']['liquid']['actual measurement']['flow rate']

                            calculate_for_every_shape(manual_shape)
                            index = index_aux - 1

                            print(manual_shape)

fig, ax = plt.subplots()
labels_name = []

for i in range(0, len(name)):
    labels_name.append(name[i])
# plt.axvline(mean_value_array, color='k', linestyle='dashed', linewidth=1)
x1 = np.linspace(-20, 200, endpoint=True)
ax.set_xlim(-20, 175)

for i in range(0, index_aux):
    """mu, sigma = scipy.stats.norm.fit(data_each_shape[i][0])
    best_fit_line = scipy.stats.norm.pdf(x1, mu, sigma)"""
    # ax.plot(x1, best_fit_line)
    # ax.hist(mean_value_array[i], edgecolor=colors[i], alpha=0.3) #bins=len(current_shapes)
    #ax.hist(data_each_shape[i][0], density=True, bins=x1, edgecolor=colors[i], alpha=0.3, color=colors[i])
    # ax.vlines(mean_each_shape[i][0], ymin=0, ymax=10000, colors=colors[i], label="mean "+name[i])
    ax.axvline(mean_each_shape[i][0], color=colors[i], label="mean "+name[i])
    sns.histplot(data_each_shape[i][0], color=colors[i], kde=True)
    """    
    best_fit_line = np.linspace(norm.ppf(0.01), norm.ppf(0.99), 180)
    ax.plot(best_fit_line, norm.pdf(best_fit_line), color=colors[i])
    """
    # ax.plot(mean_each_shape[i][0])
    print("!!!!!"+str(i))
    # ax.axhline(mean_value_array[i], color=colors[i], lw=2, alpha=0.5)

# ax.hist(mean_div_max_variation_array, bins=len(current_shapes), edgecolor='black', alpha=0.3)
ax.set_title("Histogram and vertical line with the mean of 50k values for each shape of " + name_liquid, fontsize=10)
ax.set_xlabel("Value current [nA]")
ax.set_ylabel("Count of datapoints")

# ax.label(labels_name)
ax.legend(loc='best')
handles = [Rectangle((0, 0), 1, 1, color=c, ec="k") for c in colors]
ax.legend(handles, labels_name)
plt.rcParams["figure.figsize"] = (20, 12)
# ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=len(name)))
plt.show()
plt.savefig(
    "C:/Users/hvvhl/PycharmProjects/pyco/plot_generated/plot_sjaak_std_mean_mean_median" + current_shapes[3] + str(
        name[j]) + ".svg", format='svg', dpi=300)
