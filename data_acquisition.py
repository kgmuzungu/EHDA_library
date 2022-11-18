from simple_pid import PID
import os
import re
import numpy as np
import json
import logging
import pylab
import numpy as np
import libtiepie
from configuration_FUG import *
import configuration_tiepie
from scipy.signal import butter, lfilter
from time import gmtime, strftime
from electrospray import ElectrosprayDataProcessing, ElectrosprayConfig, ElectrosprayMeasurements
from validation_electrospray import ElectrosprayValidation
from classification_electrospray import ElectrosprayClassification

# tiepie params
sampling_frequency = 1e5  # 100 KHz
multiplier_for_nA = 500


name_setup = "setup10"
setup = "C:/Users/hvvhl/Desktop/joao/EHDA_library/setup/nozzle/" + name_setup
# liquids = ["ethyleneglycolHNO3", "ethanol", water60alcohol40, 2propanol]
name_liquid = "water60alcohol40"
liquid = "setup/liquid/" + name_liquid
current_shapes = ["no voltage no fr", "no voltage", "dripping", "intermittent", "cone jet", "multijet",
                  "streamer onset", "dry", "all shapes"]  # 0no voltage no fr/1no voltage/2dripping/3intermittent/4cone jet/5multijet/6streamer onset/7dry/8all shapes"]
current_shape = current_shapes[8]
current_shape_comment = "difficult cone jet stabilization"

a_electrospray_measurements = []
a_electrospray_measurements_data = []
a_electrospray_processing = []

append_array_data = True
append_array_processing = True
FLAG_PLOT = False
SAVE_DATA = True
SAVE_PROCESSING = True
SAVE_CONFIG = True
SAVE_JSON = True


def data_acquisition(queue,
                     fug_queue,
                     event, 
                     electrospray_config_liquid_setup_obj,
                     electrospray_processing,
                     electrospray_classification,
                     electrospray_validation,
                     txt_mode,
                     slope,
                     voltage_start,
                     voltage_stop,
                     step_size,
                     step_time,
                     Q,
                     current_shape,
                     save_path):

    voltage_array = []
    current_array = []
    temperature = 10
    humidity = 10
    day_measurement = strftime("%a_%d %b %Y", gmtime())

    # **************************************
    #           OSCILLOSCOPE
    # **************************************

    # print_library_info()
    time_step = 1 / sampling_frequency
    libtiepie.network.auto_detect_enabled = True  # Enable network search
    libtiepie.device_list.update()  # Search for devices
    scp = None
    for item in libtiepie.device_list:
        # Try to open an oscilloscope with block measurement support
        if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):
            scp = item.open_oscilloscope()
        else:
            print('[DATA_ACQUISITION THREAD] No oscilloscope available with block measurement support!')
            sys.exit(1)
    print('[DATA_ACQUISITION THREAD] Oscilloscope initialized!')

    try:
        scp = configuration_tiepie.config_TiePieScope(scp, sampling_frequency)
        # print_device_info(scp)
    except:
        print("[DATA_ACQUISITION THREAD] Failed to config tie pie!")
        sys.exit(1)

    print("[DATA_ACQUISITION THREAD] No values in the fug_queue yet")
    while fug_queue.empty():
        time.sleep(0.1)

    # **************************************
    #           THREAD LOOP
    # **************************************

    voltage_from_PS = voltage_start
    sample = 0

    while sample < 600:

        try:
            if not fug_queue.empty():
                fug_values = fug_queue.get()
                voltage_from_PS, current_from_PS = fug_values

            current_array.append(current_from_PS)
            voltage_array.append(voltage_from_PS)

            print('[DATA_ACQUISITION THREAD] got fug_queue data')

        except:
            print("[DATA_ACQUISITION THREAD] Failed to get FUG values!")
            sys.exit(1)

        try:

            scp.start()
            # Wait for measurement to complete:
            while not scp.is_data_ready:
                time.sleep(0.05)  # 50 ms delay, to save CPU time

            data = scp.get_data()
            print('[DATA_ACQUISITION THREAD] got tiepie data')

        except:
            print("[DATA_ACQUISITION THREAD] Failed to get tiePie values!")
            sys.exit(1)

        try:

            #  1Mohm input resistance when in single ended input mode
            # 2Mohm default input resistance
            datapoints = np.array(data[0]) * multiplier_for_nA

            # low pass filter to flatten out noise
            cutoff_freq_normalized = 3000 / (0.5 * sampling_frequency)  # in Hz
            b, a = butter(6, Wn=cutoff_freq_normalized, btype='low',
                          analog=False)  # first argument is the order of the filter
            datapoints_filtered = lfilter(b, a, datapoints)

            electrospray_data = ElectrosprayMeasurements(liquid, datapoints, voltage_from_PS, Q, temperature,
                                                         humidity, day_measurement, current_shape, current_from_PS)

            d_electrospray_measurements = electrospray_data.get_measurements_dictionary()
            a_electrospray_measurements.append(d_electrospray_measurements)

            electrospray_data = ElectrosprayMeasurements(liquid, datapoints, voltage_from_PS, Q, temperature,
                                                         humidity, day_measurement, current_shape, current_from_PS)

            electrospray_processing.calculate_filter(
                a, b, electrospray_data.data)
            electrospray_processing.calculate_fft_raw(electrospray_data.data)

            electrospray_processing.calculate_statistics(electrospray_data.data,
                                                         electrospray_processing.datapoints_filtered)
            electrospray_processing_freq, electrospray_processing_psd = electrospray_processing.calculate_power_spectral_density(
                electrospray_data.data)

            max_data, quantity_max_data, percentage_max = electrospray_processing.calculate_peaks_signal(
                electrospray_data.data)

            max_fft_peaks, cont_max_fft_peaks = electrospray_processing.calculate_peaks_fft(
                electrospray_data.data)

            classification_sjaak = electrospray_classification.do_sjaak(electrospray_processing.mean_value,
                                                                        electrospray_processing.med,
                                                                        electrospray_processing.stddev,
                                                                        electrospray_processing.psd_welch,
                                                                        electrospray_processing.variance)

            classification_monica = electrospray_classification.do_monica(float(max_data), float(quantity_max_data),
                                                                          float(percentage_max), float(
                                                                              Q), max_fft_peaks,
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

            # put values in the queue
            message = [datapoints, datapoints_filtered, time_step, electrospray_data, electrospray_processing, txt_sjaak_str, txt_monica_str, txt_max_peaks, voltage_from_PS, current_from_PS]
            queue.put(message)

            sample += 1

            print(f"[DATA_ACQUISITION THREAD] put data sample \f{sample} in data_queue")


        except:
            print("[DATA_ACQUISITION THREAD] Failed to process values!")
            sys.exit(1)

    print("[DATA_ACQUISITION THREAD] Finish acquirind data")

    # **************************************
    #              SAVING
    # **************************************

    print("[DATA_ACQUISITION THREAD] start saving")

    typeofmeasurement = {
        "sequency": str(txt_mode),
        "start": str(voltage_start),
        "stop": str(voltage_stop),
        "slope": str(slope),
        "size": str(step_size),
        "step time": str(step_time)
    }
    # electrospray_config_liquid_setup_obj.set_comment_current(current_shape_comment)

    electrospray_config_liquid_setup_obj.set_type_of_measurement(
        typeofmeasurement)
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

        print("[DATA_ACQUISITION THREAD] FILE SAVED")



