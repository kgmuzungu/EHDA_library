'''
	JSON Data flattening to pandas
	AUTHOR: 乔昂 - jueta
	DATE: 28/11/2022
'''

import pandas as pd
import json
import matplotlib.pyplot as plt



file_path1 = "joaoData/control/"
sampling_frequency = 1e5

with open(file_path1 + 'data5' + ".json", 'r') as data_file:    
    data = json.loads(data_file.read())  

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


plt.plot(data_window.index, data_window['target voltage'].astype(float))
plt.scatter(data_window.index, data_window['voltage'].astype(float))

plt.show()

