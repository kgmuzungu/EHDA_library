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

file_path = "joaoData/mapping/"

file_name = "map2"


with open(file_path + file_name + ".json", 'r') as data_file:    
    data = json.loads(data_file.read())  


######################################
#          NORMALIZING DATA
######################################


print("\ndata_sample\n")
data_sample = pd.json_normalize(
    data['measurements'], 
    record_path = ["current"], 
    record_prefix ='data-',
    meta = ["name", "flow_rate", "voltage", "current_PS", "temperature", "humidity", "target_voltage"]
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
#           fft on_cick
######################################

def onpick(event):
    print (f'button={event.button}, x={event.x}, y={event.y}, xdata={event.xdata}, ydata={event.ydata}')
    
    x_value = event.xdata / 5 # round x value per multiple of five
    x_value = round(x_value) * 5

    # low pass filter to flatten out noise
    cutoff_freq_normalized = 3000 / (0.5 * sampling_frequency)  # in Hz
    b, a = butter(6, Wn=cutoff_freq_normalized, btype='low',
                    analog=False)  # first argument is the order of the filter
    datapoints = np.array(data_window['current'])[x_value]
    datapoints_filtered = lfilter(b, a,datapoints)

    
    fig, axs = plt.subplots(2, 1)
    axs[0].set(xlabel='time [s]', ylabel='current (nA)', title='datapoints filtered', ylim=[-1e2, 4e2])
    axs[0].plot(datapoints_filtered)
    axs[0].grid()

    axs[1].set(xlabel='Frequency [Hz]', ylabel='mag',title='fourier transform of filtered data', ylim=[0, 1e6], xlim=[0, 300])
    freq = np.fft.fftfreq(len(datapoints_filtered), d=(1/sampling_frequency))
    axs[1].plot(freq, np.fft.fft(datapoints_filtered))
    axs[1].grid()

    plt.title(f'sample window: {x_value}')
    plt.show()



######################################
#              PLOTTING
######################################

#Oscilloscope data
fig, axs = plt.subplots(2, 1)
plt.title(file_name)
axs[0].set(ylabel='ccurent nA')
axs[0].plot(data_sample.index/sampling_frequency, data_sample['data-0'])
axs[0].grid()

axs[1].set(ylabel='voltage (V)')
axs[1].set_yticks(np.arange(0, 7500, 10))
axs[1].plot(data_sample.index/sampling_frequency, data_sample['voltage'])
axs[1].grid()
plt.show()

# # Other data
# fig, axs = plt.subplots(5, 1)

# axs[0].set(ylabel='ccurent nA')
# axs[0].plot((data_sample.index/sampling_frequency)/60, data_sample['data-0'])
# axs[0].grid()

# axs[1].set(ylabel='voltage (V)')
# axs[1].set_yticks(np.arange(0, 5000, 10))
# axs[1].plot(data_sample.index/sampling_frequency, data_sample['voltage'])
# axs[1].grid()

# axs[2].set(ylabel='mean')
# axs[2].set_ylim(0, 300)
# axs[2].scatter( data_window.index, data_window['mean'], color=data_window['colormap'])
# axs[2].grid()

# axs[3].set(ylabel='median')
# axs[3].scatter( data_window.index, data_window['median'], color=data_window['colormap'])
# axs[3].grid()

# axs[4].set(ylabel='deviation')
# axs[4].scatter( data_window.index, data_window['deviation'], color=data_window['colormap'])
# axs[4].grid()

# fig.canvas.mpl_connect('button_press_event', onpick)

# plt.xlabel('Legend:  blue = Intermittend ; red = Cone Jet ; green = Dripping ; purple = streamer onset ; black = Undefined ')
# plt.show()





