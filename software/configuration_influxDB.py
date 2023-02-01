"""
TITLE: Code for testing Influx database usage with grafana GUI
AUTHOR: 乔昂  @jueta
DATE: 21/10/2022
FRAMEWORK: influxDB v2
"""

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import numpy as np
import datetime
import time


# *************************************
#       DATABASE CONFIGURATION
# *************************************

# token = os.environ.get("INFLUXDB_TOKEN")
token = "X0wU2OIZbscp32eFh2fFfV83RKKd4hDV27wtj8OlRfBE7wm0scW1ntb63FleGF55a7es4IP3FFQ35ZsqFzLzRg=="
print(token)
org = "jpmm2209@gmail.com"
url = "https://europe-west1-1.gcp.cloud2.influxdata.com"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

bucket = "test2"

write_api = client.write_api(write_options=SYNCHRONOUS)


# *************************************
#      			 FUNCTIONS
# *************************************

# Logs the data to your InfluxDB
def send_to_influxdb(id, mean, std, voltage_PS, timestamp, classification, temperature, humidity):
    
    json_body = [
        {"measurement": "HighVoltage",
         "tags": {
             "classification": classification,
        },
         "time": timestamp,
         "fields": {
             "running_id": id,
             "std_current": std,
             "voltage_PS": voltage_PS,
             "temperature": temperature,
             "humidity": humidity
        }
        }
    ]
    try:
        write_api.write(bucket='test2', record=json_body)
        print("JSON Sent!")
    except Exception as e:
            print("ERROR: ", str(e)) 
        print("Package Lost!")  


# *************************************
#      	MAIN for testing purpose
# *************************************


# def main():


#     for i in range(100):
#         send_to_influxdb(
#             id='01',
#             mean= 1 + 1 * np.random.random(),
#             std= 1 + 2 * np.random.random(),
#             voltage_PS= 5 + 5 * np.random.random(),
#             timestamp=datetime.datetime.utcnow(),
#             classification=np.random.randint(0,5),
#             temperature=20 + 10 * np.random.random(),
#             humidity=80 + 20 * np.random.random()
#         )
#         time.sleep(0.5)



# if __name__ == "__main__":
#     main()

