'''
	Transforming Monica JSON data captured in summer experiments
	AUTHOR: 乔昂 - jueta
	DATE: 01/11/2022
'''

import pandas as pd
from pandas.io.json import json_normalize
import json
import matplotlib.pyplot as plt
from sklearn.utils import column_or_1d
import numpy as np
import scipy.fftpack
import easygui



# warnings.filterwarnings('ignore')
osci_freq = 100000


file_path1 = "monicaData/summer2022/"
file_path2 = "joaoData/"

file_name1 = "rampsetup9water60alcohol40_all shapes_1.3889e-09m3_s"
file_name2 = "stepsetup9water60alcohol40_all shapes_1.3611220000000002e-09m3_s"
file_name3 = "rampsetup9water60alcohol40_all shapes_1.416678e-09m3_s"
file_name4 = "rampsetup92propanol_all shapes_1.777792e-09m3_s"
file_name5 = "stepsetup9ethanol_all shapes_9.7223e-10m3_s"
file_name6 = "rampsetup9ethanol_all shapes_9.7223e-10m3_s"
file_name7 = "stepsetup10water60alcohol40_all shapes_4.02781e-09m3_s"
file_name8 = "data1"
file_name9 = "data2"

easygui.msgbox("How to use this code: ..............")

msg ="What experiment do you want to run?"
title = "EDHA - Monicas data"
choices = [file_name1, file_name2, file_name3, file_name4, file_name5, file_name6, file_name7, file_name8, file_name9]
exp_choice = easygui.choicebox(msg, title, choices)


easygui.msgbox("You chose: " + str(exp_choice), "Survey Result")

with open(file_path2 + exp_choice + ".json", 'r') as data_file:    
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

    fig, axs = plt.subplots(2, 1)
    axs[0].set(ylabel='ccurent nA')
    axs[0].plot(np.array(data_window['data [nA]'])[x_value])
    axs[0].grid()

    axs[1].set(ylabel='fft magnitude', xlabel='frequency (Hz)')
    axs[1].plot(abs(scipy.fftpack.fft(np.array(data_window['data [nA]'])[x_value])[:300]))
    axs[1].grid()

    plt.title(f'fast fourier of sample window: {x_value}')
    plt.show()



######################################
#              PLOTTING
######################################


if easygui.ynbox(msg="What tool want to use", title="Monica Data Analysis", choices=["Oscilloscope data", "Statistic Data"]):

    fig, axs = plt.subplots(2, 1)
    plt.title(exp_choice)
    axs[0].set(ylabel='ccurent nA')
    axs[0].plot(data_sample.index/osci_freq, data_sample['data-0'])
    axs[0].grid()

    axs[1].set(ylabel='voltage (V)')
    axs[1].set_yticks(np.arange(0, 5000, 10))
    axs[1].plot(data_sample.index/osci_freq, data_sample['voltage'])
    axs[1].grid()
    plt.show()

else:

    fig, axs = plt.subplots(7, 1)

    axs[0].set(ylabel='ccurent nA')
    axs[0].plot(data_sample.index/osci_freq, data_sample['data-0'])
    axs[0].grid()

    axs[1].set(ylabel='voltage (V)')
    axs[1].set_yticks(np.arange(0, 5000, 10))
    axs[1].plot(data_sample.index/osci_freq, data_sample['voltage'])
    axs[1].grid()

    axs[2].set(ylabel='rms')
    axs[2].scatter( data_window.index, data_window['rms'], color=data_window['colormap'])
    axs[2].grid()

    axs[3].set(ylabel='mean')
    axs[3].set_ylim(0, 300)
    axs[3].scatter( data_window.index, data_window['mean'], color=data_window['colormap'])
    axs[3].grid()

    axs[4].set(ylabel='variance')
    axs[4].scatter( data_window.index, data_window['variance'], color=data_window['colormap'])
    axs[4].grid()

    axs[5].set(ylabel='deviation')
    axs[5].scatter( data_window.index, data_window['deviation'], color=data_window['colormap'])
    axs[5].grid()

    axs[6].set(ylabel='median')
    axs[6].scatter( data_window.index, data_window['median'], color=data_window['colormap'])
    axs[6].grid()

    fig.canvas.mpl_connect('button_press_event', onpick)

    plt.xlabel('samples')
    plt.show()





