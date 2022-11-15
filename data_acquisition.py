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
from electrospray import ElectrosprayDataProcessing, ElectrosprayConfig, ElectrosprayMeasurements

from multiprocessing import Process, Queue

# tiepie params
sampling_frequency = 1e5  # 100 KHz
multiplier_for_nA = 500




name_setup = "setup10"
setup = "C:/Users/hvvhl/Desktop/joao/EHDA_library/setup/nozzle/" + name_setup
name_liquid = "water60alcohol40"  # liquids = ["ethyleneglycolHNO3", "ethanol", water60alcohol40, 2propanol]
liquid = "setup/liquid/" + name_liquid
current_shapes = ["no voltage no fr", "no voltage", "dripping", "intermittent", "cone jet", "multijet",
                  "streamer onset", "dry", "all shapes"]  # 0no voltage no fr/1no voltage/2dripping/3intermittent/4cone jet/5multijet/6streamer onset/7dry/8all shapes"]
current_shape = current_shapes[8]  
current_shape_comment = "difficult cone jet stabilization"

a_electrospray_measurements = []
a_electrospray_measurements_data = []



def data_acquisition(data_queue):


    # **************************************
    #           OSCILLOSCOPE
    # **************************************

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


    try:
        scp = configuration_tiepie.config_TiePieScope(scp, sampling_frequency)
        # print_device_info(scp)
    except:
        print("Failed to config tie pie!")
        sys.exit(1) 
    
    for j in range(50):
        try: 

            scp.start()
            # Wait for measurement to complete:
            while not scp.is_data_ready:
                time.sleep(0.05)  # 50 ms delay, to save CPU time

            data = scp.get_data()
            print('got data points')

            #  1Mohm input resistance when in single ended input mode
            datapoints = np.array(data[0]) * multiplier_for_nA  # 2Mohm default input resistance

            # low pass filter to flatten out noise
            cutoff_freq_normalized = 3000 / (0.5 * sampling_frequency)  # in Hz
            b, a = butter(6, Wn=cutoff_freq_normalized, btype='low',
                            analog=False)  # first argument is the order of the filter
            datapoints_filtered = lfilter(b, a, datapoints)

            electrospray_data = ElectrosprayMeasurements(liquid, datapoints, 10, 10, 10, 10, 10, current_shape, 10)

            d_electrospray_measurements = electrospray_data.get_measurements_dictionary()
            data_queue.put(d_electrospray_measurements)
            

        except:
            print("Failed to get tiePie values!")
            sys.exit(1) 

    full_dict = {}
    full_dict['measurements'] = a_electrospray_measurements
    # Q = str(Q) + 'm3_s'
    # voltage_filename = str(voltage_array) + 'V'
    file_name = "ramp" + name_setup + name_liquid + "_all shapes_" + str(10) + ".json"
    completeName = os.path.join("""C:/Users/hvvhl/Desktop/teste""", file_name)

    with open(completeName, 'w') as file:
        json.dump((full_dict), file, indent=4)



def data_process(data_queue):

    while(1):
        if data_queue.empty():
            print("fila vazia")
        else:
            a_electrospray_measurements.append(data_queue.get())
            print('Data Append!')
        time.sleep(0.5)
