
import serial
import time

# make sure the 'COM#' is set according the Windows Device Manager
ser = serial.Serial('COM8', 115200, timeout=1)
time.sleep(2)

for i in range(50):
    line = ser.readline()   # read a byte
    if line:
        string = line.decode()  # convert the byte string to a unicode string
        num = int(string) # convert the unicode string to an int
        print(num)

ser.close()

# https://www.youtube.com/watch?v=KOig5ndq2ek&ab_channel=CytronTechnologies