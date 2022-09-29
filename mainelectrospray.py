# OscilloscopeBlock.py
# This example performs a block mode measurement and writes the data to OscilloscopeBlock.csv.
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function

import codecs
import time
import threading
import sys
import libtiepie
from printinfo import *
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from scipy import signal
from time import gmtime, strftime
import csv
import configparser
from electrospray import ElectrosprayDataProcessing
from electrospray import ElectrosprayConfig
from electrospray import ElectrosprayMeasurements
from validationelectrospray import ElectrosprayValidation
from classification_electrospray import ElectrosprayClassification
from aux_functions_electrospray import *
from serial_FUG import serial_sync
import configuration_tiepie

import os
import re
import numpy as np
import json
import logging
import pylab

fig = pylab.gcf()

LOG_FILENAME = r'logging_test.out'

logging.basicConfig(filename=LOG_FILENAME, encoding='utf-8', format='%(asctime)s %(message)s', level=logging.INFO)
logging.info('Started')

multiplier_for_nA = 500
sampling_frequency = 1e5

a_electrospray_measurements = []
a_electrospray_measurements_data = []
a_electrospray_processing = []
a_statistics = []
append_array_measurements = []

d_electrospray_measurements = {}
d_electrospray_measurements_data = {}
d_electrospray_processing = {}
d_statistics = {}


# ************************************
#       INITIAL CONFIGURATION
# ************************************
#  save_data = input("Would you like to save data? [True/False] ")
VAR_BIN_CONFIG = True
save_data = VAR_BIN_CONFIG
append_array_data = VAR_BIN_CONFIG
save_processing = VAR_BIN_CONFIG
append_array_processing = VAR_BIN_CONFIG
save_config = VAR_BIN_CONFIG
save_liquid = VAR_BIN_CONFIG

# ************************************
#   INIT CONFIG OF LIQUID AND SETUP
# ************************************
impedance, temperature, humidity = 2000000, 21, 31
# Q = 0.0110  # ml/h flow rate
# Q = Q * 2.7778e-3  # cm3/s
Q = 106 
Q = Q * 10e-6  # liter/h
Q = Q * 2.7778e-7  # m3/s

name_setup = "setup7"
setup = "C:/Users/hvvhl/PycharmProjects/pyco/setup/" + name_setup
name_liquid = "ethyleneglycol"
liquid = "liquid/" + name_liquid
# liquids = ["ethyleneglycolHNO3", "ethanol", water60alcohol40]

current_shapes = ["no voltage no fr", "no voltage", "dripping", "intermittent", "cone jet", "multijet",
                  "streamer onset", "dry"]
# 0no voltage no fr/1no voltage/2dripping/3intermittent/4cone jet/5multijet/6streamer onset/7dry"]
current_shape = current_shapes[6]  
current_shape_comment = ""

voltage = 9.2 
# voltage = input("Enter voltage [kV]: ")
voltage = voltage * 1000  # V

k_electrical_conductivity = 0.34  # uS/cm 
k_electrical_conductivity = k_electrical_conductivity * 10e-4  # S/m

number_measurements = 10
flag_sjaak = ""
flag_plot = False
day_measurement = strftime("%a_%d %b %Y", gmtime())
res = ""
j = 0
plt.style.use('seaborn-colorblind')
plt.ion()


# ************************************
#           Electrospray
# ************************************
electrospray_config_liquid_setup_obj = ElectrosprayConfig(setup + ".json", liquid + ".json")
electrospray_config_liquid_setup_obj.load_json_config_liquid()
electrospray_config_liquid_setup_obj.load_json_config_setup()

electrospray_config_liquid_setup_obj.set_flow_rate(Q)
electrospray_config_liquid_setup_obj.set_voltage(voltage)
electrospray_config_liquid_setup_obj.set_electrical_conductivity(k_electrical_conductivity)
electrospray_config_liquid_setup_obj.set_shape_manual(current_shape)
electrospray_config_liquid_setup_obj.set_comment_current(current_shape_comment)
electrospray_config_liquid_setup_obj.flow_rate_min_est_chen_pui()

