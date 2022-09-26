#!/usr/bin/env python3

import datetime
from influxdb import InfluxDBClient
import numpy as np

# todo: separate this func sync to the send
def connect_send_to_influxdb_allsignal(id, mean, std, voltage_PS, timestamp, classification, datapoints, temperature, humidity):
    # sync InfluxDB

    host = 'localhost'  # Change this as necessary
    # port = 25826
    port = 8086
    username = 'admin'  # Change this as necessary
    password = 'admin1234'  # Change this as necessary
    db = 'testdb'  # Change this as necessary

    # InfluxDB client to write to

    client = InfluxDBClient(host, port)
    client = InfluxDBClient(host, port, username, password)
    client.switch_database(db)

    json_body = [
        {"measurement": "tiepie-rpi",
         "tags": {
             "classification": classification,
         },
         "time": timestamp,
         "fields": {
             "current_signal": id,
             "std_current": std,
             "mean_current": mean,
             "voltage_PS": voltage_PS,
             "datapoints": datapoints,
             "temperature": temperature,
             "humidity": humidity
         }
         }
    ]
    client.write_points(json_body)
    #return json_body

"""

for i in range(10):
    measurement = i
    var = np.random.randint(100, size=100)
    mean_val = np.mean(var)
    std_val = np.std(var)
    voltage_PS_val = int(np.random.randint(10000, size=1))
    timestamp_val = datetime.datetime.utcnow()
    class_val = possible_class[int(np.random.randint(low=0, high=3, size=1))]
    temperature_val = 10 * np.random.random()
    humidity_val = 20 * np.random.random()
    # send_to_influxdb(i, mean_val, std_val, voltage_PS_val, timestamp_val, class_val, temperature_val, humidity_val)
    send_to_influxdb(i, mean_val, std_val, voltage_PS_val, timestamp_val, class_val, temperature_val, humidity_val)
"""
