# OscilloscopeBlock.py
#
# This example performs a block mode measurement and writes the data to OscilloscopeBlock.csv.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
import time
import _datetime
import os
import sys
import libtiepie
from printinfo import *
import numpy as np
import datetime
from influxdb import InfluxDBClient

def send_to_influxdb(measurement, mean, std, voltage_PS, timestamp, classification, temperature, humidity):
    json_body = [
        {"measurement": measurement,
         "tags": {
             "classification": classification,
         },
         "time": timestamp,
         "fields": {
             "std_current": std,
             "voltage_PS": voltage_PS,
             "temperature": temperature,
             "humidity": humidity
         }
         }
    ]

    payload = [{
        "mean_current": mean,

        "time and date": timestamp,
        "classification": classification,
        "sensor": {
            "temperature": temperature,
            "humidity": humidity
        }
    }]
    # client.write_points(payload)
    client.write_points(json_body)



# Print library info:
print_library_info()

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# Try to open an oscilloscope with block measurement support:
scp = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):
        scp = item.open_oscilloscope()
        """if scp.measure_modes & libtiepie.MM_BLOCK:
            break
        else:
            scp = None
        """

if scp:
    try:
        # Set measure mode:
        scp.measure_mode = libtiepie.MM_BLOCK

        # Set sample frequency:
        scp.sample_frequency = 1e5  # 1 MHz

        # Set record length:
        scp.record_length = 10000  # TODO: 50000 samples

        # Set pre sample ratio:
        scp.pre_sample_ratio = 0  # 0 %

        # For 1 channel:
        scp.channels[1].enabled = True
        scp.channels[1].range = 8  # in V
        scp.channels[1].coupling = libtiepie.CK_DCV # DC Volt
        scp.channels[1].trigger.enabled = True
        scp.channels[1].trigger.kind = libtiepie.TK_RISINGEDGE
        scp.channels[0].enabled = False
        scp.channels[2].enabled = False
        scp.channels[3].enabled = False

        # Setup channel trigger:
        ch = scp.channels[1]  # Ch 2
        # Enable trigger source:
        ch.trigger.enabled = True

        # Kind:
        ch.trigger.kind = libtiepie.TK_RISINGEDGE  # Rising edge

        # Level:
        ch.trigger.levels[1] = 0.5  # 50 %

        # Hysteresis:
        ch.trigger.hystereses[1] = 0.05  # 5 %
        # Set trigger timeout:
        scp.trigger_time_out = 100e-3  # 100 ms

        # Print oscilloscope info:
        print_device_info(scp)

        # Start measurement:
        scp.start()

        # Print oscilloscope info:
        print_device_info(scp)

        # Print oscilloscope info:
        print_device_info(scp)

        # Wait for measurement to complete:
        while not scp.is_data_ready:
            time.sleep(0.05)  # 50 ms delay, to save CPU time

        # Get data:
        data = scp.get_data()
        time_now = _datetime.date.today()
        datapoints = np.array(data[1]) * 1000
        possible_class = ['dripping', 'cone-jet', 'multi-jet']
        host = 'localhost'  # Change this as necessary
        # port = 25826
        port = 8086
        username = 'admin'  # Change this as necessary
        password = 'admin1234'  # Change this as necessary
        db = 'testdb'  # Change this as necessary

        # InfluxDB client to write to
        # client = InfluxDBClient(host, port, username, password, db)
        client = InfluxDBClient(host, port)
        client = InfluxDBClient(host, port, username, password)
        client.switch_database('testdb')
        for i in range(10):
            measurement = i
            mean_val = np.mean(datapoints)
            std_val = np.std(datapoints)
            voltage_PS_val = int(np.random.randint(10000, size=1))
            timestamp_val = datetime.datetime.utcnow()
            class_val = possible_class[int(np.random.randint(low=0, high=3, size=1))]
            temperature_val = 10 * np.random.random()
            humidity_val = 20 * np.random.random()
            # send_to_influxdb(i, mean_val, std_val, voltage_PS_val, timestamp_val, class_val, temperature_val, humidity_val)
            send_to_influxdb(i, mean_val, std_val, voltage_PS_val, timestamp_val, class_val, temperature_val,
                             humidity_val)

        # Output CSV data:
        csv_file = open('D:\OscilloscopeBlockCH1.csv', 'w')
        try:
            csv_file.write('Sample')
            # for i in range(len(data)):
            csv_file.write(';Ch' + str(1))
            csv_file.write(os.linesep)
            for i in range(len(data[0])):
                csv_file.write(str(i))
                # for j in range(len(data)):
                csv_file.write(';' + str(datapoints[i]))
                csv_file.write(os.linesep)

            print()
            print('Data written to: ' + csv_file.name)

        finally:
            csv_file.close()

    except Exception as e:
        print('Exception: ' + e.message)
        sys.exit(1)

    # Close oscilloscope:
    del scp

else:
    print('No oscilloscope available with block measurement support!')
    sys.exit(1)

sys.exit(0)