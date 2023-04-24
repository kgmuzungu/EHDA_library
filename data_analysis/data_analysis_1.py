'''
	JSON Data analysis from the experiments
	AUTHOR: 乔昂 - jueta
	DATE: 24/11/2022
'''

import pandas as pd
from pandas.io.json import json_normalize
import json
import matplotlib.pyplot as plt
from sklearn.utils import column_or_1d
import numpy as np
from scipy.signal import butter, lfilter


# warnings.filterwarnings('ignore')
sampling_frequency = 1e5

file_path = "Data/control/"

file_name = "data3"


with open(file_path + file_name + ".json", 'r') as data_file:    
    data = json.loads(data_file.read())  


######################################
#          NORMALIZING DATA
######################################


print("\ndata_sample\n")


data_sample = pd.json_normalize(
    data['measurements'], 
    record_path = ["data [nA]"], 
    record_prefix ='data [nA]-',
    meta = ["name", "flow rate [m3/s]", "voltage", "current PS", "temperature", "humidity", "target voltage"]
)
print(data_sample.info())


print("\data_window\n")
measurements_data_window = pd.json_normalize(data['measurements'])
processing_data_window = pd.json_normalize(data['processing'])
data_window = [measurements_data_window, processing_data_window]
data_window = pd.concat(data_window, axis=1)

colormap = []
for electro_class in data_window['spray mode.Sjaak']:
    if electro_class == 'Intermittent':
        colormap.append('blue')
    elif electro_class == 'Cone Jet':
        colormap.append('red')
    elif electro_class == 'Dripping':
        colormap.append('green')
    else:
        colormap.append('black')

# Monica spark classification
sampleIndex = 0
for monica_class in data_window['spray mode.Monica']:
    if monica_class == 'streamer onset':
        colormap[sampleIndex] = 'purple'
    sampleIndex+=1



data_window.insert(1, 'colormap', colormap)

print(data_window.info())


######################################
#              PLOTTING
######################################

#Oscilloscope data
fig, axs = plt.subplots(3, 1)
# plt.title(file_name)
# axs[0].set(ylabel='curent nA')
# axs[0].plot(data_sample['data [nA]'])
# axs[0].grid()

axs[1].set(ylabel='voltage (V)')
axs[1].set_yticks(np.arange(0, 7500, 10))
axs[1].plot(data_sample.index/sampling_frequency, data_sample['voltage'])
axs[1].grid()
plt.show()

axs[2].set(ylabel='mean')
axs[2].set_ylim(0, 300)
axs[2].scatter( data_window.index, data_window['mean'], color=data_window['colormap'])
axs[2].grid()

from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], marker='o', color='w', label='Intermittent', markerfacecolor='blue', markersize=7),
                   Line2D([0], [0], marker='o', color='w', label='Dripping', markerfacecolor='green', markersize=7),
                   Line2D([0], [0], marker='o', color='w', label='Cone Jet', markerfacecolor='red', markersize=7),
                   Line2D([0], [0], marker='o', color='w', label='Multi Jet', markerfacecolor='purple', markersize=7),
                   Line2D([0], [0], marker='o', color='w', label='Undefined', markerfacecolor='black', markersize=7)]

plt.title("Automatic mapping jet modes - Pure Ethanol")
plt.legend(handles=legend_elements, bbox_to_anchor=(1.04, 1))

plt.show()





