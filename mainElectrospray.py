
import time
import threading
import sys
import libtiepie
import random
import queue

import classification_electrospray
from printinfo import *
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from scipy import signal
from time import gmtime, strftime


from electrospray import ElectrosprayDataProcessing, ElectrosprayConfig, ElectrosprayMeasurements
from validation_electrospray import ElectrosprayValidation
from classification_electrospray import ElectrosprayClassification


from configuration_FUG import *
import configuration_tiepie
import cameraTrigger
import data_acquisition
import plotting

import os
import numpy as np
import json
import logging
import pylab
import numpy as np



# *************************************
#            MAIN FUNCTION
# *************************************
if __name__ == '__main__':




    # *************************************
    #       INITIAL CONFIGURATION
    # *************************************

    event = threading.Event()  # this is somehow important to fug

    # fig = pylab.gcf()
    save_path = """C:/Users/hvvhl/Desktop/teste"""

    # LOGGING CONFIG
    LOG_FILENAME = r'logging_test.out'
    logging.basicConfig(filename=LOG_FILENAME, encoding='utf-8',
                        format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info('Started')


    # tiepie params
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

    #  VAR_BIN_CONFIG = input("Would you like to save data? [True/False] ")
    VAR_BIN_CONFIG = True
    SAVE_DATA = VAR_BIN_CONFIG
    SAVE_PROCESSING = VAR_BIN_CONFIG
    SAVE_CONFIG = VAR_BIN_CONFIG
    SAVE_JSON = VAR_BIN_CONFIG
    append_array_data = VAR_BIN_CONFIG
    append_array_processing = VAR_BIN_CONFIG

    MODERAMP = True  # else go in steps
    # maybe change to 100 (45 looks to be a good size for saving)
    number_measurements = 45
    print('number_measurements: ', number_measurements)

    Q = 1450  # flow rate  uL/h
    Q = Q * 10e-6  # liter/h   # Q = 0.0110  # ml/h flow rate
    Q = Q * 2.7778e-7  # m3/s  # Q = Q * 2.7778e-3  # cm3/s
    print('flowrate cm3/s: ', Q)

    impedance, temperature, humidity = 2000000, 27.8, 49
    print('impedance: ', impedance)
    print('temperature: ', temperature)
    print('humidity: ', humidity)

    name_setup = "setup10"
    setup = "C:/Users/hvvhl/Desktop/joao/EHDA_library/setup/nozzle/" + name_setup
    # liquids = ["ethyleneglycolHNO3", "ethanol", water60alcohol40, 2propanol]
    name_liquid = "water60alcohol40"
    liquid = "setup/liquid/" + name_liquid
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

    FLAG_PLOT = False
    classification_sjaak = ""
    day_measurement = strftime("%a_%d %b %Y", gmtime())
    res = ""
    count_sequency_cone_jet = 0
    listdir = os.listdir()
    j = 0
    plt.style.use('seaborn-colorblind')
    plt.ion()
    # PORTS
    arduino_COM_port = 0
    fug_COM_port = 4


    # **************************************
    #          CREATING INSTANCES
    # **************************************
    electrospray_config_liquid_setup_obj = ElectrosprayConfig(
        setup + ".json", liquid + ".json")
    electrospray_config_liquid_setup_obj.load_json_config_liquid()
    electrospray_config_liquid_setup_obj.load_json_config_setup()
    electrospray_validation = ElectrosprayValidation(name_liquid)
    electrospray_classification = classification_electrospray.ElectrosprayClassification(
        name_liquid)
    electrospray_processing = ElectrosprayDataProcessing(sampling_frequency)



    # **************************************
    #              FUG INIT
    # **************************************
    obj_fug_com = FUG_initialize(fug_COM_port)  # parameter: COM port idx
    print("obj_fug_com: ", obj_fug_com)
    get_voltage_from_PS(obj_fug_com)



    # **************************************
    #              THREADS
    # **************************************

    threads = list()


    # 
    #           FUG   ->   Power supply controller thread. It will be the future actuator thread.
    #

    fug_queue = queue.Queue(maxsize=10)

    if MODERAMP:
        txt_mode = "ramp"
        slope = 200
        voltage_start = 3000
        voltage_stop = 11000
        step_size = 0
        step_time = 0

        # ramp_sequency(obj_fug_com, ramp_slope=slope, voltage_start=voltage_start, voltage_stop=voltage_stop)
        ramp_sequency_thread = threading.Thread(target=ramp_sequency, name='ramp sequency FUG',
                                                args=(
                                                    fug_queue, obj_fug_com, slope, voltage_start,
                                                    voltage_stop))
        ramp_sequency_thread.start()


    else:  # MODESTEP
        txt_mode = "step"
        slope = 10000
        voltage_start = 3000
        voltage_stop = 10000
        step_size = 100
        step_time = 10  # 10

        # step_sequency(obj_fug_com,  step_size=300, step_time=5, step_slope=300, voltage_start=3000, voltage_stop=6000)
        step_sequency_thread = threading.Thread(target=step_sequency, name='step sequency FUG',
                                                args=(fug_queue, obj_fug_com, step_size, step_time, slope, voltage_start,
                                                    voltage_stop))
        step_sequency_thread.start()

    # 
    #           VIDEO   ->   Camera trigger thread using arduino microcontroller
    #

    makeVideo_thread = threading.Thread(
        target=cameraTrigger.activateTrigger, name='video reccording thread', args=(arduino_COM_port,))
    threads.append(makeVideo_thread)
    makeVideo_thread.start()

    # 
    #          DATA ACQUISITION  ->   Data acquisition + data proccessing + data saving thread  (it will be the future sensor thread)
    #   

    data_queue = queue.Queue(maxsize=10)

    data_acquisition_thread = threading.Thread(
        target=data_acquisition.data_acquisition,
        name='Data acquisition thread',
        args=(
            data_queue,
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
            save_path
        )
    )
    threads.append(data_acquisition_thread)
    data_acquisition_thread.start()


    # **************************************
    #              PLOTTING
    # **************************************

    #  plotting is not a thread. It is a function running in a loop in the main.
    fig, ax, ln0, ln1, ln2, bg = plotting.start_plot(data_queue, event)
    while not event.is_set() or not data_queue.empty():
        plotting.real_time_plot(data_queue, event, fig, ax, ln0, ln1, ln2, bg)




    # # **************************************
    # #                EXIT
    # # **************************************

        # fazer funcao de saida do loop
        #     ramp_sequency_thread.join()
        #     makeVideo_thread.join()
        #     FUG_sendcommands(obj_fug_com, ['U 0'])
        #     sys.exit(1)
        #     # Close oscilloscope:
        #     del scp
        # logging.info('Finished')
        # sys.exit(0)
