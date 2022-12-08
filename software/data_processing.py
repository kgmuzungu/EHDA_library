from configuration_FUG import *
from scipy.signal import butter, lfilter

# tiepie params
sampling_frequency = 1e5  # 100 KHz
multiplier_for_nA = 500

append_array_data = True
append_array_processing = True
FLAG_PLOT = True


def data_processing(data_queue,
                    finish_event,
                    data_processed_queue,
                    electrospray_config_liquid_setup_obj,
                    electrospray_processing,
                    array_electrospray_processing,
                    electrospray_classification,
                    electrospray_validation,
                    Q,
                    current_state
                    ):


    print("[DATA_PROCESSING THREAD] STARTING")

    time_step = 1 / sampling_frequency
    sample = 0

    # THREAD LOOP
    while not finish_event.is_set():

        # wait for first value
        while data_queue.empty():
            time.sleep(0.1)

        electrospray_data  = data_queue.get()


        print("[DATA_PROCESSING THREAD] got datapoints from data_queue")

        try:

            # low pass filter to flatten out noise
            cutoff_freq_normalized = 3000 / (0.5 * sampling_frequency)  # in Hz
            b, a = butter(6, Wn=cutoff_freq_normalized, btype='low', analog=False)  # first argument is the order of the filter
            datapoints_filtered = lfilter(b, a, electrospray_data.data)

        except:
            print("[DATA_PROCESSING THREAD] Failed to filter points!")
            sys.exit(1)

        try:

            electrospray_processing.calculate_filter(a, b, electrospray_data.data)
            
            electrospray_processing.calculate_fft_raw(electrospray_data.data)

            electrospray_processing.calculate_statistics( electrospray_data.data)
            
            electrospray_processing_freq, electrospray_processing_psd = electrospray_processing.calculate_power_spectral_density(electrospray_data.data)

            max_data, quantity_max_data, percentage_max = electrospray_processing.calculate_peaks_signal(electrospray_data.data)

            max_fft_peaks, cont_max_fft_peaks = electrospray_processing.calculate_peaks_fft(electrospray_data.data)

        except:
            print("[DATA_PROCESSING THREAD] Failed to process data")
            sys.exit(1)

        try:

            classification_sjaak = electrospray_classification.do_sjaak(
                                                                        electrospray_processing.mean_value,
                                                                        electrospray_processing.med,
                                                                        electrospray_processing.stddev,
                                                                        electrospray_processing.psd_welch,
                                                                        electrospray_processing.variance
                                                                        )

            classification_monica = electrospray_classification.do_monica(
                                                                        float(max_data), 
                                                                        float(quantity_max_data),
                                                                        float(percentage_max),
                                                                        float(Q),
                                                                        max_fft_peaks,
                                                                        cont_max_fft_peaks
                                                                        )
            txt_sjaak_str = str(classification_sjaak)
            txt_monica_str = str(classification_monica)

            current_shape = {
                "Sjaak":  str(classification_sjaak),
                "Monica": str(classification_monica),
            }

            current_state = str(classification_sjaak)

        except:
            print("[DATA_PROCESSING THREAD] Failed to classify")
            sys.exit(1)

        try:

            electrospray_processing.set_shape(current_shape)

            txt_max_peaks = " Max: " + str(max_data) + " Quantity max: " + str(quantity_max_data) + " Percentage: " + str(percentage_max)

            electrospray_processing.calculate_fft_filtered()
            electrospray_processing.calculate_fft_peaks()

            if current_shape["Sjaak"] == "cone jet" and FLAG_PLOT:
                electrospray_validation.set_data_from_dict_liquid(electrospray_config_liquid_setup_obj.get_json_liquid())

                electrospray_validation.calculate_scaling_laws_cone_jet(electrospray_data.data, electrospray_processing.mean_value, Q)

            if append_array_processing:
                d_electrospray_processing = electrospray_processing.get_statistics_dictionary()
                array_electrospray_processing.append(d_electrospray_processing)

            # put values in the queue
            message = [electrospray_data, datapoints_filtered, time_step, electrospray_processing, txt_sjaak_str, txt_monica_str, txt_max_peaks]
            data_processed_queue.put(message)

            sample += 1

            print(f"[DATA_PROCESSING THREAD] put data sample \f{sample} in data_processed_queue")


        except:
            print("[DATA_PROCESSING THREAD] Failed to finish process")
            sys.exit(1)

    print("[DATA_PROCESSING THREAD] Finish Processing data")
