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


data_window = pd.read_feather("map4.feather")
print(data_window.info())
print(data_window.head())




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
    datapoints = np.array(data_window['data [nA]'])[x_value]
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
#              PLOTTING 1
######################################

fig, axs = plt.subplots(3, 1)

axs[0].set(ylabel='ccurent nA')
axs[0].plot(data_window['data [nA]'].explode())
axs[0].grid()

axs[1].set(ylabel='voltage (V)')
axs[1].set_yticks(np.arange(0, 7500, 500))
axs[1].scatter(data_window.index, data_window['target voltage'], color=data_window['colormap'])
axs[1].grid()

axs[2].set(ylabel='mean')
axs[2].set_ylim(0, 300)
axs[2].scatter( data_window.index, data_window['mean'], color=data_window['colormap'])
axs[2].grid()

fig.canvas.mpl_connect('button_press_event', onpick)

plt.xlabel('Legend:  blue = Intermittend ; red = Cone Jet ; green = Dripping ; purple = streamer onset ; black = Undefined ')
plt.show()


# ######################################
# #              PLOTTING  2
# ######################################

# data_window['flow rate [m3/s]'] = data_window['flow rate [m3/s]'].astype(float)
# plt.scatter(data_window['flow rate [m3/s]'], data_window['target voltage'], color=data_window['colormap'])
# plt.ylabel('Voltage [V]')
# plt.xlabel('Flow Rate [uL/min]')
# plt.title("colors = {'Cone Jet':'red', 'Dripping':'green', 'Intermittent':'blue', 'Multi Jet':'purple', 'Undefined':'black', 'Corona':'cyan'}")
# plt.show()





