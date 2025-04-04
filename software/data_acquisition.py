
"""
TITLE: data acquisistion thread function
AUTHOR: 乔昂  @jueta
DATE: 21/10/2022
"""

import numpy as np
import libtiepie
from FUG_functions import *
import configuration_tiepie
from time import gmtime, strftime
from electrospray import ElectrosprayMeasurements
from datetime import datetime

# tiepie params
sampling_frequency = 1e5  # 100 KHz
multiplier_for_nA = 500


def data_acquisition(data_queue,
                     controller_output_queue,
                     finish_event,
                     typeofmeasurement,
                     liquid,
                     arduino_COM_port
                     ):
    
    #  *************************************
    # 	Initiate sensors
    #  *************************************

    #           TEMPERATURE AND HUMIDITY
    temperature = 0
    humidity = 0
    day_measurement = datetime.now()
    arduino_responses = []

    com_ports = list(serial.tools.list_ports.comports())
    arduino_port = serial.Serial(
        port=com_ports[arduino_COM_port].device,
        baudrate=9600,
        timeout=0.1
    )
    arduino_port.write(bytes('1', 'utf-8'))

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
            print(
                '[DATA_ACQUISITION THREAD] No oscilloscope available with block measurement support!')
            sys.exit(1)

    try:
        scp = configuration_tiepie.config_TiePieScope(scp, sampling_frequency)
        # print_device_info(scp)
        print('[DATA_ACQUISITION THREAD] Oscilloscope initialized!')
    except Exception as e:
        print("ERROR: ", str(e))
        print("[DATA_ACQUISITION THREAD] Failed to config tie pie!")
        sys.exit(1)

    # print("[DATA_ACQUISITION THREAD] No values in the controller_output_queue yet")
    while controller_output_queue.empty():
        time.sleep(0.1)

    voltage_from_PS = typeofmeasurement['voltage_start']
    flow_rate = typeofmeasurement['flow_rate']
    sample = 0


    #  *************************************
    #  thread main loop
    #  *************************************

    print("[DATA_ACQUISITION THREAD] Starting Saving loop")
    while not finish_event.is_set():

        # try to get values from queue
        try:
            if not controller_output_queue.empty():
                controller_output = controller_output_queue.get()
                voltage_from_PS, current_from_PS, target_voltage, flow_rate = controller_output

            # print('[DATA_ACQUISITION THREAD] got controller_output_queue data')

        except Exception as e:
            print("ERROR: ", str(e))
            print("[DATA_ACQUISITION THREAD] Failed to get controller_output_queue!")
            sys.exit(1)

        # try to get values from oscilloscope
        try:

            scp.start()
            # Wait for measurement to complete:
            while not scp.is_data_ready:
                time.sleep(0.05)  # 50 ms delay, to save CPU time

            data = scp.get_data()
            day_measurement = datetime.now()
            # print('[DATA_ACQUISITION THREAD] got tiepie data')

        except Exception as e:
            print("ERROR: ", str(e))
            print("[DATA_ACQUISITION THREAD] Failed to get tiePie values!")

        # try to get values from temperature and humidity sensors (arduino code is in software/literature/peripherals/Arduino_DHT11)
        try:

            if arduino_port.in_waiting > 0:
                response = arduino_port.readline()
                val1, val2 = response.decode("utf-8").split("-")
                if (val1 == "temp"):
                    temperature = float(val2)
                    # print("temperature: ", temperature)
                elif (val1 == "humy"):
                    humidity = float(val2)
                    # print("humidity: ", humidity)

        except Exception as e:
            print("ERROR: ", str(e))
            print("[DATA_ACQUISITION THREAD] Failed to get Humidity and Temperature!")

        # adjust gain of input depending on the oscilloscope internal impedance being used
        try:

            #  1Mohm input resistance when in single ended input mode
            # 2Mohm default input resistance
            datapoints = np.array(data[0]) * multiplier_for_nA

        except Exception as e:
            print("ERROR: ", str(e))
            print("[DATA_ACQUISITION THREAD] Failed to create datapoints!")
            sys.exit(1)

        # Set all the measurements in the object electrospray_data
        try:

            electrospray_data = ElectrosprayMeasurements(liquid, datapoints, voltage_from_PS, flow_rate, temperature,
                                                         humidity, day_measurement, current_from_PS, target_voltage)

            print("\n ------------------------------- \n")
            # print(f"    temperature:\f{temperature}    Humidity:\f{humidity}\n    voltage:\f{voltage_from_PS}    Flow Rate:\f{flow_rate} uL/min")
            print(f"voltage:\f{voltage_from_PS} V   Flow Rate:\f{flow_rate} uL/min")

        except Exception as e:
            print("ERROR: ", str(e))
            print("[DATA_ACQUISITION THREAD] Failed to ElectrosprayMeasurements")
            sys.exit(1)

        # put values on the next queue
        try:

            # put values in the queue
            data_queue.put(electrospray_data)

            sample += 1

            # print(f"[DATA_ACQUISITION THREAD] put data sample \f{sample} in data_queue")

        except Exception as e:
            print("ERROR: ", str(e))
            print("[DATA_ACQUISITION THREAD] Failed to put values on data_queue")
            sys.exit(1)

    print("[DATA_ACQUISITION THREAD] Finish acquiring data")
