'''
	Analysis of mapping V x FR experiments
	AUTHOR: 乔昂 - jueta
	DATE: 19/01/2023
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

file_path = "../Data/mapping/"


data = pd.read_feather("map4.feather")

# colormap = []
# for electro_class in data['spray mode']:
#     if electro_class == 'Intermittent':
#         colormap.append('blue')
#     elif electro_class == 'Cone Jet':
#         colormap.append('red')
#     elif electro_class == 'Dripping':
#         colormap.append('green')
#     elif electro_class == 'Multi Jet':
#         colormap.append('purple')
#     elif electro_class == 'Corona':
#         colormap.append('cyan')
#     elif electro_class == 'Undefined':
#         colormap.append('black')
#     else:
#         colormap.append('black')


# data.insert(1, 'colormap', colormap)

print(data.info())
print(data.head())



data['flow rate [m3/s]'] = data['flow rate [m3/s]'].astype(float)
plt.scatter(data['flow rate [m3/s]'], data['target voltage'], color=data['colormap'])
plt.ylabel('Voltage [V]')
plt.xlabel('Flow Rate [uL/min]')
plt.title("colors = {'Cone Jet':'red', 'Dripping':'green', 'Intermittent':'blue', 'Multi Jet':'purple', 'Undefined':'black', 'Corona':'cyan'}")
plt.show()
