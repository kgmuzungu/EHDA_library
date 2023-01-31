'''
	Non Real Time Processing the data
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
from electrospray import ElectrosprayDataProcessing, ElectrosprayConfig
from classification_electrospray import ElectrosprayClassification

# tiepie params
sampling_frequency = 1e5  # 100 KHz
multiplier_for_nA = 500

append_array_data = True
append_array_processing = True
FLAG_PLOT = True



# warnings.filterwarnings('ignore')
sampling_frequency = 1e5

file_path = "../Data/mapping/"

file_name = "map3"

electrospray_processing = ElectrosprayDataProcessing(sampling_frequency)
electrospray_classification = ElectrosprayClassification("name_liquid")

array_electrospray_processing = []
array_values = []


data = pd.read_feather("map3.feather")



#
#
#
#
#

# time_step = 1 / sampling_frequency

# # THREAD LOOP
# for data_queue in data['data [nA]']:


#     electrospray_data  = data_queue 

#     try:

#         # low pass filter to flatten out noise
#         cutoff_freq_normalized = 3000 / (0.5 * sampling_frequency)  # in Hz
#         b, a = butter(6, Wn=cutoff_freq_normalized, btype='low', analog=False)  # first argument is the order of the filter
#         datapoints_filtered = lfilter(b, a, electrospray_data)

#     except:
#         print("[DATA_PROCESSING THREAD] Failed to filter points!")

#     try:

#         electrospray_processing.calculate_filter(a, b, electrospray_data)
        
#         electrospray_processing.calculate_fft_raw(electrospray_data)

#         electrospray_processing.calculate_statistics( electrospray_data)
        
#         electrospray_processing_freq, electrospray_processing_psd = electrospray_processing.calculate_power_spectral_density(electrospray_data)

#         max_data, quantity_max_data, percentage_max = electrospray_processing.calculate_peaks_signal(electrospray_data)

#         max_fft_peaks, cont_max_fft_peaks = electrospray_processing.calculate_peaks_fft(electrospray_data)

#     except:
#         print("[DATA_PROCESSING THREAD] Failed to process data")

#     try:

#         classification_txt = electrospray_classification.do_classification(
#                                                                     electrospray_processing.mean_value,
#                                                                     electrospray_processing.med,
#                                                                     electrospray_processing.stddev,
#                                                                     electrospray_processing.psd_welch,
#                                                                     electrospray_processing.variance,
#                                                                     float(max_data), 
#                                                                     float(quantity_max_data),
#                                                                     float(percentage_max),
#                                                                     10,
#                                                                     max_fft_peaks,
#                                                                     cont_max_fft_peaks
#                                                                     )
#     except:
#         print("[DATA_PROCESSING THREAD] Failed to classify")


#     try:

#         current_shape = str(classification_txt)
#         print(current_shape)

#         electrospray_processing.set_shape(current_shape)

#         txt_max_peaks = " Max: " + str(max_data) + " Quantity max: " + str(quantity_max_data) + " Percentage: " + str(percentage_max)

#         electrospray_processing.calculate_fft_filtered()
#         electrospray_processing.calculate_fft_peaks()

#         d_electrospray_processing = electrospray_processing.get_statistics_dictionary()
#         array_electrospray_processing.append(current_shape)
#         array_values = electrospray_data



#     except:
#         print("[DATA_PROCESSING THREAD] Failed to finish process")

# print("[DATA_PROCESSING THREAD] Finish Processing data")


# print(array_electrospray_processing)


# #
# #
# #
# #

# colormap = []
# for electro_class in array_electrospray_processing:
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

fig, axs = plt.subplots(3, 1)
axs[0].plot(data['data [nA]'][459])
axs[0].grid()

axs[1].plot(data['data [nA]'][460])
axs[1].grid()

axs[2].plot(data['data [nA]'][461])
axs[2].grid()
plt.show()


# data['flow rate [m3/s]'] = data['flow rate [m3/s]'].astype(float)
# plt.scatter(data['flow rate [m3/s]'], data['target voltage'], color=data['colormap'])
# plt.ylabel('Voltage [V]')
# plt.xlabel('Flow Rate [uL/min]')
# plt.title("colors = {'Cone Jet':'red', 'Dripping':'green', 'Intermittent':'blue', 'Multi Jet':'purple', 'Undefined':'black', 'Corona':'cyan'}")
# plt.show()