aux_obj = electrospray_config_liquid_setup_obj.get_dict_config()
electrospray_validation = ElectrosprayValidation(name_liquid)
electrospray_classification = ElectrosprayClassification(name_liquid)
electrospray_processing = ElectrosprayDataProcessing(sampling_frequency)

#  search json dir
listdir = os.listdir()
for i in listdir:
    res = re.search(liquid + ".json", i)
    if res is None:
        continue
    else:
        filename = i
        print(filename)
        print("*******")



# ************************************
#              TiePie
# ************************************
def config_TiePieScope(scp):
    # ToDo set input to single ended or differential
    # in oscilloscopechannel.py _get_is_differential or _get_impedance ... investigate further
    """print("SCP is differential: %s" % scp.channels[0].is_differential)
    print("SCP impedance: %s" % scp.channels[0].impedance)
    print("SCP is safe_ground: %s" % scp.channels[0].safe_ground_enabled)"""
    # !!!! input impedance by default is 2MOhm ... is in differential mode
    scp.measure_mode = libtiepie.MM_BLOCK
    scp.sample_frequency = sampling_frequency
    scp.record_length = 50000  # 10000 samples
    scp.pre_sample_ratio = 0  # 0 %
    scp.channels[0].enabled = True
    scp.channels[0].range = 4  # range in V
    # ToDo using autoranging would be an advantage?
    scp.channels[0].coupling = libtiepie.CK_DCV  # DC Volt
    scp.channels[0].trigger.enabled = True
    scp.channels[0].trigger.kind = libtiepie.TK_RISINGEDGE
    scp.channels[1].enabled = False
    scp.channels[2].enabled = False
    scp.channels[3].enabled = False
    scp.trigger_time_out = 100e-3  # 100 ms
    # Disable all channel trigger sources:
    for ch in scp.channels:
        ch.trigger.enabled = False
    # Setup channel trigger:
    ch = scp.channels[0]  # Ch 1
    # Enable trigger source:
    ch.trigger.enabled = True
    ch.trigger.kind = libtiepie.TK_RISINGEDGE  # Rising edge
    ch.trigger.levels[0] = 0.5  # 50 %
    ch.trigger.hystereses[0] = 0.05  # 5 %
    return scp


# Print library info:
print_library_info()

time_step = 1 / sampling_frequency

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

fig, ax = plt.subplots(3)

# Try to open an oscilloscope with block measurement support:
scp = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):
        scp = item.open_oscilloscope()

