import time
import serial
import sys
import RPi.GPIO as GPIO

SERIAL_PORT ="/dev/ttyS0"

ser = serial.Serial (SERIAL_PORT, baudrate = 9600, timeout=5)
ser.write("AT")
print("dialing")
time.sleep(10)
ser.write("ATD9443680313;\r ")
print("dialing")
time.sleep(10)
ser.write("ATH\r ")
