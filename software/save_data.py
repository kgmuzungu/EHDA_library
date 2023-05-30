"""
TITLE: saving data thread function
"""


import os
import time
import sys
import jsonstreams
import json

def save_data(
            save_data_queue,
            typeofmeasurement,
            save_path,
            finish_event,
            electrospray_validation,
            electrospray_config_liquid_setup_obj,
            electrospray_config_setup
            ):
    

    # if config file is configured to save the data
    if electrospray_config_setup["save_json"]:

        try:
            # electrospray_config_liquid_setup_obj.set_comment_current(current_shape_comment)
            electrospray_config_liquid_setup_obj.set_type_of_measurement(typeofmeasurement)
            aux_obj = electrospray_config_liquid_setup_obj.get_dict_config()
            # if FLAG_PLOT:
            #     electrospray_classification.plot_sjaak_cone_jet()
            #     electrospray_classification.plot_sjaak_classification()

        except Exception as e:
            print("ERROR: ", str(e))
            print("[SAVING] failed creating saving files")
            sys.exit(1)

        try:
            config_dict = {}

            if electrospray_config_setup["save_config"]:
                electrospray_config_liquid = electrospray_config_liquid_setup_obj.get_json_liquid()
                electrospray_config_setup = electrospray_config_liquid_setup_obj.get_json_setup()
                config_dict['liquid'] = electrospray_config_liquid
                config_dict['liquid']['flow_rate min'] = electrospray_config_liquid_setup_obj.get_flow_rate_min_ian()
                config_dict['setup'] = electrospray_config_setup

            # Writing
            os.makedirs(save_path, exist_ok=True)
            out_file = open(save_path + "/config.json", "w")
            json.dump(config_dict, out_file, indent = 6)
            out_file.close()

            print("[SAVING] saved config file")


        except Exception as e:
            print("ERROR: ", str(e))
            print("[SAVING] failed saving configuration values")
            sys.exit(1)




        #  *************************************
        # 	thread main loop
        #  *************************************

        with jsonstreams.Stream(jsonstreams.Type.OBJECT, filename=save_path+"/data.json", indent=4, pretty=True) as s:
            
            sample = 0
            print("[SAVE DATA THREAD] starting saving samples")


            while not finish_event.is_set():
                # get values from the queue
                while save_data_queue.empty():
                    time.sleep(0.1)
                # print("[SAVING] before get, queue size:", save_data_queue.qsize())
                data_measurement, data_processing = save_data_queue.get() # block=True, timeout=None)  # expecting a list with two dictionary objects
                # print("[SAVING] after get, queue size:", save_data_queue.qsize())


                try:
                    if electrospray_config_setup["save_data"]:
                        # if electrospray_config_setup["save_validation"]:
                        #     data_validation = electrospray_validation.get_validation_dictionary()
                        #     s.write('sample '+str(sample), {**data_measurement, **data_processing, **data_validation})
                        # el
                        if electrospray_config_setup["save_processing"]:
                            s.write('sample '+str(sample), {**data_measurement, **data_processing})  #taking values inside the two dicts and creating one dict
                        else:
                            s.write('sample '+str(sample), data_measurement)

                        print("[SAVING] saved electrospray sample:", sample)
                        


                except Exception as e:
                    print("ERROR: ", str(e))
                    print("[SAVING] failed saving electrospray measurements sample:", sample)
                    sys.exit(1)


                sample += 1


    print("[SAVE DATA THREAD] end of saving data thread")
