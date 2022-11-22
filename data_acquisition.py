import numpy as np
import libtiepie
from configuration_FUG import *
import configuration_tiepie
from time import gmtime, strftime
from electrospray import ElectrosprayMeasurements

# tiepie params
sampling_frequency = 1e5  # 100 KHz
multiplier_for_nA = 500



append_array_data = True
FLAG_PLOT = False
SAVE_DATA = True
SAVE_PROCESSING = False
SAVE_CONFIG = True
SAVE_JSON = True


def data_acquisition(data_queue,
                     fug_queue,
                     finish_event,
                     voltage_start,
                     liquid,
                     array_electrospray_measurements,
                     Q
                     ):


    temperature = 10
    humidity = 10
    day_measurement = strftime("%a_%d %b %Y", gmtime())

    #           OSCILLOSCOPE
    # print_library_info()
    time_step = 1 / sampling_frequency
    libtiepie.network.auto_detect_enabled = True  # Enable network search
    libtiepie.device_list.update()  # Search for devices
    scp = None
    for item in libtiepie.device_list:
        # Try to open an oscilloscope with block measurement support
        if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):
            scp = item.open_oscilloscope()
        else:
            print('[DATA_ACQUISITION THREAD] No oscilloscope available with block measurement support!')
            sys.exit(1)
    print('[DATA_ACQUISITION THREAD] Oscilloscope initialized!')

    try:
        scp = configuration_tiepie.config_TiePieScope(scp, sampling_frequency)
        # print_device_info(scp)
    except:
        print("[DATA_ACQUISITION THREAD] Failed to config tie pie!")
        sys.exit(1)

    print("[DATA_ACQUISITION THREAD] No values in the fug_queue yet")
    while fug_queue.empty():
        time.sleep(0.1)

    voltage_from_PS = voltage_start
    sample = 0

    #  THREAD LOOP
    while not finish_event.is_set():

        try:
            if not fug_queue.empty():
                fug_values = fug_queue.get()
                voltage_from_PS, current_from_PS = fug_values


            print('[DATA_ACQUISITION THREAD] got fug_queue data')

        except:
            print("[DATA_ACQUISITION THREAD] Failed to get FUG values!")
            sys.exit(1)

        try:

            scp.start()
            # Wait for measurement to complete:
            while not scp.is_data_ready:
                time.sleep(0.05)  # 50 ms delay, to save CPU time

            data = scp.get_data()
            print('[DATA_ACQUISITION THREAD] got tiepie data')

        except:
            print("[DATA_ACQUISITION THREAD] Failed to get tiePie values!")
            sys.exit(1)

        try:

            #  1Mohm input resistance when in single ended input mode
            # 2Mohm default input resistance
            datapoints = np.array(data[0]) * multiplier_for_nA

        except:
            print("[DATA_ACQUISITION THREAD] Failed to create datapoints!")
            sys.exit(1)

        try:

            electrospray_data = ElectrosprayMeasurements(liquid, datapoints, voltage_from_PS, Q, temperature,
                                                         humidity, day_measurement, current_from_PS)

        except:
            print("[DATA_ACQUISITION THREAD] Failed to EsctrosprayMeasurements")
            sys.exit(1)

        try:

            if append_array_data:
                d_electrospray_measurements = electrospray_data.get_measurements_dictionary()
                array_electrospray_measurements.append(d_electrospray_measurements)

        except:
            print("[DATA_ACQUISITION THREAD] Failed to append array")
            sys.exit(1)

        try:

            # put values in the queue
            data_queue.put(electrospray_data)

            sample += 1

            print(f"[DATA_ACQUISITION THREAD] put data sample \f{sample} in data_queue")


        except:
            print("[DATA_ACQUISITION THREAD] Failed to put values on data_queue")
            sys.exit(1)

    print("[DATA_ACQUISITION THREAD] Finish acquirind data")