if scp:
    try:
        scp = configuration_tiepie.config_TiePieScope(scp, sampling_frequency)

        # Print oscilloscope info:
        print_device_info(scp)

        # Start measurement:
        scp.start()

        # Wait for measurement to complete:
        while not scp.is_data_ready:
            time.sleep(0.05)  # 50 ms delay, to save CPU time

        # Get data:
        data = scp.get_data()
        time_start = time.time()

        #  1Mohm input resistance when in single ended input mode
        datapoints = np.array(data[0]) * multiplier_for_nA  # 2Mohm default input resistance

        # low pass filter to flatten out noise
        cutoff_freq_normalized = 3000 / (0.5 * sampling_frequency)  # in Hz
        b, a = butter(6, Wn=cutoff_freq_normalized, btype='low',
                      analog=False)  # first argument is the order of the filter
        datapoints_filtered = lfilter(b, a, datapoints)
        # check here to plot the transfer function of the filter
        # https://stackoverflow.com/questions/25191620/creating-lowpass-filter-in-scipy-understanding-methods-and-units

        # animated=True tells matplotlib to only draw the artist when we explicitly request it
        ax[0].set(xlabel='time [s]', ylabel='current (nA)', title='osci reading', ylim=[-3e2, 3e2])
        # ax[0].text(.5, .5, 'blabla', animated=True)
        (ln0,) = ax[0].plot(np.arange(0, len(datapoints) * time_step, time_step), datapoints, animated=True)
        (ln1,) = ax[1].plot(np.arange(0, len(datapoints_filtered) * time_step, time_step), datapoints_filtered,
                            animated=True)
        freq = np.fft.fftfreq(len(datapoints_filtered), d=time_step)

        ax[1].set(xlabel='time', ylabel='nA', title='LP filtered', ylim=[-1e1, 5e2])
        (ln2,) = ax[2].plot(freq[0:500], np.zeros(500), animated=True)
        # (ln2,) = ax[2].plot(freq, np.zeros(len(datapoints_filtered)), animated=True)
        ax[2].set(xlabel='Frequency [Hz]', ylabel='mag', title='fourier transform', ylim=[0, 1e6])
        # freqs_psd, psd = signal.welch(datapoints)
        # (ln3,) = ax[3].semilogx(freqs_psd, psd)
        # ax[3].set(xlabel='Frequency [Hz]', ylabel='Power', title='power spectral density')
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()

        # make sure the window is raised, but the script keeps going
        plt.show(block=False)
        plt.pause(0.1)

        # get copy of entire figure (everything inside fig.bbox) sans animated artist
        bg = fig.canvas.copy_from_bbox(fig.bbox)

        # draw the animated artist, this uses a cached renderer
        ax[0].draw_artist(ln0)
        ax[1].draw_artist(ln1)
        ax[2].draw_artist(ln2)
        # fig.canvas.manager.set_window_title('Sjaak: ' + str(flag_sjaak))
        fig.canvas.blit(fig.bbox)
        # fig.canvas.text(0.01, 0.01, 'sjaak = ' + str(flag_sjaak), fontsize=16, color='C1')

        # 600 measurements a 50k samples a 100kHz equals to 5min, one measurement is 500ms
        for j in range(number_measurements):
            # reset the background back in the canvas state, screen unchanged
            fig.canvas.restore_region(bg)

            electrospray_data = ElectrosprayMeasurements(liquid, datapoints, voltage, Q, temperature,
                                                         humidity, day_measurement)

            electrospray_processing.calculate_filter(a, b, electrospray_data.data)
            electrospray_processing.calculate_fft_raw(electrospray_data.data)
            electrospray_processing.calculate_statistics(electrospray_data.data,
                                                         electrospray_processing.datapoints_filtered)
            electrospray_processing.calculate_fft_filtered()
            electrospray_processing_freq, electrospray_processing_psd = electrospray_processing.calculate_power_spectral_density(
                electrospray_data.data)
            electrospray_processing.calculate_fft_peaks()
            max_data, quantity_max_data, percentage_max = electrospray_processing.calculate_peaks(electrospray_data.data)
            txt_max_peaks = " Max: " + str(max_data) + " Quantity max: " + str(quantity_max_data) + " Percentage: " + str(percentage_max)

            ln0.set_ydata(electrospray_data.data)
            ln1.set_ydata(electrospray_processing.datapoints_filtered)
            ln2.set_ydata(
                (electrospray_processing.fourier_transform[0:500]))
            ax[0].legend(bbox_to_anchor=(1.05, 1),
                         loc='upper left', borderaxespad=0.)
            # re-render the artist, updating the canvas state, but not the screen
            ax[0].draw_artist(ln0)
            ax[1].draw_artist(ln1)
            ax[2].draw_artist(ln2)
            txt_sjaak_str = str(flag_sjaak)
            fig.canvas.manager.set_window_title('Sjaak: ' + txt_sjaak_str + ' ; Peaks:' + txt_max_peaks)
            # copy the image to the GUI state, but screen might not be changed yet
            fig.canvas.blit(fig.bbox)
            # flush any pending GUI events, re-painting the screen if needed
            fig.canvas.flush_events()
            flag_sjaak = electrospray_classification.do_sjaak(electrospray_processing.mean_value,
                                                              electrospray_processing.med,
                                                              electrospray_processing.stddev,
                                                              electrospray_processing.psd_welch,
                                                              electrospray_processing.variance,
                                                              current_shape, current_shape_comment)
            if current_shape == "cone jet" and flag_plot:
                # electrospray_validation.plot_mean(electrospray_processing.datapoints_filtered, electrospray_processing.mean_value)
                # electrospray_validation.open_load_cone_jet()
                electrospray_validation.set_data_from_dict_liquid(
                    electrospray_config_liquid_setup_obj.get_json_liquid())
                electrospray_validation.calculate_scaling_laws_cone_jet(electrospray_data.data,
                                                                        electrospray_processing.mean_value, Q)
            # electrospray_classification.do_monica(electrospray_data.data, electrospray_processing.mean_value)
            if append_array_data:
                d_electrospray_measurements = electrospray_data.get_measurements_dictionary()
                a_electrospray_measurements.append(d_electrospray_measurements)
                """
                a_electrospray_measurements.append(electrospray_data))
                logging.info('repr electrospray_data: %s' % repr(electrospray_data))
                a_electrospray_measurements_data.append(electrospray_data.data)
                logging.info('repr electrospray_data: %s' % (electrospray_data.data))
                a_statistics.append(repr(electrospray_processing))
                a_electrospray_processing_datafilter.append(electrospray_processing.datapoints_filtered)
                """
            if append_array_processing:
                d_electrospray_processing = electrospray_processing.get_statistics_dictionary()
                a_electrospray_processing.append(d_electrospray_processing)

            # Start new measurement:
            scp.start()
            # Wait for measurement to complete:
            while not scp.is_data_ready:
                time.sleep(0.05)  # 50 ms delay, to save CPU time

            # Get data:
            data = scp.get_data()
            datapoints = np.array(data[0]) * multiplier_for_nA
            time_end = time.time() - time_start

    except Exception as e:
        print('Exception: ' + e.message)
        sys.exit(1)
    # Close oscilloscope:
    del scp
