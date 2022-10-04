import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision 
from influxdb_client.client.write_api import SYNCHRONOUS



sample.data(set: "airSensor")