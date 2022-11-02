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

file_path1 = "summer2022/rampsetup9ethanol_all shapes_5.000040000000001e-10m3_s.json"
file_path2 = "summer2022/rampsetup9paraffin_all shapes_1.6666799999999999e-09m3_s.json"
file_path3 = "summer2022/rampsetup9water60alcohol40_all shapes_1.416678e-09m3_s.json"
file_path4 = "summer2022/rampsetup92propanol_all shapes_1.777792e-09m3_s.json"

with open(file_path1, 'r') as data_file:    
    data = json.loads(data_file.read())  


######################################
#          NORMALIZING DATA
######################################


print("\ndata_sample\n")
data_sample = pd.json_normalize(
    data['measurements'], 
    record_path = ["data [nA]"], 
    record_prefix ='data-',
    meta = ["name", "flow rate [m3/s]", "voltage", "current PS", "temperature", "humidity", "spray mode"]
)
print(data_sample.info())


print("\data_window\n")
measurements_data_window = pd.json_normalize(data['measurements'])
processing_data_window = pd.json_normalize(data['processing'])
data_window = [measurements_data_window, processing_data_window]
data_window = pd.concat(data_window, axis=1)
print(data_window.info())


######################################
#              PLOTTING
######################################

fig, axs = plt.subplots(9, 1)

axs[0].set(ylabel='data [nA]')
axs[0].plot(data_sample['data-0'])

axs[1].set(ylabel='voltage')
axs[1].plot(data_sample['voltage'])

axs[2].set(ylabel='current PS')
axs[2].plot(data_sample['current PS'])

axs[3].set(ylabel='mean')
axs[3].scatter( data_window.index, data_window['mean'])

axs[4].set(ylabel='variance')
axs[4].scatter( data_window.index, data_window['variance'])

axs[5].set(ylabel='deviation')
axs[5].scatter( data_window.index, data_window['deviation'])

axs[6].set(ylabel='median')
axs[6].scatter( data_window.index, data_window['median'])

axs[7].set(ylabel='rms')
axs[7].scatter( data_window.index, data_window['rms'])

axs[8].set(ylabel='maximum variation distance')
axs[8].scatter( data_window.index, data_window['maximum variation distance'])


plt.xlabel('samples')
plt.show()

