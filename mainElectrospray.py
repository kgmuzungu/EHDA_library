from __future__ import print_function

import codecs
import time
import threading
import sys
import libtiepie

import classification_electrospray
from printinfo import *
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from scipy import signal
from time import gmtime, strftime
import csv
import configparser

from electrospray import ElectrosprayDataProcessing, ElectrosprayConfig, ElectrosprayMeasurements
from validation_electrospray import ElectrosprayValidation
from classification_electrospray import ElectrosprayClassification
# from aux_functions_electrospray import *
from configuration_FUG import *
import configuration_tiepie
import cameraTrigger

from simple_pid import PID
import os
import re
import numpy as np
import json
import logging
import pylab
import numpy as np


event = threading.Event() # this is somehow important to fug

from threading import Thread
# fig = pylab.gcf()
save_path = """C:/Users/hvvhl/Desktop/teste"""

# LOGGING CONFIG
LOG_FILENAME = r'logging_test.out'
logging.basicConfig(filename=LOG_FILENAME, encoding='utf-8', format='%(asctime)s %(message)s', level=logging.INFO)
logging.info('Started')

multiplier_for_nA = 500
sampling_frequency = 1e5  # 100000

a_electrospray_measurements = []
a_electrospray_measurements_data = []
a_electrospray_processing = []
a_statistics = []
append_array_measurements = []

d_electrospray_measurements = {}
d_electrospray_measurements_data = {}
d_electrospray_processing = {}
d_statistics = {}



# *************************************
#       INITIAL CONFIGURATION 
# *************************************

#  VAR_BIN_CONFIG = input("Would you like to save data? [True/False] ")
VAR_BIN_CONFIG = True
SAVE_DATA = VAR_BIN_CONFIG
SAVE_PROCESSING = VAR_BIN_CONFIG
SAVE_CONFIG = VAR_BIN_CONFIG
SAVE_JSON = VAR_BIN_CONFIG
append_array_data = VAR_BIN_CONFIG
append_array_processing = VAR_BIN_CONFIG



# **************************************
#    LIQUID AND SETUP INITIAL CONFIG
# **************************************

MODERAMP = False  # else go in steps
number_measurements = 45 # maybe change to 100 (45 looks to be a good size for saving)
print('number_measurements: ', number_measurements)

Q = 1450 # flow rate  uL/h 
Q = Q * 10e-6  # liter/h   # Q = 0.0110  # ml/h flow rate
Q = Q * 2.7778e-7  # m3/s  # Q = Q * 2.7778e-3  # cm3/s
print('flowrate cm3/s: ', Q)

impedance, temperature, humidity = 2000000, 27.8, 49
print('impedance: ', impedance)
print('temperature: ', temperature)
print('humidity: ', humidity)

name_setup = "setup10"
setup = "C:/Users/hvvhl/Desktop/joao/EHDA_library/setup/nozzle" + name_setup
name_liquid = "water60alcohol40"  # liquids = ["ethyleneglycolHNO3", "ethanol", water60alcohol40, 2propanol]
liquid = "liquid/" + name_liquid  
current_shapes = ["no voltage no fr", "no voltage", "dripping", "intermittent", "cone jet", "multijet",
                  "streamer onset", "dry", "all shapes"]  # 0no voltage no fr/1no voltage/2dripping/3intermittent/4cone jet/5multijet/6streamer onset/7dry/8all shapes"]
current_shape = current_shapes[8]  
current_shape_comment = "difficult cone jet stabilization"

voltage = 0
voltage_array = []
current = 0
current_array = []
"""voltage = 9.2  
voltage = voltage * 1000  # V"""

# k_electrical_conductivity = 0.34 * 10e-4 # uS/cm

# **************************************
#            AUX VARIABLES
# **************************************
first_measurement = True
FLAG_PLOT = False
classification_sjaak = ""
day_measurement = strftime("%a_%d %b %Y", gmtime())
res = ""
count_sequency_cone_jet = 0
listdir = os.listdir()
j = 0
plt.style.use('seaborn-colorblind')
plt.ion()

# **************************************
#                 THREADS
# **************************************
#PORTS
arduino_COM_port = 0
fug_COM_port = 4





# **************************************
#          CREATING INSTANCES
# **************************************
electrospray_config_liquid_setup_obj = ElectrosprayConfig(setup + ".json", liquid + ".json")
electrospray_config_liquid_setup_obj.load_json_config_liquid()
electrospray_config_liquid_setup_obj.load_json_config_setup()
electrospray_validation = ElectrosprayValidation(name_liquid)
electrospray_classification = classification_electrospray.ElectrosprayClassification(name_liquid)
electrospray_processing = ElectrosprayDataProcessing(sampling_frequency)



