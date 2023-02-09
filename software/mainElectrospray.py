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

    sampling_frequency = 1e5  # 100000
    array_electrospray_measurements = []
    array_electrospray_processing = []

    name_setup = "setup3"
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
    Q = float(typeofmeasurement["flow_rate"])
    save_path = electrospray_config_setup["save_path"]
    syringe_diameter = electrospray_config_setup["diameter syringe"]
    number_camera_partitions = electrospray_config_setup["number_camera_partitions"]

    Q = Q * 10e-6  # liter/h   # Q = 0.0110  # ml/h flow rate
    Q = Q * 2.7778e-7  # m3/s  # Q = Q * 2.7778e-3  # cm3/sq
    print('flowrate cm3/s: ', Q)

    #        PORTS
    arduino_COM_port = 1
    fug_COM_port = 5
    pump_COM_port = 0


# # # **************************************
# # #                QUEUES
# # # **************************************


    threads = list()
    controller_output_queue = queue.Queue(maxsize=100000)
    feedback_queue = queue.Queue(maxsize=100000)
    data_queue = queue.Queue(maxsize=100000)
    save_data_queue = queue.Queue(maxsize=100000)
    plotting_data_queue = queue.Queue(maxsize=100000)




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
             arduino_COM_port,
             array_electrospray_measurements
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
            name_liquid,
            save_path,
            finish_event,
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
    fig, ax, ln0, ln1, ln2, bg = plotting.start_plot(plotting_data_queue)
    while not finish_event.is_set():
        plotting.real_time_plot(plotting_data_queue, finish_event, fig, ax, ln0, ln1, ln2, bg)


        
# # # **************************************
# # #                EXIT
# # # **************************************


    controller_thread.join()
    print('[CONTROLLER THREAD] thread CLOSED!')

    # makeVideo_thread.join()
    # print('[MAKE VIDEO THREAD] thread CLOSED!')

    data_acquisition_thread.join()
    print('[DATA ACQUISITION THREAD] thread CLOSED!')

    data_processing_thread.join()
    print('[DATA PROCESSING THREAD] thread CLOSED!')

    save_data_thread.join()
    print('[SAVE DATA THREAD] thread CLOSED!')

    print("\n---------- FINISH PROGRAM ----------")
    sys.exit(0)


