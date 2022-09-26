from __future__ import print_function

import codecs
import time
import threading
import sys
import libtiepie
from printinfo import *
from scipy.signal import butter, lfilter
# from scipy import signal
from time import gmtime, strftime
# import csv
# import configparser
from electrospray import ElectrosprayDataProcessing
from electrospray import ElectrosprayConfig
from electrospray import ElectrosprayMeasurements
from validationelectrospray import ElectrosprayValidation
from classification_electrospray import ElectrosprayClassification
from aux_functions_electrospray import *
from serial_FUG.serial_sync import *
from influx_db.sync_db import *
from influx_db.syncdb_allsignal import *
import configuration_tiepie
import os
import re
import numpy as np
import json
import logging
import threading
import datetime
from datetime import timedelta

from threading import Thread
# fig = pylab.gcf()
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
# ************************ INITIAL CONFIGURATION **********************************************
#  VAR_BIN_CONFIG = input("Would you like to save data? [True/False] ")
VAR_BIN_CONFIG = False
SAVE_DATA = VAR_BIN_CONFIG
SAVE_PROCESSING = VAR_BIN_CONFIG
SAVE_CONFIG = VAR_BIN_CONFIG
SAVE_JSON = VAR_BIN_CONFIG
append_array_data = VAR_BIN_CONFIG
append_array_processing = VAR_BIN_CONFIG
# ************************ INITIAL CONFIGURATION OF LIQUID AND SETUP **************************
# """
MODERAMP = False  # else go in steps
number_measurements = 25
"""
MODERAMP = True  # else go in steps
number_measurements = 25
"""
Q = 350   # flow rate  uL/h **********************************************************************
Q = Q * 10e-6  # liter/h                                         # Q = 0.0110  # ml/h flow rate
Q = Q * 2.7778e-7  # m3/s                                        # Q = Q * 2.7778e-3  # cm3/s

impedance, temperature, humidity = 2000000, 21, 31
# *********************************************************************************************
name_setup = "setup7"
setup = "/home/pi/testpyinflux/python-files/electrospraylib/setup/" + name_setup
name_liquid = "water60alcohol40"  # liquids = ["ethyleneglycolHNO3", "ethanol", water60alcohol40]
liquid = "liquid/" + name_liquid  # ***********************************************************
# *********************************************************************************************
current_shapes = ["no voltage no fr", "no voltage", "dripping", "intermittent", "cone jet", "multijet",
                  "streamer onset", "dry", "all shapes"]  # 0no voltage no fr/1no voltage/2dripping/3intermittent/4cone jet/5multijet/6streamer onset/7dry/8all shapes"]
current_shape = current_shapes[8]  # **********************************************************
current_shape_comment = ""
# *********************************************************************************************
voltage = 0
voltage_array = []
current = 0
current_array = []
"""voltage = 9.2  # **********************************************************************
voltage = voltage * 1000  # V"""
# *********************
# k_electrical_conductivity = 0.34 * 10e-4 # uS/cm ******************************************************
# ***********************************************
""" AUX VARIABLES"""
first_measurement = True
FLAG_PLOT = False
classification_sjaak = ""
day_measurement = strftime("%a_%d %b %Y", gmtime())
res = ""
count_sequency_cone_jet = 0
listdir = os.listdir()
j = 0
"""plt.style.use('seaborn-colorblind')
plt.ion()"""
# ***********************************************
electrospray_config_liquid_setup_obj = ElectrosprayConfig(setup + ".json", liquid + ".json")
electrospray_config_liquid_setup_obj.load_json_config_liquid()
electrospray_config_liquid_setup_obj.load_json_config_setup()

electrospray_validation = ElectrosprayValidation(name_liquid)
electrospray_classification = ElectrosprayClassification(name_liquid)
electrospray_processing = ElectrosprayDataProcessing(sampling_frequency)


# returns float
def get_voltage_from_PS():
    try:
        voltage_reading = str.rstrip(str(FUG_sendcommands(obj_fug_com, ['>M0?'])[0]))
        numbers = (re.findall('[+,-][0-9].+E[+,-][0-9].', voltage_reading))
        print(numbers[0])
    except:
        numbers = ["0"]
    return float(numbers[0])


# returns float
def get_current_from_PS():
    try:
        current_reading = str.rstrip(str(FUG_sendcommands(obj_fug_com, ['>M1?'])[0]))
        numbers = (re.findall('[+,-][0-9].+E[+,-][0-9].', current_reading))
        print(numbers[0])
    except:
        numbers = ["0"]
    return float(numbers[0])


# obj_fug_com ... fug serial object
# step_size=300 ... in volt
# step_time=1 step time in seconds : sleep time in seconds
# step_slope=0 step slope in voltage per second
# voltage_start=0  ... in volt
# voltage_stop=100 ... in volt

def step_sequency(obj_fug_com, step_size=300, step_time=1, step_slope=0, voltage_start=0, voltage_stop=100):
    """responses = FUG_sendcommands(obj_fug_com, ['F0', '>S1B 0', 'I 600e-6', '>S0B 2', '>S0R ' + str(step_slope),
                                               'U ' + str(voltage_start), 'F1'])"""
    responses = FUG_sendcommands(obj_fug_com, ['>S1B 0', 'I 600e-6', '>S0B 2', '>S0R ' + str(step_slope),
                                               'U ' + str(voltage_start), 'F1'])

    if (get_voltage_from_PS() < voltage_start or get_voltage_from_PS() > voltage_start):
        time.sleep(step_time)

    voltage = voltage_start
    while voltage < voltage_stop:
        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
        time.sleep(step_time)
        voltage += step_size

    responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage_stop)]))
    responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(0)]))

    print("Responses from step frequency : ", str(responses) + " *********************** ")


