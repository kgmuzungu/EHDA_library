'''
	JSON Data flattening to pandas
	AUTHOR: 乔昂 - jueta
	DATE: 28/11/2022
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


with open("joaoData/" + "data3" + ".json", 'r') as data_file:    
    data = json.loads(data_file.read())  

data_measurements = pd.json_normalize(data, record_path=['measurements'])
data_processing = pd.json_normalize(data, record_path=['processing'])
df = pd.concat([data_measurements, data_processing], axis=1)

print(df)

current_df = pd.concat([df['data [nA]'], df['spray mode.Sjaak']],  axis=1)

print(current_df)

size = 50000
last_value = 0

for sample in current_df.index:
    if current_df['spray mode.Sjaak'][sample] == 'intermittent' or current_df['spray mode.Sjaak'][sample] == 'intermittent 1':
        plt.plot(np.arange(last_value, last_value + size), current_df['data [nA]'][sample], c='blue', label='intermittent')
    elif current_df['spray mode.Sjaak'][sample] == 'cone jet ':
        plt.plot(np.arange(last_value, last_value + size), current_df['data [nA]'][sample], c='red', label='cone jet')
    elif current_df['spray mode.Sjaak'][sample] == 'dripping' or current_df['spray mode.Sjaak'][sample] == 'dripping 1 ':
        plt.plot(np.arange(last_value, last_value + size), current_df['data [nA]'][sample], c='green', label='dripping')
    else:
        plt.plot(np.arange(last_value, last_value + size), current_df['data [nA]'][sample], c='black', label='Undefined')
    # plt.plot(np.arange(last_value, last_value + size), current_df['data [nA]'][sample])
    last_value += size

    
plt.figtext(.2, .7, "               Legend \n blue = Intermittend \n red = Cone Jet \n green = Dripping \n black = Undefined \n ")
plt.show()