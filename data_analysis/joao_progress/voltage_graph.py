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


with open("joaoData/" + "data2" + ".json", 'r') as data_file:    
    data = json.loads(data_file.read())  

data_measurements = pd.json_normalize(data, record_path=['measurements'])
data_processing = pd.json_normalize(data, record_path=['processing'])
df = pd.concat([data_measurements, data_processing], axis=1)

print(df.info())

fig, axs = plt.subplots(2, 2)
# plt.title()
axs[0].set(ylabel='mean curent nA',  xlabel='Voltage')
axs[0].scatter(df['voltage'], df['mean'])
# axs[0].set_xticks(np.arange(3000, 11000, 100))
axs[0].grid()

plt.show()