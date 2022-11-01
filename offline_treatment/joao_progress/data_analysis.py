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

print("measurements_data_sample")
measurements_data_sample = pd.json_normalize(
    data['measurements'], 
    record_path =["data [nA]"], 
    record_prefix='data-',
    meta=["name", "flow rate [m3/s]", "voltage", "current PS", "temperature", "humidity", "spray mode"]
)
print(measurements_data_sample)

print("measurements_data_window")
measurements_data_window = pd.json_normalize(data['measurements'])
print(measurements_data_window)

# PROCESSING DATA

# processing_data_sample = pd.json_normalize(data['processing'], "psd welch", ["mean", "variance", "deviation", "median", "rms", "maximum variation distance"])
# print(processing_data_sample)

print("processing_data_window")
processing_data_window = pd.json_normalize(data['processing'])
print(processing_data_window)





######################################
#              PLOTTING
######################################

fig, axs = plt.subplots(3, 1, sharex=True)

axs[0].set(ylabel='data [nA]')
axs[0].plot(measurements_data_sample['data-0'])

axs[1].set(ylabel='voltage')
axs[1].plot(measurements_data_sample['voltage'])

axs[2].set(ylabel='current PS')
axs[2].plot(measurements_data_sample['current PS'])




plt.xlabel('samples')
plt.show()

