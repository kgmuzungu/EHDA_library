import threading
import sys
import queue
import classification_electrospray
from printinfo import *
import matplotlib.pyplot as plt
from electrospray import ElectrosprayDataProcessing, ElectrosprayConfig
from validation_electrospray import ElectrosprayValidation
from classification_electrospray import ElectrosprayClassification
from FUG_functions import *
from controller import *
import cameraTrigger
import data_acquisition
import plotting 
import data_processing
import os
import json
import logging


state_machine = ["Dripping", "Intermittent", "Cone Jet", "Multi Jet", "Corona Sparks"] # total 5 states


# # # **************************************
# # #                 MAIN
# # # **************************************
if __name__ == '__main__':


# # # **************************************
# # #         INITIAL CONFIGURATION
# # # **************************************

    current_state = state_machine[0]    

    finish_event = threading.Event()  # when Power Supply finish the finish_event will be set

    # LOGGING CONFIG
    LOG_FILENAME = r'logging_test.out'
    logging.basicConfig(filename=LOG_FILENAME, encoding='utf-8',
                        format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info('Started')

    sampling_frequency = 1e5  # 100000
    array_electrospray_measurements = []
    array_electrospray_processing = []

    name_setup = "setup11"
    setup = "setup/nozzle/" + name_setup
    name_liquid = "ethanol" # ["ethyleneglycolHNO3", "ethanol", water60alcohol40, 2propanol]
    liquid = "setup/liquid/" + name_liquid
    current_shape_comment = "difficult cone jet stabilization"
   
    FLAG_PLOT = True
    plt.style.use('seaborn-colorblind')
    plt.ion()

    electrospray_config_liquid_setup_obj = ElectrosprayConfig(setup + ".json", liquid + ".json")
    electrospray_config_liquid_setup_obj.load_json_config_liquid()
    electrospray_config_liquid_setup_obj.load_json_config_setup()
    electrospray_validation = ElectrosprayValidation(name_liquid)
    electrospray_classification = classification_electrospray.ElectrosprayClassification(name_liquid)
    electrospray_processing = ElectrosprayDataProcessing(sampling_frequency)
    electrospray_config_setup = electrospray_config_liquid_setup_obj.get_json_setup()
    impedance = electrospray_config_setup["osc_impedance"]
    typeofmeasurement = electrospray_config_setup["typeofmeasurement"]
    Q = electrospray_config_setup["flow_rate"]  # flow rate  uL/h
    save_path = electrospray_config_setup["save_path"]
    number_camera_partitions = electrospray_config_setup["number_camera_partitions"]

    Q = Q * 10e-6  # liter/h   # Q = 0.0110  # ml/h flow rate
    Q = Q * 2.7778e-7  # m3/s  # Q = Q * 2.7778e-3  # cm3/sq
    print('flowrate cm3/s: ', Q)

    #        PORTS
    arduino_COM_port = 0
    fug_COM_port = 4


# # # **************************************
# # #                THREADS
# # # **************************************

    threads = list()
    fug_values_queue = queue.Queue(maxsize=100)
    feedback_queue = queue.Queue(maxsize=100)
    data_queue = queue.Queue(maxsize=100)
    plotting_data_queue = queue.Queue(maxsize=100)


    # 
    #           CONTROLLER   ->   Power supply controller thread. 
    #

    controller_thread = threading.Thread(target=controller, name='CONTROLLER THREAD',
                                            args=(
                                                typeofmeasurement,
                                                finish_event,
                                                fug_values_queue,
                                                fug_COM_port,
                                                feedback_queue
                                                ))
    controller_thread.start()


    #
    #           VIDEO   ->   Camera trigger thread using arduino microcontroller
    #

    makeVideo_thread = threading.Thread(target=cameraTrigger.activateTrigger, name='video reccording thread', args=(arduino_COM_port, finish_event, typeofmeasurement, number_camera_partitions))
    threads.append(makeVideo_thread)
    makeVideo_thread.start()

    
    # 
    #          SENSOR  ->   Data acquisition
    #   


    data_acquisition_thread = threading.Thread(
        target=data_acquisition.data_acquisition,
        name='Data acquisition thread',
        args=(data_queue,
             fug_values_queue,
             finish_event,
             typeofmeasurement['voltage_start'],
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


    data_processing_thread = threading.Thread(
        target=data_processing.data_processing,
        name='Data acquisition thread',
        args=(data_queue,
            finish_event,
            plotting_data_queue,
            electrospray_config_liquid_setup_obj,
            electrospray_processing,
            array_electrospray_processing,
            electrospray_classification,
            electrospray_validation,
            Q,
            feedback_queue
        )
    )
    threads.append(data_processing_thread)
    data_processing_thread.start()


    # 
    #          PLOTTING LOOP  ->    (注意) It's not a Thread 
    #  

    #  plotting is not a thread. It is a function running in a loop in the main.
    fig, ax, ln0, ln1, ln2, bg = plotting.start_plot(plotting_data_queue)
    while not finish_event.is_set():
        plotting.real_time_plot(plotting_data_queue, finish_event, fig, ax, ln0, ln1, ln2, bg)


        
# # # **************************************
# # #                EXIT
# # # **************************************

    controller_thread.join()
    print('[POWER SUPPLY THREAD] thread CLOSED!')

    makeVideo_thread.join()
    print('[MAKE VIDEO THREAD] thread CLOSED!')


    
# # # **************************************
# # #                SAVING
# # # **************************************

    print("[SAVING] START SAVING")

    try:

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

        if electrospray_config_setup["save_config"]:
            electrospray_config_liquid = electrospray_config_liquid_setup_obj.get_json_liquid()
            electrospray_config_setup = electrospray_config_liquid_setup_obj.get_json_setup()
            full_dict['config']['liquid'] = electrospray_config_liquid
            full_dict['config']['liquid']['flow rate min'] = electrospray_config_liquid_setup_obj.get_flow_rate_min_ian()
            full_dict['config']['setup'] = electrospray_config_setup
            full_dict['config']['setup']['comments'] = current_shape_comment


        try:
            if electrospray_config_setup["save_processing"]:
                full_dict['processing'] = array_electrospray_processing

        except:
            print("[SAVING] failed saving array_electrospray_processing")
            sys.exit(1)

        try:

            if electrospray_config_setup["save_data"]:
                full_dict['measurements'] = array_electrospray_measurements

        except:
            print("[SAVING] failed saving array_electrospray_measurements")
            sys.exit(1)

        try:

            # voltage = str(voltage) + 'V'
            if electrospray_config_setup["save_json"]:
                # arbitrary, defined in the header
                file_name = name_liquid + '_step_size_' + str(typeofmeasurement['step_size']) + "_step_time_" + str(typeofmeasurement['step_time']) +  ".json"
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