else:
    print('No oscilloscope available with block measurement support!')
    sys.exit(1)

"""                                                                                                                                                                                                                                                                                                     
    if save_config:
    load_setup("ethanol.json", repr(electrospray_config_liquid_setup_obj))
    shape = input("Enter manual classification for the recorded shape : ")
    a_statistics.append("manual_shape: " + shape + ", voltage:"+str(voltage))
"""
if flag_plot:
    electrospray_classification.plot_sjaak_cone_jet()
    electrospray_classification.plot_sjaak_classification()

full_dict = {}
full_dict['config'] = {}

if save_config:
    electrospray_config_liquid = electrospray_config_liquid_setup_obj.get_json_liquid()
    electrospray_config_setup = electrospray_config_liquid_setup_obj.get_json_setup()

    full_dict['config']['liquid'] = electrospray_config_liquid
    full_dict['config']['liquid']['actual measurement'] = aux_obj
    full_dict['config']['setup'] = electrospray_config_setup

if save_processing:
    full_dict['processing'] = a_electrospray_processing

if save_data:
    full_dict['measurements'] = a_electrospray_measurements

Q = str(Q) + 'm3_s'
voltage = str(voltage) + 'V'

save_path = """E:/2022json/"""
file_name = name_setup + name_liquid + current_shape + voltage + Q + ".json"
completeName = os.path.join(save_path, file_name)

with open(completeName, 'w') as file:
    json.dump((full_dict), file, indent=4)
# electrospray_load_plot.plot_validation(number_measurements, sampling_frequency)


electrospray_validation.open_load_json_data(filename=completeName)
logging.info('Finished')
sys.exit(0)
