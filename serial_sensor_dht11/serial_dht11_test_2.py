#############################################
#    Retrieving the data from a DHT sensor
#    connected to an Arduino Uno board
# by A.LINA June 2014
#############################################

import os
import re
import matplotlib.pyplot as plt
import threading as thr
import serial as srl
import time

ArduinoPort = "/dev/tty.usbmodem1451"
ArduinoSerial = None
DataTime = None
ArduinoDataH = None
ArduinoDataT = None


def InitSerial():
    global ArduinoSerial

    ArduinoSerial = srl.Serial(ArduinoPort,
                               baudrate=9600,
                               bytesize=srl.EIGHTBITS,
                               parity=srl.PARITY_NONE,
                               stopbits=srl.STOPBITS_ONE,
                               timeout=2,
                               xonxoff=0,
                               rtscts=0)

    time.sleep(2)
    ArduinoSerial.baudrate = 9600
    print("Open serial communication with Arduino")
    print(ArduinoSerial)
    print("======================================")
    return ArduinoSerial.isOpen()


def SetSamplingRate(SamplingRate):
    if (ArduinoSerial.isOpen()):
        ArduinoSerial.readline()
        temp = str(20000 + SamplingRate);
        ArduinoSerial.write(temp.encode('utf-8'))


def StartSendData():
    if (ArduinoSerial.isOpen()):
        ArduinoSerial.readline()
        temp = str(10001);
        ArduinoSerial.write(temp.encode('utf-8'))


def StopSendData():
    if (ArduinoSerial.isOpen()):
        ArduinoSerial.readline()
        temp = str(10000);
        ArduinoSerial.write(temp.encode('utf-8'))


def GetData(DurationSec):
    global ArduinoDataH, ArduinoDataT, DataTime

    DataTime = []
    ArduinoDataH = []
    ArduinoDataT = []
    Inc = 0

    InitTime = time.time()

    # dummy read to flush the port
    ArduinoSerial.readline()

    while ((time.time() - InitTime) < DurationSec):
        print
        str(Inc) + " " + str(ArduinoSerial.isOpen()) + " " + str(time.time() - InitTime)
        data = str(ArduinoSerial.readline())
        parse_data = re.match(r"DHT:H ([-]{0,1}\d+) T ([-]{0,1}\d+)", data)
        if (parse_data != None):
            if (len(parse_data.groups()) == 2):
                print
                "ADD"
                Humidity = int(parse_data.group(1))
                Temperature = int(parse_data.group(2))
                DataTime.append(time.time() - InitTime)
                ArduinoDataH.append(float(Humidity / 1024.0))
                ArduinoDataT.append(float(Temperature / 1024.0))
        Inc += 1

    print("END:" + str(ArduinoSerial.isOpen()) + " " + str(time.time() - InitTime))


def PlotData():
    plt.title("Arduino DHT data")

    plt.subplot(2, 1, 1, axisbg='y')
    plt.plot(DataTime[1:], ArduinoDataT[1:], 'r-', DataTime[1:], ArduinoDataT[1:], 'go')
    plt.xlabel('time (iter)')
    plt.ylabel('Temperature')

    plt.subplot(2, 1, 2, axisbg='y')
    plt.plot(DataTime[1:], ArduinoDataH[1:], 'r-', DataTime[1:], ArduinoDataH[1:], 'go')
    plt.xlabel('time (iter)')
    plt.ylabel('Humidity')

    plt.show(block=False)


def MainArduino(SamplingRate, DurationSec):
    if (InitSerial() == True):
        time.sleep(3)
        SetSamplingRate(SamplingRate)
        time.sleep(3)
        StartSendData()
        time.sleep(3)
        GetData(DurationSec)
        time.sleep(3)
        StopSendData()
        time.sleep(3)
        PlotData()
    ArduinoSerial.close()


##################################
# Arduino sample code
#
'''

#include <dht.h>

/*
Retrieve DHT data (temp, humidity)
A.LINA 
*/

/*-----( Declare objects )-----*/
dht DHT_sensor;

/*-----( Declare Constants, Pin Numbers )-----*/
#define DHT_PIN 2
#define SAMPLING_RATE 500 //ms

/*--(start setup )---*/
void setup()
  {
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
    }
  Serial.println("DHT SENSOR");
  Serial.println();
  }
/*--(end setup )---*/

/*--(start loop )---*/
void loop()
  {
  Serial.println("\n");

  int chk = DHT_sensor.read11(DHT_PIN);

  if(chk==0)
    {
    String str = "DHT:";
    long   val;

    str += "H ";
    val = (long)(DHT_sensor.humidity*1024+0.5);
    str += val;
    str += " T ";
    val = (long)(DHT_sensor.temperature*1024+0.5);
    str += val;

    Serial.println(str);
    Serial.flush();
    delay(20);
    }
  else
    {
    Serial.println("DHT_Error");
    }

  delay(SAMPLING_RATE);
  }
/* --(end main loop )-- */


'''