def ramp_sequency(obj_fug_com, ramp_slope=250, voltage_start=0, voltage_stop=100):
    responses = FUG_sendcommands(obj_fug_com, ['F0', '>S1B 0', 'I 600e-6', '>S0B 0', 'U ' + str(voltage_start), 'F1'])

    responses.append(FUG_sendcommands(obj_fug_com, ['>S0B 2', '>S0R ' + str(ramp_slope), 'U ' + str(voltage_stop)]))

    # FUG_sendcommands(obj_fug_com, ['U ' + str(voltage_stop)])

    return responses

"""
     **************************************************** MAIN *********************************************
"""

# if __name__ == "__main__":
# with serial_sync('COM8', 9600, timeout=0) as ser, open("voltages.txt", 'w') as text_file:
obj_fug_com = FUG_initialize(0)
with obj_fug_com:
    # Print info about serial open port:
    print("Opened port!")
    # print(serial_sync.FUG_sendcommands(obj_fug_com, ['F0']))
    print(obj_fug_com)  # port COM 2 - if does not work, verify with file serial_com.py

    # Print oscilloscope library info:
    print_library_info()
    time_step = 1 / sampling_frequency
    # Enable network search:
    libtiepie.network.auto_detect_enabled = True
    # Search for devices:
    libtiepie.device_list.update()
    # Try to open an oscilloscope with block measurement support:
    scp = None
    for item in libtiepie.device_list:
        if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):
            scp = item.open_oscilloscope()
    if scp:
        txt_mode = "step"
        slope = 150
        voltage_start = 3000
        voltage_stop =  9000
        step_size = 300
        step_time = 5 # 10

        step_sequency_thread = threading.Thread(target=step_sequency, name='step sequency FUG',
                                                args=(
                                                obj_fug_com, step_size, step_time, slope, voltage_start, voltage_stop))
        if MODERAMP:
            txt_mode = "ramp"
            slope = 200
            voltage_start = 3000
            voltage_stop = 9000
            step_size = 0
            step_time = 0

            # ramp_sequency(obj_fug_com, ramp_slope=slope, voltage_start=voltage_start, voltage_stop=voltage_stop)
            ramp_sequency_thread = threading.Thread(target=ramp_sequency, name='ramp sequency FUG',
                                                    args=(
                                                        obj_fug_com, slope, voltage_start,
                                                        voltage_stop))
            ramp_sequency_thread.start()

        else:
            # step_sequency(obj_fug_com,  step_size=300, step_time=5, step_slope=300, voltage_start=3000, voltage_stop=6000)
            step_sequency_thread.start()
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
            print(get_voltage_from_PS())

            for j in range(number_measurements):
                voltage_from_PS = get_voltage_from_PS()
                current_from_PS = get_current_from_PS()
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

                classification_monica = electrospray_classification.do_monica(max_data, quantity_max_data, percentage_max, Q, max_fft_peaks, cont_max_fft_peaks)

                current_shape = {
                    "Sjaak":  str(classification_sjaak),
                    "Monica": str(classification_monica),
                }
                electrospray_data.set_shape(current_shape)

                time_now = datetime.datetime.utcnow()

                # influxdb_data = connect_send_to_influxdb(j, electrospray_processing.mean_value, electrospray_processing.stddev, voltage_from_PS, time_now, str(classification_sjaak), str([1,2,3,4]), temperature, humidity)

                counter = 0
                for x in electrospray_data.data:
                    time_past = time_now - timedelta(milliseconds = 500 - counter)
                    connect_send_to_influxdb_allsignal(x, electrospray_processing.mean_value,
                                                       electrospray_processing.stddev, voltage_from_PS, time_now,
                                                       str(classification_sjaak), str([1, 2, 3, 4]), temperature,
                                                       humidity)
                    counter = counter + 1


                #append_data_to_excel('/home/pi/testpyinflux/python-files/electrospraylib/influxdb/fileinflux.xlsx', str(j), influxdb_data)

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
    else:
        print('No oscilloscope available with block measurement support!')
        sys.exit(1)

    # wait until threads finish
    if MODERAMP:
        ramp_sequency_thread.join()
        print(FUG_sendcommands(obj_fug_com, ['U 0']))
    else:
        step_sequency_thread.join()
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
        save_path = """/home/pi/testpyinflux/python-files/electrospraylib/jsonfiles/"""
        voltage_filename = str(voltage_array) + 'V'
        file_name = txt_mode + name_setup + name_liquid + "_all shapes_" + Q + ".json"
        completeName = os.path.join(save_path, file_name)

        with open(completeName, 'w') as file:
            json.dump((full_dict), file, indent=4)
        # electrospray_load_plot.plot_validation(number_measurements, sampling_frequency)
        electrospray_validation.open_load_json_data(filename=completeName)

logging.info('Finished')
sys.exit(0)
