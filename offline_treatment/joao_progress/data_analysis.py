'''
	Transforming Monica JSON data captured in summer experiments
	AUTHOR: 乔昂 - jueta
	DATE: 01/11/2022
'''

import pandas as pd
import warnings
from pandas.io.json import json_normalize
import json
import matplotlib.pyplot as plt


warnings.filterwarnings('ignore')

file_path = "summer2022/rampsetup9ethanol_all shapes_5.000040000000001e-10m3_s.json"

with open(file_path, 'r') as data_file:    
    data = json.loads(data_file.read())  


######################################
#          NORMALIZING DATA
######################################


# MEASUREMENT DATA

print("\nmeasurements_data_sample\n")
measurements_data_sample = pd.json_normalize(
    data['measurements'], 
    record_path = ["data [nA]"], 
    record_prefix ='data-',
    meta = ["name", "flow rate [m3/s]", "voltage", "current PS", "temperature", "humidity", "spray mode"]
)
print(measurements_data_sample.info())

print("\nmeasurements_data_window\n")
measurements_data_window = pd.json_normalize(data['measurements'])
print(measurements_data_window.info())

# PROCESSING DATA

print("\nprocessing_data_sample\n")
processing_data_sample = pd.json_normalize(
    data['processing'],
    record_path = "psd welch",   # what is psd welch??   is it really the record path??
    meta = ["mean", "variance", "deviation", "median", "rms", "maximum variation distance"]
)
print(processing_data_sample.info())

print("\nprocessing_data_window\n")
processing_data_window = pd.json_normalize(data['processing'])
print(processing_data_window.info())





######################################
#              PLOTTING
######################################

fig, axs = plt.subplots(9, 1)

axs[0].set(ylabel='data [nA]')
axs[0].plot(measurements_data_sample['data-0'])

axs[1].set(ylabel='voltage')
axs[1].plot(measurements_data_sample['voltage'])

axs[2].set(ylabel='current PS')
axs[2].plot(measurements_data_sample['current PS'])



axs[3].set(ylabel='mean')
axs[3].scatter( processing_data_window.index, processing_data_window['mean'])

axs[4].set(ylabel='variance')
axs[4].scatter( processing_data_window.index, processing_data_window['variance'])

axs[5].set(ylabel='deviation')
axs[5].scatter( processing_data_window.index, processing_data_window['deviation'])

axs[6].set(ylabel='median')
axs[6].scatter( processing_data_window.index, processing_data_window['median'])

axs[7].set(ylabel='rms')
axs[7].scatter( processing_data_window.index, processing_data_window['rms'])

axs[8].set(ylabel='maximum variation distance')
axs[8].scatter( processing_data_window.index, processing_data_window['maximum variation distance'])





plt.xlabel('samples')
plt.show()

