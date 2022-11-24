import threading
import sys
import queue
import classification_electrospray
from printinfo import *
import matplotlib.pyplot as plt
from electrospray import ElectrosprayDataProcessing, ElectrosprayConfig
from validation_electrospray import ElectrosprayValidation
from classification_electrospray import ElectrosprayClassification
from configuration_FUG import *
import cameraTrigger
import data_acquisition
import plotting 
import data_processing
import os
import json
import logging



# *************************************
#            MAIN FUNCTION
# *************************************
if __name__ == '__main__':


    #       INITIAL CONFIGURATION

    finish_event = threading.Event()  # when Power Supply finish the finish_event will be set

    save_path = """C:/Users/hvvhl/Desktop/teste"""

    # LOGGING CONFIG
    LOG_FILENAME = r'logging_test.out'
    logging.basicConfig(filename=LOG_FILENAME, encoding='utf-8',
                        format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info('Started')


    sampling_frequency = 1e5  # 100000
    array_electrospray_measurements = []
    array_electrospray_processing = []


    name_setup = "setup10"
    setup = "C:/Users/hvvhl/Desktop/joao/EHDA_library/setup/nozzle/" + name_setup
    name_liquid = "water60alcohol40" # ["ethyleneglycolHNO3", "ethanol", water60alcohol40, 2propanol]
    liquid = "setup/liquid/" + name_liquid
    current_shape_comment = "difficult cone jet stabilization"

   
    FLAG_PLOT = True
    plt.style.use('seaborn-colorblind')
    plt.ion()




    #          CREATING INSTANCES

    electrospray_config_liquid_setup_obj = ElectrosprayConfig(setup + ".json", liquid + ".json")
    electrospray_config_liquid_setup_obj.load_json_config_liquid()
    electrospray_config_liquid_setup_obj.load_json_config_setup()
    electrospray_validation = ElectrosprayValidation(name_liquid)
    electrospray_classification = classification_electrospray.ElectrosprayClassification(name_liquid)
    electrospray_processing = ElectrosprayDataProcessing(sampling_frequency)
    
    electrospray_config_setup = electrospray_config_liquid_setup_obj.get_json_setup()
    impedance = electrospray_config_setup["osc_impedance"]

    SAVE_DATA = electrospray_config_setup["save_data"]
    SAVE_PROCESSING = electrospray_config_setup["save_processing"]
    SAVE_CONFIG = electrospray_config_setup["save_config"]
    SAVE_JSON = electrospray_config_setup["save_json"]
    MODERAMP = electrospray_config_setup["moderamp"]  # else go in steps

    Q = electrospray_config_setup["flow_rate"]  # flow rate  uL/h
    Q = Q * 10e-6  # liter/h   # Q = 0.0110  # ml/h flow rate
    Q = Q * 2.7778e-7  # m3/s  # Q = Q * 2.7778e-3  # cm3/s
    print('flowrate cm3/s: ', Q)

    #        PORTS
    arduino_COM_port = 0
    fug_COM_port = 4

    #              FUG INIT
    obj_fug_com = FUG_initialize(fug_COM_port)  # parameter: COM port idx
    print("[FUG] obj_fug_com: ", obj_fug_com)
    get_voltage_from_PS(obj_fug_com)



    #              THREADS

    threads = list()

    # 
    #           FUG   ->   Power supply controller thread. (It will be the future actuator thread.)
    #

    fug_queue = queue.Queue(maxsize=100)

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
        step_size = 500
        step_time = 5  # 10

        # step_sequency(obj_fug_com,  step_size=300, step_time=5, step_slope=300, voltage_start=3000, voltage_stop=6000)
        step_sequency_thread = threading.Thread(target=step_sequency, name='step sequency FUG',
                                                args=(finish_event, fug_queue, obj_fug_com, step_size, step_time, slope, voltage_start,
                                                    voltage_stop))
        step_sequency_thread.start()

    #
    #           VIDEO   ->   Camera trigger thread using arduino microcontroller
    #

    makeVideo_thread = threading.Thread(
        target=cameraTrigger.activateTrigger, name='video reccording thread', args=(arduino_COM_port,finish_event))
    threads.append(makeVideo_thread)
    makeVideo_thread.start()

    # 
    #          DATA ACQUISITION  ->   Data acquisition (it will be the future sensor thread)
    #   

    data_queue = queue.Queue(maxsize=100)

    data_acquisition_thread = threading.Thread(
        target=data_acquisition.data_acquisition,
        name='Data acquisition thread',
        args=(data_queue,
             fug_queue,
             finish_event,
             voltage_start,
             liquid,
             array_electrospray_measurements,
             Q
        )
    )
    threads.append(data_acquisition_thread)
    data_acquisition_thread.start()


    # 
    #          DATA PROCESSING  ->  data proccessing
    #   

    data_processed_queue = queue.Queue(maxsize=100)

    data_processing_thread = threading.Thread(
        target=data_processing.data_processing,
        name='Data acquisition thread',
        args=(data_queue,
            finish_event,
            data_processed_queue,
            electrospray_config_liquid_setup_obj,
            electrospray_processing,
            array_electrospray_processing,
            electrospray_classification,
            electrospray_validation,
            Q,
        )
    )
    threads.append(data_processing_thread)
    data_processing_thread.start()


    #            PLOTTING LOOP

    #  plotting is not a thread. It is a function running in a loop in the main.
    fig, ax, ln0, ln1, ln2, bg = plotting.start_plot(data_processed_queue, finish_event)
    while not finish_event.is_set():
        plotting.real_time_plot(data_processed_queue, finish_event, fig, ax, ln0, ln1, ln2, bg)

    #                EXIT

    if MODERAMP:
        ramp_sequency_thread.join()
        print(print('[RAMP THREAD] thread CLOSED!'))
    else:
        step_sequency_thread.join()
        print(print('[STEP THREAD] thread CLOSED!'))

    makeVideo_thread.join()
    print(print('[MAKE VIDEO THREAD] thread CLOSED!'))


    
    #              SAVING

    print("[SAVING] START SAVING")

    try:

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

        # if FLAG_PLOT:
        #     electrospray_classification.plot_sjaak_cone_jet()
        #     electrospray_classification.plot_sjaak_classification()

        full_dict = {}
        full_dict['config'] = {}

    except:
        print("[SAVING] failed creating saving files")
        sys.exit(1)

    try:

        if SAVE_CONFIG:
            electrospray_config_liquid = electrospray_config_liquid_setup_obj.get_json_liquid()
            electrospray_config_setup = electrospray_config_liquid_setup_obj.get_json_setup()
            full_dict['config']['liquid'] = electrospray_config_liquid
            full_dict['config']['liquid']['flow rate min'] = electrospray_config_liquid_setup_obj.get_flow_rate_min_ian()

            full_dict['config']['setup'] = electrospray_config_setup
            full_dict['config']['setup']['voltage regime'] = typeofmeasurement
            full_dict['config']['setup']['comments'] = current_shape_comment


        try:
            if SAVE_PROCESSING:
                full_dict['processing'] = array_electrospray_processing

        except:
            print("[SAVING] failed saving array_electrospray_processing")
            sys.exit(1)

        try:

            if SAVE_DATA:
                full_dict['measurements'] = array_electrospray_measurements

        except:
            print("[SAVING] failed saving array_electrospray_measurements")
            sys.exit(1)

        try:

            # voltage = str(voltage) + 'V'
            if SAVE_JSON:
                # arbitrary, defined in the header
                Q = str(Q) + 'm3_s'
                file_name = txt_mode + name_setup + name_liquid + "_all shapes_" + Q + ".json"
                completeName = os.path.join(save_path, file_name)

                with open(completeName, 'w') as file:
                    json.dump((full_dict), file, indent=4)
                electrospray_validation.open_load_json_data(filename=completeName)

            print("[SAVING] FILE SAVED")
            sys.exit(0)

        except:
            print("[SAVING] Failed to SAVE JSON")
            sys.exit(1)

    except:
        print("[SAVING] Failed to on saving function")
        sys.exit(1)



    # # # **************************************
    # # #                EXIT
    # # # **************************************
    #
    #
    #
    # if MODERAMP:
    #     ramp_sequency_thread.join()
    #     print(print('[RAMP THREAD] thread CLOSED!'))
    # else:
    #     step_sequency_thread.join()
    #     print(print('[STEP THREAD] thread CLOSED!'))
    #
    # makeVideo_thread.join()
    # print(print('[MAKE VIDEO THREAD] thread CLOSED!'))

        # fazer funcao de saida do loop
        #     ramp_sequency_thread.join()
        #     makeVideo_thread.join()
        #     FUG_sendcommands(obj_fug_com, ['U 0'])
        #     sys.exit(1)
        #     # Close oscilloscope:
        #     del scp
        # logging.info('Finished')
        # sys.exit(0)
