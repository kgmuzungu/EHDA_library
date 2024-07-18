"""
TITLE: data processing thread function
"""

from FUG_functions import *
from scipy.signal import butter, lfilter

from joblib import load

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

    # setup = electrospray_config_liquid_setup_obj.get_json_setup

    electrospray_validation.set_data_from_dict_liquid(electrospray_config_liquid_setup_obj.get_json_liquid())

    setup = electrospray_config_liquid_setup_obj.get_json_setup()

    generalist_clf_model = load(setup["generalist_ml_model"])

    clf_model = load(setup["ml_model"])

    nn_model = load(setup["nn_model"])

    #  *************************************
    # 	thread main loop
    #  *************************************
    print("[DATA_PROCESSING THREAD] starting loop")
    while not finish_event.is_set():

        # get value from the queue
        while data_queue.empty():
            time.sleep(0.1)
        electrospray_data = data_queue.get()
        # print("[DATA_PROCESSING THREAD] got datapoints from data_queue")

        # low pass filter to flatten out noise
        try:
            cutoff_freq_normalized = 3000 / (0.5 * sampling_frequency)  # in Hz
            b, a = butter(6, Wn=cutoff_freq_normalized, btype='low',
                          analog=False)  # first argument is the order of the filter
            datapoints_filtered = lfilter(b, a, electrospray_data.data)

        except Exception as e:
            print("ERROR: ", str(e))
            print("[DATA_PROCESSING THREAD] Failed to filter points!")
            sys.exit(1)

        # calculate statistics
        try:

            electrospray_processing.calculate_filter(a, b, electrospray_data.data)

            electrospray_processing.calculate_fft_raw(electrospray_data.data)

            electrospray_processing.calculate_statistics(electrospray_data.data)

            electrospray_processing_freq, electrospray_processing_psd = electrospray_processing.calculate_power_spectral_density(
                electrospray_data.data)

            max_data, quantity_max_data, percentage_max = electrospray_processing.calculate_peaks_signal(
                electrospray_data.data)

            max_fft_peaks, cont_max_fft_peaks = electrospray_processing.calculate_peaks_fft(electrospray_data.data)

        except Exception as e:
            print("ERROR: ", str(e))
            print("[DATA_PROCESSING THREAD] Failed to process data")

        # Validation through the Chen_Pui Article
        try:
            electrospray_validation.calculate_scaling_laws_cone_jet(electrospray_data.data,
                                                                    electrospray_processing.mean_value,
                                                                    electrospray_data.flow_rate)
            # print("alpha:", electrospray_validation.alpha_chen_pui * 10e10)

        except Exception as e:
            print("ERROR: ", str(e))
            print("[DATA_PROCESSING THREAD] Failed to electrospray_validation")

        # call automatic classification function
        try:

            # if change flowrate restart conejet mean values
            if (electrospray_data.flow_rate != previous_flowrate):
                previous_flowrate = electrospray_data.flow_rate

            classification_txt = electrospray_classification.do_classification(
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
                electrospray_validation.I_emitted_chen_pui
            )

            generalist_machine_learning_classification_txt = electrospray_classification.do_generalist_ml_classification(
                generalist_clf_model,
                electrospray_processing.mean_value,
                electrospray_processing.variance,
                electrospray_processing.stddev,
                electrospray_processing.med,
                electrospray_processing.rms,
                electrospray_data.voltage,
                electrospray_data.flow_rate
            )

            machine_learning_classification_txt = electrospray_classification.do_ml_classification(
                clf_model,
                electrospray_processing.mean_value,
                electrospray_processing.variance,
                electrospray_processing.stddev,
                electrospray_processing.med,
                electrospray_processing.rms,
                electrospray_data.voltage,
                electrospray_data.flow_rate,
                electrospray_data.temperature,
                electrospray_data.humidity
            )

            neural_network_classification_txt = electrospray_classification.do_nn_classification(
                nn_model,
                electrospray_processing.mean_value,
                electrospray_processing.variance,
                electrospray_processing.stddev,
                electrospray_processing.med,
                electrospray_processing.rms,
                electrospray_data.voltage,
                electrospray_data.flow_rate,
                electrospray_data.temperature,
                electrospray_data.humidity
            )

        except Exception as e:
            print("ERROR: ", str(e))
            print("[DATA_PROCESSING THREAD] Failed to classify")
            sys.exit(1)

        # update current classification and put values on the saving and controller feedback queues
        try:

            current_shape = classification_txt,

            generalist_ml_current_shape = generalist_machine_learning_classification_txt,

            ml_current_shape = machine_learning_classification_txt,

            nn_current_shape = neural_network_classification_txt,

            feedback_queue.put(classification_txt)

            electrospray_processing.set_shape(current_shape)

            electrospray_processing.set_generalist_ml_shape(generalist_ml_current_shape)

            electrospray_processing.set_ml_shape(ml_current_shape)

            electrospray_processing.set_nn_shape(nn_current_shape)

            txt_max_peaks = " Max: " + str(max_data) + " Quantity max: " + str(
                quantity_max_data) + " Percentage: " + str(percentage_max)

            electrospray_processing.calculate_fft_filtered()
            electrospray_processing.calculate_fft_peaks()

            # put values in the saving queue
            save_message = [electrospray_data.get_measurements_dictionary(),
                            electrospray_processing.get_statistics_dictionary()]
            save_data_queue.put(save_message)

            sample += 1

            print(f"[DATA_PROCESSING THREAD] data sample \f{sample} is classified as: ", classification_txt)

            print(f"[DATA_PROCESSING THREAD - GENERALIST ML MODEL] data sample \f{sample} is classified as: ",
                  generalist_machine_learning_classification_txt)

            print(f"[DATA_PROCESSING THREAD - ML MODEL] data sample \f{sample} is classified as: ",
                  machine_learning_classification_txt)

            print(f"[DATA_PROCESSING THREAD - NN Classification] data sample \f{sample} is classified as: ",
                  neural_network_classification_txt)

        except Exception as e:
            print("ERROR: ", str(e))
            print("[DATA_PROCESSING THREAD] Failed to put value in save_data_queue")

        # put values in the plotting queue
        try:
            if (plot_real_time):
                message = [electrospray_data, datapoints_filtered, time_step, electrospray_processing,
                           classification_txt, txt_max_peaks]
                plotting_data_queue.put(message)
            # print(f"[DATA_PROCESSING THREAD] put data sample \f{sample} in plotting_data_queue")

        except Exception as e:
            print("ERROR: ", str(e))
            print("[DATA_PROCESSING THREAD] Failed to put value in plotting queue")

    print("[DATA_PROCESSING THREAD] Finish Processing data")
