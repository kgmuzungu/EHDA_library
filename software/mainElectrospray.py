"""
TITLE: MAIN CODE
VERSION: 2.7.0
"""

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
import save_data

# # # **************************************
# # #                 MAIN
# # # **************************************
if __name__ == '__main__':

# # # **************************************
# # #         INITIAL CONFIGURATION
# # # **************************************


    finish_event = threading.Event()  # controller thread decide when finish_event must me True

    sampling_frequency = 1e5  # 100000

    name_setup = "mapsetup"
    setup = "setup/nozzle/" + name_setup
   
    plt.style.use('seaborn-colorblind')
    plt.ion()

    # Starting Class Objects
    electrospray_config_liquid_setup_obj = ElectrosprayConfig(setup + ".json")
    electrospray_config_liquid_setup_obj.load_json_config_setup()
    electrospray_config_setup = electrospray_config_liquid_setup_obj.get_json_setup()
    liquid = "setup/liquid/" + electrospray_config_setup["name_liquid"]
    electrospray_config_liquid_setup_obj.load_json_config_liquid(liquid + ".json")
    electrospray_validation = ElectrosprayValidation(electrospray_config_setup["name_liquid"])
    electrospray_classification = classification_electrospray.ElectrosprayClassification(electrospray_config_setup["name_liquid"])
    electrospray_processing = ElectrosprayDataProcessing(sampling_frequency)

    # Program variables
    impedance = electrospray_config_setup["osc_impedance"]
    typeofmeasurement = electrospray_config_setup["typeofmeasurement"]
    save_path = electrospray_config_setup["save_path"]
    plot_real_time = electrospray_config_setup["plot_real_time"]
    syringe_diameter = electrospray_config_setup["diameter syringe"]
    number_camera_partitions = electrospray_config_setup["number_camera_partitions"]


    #        PORTS
    arduino_COM_port = electrospray_config_setup["arduino_com_port"]
    fug_COM_port = electrospray_config_setup["fug_com_port"]
    pump_COM_port = electrospray_config_setup["pump_com_port"]


# # # **************************************
# # #                QUEUES
# # # **************************************


    threads = list()
    controller_output_queue = queue.Queue()
    feedback_queue = queue.Queue()
    data_queue = queue.Queue()
    save_data_queue = queue.Queue()
    plotting_data_queue = queue.Queue()


# # # **************************************
# # #                THREADS
# # # **************************************


    # 
    #           CONTROLLER   ->   Power supply controller thread. 
    #

    controller_thread = threading.Thread(target=controller, name='CONTROLLER THREAD',
                                            args=(
                                                typeofmeasurement,
                                                finish_event,
                                                controller_output_queue,
                                                fug_COM_port,
                                                pump_COM_port,
                                                feedback_queue,
                                                syringe_diameter
                                                ))
    controller_thread.start()



    #
    #           VIDEO   ->   Camera trigger thread using arduino microcontroller
    #

    # makeVideo_thread = threading.Thread(target=cameraTrigger.activateTrigger, name='video reccording thread', args=(arduino_COM_port, finish_event, typeofmeasurement, number_camera_partitions))
    # threads.append(makeVideo_thread)
    # makeVideo_thread.start()

    

    # 
    #          SENSOR  ->   Data acquisition
    #   


    data_acquisition_thread = threading.Thread(
        target=data_acquisition.data_acquisition,
        name='Data acquisition thread',
        args=(data_queue,
             controller_output_queue,
             finish_event,
             typeofmeasurement,
             liquid,
             arduino_COM_port
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
            plot_real_time,
            plotting_data_queue,
            electrospray_config_liquid_setup_obj,
            electrospray_processing,
            electrospray_classification,
            electrospray_validation,
            feedback_queue,
            save_data_queue
        )
    )
    threads.append(data_processing_thread)
    data_processing_thread.start()



    # 
    #          SAVE DATA  ->  save data thread
    #   


    save_data_thread = threading.Thread(
        target=save_data.save_data,
        name='Saving Data thread',
        args=(save_data_queue,
            typeofmeasurement,
            save_path,
            finish_event,
            electrospray_validation,
            electrospray_config_liquid_setup_obj,
            electrospray_config_setup
        )
    )
    threads.append(save_data_thread)
    save_data_thread.start()



    # 
    #          PLOTTING LOOP  ->    (注意) It's not a Thread 
    #  

    # plotting is not a thread. It is a function running in a loop in the main.
    if(plot_real_time):
        fig, ax, ln0, ln1, ln2, bg = plotting.start_plot(plotting_data_queue)
    while not finish_event.is_set():
        if(plot_real_time):
            plotting.real_time_plot(plotting_data_queue, finish_event, fig, ax, ln0, ln1, ln2, bg)


        
# # # **************************************
# # #                EXIT
# # # **************************************


    controller_thread.join()
    print('[MAIN] CONTROLLER THREAD CLOSED!')

    # makeVideo_thread.join()
    # print('[MAKE VIDEO THREAD] thread CLOSED!')

    data_acquisition_thread.join() 
    print('[MAIN] DATA ACQUISITION THREAD CLOSED!')

    data_processing_thread.join()
    print('[MAIND] DATA PROCESSING THREAD CLOSED!')

    save_data_thread.join()
    print('[MAIN] SAVE DATA THREAD CLOSED!')

    print("\n---------- FINISH PROGRAM ----------")
    sys.exit(0)





