import os
import json
import time
import sys

def save_data(
            save_data_queue,
            typeofmeasurement,
            name_liquid,
            save_path,
            finish_event,
            electrospray_config_liquid_setup_obj
            ):

    try:

        # voltage = str(voltage) + 'V'
        if electrospray_config_setup["save_json"]:
            # arbitrary, defined in the header
            file_name = name_liquid + '_step_size_' + \
                str(typeofmeasurement['step_size']) + "_step_time_" + \
                str(typeofmeasurement['step_time']) + ".json"
            completeName = os.path.join(save_path, file_name)


        file = open(completeName, 'w')
            # with open(completeName, 'w') as file:
            #     json.dump((full_dict), file, indent=4)
            # electrospray_validation.open_load_json_data(filename=completeName)

        print("[SAVING] File Opened")

    except:
        print("[SAVING] Failed to open file")


    try:

        # electrospray_config_liquid_setup_obj.set_comment_current(current_shape_comment)

        electrospray_config_liquid_setup_obj.set_type_of_measurement(typeofmeasurement)
        aux_obj = electrospray_config_liquid_setup_obj.get_dict_config()

        # if FLAG_PLOT:
        #     electrospray_classification.plot_sjaak_cone_jet()
        #     electrospray_classification.plot_sjaak_classification()

        config_dict = {}
        config_dict['config'] = {}

    except:
        print("[SAVING] failed creating saving files")
        sys.exit(1)

    try:

        if electrospray_config_setup["save_config"]:
            electrospray_config_liquid = electrospray_config_liquid_setup_obj.get_json_liquid()
            electrospray_config_setup = electrospray_config_liquid_setup_obj.get_json_setup()
            config_dict['config']['liquid'] = electrospray_config_liquid
            config_dict['config']['liquid']['flow rate min'] = electrospray_config_liquid_setup_obj.get_flow_rate_min_ian()
            config_dict['config']['setup'] = electrospray_config_setup

            json.dump(config_dict, file, indent=4)


    except:
        print("[SAVING] failed saving configuration values")
        sys.exit(1)



    #
    #     THREAD LOOP
    #
    
    sample = 0
    print("[SAVE DATA THREAD] starting loop")
    while not finish_event.is_set():

        # wait for first value
        while save_data_queue.empty():
            time.sleep(0.1)

        data_measurement, data_processing = save_data_queue.get()

        try:
            if electrospray_config_setup["save_processing"]:
                json.dump(data_processing, file, indent=4)

        except:
            print("[SAVING] failed saving electrospray processing sample:", sample)
            sys.exit(1)

        try:

            if electrospray_config_setup["save_data"]:
                json.dump(data_measurement, file, indent=4)

        except:
            print("[SAVING] failed saving electrospray measurements sample:", sample)
            sys.exit(1)

        sample += 1


    file.close()
    print("[SAVE DATA THREAD] Finish Processing data")
