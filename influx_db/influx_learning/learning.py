import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


#*******************
#    Connecting
#*******************

# OBS: we need to reconfigure the token later. 
# It is in the import files of the os library in INFLUXDB_TOKEN variable.

token = os.environ.get("INFLUXDB_TOKEN")
org = "jpmm2209@gmail.com"
url = "https://europe-west1-1.gcp.cloud2.influxdata.com"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

bucket="test"


#*******************
#     Writing
#*******************

write_api = client.write_api(write_options=SYNCHRONOUS)
   
for value in range(5):
  point = (
    Point("measurement1")
    .tag("tagname1", "tagvalue1")
    .field("field1", value)
  )
  write_api.write(bucket=bucket, org="jpmm2209@gmail.com", record=point)
  time.sleep(1) # separate points by 1 second


#*******************
#     Reading
#*******************

query_api = client.query_api()

query = """from(bucket: "test")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "measurement1")
  |> mean()"""
tables = query_api.query(query, org="jpmm2209@gmail.com")

for table in tables:
    for record in table.records:
        print(record)