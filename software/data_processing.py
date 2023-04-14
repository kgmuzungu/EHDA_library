from FUG_functions import *
from scipy.signal import butter, lfilter

# tiepie params
sampling_frequency = 1e5  # 100 KHz
multiplier_for_nA = 500

append_array_data = True
append_array_processing = True


def data_processing(data_queue,
                    finish_event,
                    plot_real_time,
                    plotting_data_queue,
                    electrospray_config_liquid_setup_obj,
                    electrospray_processing,
                    electrospray_classification,
                    electrospray_validation,
                    feedback_queue,
                    save_data_queue
                    ):



    time_step = 1 / sampling_frequency
    sample = 0
    previous_flowrate = 0

    electrospray_validation.set_data_from_dict_liquid(electrospray_config_liquid_setup_obj.get_json_liquid())

    # THREAD LOOP
    print("[DATA_PROCESSING THREAD] starting loop")
    while not finish_event.is_set():

        # wait for first value
        while data_queue.empty():
            time.sleep(0.1)

        electrospray_data  = data_queue.get()


        # print("[DATA_PROCESSING THREAD] got datapoints from data_queue")

        try:

            # low pass filter to flatten out noise
            cutoff_freq_normalized = 3000 / (0.5 * sampling_frequency)  # in Hz
            b, a = butter(6, Wn=cutoff_freq_normalized, btype='low', analog=False)  # first argument is the order of the filter
            datapoints_filtered = lfilter(b, a, electrospray_data.data)

        except Exception as e:
            print("ERROR: ", str(e)) 
            print("[DATA_PROCESSING THREAD] Failed to filter points!")
            sys.exit(1)

        try:

            electrospray_processing.calculate_filter(a, b, electrospray_data.data)
            
            electrospray_processing.calculate_fft_raw(electrospray_data.data)

            electrospray_processing.calculate_statistics( electrospray_data.data)
            
            electrospray_processing_freq, electrospray_processing_psd = electrospray_processing.calculate_power_spectral_density(electrospray_data.data)

            max_data, quantity_max_data, percentage_max = electrospray_processing.calculate_peaks_signal(electrospray_data.data)

            max_fft_peaks, cont_max_fft_peaks = electrospray_processing.calculate_peaks_fft(electrospray_data.data)

        except Exception as e:
            print("ERROR: ", str(e)) 
            print("[DATA_PROCESSING THREAD] Failed to process data")
            sys.exit(1)

        try:

            # if change flowrate restart conejet mean values
            if(electrospray_data.flow_rate != previous_flowrate):
                cone_jet_mean = 0
                previous_flowrate = electrospray_data.flow_rate


            classification_txt, cone_jet_mean = electrospray_classification.do_classification(
                                                                        electrospray_processing.mean_value,
                                                                        electrospray_processing.med,
                                                                        electrospray_processing.stddev,
                                                                        electrospray_processing.psd_welch,
                                                                        electrospray_processing.variance,
                                                                        float(max_data), 
                                                                        float(quantity_max_data),
                                                                        float(percentage_max),
                                                                        electrospray_data.flow_rate,
                                                                        max_fft_peaks,
                                                                        cont_max_fft_peaks,
                                                                        cone_jet_mean

            )
        except Exception as e:
            print("ERROR: ", str(e)) 
            print("[DATA_PROCESSING THREAD] Failed to classify")
            sys.exit(1)


        try:

            current_shape = classification_txt,

            feedback_queue.put(classification_txt)

            electrospray_processing.set_shape(current_shape)

            txt_max_peaks = " Max: " + str(max_data) + " Quantity max: " + str(quantity_max_data) + " Percentage: " + str(percentage_max)

            electrospray_processing.calculate_fft_filtered()
            electrospray_processing.calculate_fft_peaks()

            # put values in the saving queue
            save_message = [electrospray_data.get_measurements_dictionary(), electrospray_processing.get_statistics_dictionary()]
            save_data_queue.put(save_message)

            sample += 1

            print(f"[DATA_PROCESSING THREAD] data sample \f{sample} is classified as: ", classification_txt)

        except Exception as e:
            print("ERROR: ", str(e)) 
            print("[DATA_PROCESSING THREAD] Failed to put value in save_data_queue")

        try:

            # Validation through the Chen_Pui Article
            electrospray_validation.calculate_scaling_laws_cone_jet(electrospray_data.data, electrospray_processing.mean_value, electrospray_data.flow_rate)
            print(electrospray_validation.get_validation_dictionary())

        except Exception as e:
            print("ERROR: ", str(e)) 
            print("[DATA_PROCESSING THREAD] Failed to electrospray_validation")

        try: 

            # put values in the plotting queue
            if(plot_real_time):
                message = [electrospray_data, datapoints_filtered, time_step, electrospray_processing, classification_txt, txt_max_peaks]
                plotting_data_queue.put(message)

            # print(f"[DATA_PROCESSING THREAD] put data sample \f{sample} in plotting_data_queue")

        except Exception as e:
            print("ERROR: ", str(e)) 
            print("[DATA_PROCESSING THREAD] Failed to put value in plotting queue")


    print("[DATA_PROCESSING THREAD] Finish Processing data")
