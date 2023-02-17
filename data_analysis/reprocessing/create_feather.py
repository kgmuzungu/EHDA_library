'''
	AUTHOR: 乔昂 - jueta
	DATE: 27/01/2023
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

file_path = "../../Data/"

file_name = "exp26-01-1"


with open(file_path + file_name + ".json", 'r') as data_file:    
    data = json.loads(data_file.read())  


######################################
#          NORMALIZING DATA
######################################


print("\data_window\n")
measurements_data_window = pd.json_normalize(data['measurements'])
processing_data_window = pd.json_normalize(data['processing'])
data_window = [measurements_data_window, processing_data_window]
data_window = pd.concat(data_window, axis=1)


colormap = []
for electro_class in data['spray mode']:
    if electro_class == 'Intermittent':
        colormap.append('blue')
    elif electro_class == 'Cone Jet':
        colormap.append('red')
    elif electro_class == 'Dripping':
        colormap.append('green')
    elif electro_class == 'Multi Jet':
        colormap.append('purple')
    elif electro_class == 'Corona':
        colormap.append('cyan')
    elif electro_class == 'Undefined':
        colormap.append('black')
    else:
        colormap.append('black')


data.insert(1, 'colormap', colormap)



data_window.to_feather("map4.feather")