# **************************************
#                MAIN
# **************************************

# if __name__ == "__main__":


# FUG - POWER SUPPLY
try:
    obj_fug_com = FUG_initialize(fug_COM_port) # parameter: COM port idx
except Exception as e:
            print('Could not initialize FUG')
            print('Exception: ' + e.message)
            sys.exit(1)


# OSCILLOSCOPE
# print_library_info()
time_step = 1 / sampling_frequency
libtiepie.network.auto_detect_enabled = True # Enable network search
libtiepie.device_list.update() # Search for devices
scp = None 
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):  # Try to open an oscilloscope with block measurement support
        scp = item.open_oscilloscope()
    else:
        print('No oscilloscope available with block measurement support!')
        sys.exit(1)
print('Oscilloscope initialized!')



with obj_fug_com:

    fig, ax = plt.subplots(3)

    threads = list()


    if MODERAMP:
        txt_mode = "ramp"
        slope = 200
        voltage_start = 3000
        voltage_stop = 11000
        step_size=0
        step_time=0

        # ramp_sequency(obj_fug_com, ramp_slope=slope, voltage_start=voltage_start, voltage_stop=voltage_stop)
        ramp_sequency_thread = threading.Thread(target=ramp_sequency, name='ramp sequency FUG',
                                                args=(
                                                    obj_fug_com, slope, voltage_start,
                                                    voltage_stop))
        ramp_sequency_thread.start()


    else: # MODESTEP
        txt_mode = "step"
        slope = 10000
        voltage_start = 3000
        voltage_stop = 10000
        step_size = 100
        step_time = 10  # 10

        # step_sequency(obj_fug_com,  step_size=300, step_time=5, step_slope=300, voltage_start=3000, voltage_stop=6000)
        step_sequency_thread = threading.Thread(target=step_sequency, name='step sequency FUG',
                                        args=(obj_fug_com, step_size, step_time, slope, voltage_start,
                                            voltage_stop))
        step_sequency_thread.start()


    # Video Thread
    makeVideo_thread = threading.Thread(target=cameraTrigger.activateTrigger, name='video', args=(arduino_COM_port,))
    threads.append(makeVideo_thread)
    makeVideo_thread.start()

    try:
        scp = configuration_tiepie.config_TiePieScope(scp, sampling_frequency)
        # print_device_info(scp)
        scp.start()

        # Wait for measurement to complete:
        while not scp.is_data_ready:
            time.sleep(0.05)  # 50 ms delay, to save CPU time

        # Get 1st data:
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
        # ax[0].text(.5, .5, 'blabla', animated=True)

        # animated=True tells matplotlib to only draw the artist when we explicitly request it
        (ln0,) = ax[0].plot(np.arange(0, len(datapoints) * time_step, time_step), datapoints, animated=True)

        (ln1,) = ax[1].plot(np.arange(0, len(datapoints_filtered) * time_step, time_step), datapoints_filtered,
                            animated=True)
        freq = np.fft.fftfreq(len(datapoints_filtered), d=time_step)

        (ln2,) = ax[2].plot(freq[0:500], np.zeros(500), animated=True)

        ax[0].set(xlabel='time [s]', ylabel='current (nA)', title='osci reading', ylim=[-3e2, 3e2])
        ax[1].set(xlabel='time', ylabel='nA', title='LP filtered', ylim=[-1e1, 5e2])
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

        fig.canvas.blit(fig.bbox)

        get_voltage_from_PS(obj_fug_com)

        for j in range(number_measurements):

            # reset the background back in the canvas state, screen unchange
            fig.canvas.restore_region(bg)

            voltage_from_PS = get_voltage_from_PS(obj_fug_com)
            current_from_PS = get_current_from_PS(obj_fug_com)
            current_array.append(current_from_PS)
            voltage_array.append(voltage_from_PS)
            print("Actual voltage: " + str(voltage_from_PS) + " for the measurement " + str(
                j) + " actual current: " + str(current_from_PS))

            electrospray_data = ElectrosprayMeasurements(liquid, datapoints, voltage_from_PS, Q, temperature,
                                                            humidity, day_measurement, current_shape, current_from_PS)

            electrospray_processing.calculate_filter(a, b, electrospray_data.data)
            electrospray_processing.calculate_fft_raw(electrospray_data.data)

            electrospray_processing.calculate_statistics(electrospray_data.data,
                                                            electrospray_processing.datapoints_filtered)
            electrospray_processing_freq, electrospray_processing_psd = electrospray_processing.calculate_power_spectral_density(
                electrospray_data.data)


            max_data, quantity_max_data, percentage_max = electrospray_processing.calculate_peaks_signal(
                electrospray_data.data)

            max_fft_peaks, cont_max_fft_peaks = electrospray_processing.calculate_peaks_fft(electrospray_data.data)

            classification_sjaak = electrospray_classification.do_sjaak(electrospray_processing.mean_value,
                                                                electrospray_processing.med,
                                                                electrospray_processing.stddev,
                                                                electrospray_processing.psd_welch,
                                                                electrospray_processing.variance)

            classification_monica = electrospray_classification.do_monica(float(max_data), float(quantity_max_data),
                                                                            float(percentage_max), float(Q), max_fft_peaks,
                                                                            cont_max_fft_peaks)
            txt_sjaak_str = str(classification_sjaak)
            txt_monica_str = str(classification_monica)

            current_shape = {
                "Sjaak":  str(classification_sjaak),
                "Monica": str(classification_monica),
            }
            electrospray_data.set_shape(current_shape)

            txt_max_peaks = " Max: " + str(max_data) + " Quantity max: " + str(
                quantity_max_data) + " Percentage: " + str(percentage_max)

            electrospray_processing.calculate_fft_filtered()
            electrospray_processing.calculate_fft_peaks()

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

            fig.canvas.manager.set_window_title('Sjaak: ' + txt_sjaak_str + 'monnica' + txt_monica_str + '; Peaks:' + txt_max_peaks +
                                                " voltage_PS= " + str(voltage_from_PS) + " current_PS= " + str(
                current_from_PS * 1e6) + " current mean osci= " + str(electrospray_processing.mean_value))


            """df = pd.DataFrame({str(j): ['Sjaak: ' + txt_sjaak_str + ' ; Peaks:' + txt_max_peaks +
                                                " voltage_PS= " + str(voltage_from_PS) + " current_PS= " + str(
                current_from_PS * 1e6) + " current mean osci= " + str(electrospray_processing.mean_value) ] } ) """


            # copy the image to the GUI state, but screen might not be changed yet
            fig.canvas.blit(fig.bbox)
            # flush any pending GUI events, re-painting the screen if needed
            fig.canvas.flush_events()

            if current_shape["Sjaak"] == "cone jet" and FLAG_PLOT:
                electrospray_validation.set_data_from_dict_liquid(
                    electrospray_config_liquid_setup_obj.get_json_liquid())
                electrospray_validation.calculate_scaling_laws_cone_jet(electrospray_data.data,
                                                                        electrospray_processing.mean_value, Q)
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
            # Get more data:
            data = scp.get_data()
            first_measurement = False
            datapoints = np.array(data[0]) * multiplier_for_nA
            time_end = time.time() - time_start

    except Exception as e:
        print('Exception: ' + e.message)
        sys.exit(1)
        # Close oscilloscope:
        del scp


    # printscreen_thread.join()
    # wait until threads finish
    if MODERAMP:
        ramp_sequency_thread.join()
        makeVideo_thread.join()
        print(FUG_sendcommands(obj_fug_com, ['U 0']))
    else:
        step_sequency_thread.join()
        makeVideo_thread.join()
        print(FUG_sendcommands(obj_fug_com, ['U 0']))


typeofmeasurement = {
    "sequency": str(txt_mode),
    "start": str(voltage_start),
    "stop": str(voltage_stop),
    "slope": str(slope),
    "size": str(step_size),
    "step time": str(step_time)
}
#electrospray_config_liquid_setup_obj.set_comment_current(current_shape_comment)

electrospray_config_liquid_setup_obj.set_type_of_measurement(typeofmeasurement)
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
    full_dict['config']['liquid']['flow rate min'] = electrospray_config_liquid_setup_obj.get_flow_rate_min_ian()

    full_dict['config']['setup'] = electrospray_config_setup
    full_dict['config']['setup']['voltage regime'] = typeofmeasurement
    full_dict['config']['setup']['comments'] = current_shape_comment

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
        voltage_filename = str(voltage_array) + 'V'
        file_name = txt_mode + name_setup + name_liquid + "_all shapes_" + Q + ".json"
        completeName = os.path.join(save_path, file_name)

        with open(completeName, 'w') as file:
            json.dump((full_dict), file, indent=4)
        # electrospray_load_plot.plot_validation(number_measurements, sampling_frequency)
        electrospray_validation.open_load_json_data(filename=completeName)

logging.info('Finished')
sys.exit(0)
