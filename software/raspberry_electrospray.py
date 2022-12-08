from __future__ import print_function

import codecs
import time
import threading
import sys
import libtiepie

import classification_electrospray
from printinfo import *
from scipy.signal import butter, lfilter
from scipy import signal
from time import gmtime, strftime
import csv
import configparser

from electrospray import ElectrosprayDataProcessing, ElectrosprayConfig, ElectrosprayMeasurements
from classification_electrospray import ElectrosprayClassification
# from aux_functions_electrospray import *
from FUG_functions import *
import configuration_tiepie
import configuration_influxDB

import os
import re
import numpy as np
import json
import logging
import threading
import numpy as np


event = threading.Event()


from threading import Thread
# fig = pylab.gcf()

# LOGGING CONFIG
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



# *************************************
#       INITIAL CONFIGURATION 
# *************************************

#  VAR_BIN_CONFIG = input("Would you like to save data? [True/False] ")
VAR_BIN_CONFIG = False
SAVE_DB = True
SAVE_DATA = VAR_BIN_CONFIG
SAVE_PROCESSING = VAR_BIN_CONFIG
SAVE_CONFIG = VAR_BIN_CONFIG
SAVE_JSON = VAR_BIN_CONFIG
append_array_data = VAR_BIN_CONFIG
append_array_processing = VAR_BIN_CONFIG



# **************************************
#    LIQUID AND SETUP INITIAL CONFIG
# **************************************

MODERAMP = True  # else go in steps
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

fug_com_port = 0
name_setup = "setup9"
setup = "/home/lab/EHDA_library/setup/" + name_setup 
name_liquid = "ethyleneglycolHNO3"  # liquids = ["ethyleneglycolHNO3", "ethanol", water60alcohol40, 2propanol]
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
count_sequence_cone_jet = 0
listdir = os.listdir()
j = 0


# **************************************
#          CREATING INSTANCES
# **************************************
electrospray_config_liquid_setup_obj = ElectrosprayConfig(setup + ".json", liquid + ".json")
electrospray_config_liquid_setup_obj.load_json_config_liquid()
electrospray_config_liquid_setup_obj.load_json_config_setup()
electrospray_classification = classification_electrospray.ElectrosprayClassification(name_liquid)
electrospray_processing = ElectrosprayDataProcessing(sampling_frequency)



# **************************************
#                MAIN
# **************************************

# if __name__ == "__main__":


# FUG - POWER SUPPLY
try:
    obj_fug_com = FUG_initialize(fug_com_port) # parameter: COM port idx
except Exception as e:
            print('Could not initialize FUG')
            print('Exception: ' + e.message)
            sys.exit(1)

print('FUG initialized!')
print("FUG Opened port:")
print(obj_fug_com)  # port COM 2 - if does not work, verify with file serial_com.py


# OSCILLOSCOPE
print_library_info()
time_step = 1 / sampling_frequency
libtiepie.network.auto_detect_enabled = True # Enable network search
libtiepie.device_list.update() # Search for devices
scp = None 
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE): # Try to open an oscilloscope with block measurement support
        scp = item.open_oscilloscope()
    else:
        print('No oscilloscope available with block measurement support!')
        sys.exit(1)
print('Oscilloscope initialized!')



with obj_fug_com:


    # ROUTINE
    txt_mode = "step"
    slope = 350
    voltage_start = 3000
    voltage_stop = 11000
    step_size = 300
    step_time = 4  # 10

    step_sequence_thread = threading.Thread(target=step_sequence, name='step sequence FUG',
                                            args=(
                                                obj_fug_com, step_size, step_time, slope, voltage_start,
                                                voltage_stop))

    if MODERAMP:
        txt_mode = "ramp"
        slope = 200
        voltage_start = 3000
        voltage_stop = 11000
        step_size=0
        step_time=0

        # ramp_sequence(obj_fug_com, ramp_slope=slope, voltage_start=voltage_start, voltage_stop=voltage_stop)
        ramp_sequence_thread = threading.Thread(target=ramp_sequence, name='ramp sequence FUG',
                                                args=(
                                                    obj_fug_com, slope, voltage_start,
                                                    voltage_stop))
        ramp_sequence_thread.start()


    else:
        # step_sequence(obj_fug_com,  step_size=300, step_time=5, step_slope=300, voltage_start=3000, voltage_stop=6000)
        step_sequence_thread.start()
        txt_mode = "step"

    try:
        scp = configuration_tiepie.config_TiePieScope(scp, sampling_frequency)
        # Print oscilloscope info:
        print_device_info(scp)
        # Start measurement:
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

        print(get_voltage_from_PS(obj_fug_com))

        for j in range(number_measurements):
            # reset the background back in the canvas state, screen unchange

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

            electrospray_processing.calculate_statistics(electrospray_data.data)
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


    # wait until threads finish
    if MODERAMP:
        ramp_sequence_thread.join()
        print(FUG_sendcommands(obj_fug_com, ['U 0']))
    else:
        step_sequence_thread.join()
        print(FUG_sendcommands(obj_fug_com, ['U 0']))


typeofmeasurement = {
    "sequence": str(txt_mode),
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
        # put here the code to save json file somewhere

    if SAVE_DB:   
        # Send data to database
        configuration_influxDB.send_to_influxdb(
            id='01',
            mean=electrospray_processing.mean_value,
            sdt=electrospray_processing.stddev,
            voltage_PS=voltage_from_PS,
            timestamp=datetime.datetime.utcnow(),
            classification=classification_sjaak,
            temperature=temperature,
            humidity=humidity
        )


logging.info('Finished')
sys.exit(0)
