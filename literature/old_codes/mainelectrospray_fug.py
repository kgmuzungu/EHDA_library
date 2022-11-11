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
from validation_electrospray import ElectrosprayValidation
from classification_electrospray import ElectrosprayClassification
from old_codes.aux_functions_electrospray import *
from configuration_FUG import *
import configuration_tiepie
import os
import re
import numpy as np
import json
import logging
import pylab
import threading
from threading import Thread

event = threading.Event()

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
# ************************ INITIAL CONFIGURATION ************************
#  VAR_BIN_CONFIG = input("Would you like to save data? [True/False] ")
VAR_BIN_CONFIG = True
SAVE_DATA = VAR_BIN_CONFIG
SAVE_PROCESSING = VAR_BIN_CONFIG
SAVE_CONFIG = VAR_BIN_CONFIG
SAVE_JSON = VAR_BIN_CONFIG
append_array_data = VAR_BIN_CONFIG
append_array_processing = VAR_BIN_CONFIG
flag_record_transition = False
flag_last_measurement = False
flag_voltage_low = True
flag_increase_voltage = False
# ************************ INITIAL CONFIGURATION OF LIQUID AND SETUP ************************
impedance, temperature, humidity = 2000000, 21, 31
Q = 5  # flow rate  uL/h **********************************************************************
Q = Q * 10e-6  # liter/h                                         # Q = 0.0110  # ml/h flow rate
Q = Q * 2.7778e-7  # m3/s                                        # Q = Q * 2.7778e-3  # cm3/s
# **********************************************************************
name_setup = "setup7"
setup = "C:/Users/hvvhl/Desktop/joao/EHDA_library/setup/" + name_setup
name_liquid = "ethyleneglycol"  # liquids = ["ethyleneglycolHNO3", "ethanol", water60alcohol40]
liquid = "liquid/" + name_liquid  # **********************************************************************
# ******************************************
current_shapes = ["no voltage no fr", "no voltage", "dripping", "intermittent", "cone jet", "multijet",
                  "streamer onset", "dry",
                  "all shapes"]  # 0no voltage no fr/1no voltage/2dripping/3intermittent/4cone jet/5multijet/6streamer onset/7dry/8all shapes"]
current_shape = current_shapes[8]  # **********************************************************************
current_shape_comment = ""
# *********************
voltage = 0
main_voltage = 3000
voltage_array = []
current = 0
current_array = []
"""voltage = 9.2  # **********************************************************************
voltage = voltage * 1000  # V"""
# *********************
k_electrical_conductivity = 0.34  # uS/cm **********************************************************************
k_electrical_conductivity = k_electrical_conductivity * 10e-4  # S/m
# ***********************************************
number_measurements = 200
flag_sjaak = ""
FLAG_PLOT = False
day_measurement = strftime("%a_%d %b %Y", gmtime())
res = ""
listdir = os.listdir()
j = 0
plt.style.use('seaborn-colorblind')
plt.ion()

electrospray_config_liquid_setup_obj = ElectrosprayConfig(setup + ".json", liquid + ".json")
electrospray_config_liquid_setup_obj.load_json_config_liquid()
electrospray_config_liquid_setup_obj.load_json_config_setup()

electrospray_validation = ElectrosprayValidation(name_liquid)
electrospray_classification = ElectrosprayClassification(name_liquid)
electrospray_processing = ElectrosprayDataProcessing(sampling_frequency)


# returns float
def get_voltage_from_PS():
    voltage_reading = str.rstrip(str(FUG_sendcommands(obj_fug_com, ['>M0?'])[0]))
    numbers = (re.findall('[+,-][0-9].+E[+,-][0-9].', voltage_reading))
    return float(numbers[0])


# returns float
def get_current_from_PS():
    current_reading = str.rstrip(str(FUG_sendcommands(obj_fug_com, ['>M1?'])[0]))
    numbers = (re.findall('[+,-][0-9].+E[+,-][0-9].', current_reading))
    return float(numbers[0])


# obj_fug_com ... fug serial object
# step_size=300 ... in volt
# step_time=1 step time in seconds : sleep time in seconds
# step_slope=0 step slope in voltage per second
# voltage_start=0  ... in volt
# voltage_stop=100 ... in volt
def step_sequency(obj_fug_com, step_size=300, step_time=1, step_slope=0, voltage_start=0, voltage_stop=100):
    responses = FUG_sendcommands(obj_fug_com, ['F0', '>S1B 0', 'I 600e-6', '>S0B 2', '>S0R ' + str(step_slope),
                                               'U ' + str(voltage_start), 'F1'])
    voltage = voltage_start
    while voltage < voltage_stop:
        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
        time.sleep(step_time+5)
        voltage += step_size
    return responses


def ramp_sequency(obj_fug_com, ramp_slope=250, voltage_start=0, voltage_stop=100):
    responses = FUG_sendcommands(obj_fug_com, ['F0', '>S1B 0', 'I 600e-6', '>S0B 0', 'U ' + str(voltage_start), 'F1'])
    responses.append(FUG_sendcommands(obj_fug_com, ['>S0B 2', '>S0R ' + str(ramp_slope), 'U ' + str(voltage_stop)]))
    return responses


# if __name__ == "__main__":
# with configuration_FUG('COM8', 9600, timeout=0) as ser, open("voltages.txt", 'w') as text_file:

obj_fug_com = FUG_initialize(2)
with obj_fug_com:
    print("Opened port!")
    # print(configuration_FUG.FUG_sendcommands(obj_fug_com, ['F0']))
    print(obj_fug_com)  # port COM 2 - if does not work, verify with file serial_com.py

    MODERAMP = False  # else go in steps
    print(" ********** Responses: ")
    if MODERAMP:
        ramp_sequency(obj_fug_com, ramp_slope=150, voltage_start=3000, voltage_stop=6000)
    else:
        step_sequency(obj_fug_com,  step_size=300, step_time=5, step_slope=300, voltage_start=3000, voltage_stop=6000)


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
            # print(configuration_FUG.FUG_sendcommands(obj_fug_com, ['U 8000']))

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
            print(get_voltage_from_PS())

            for j in range(number_measurements):
                # reset the background back in the canvas state, screen unchange
                fig.canvas.restore_region(bg)
                voltage_from_PS = get_voltage_from_PS()
                current_from_PS = get_current_from_PS()
                current_array.append(current)
                voltage_array.append(voltage)
                print("Actual voltage: " + str(voltage_from_PS) + " for the measurement " + str(
                    j) + " actual current: " + str(current_from_PS))
                electrospray_data = ElectrosprayMeasurements(liquid, datapoints, voltage, Q, temperature,
                                                             humidity, day_measurement, current_shape, current)

                electrospray_processing.calculate_filter(a, b, electrospray_data.data)
                electrospray_processing.calculate_fft_raw(electrospray_data.data)
                electrospray_processing.calculate_statistics(electrospray_data.data,
                                                             electrospray_processing.datapoints_filtered)
                electrospray_processing.calculate_fft_filtered()
                electrospray_processing_freq, electrospray_processing_psd = electrospray_processing.calculate_power_spectral_density(
                    electrospray_data.data)
                electrospray_processing.calculate_fft_peaks()
                max_data, quantity_max_data, percentage_max = electrospray_processing.calculate_peaks(
                    electrospray_data.data)
                txt_max_peaks = " Max: " + str(max_data) + " Quantity max: " + str(
                    quantity_max_data) + " Percentage: " + str(percentage_max)

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
                fig.canvas.manager.set_window_title('Sjaak: ' + txt_sjaak_str + ' ; Peaks:' + txt_max_peaks +
                                                    " voltage_PS= " + str(voltage_from_PS) + " current_PS= " + str(
                    current_from_PS * 1e6) + " current mean osci= " + str(electrospray_processing.mean_value))
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
                current_shape = flag_sjaak

                if current_shape == "cone jet" and FLAG_PLOT:
                    electrospray_validation.set_data_from_dict_liquid(
                        electrospray_config_liquid_setup_obj.get_json_liquid())
                    electrospray_validation.calculate_scaling_laws_cone_jet(electrospray_data.data,
                                                                            electrospray_processing.mean_value, Q)
                # electrospray_classification.do_monica(electrospray_data.data, electrospray_processing.mean_value)

                if append_array_data:
                    d_electrospray_measurements = electrospray_data.get_measurements_dictionary()
                    a_electrospray_measurements.append(d_electrospray_measurements)

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
    print(configuration_FUG.FUG_sendcommands(obj_fug_com, ['U0']))
    print("**********************")
    print(configuration_FUG.FUG_sendcommands(obj_fug_com, ['F0']))
    print("Command F0 sent to FUG!")
"""

electrospray_config_liquid_setup_obj.set_flow_rate(Q)
electrospray_config_liquid_setup_obj.set_voltage(voltage_array)
electrospray_config_liquid_setup_obj.set_electrical_conductivity(k_electrical_conductivity)
electrospray_config_liquid_setup_obj.set_shape_manual(current_shape)
electrospray_config_liquid_setup_obj.set_comment_current(current_shape_comment)
electrospray_config_liquid_setup_obj.flow_rate_min_est_chen_pui()
electrospray_config_liquid_setup_obj.set_type_of_measurement()

aux_obj = electrospray_config_liquid_setup_obj.get_dict_config()

if FLAG_PLOT:
    electrospray_classification.plot_sjaak_cone_jet()
    electrospray_classification.plot_sjaak_classification()

full_dict = {}
full_dict['config'] = {}

if SAVE_CONFIG:
    electrospray_config_liquid = electrospray_config_liquid_setup_obj.get_json_liquid()
    electrospray_config_setup = electrospray_config_liquid_setup_obj.get_json_setup()
    full_dict['config']['liquid'] = electrospray_config_liquid
    full_dict['config']['liquid']['actual measurement'] = aux_obj
    full_dict['config']['setup'] = electrospray_config_setup
    """                                                                                                                                                                                                                                                                                                     
        load_setup("ethanol.json", repr(electrospray_config_liquid_setup_obj))
        shape = input("Enter manual classification for the recorded shape : ")
        a_statistics.append("manual_shape: " + shape + ", voltage:"+str(voltage))
    """
if SAVE_PROCESSING:
    full_dict['processing'] = a_electrospray_processing

if SAVE_DATA:
    full_dict['measurements'] = a_electrospray_measurements

# voltage = str(voltage) + 'V'
if SAVE_JSON:
    # arbitrary, defined in the header
    Q = str(Q) + 'm3_s'
    save_path = """E:/2022json/"""
    voltage_filename = str(voltage_array) + 'V'
    file_name = name_setup + name_liquid + current_shape + voltage_filename + Q + ".json"
    completeName = os.path.join(save_path, file_name)

    with open(completeName, 'w') as file:
        json.dump((full_dict), file, indent=4)
    # electrospray_load_plot.plot_validation(number_measurements, sampling_frequency)
    electrospray_validation.open_load_json_data(filename=completeName)

logging.info('Finished')
sys.exit(0)
