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
from sklearn.utils import column_or_1d
import numpy as np
import scipy.fftpack

warnings.filterwarnings('ignore')

file_path1 = "summer2022/rampsetup9ethanol_all shapes_5.000040000000001e-10m3_s.json"
file_path2 = "summer2022/rampsetup9paraffin_all shapes_1.6666799999999999e-09m3_s.json"
file_path3 = "summer2022/rampsetup9water60alcohol40_all shapes_1.416678e-09m3_s.json"
file_path4 = "summer2022/rampsetup92propanol_all shapes_1.777792e-09m3_s.json"

sample = 20

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

colormap = []
for electro_class in data_window['spray mode.Sjaak']:
    if electro_class == 'intermittent' or electro_class == 'intermittent 1':
        colormap.append('blue')
    elif electro_class == 'cone jet ':
        colormap.append('red')
    elif electro_class == 'dripping' or electro_class == 'dripping 1 ':
        colormap.append('green')
    else:
        colormap.append('black')

data_window.insert(1, 'colormap', colormap)

print(data_window.info())



######################################
#              PLOTTING
######################################

# algoritmo para fft de cada sample
arrayUsed = np.array(data_window['data [nA]'])
print(arrayUsed[sample])
yf = scipy.fftpack.fft(arrayUsed[sample])


plt.plot(yf)
plt.grid()
plt.title(f'fast fourier of sample window: {sample}')
plt.ylabel('fft magnitude')
plt.xlabel('frequency (Hz)')
plt.show()

