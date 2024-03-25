# OscilloscopeBlock.py
#
# This example performs a block mode measurement and writes the data to OscilloscopeBlock.csv.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
import time
import os
import sys
import libtiepie
from printinfo import *
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.animation as animation
import numpy as np
from datetime import datetime
from scipy.signal import butter, lfilter
from threading import Thread
from threading import Condition, Lock
import json


# matplotlib.use('Qt5Agg')


def animate2(i, data):
    axs[0].clear()

    # axs[0].plot(data[0:i, 0], data[0:i, 1])
    # https://www.geeksforgeeks.org/using-matplotlib-for-animations/
    # axs[0].plot(np.arange(0, len(datapoints), 1), datapoints)
    # axs[0].grid()


def connection_wifi_tiepie():
    # scan available Wifi networks
    os.system('cmd /c "netsh wlan show networks"')

    # input Wifi name
    name_of_router = str('TiePie-WS6D-37427')

    try:
        # connect to the given wifi network
        os.system(f'''cmd /c "netsh wlan connect name={name_of_router}"''')
    except KeyboardInterrupt as e:
        print("\nExiting...")


if __name__ == "__main__":
    # connection_wifi()
    sampling_frequency = 1e5

    # Print library info:
    print_library_info()

    # Enable network search:
    libtiepie.network.auto_detect_enabled = True

    # Search for devices:
    libtiepie.device_list.update()

    # lock = threading.RLock()
    # condition = Condition()
    # condition.acquire()  # da a chave para essa thread
    # try:

    """
    if len(libtiepie.device_list) > 0:
        print()
        print('Available devices:')

        for item in libtiepie.device_list:
            print('  Name: ' + item.name)
            print('    Serial number  : ' + str(item.serial_number))
            print('    Available types: ' + libtiepie.device_type_str(item.types))
    else:
        print('No devices found!')"""

    # finally:
        # condition.release()  # tira a chave para essa thread """

    while True:
        # Try to open an oscilloscope with block measurement support:
        scp = None
        for item in libtiepie.device_list:
            print("can open: " + str(item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE)))
            if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):
                scp = item.open_oscilloscope()
                """if scp.measure_modes & libtiepie.MM_BLOCK:
                    break
                else:
                    scp = None"""
        if scp:
            try:
                # Set measure mode:
                scp.measure_mode = libtiepie.MM_BLOCK

                # Set sample frequency:
                scp.sample_frequency = sampling_frequency

                # Set record length:
                scp.record_length = 50000  # 50000 samples
                # every 10 micro seconds

                # Set pre sample ratio:
                scp.pre_sample_ratio = 0  # 0 %

                # For 1 channel:
                scp.channels[1].enabled = True
                scp.channels[1].range = 8  # in V
                scp.channels[1].coupling = libtiepie.CK_DCV
                scp.channels[1].trigger.enabled = True
                scp.channels[1].trigger.kind = libtiepie.TK_RISINGEDGE
                scp.channels[0].enabled = False
                scp.channels[2].enabled = False
                scp.channels[3].enabled = False

                # Setup channel trigger:
                ch = scp.channels[1]  # Ch 1
                # Enable trigger source:
                ch.trigger.enabled = True

                ch.safe_ground_enabled = True

                # Kind:
                ch.trigger.kind = libtiepie.TK_RISINGEDGE  # Rising edge

                # Level:
                ch.trigger.levels[0] = 0.5  # 50 %

                # Hysteresis:
                ch.trigger.hystereses[0] = 0.05  # 5 %

                # Set trigger timeout:
                scp.trigger_time_out = 100e-3  # 100 ms

                # Print oscilloscope info:
                print_device_info(scp)

                # Start measurement:
                scp.start()

                # Wait for measurement to complete:
                while not scp.is_data_ready:
                    time.sleep(0.050)  # 50 ms delay, to save CPU time

                # Get data:
                print(f"SAFEGROUNDS: {ch.safe_ground_enabled}")
                data = scp.get_data()
                time_now = datetime.now()
                datapoints = np.array(data[1]) * 1000

                # low pass filter to flatten out noise
                cutoff_freq_normalized = 3000 / (0.5 * sampling_frequency)  # in Hz
                b, a = butter(6, Wn=cutoff_freq_normalized, btype='low',
                              analog=False)  # first argument is the order of the filter
                datapoints_filtered = lfilter(b, a, datapoints)
                # check here to plot the transfer function of the filter
                # https://stackoverflow.com/questions/25191620/creating-lowpass-filter-in-scipy-understanding-methods-and-units


                mean_value = np.mean(datapoints)
                std_dev = np.std(datapoints) # standard deviation
                med = np.median(datapoints)  # mediana


                inf = np.percentile(datapoints, 2.5)
                sup = np.percentile(datapoints, 97.5)
                #   Range = Highest_value – Lowest_value
                data_max = max(datapoints)
                data_min = min(datapoints)
                rang = data_max - data_min
                rang_confidence = sup - inf

                print("mean=%f ; std=%f ; std/mean=%f ; mean-median=%f; avarage development-relaxation ratios " % (mean_value, std_dev, std_dev/mean_value, mean_value/med))

                dictionary = {
                    "name": item.name,
                    "serial no": str(item.serial_number),
                    "Available types:": libtiepie.device_type_str(item.types)
                }
                """
                Here is the syntax for adding a new value to a dictionary:
                """
                # a = np.arange(1).reshape(1,1)
                # nested_list_data = datapoints.tolist()
                # dictionary["current"] = datapoints
                # Serializing json
                json_object = json.dumps(dictionary, indent = 4)

                # Writing to sample.json
                with open("sample.json", "w") as outfile:
                    outfile.write(json_object)

                fig, axs = plt.subplots(2)

                axs[0].plot(np.arange(0, len(datapoints), 1), datapoints)
                axs[0].set(xlabel='data points', ylabel='data')
                axs[0].grid()

                ani = animation.FuncAnimation(fig, animate2, frames=range(1, len(datapoints)), fargs=(datapoints, ), interval=1000)
                ani.save('animation.gif', writer='imagemagick', fps=1)
                # TypeError: 'NoneType' object is not subscriptable

                axs[1].plot(np.arange(0, len(datapoints_filtered), 1), datapoints_filtered)
                axs[1].set(xlabel='data points', ylabel='data')
                axs[1].grid()
                plt.show()
                current_time = datetime.now() - time_now
                print("time passed = " + str(current_time))
                # plt.hold(True)

                # Output CSV data:
                csv_file = open('OscilloscopeBlock.csv', 'w')
                try:
                    csv_file.write('Sample')
                    for i in range(len(data)):
                        csv_file.write(';Ch' + str(i + 1))
                    csv_file.write(os.linesep)
                    for i in range(len(data[1])):
                        csv_file.write(str(i))
                        for j in range(len(data)):
                            csv_file.write(';' + str(data[j][i]))
                        csv_file.write(os.linesep)

                    print()
                    print('Data written to: ' + csv_file.name)

                finally:
                    csv_file.close()

            except Exception as e:
                print('Exception: ' + e.message)
                # Close oscilloscope:
                del scp
                # sys.exit(1)
                time.sleep(1)

            # Close oscilloscope:
            del scp
            name_of_router = 'TP-Link_F0BA'
            try:
                # connect to the given wifi network
                os.system(f'''cmd /c "netsh wlan connect name={name_of_router}"''')
            except KeyboardInterrupt as e:
                print("\nExiting...")

        else:
            print('No oscilloscope available with block measurement support!')
            # connection_wifi_tiepie()
            # Close oscilloscope:
            del scp
            # sys.exit(1)
            time.sleep(1)


    """
    name_of_router = 'TP-Link_F0BA'
        try:
            # connect to the given wifi network
            os.system(f'''cmd /c "netsh wlan connect name={name_of_router}"''')
        except KeyboardInterrupt as e:
            print("\nExiting...")
    """
    # sys.exit(0)


    """
    # comparing absolute sample differential inequation "dy/dx < |(x - y)|"
    def dydx(x, y):
    #    print("\nRelative accuracy: abs((yApprox - yExact)/yExact)")
        dif = 0.00001
        if abs(x - y) < dif:
            return True
        else:
        else:
            return False
    """

    # name_of_router = 'TP-Link_F0BA'
    # name_of_router = 'TiePie-WS6D-37426'
    # password_of_router = '44716776'
