import Adafruit_DHT
import time
from py7seg import Py7Seg #
xxx

ps = Py7Seg() # xxx
SENSOR_TYPE = Adafruit_DHT.DHT11
P_DHT = 4 # GPIO numbering (Pin # 7)
while True:
    hum, temp = Adafruit_DHT.read_retry(SENSOR_TYPE, P_DHT)
    if temp == None:
        t = "--.-"
    else:
        t = "%2.1f" %temp
    if hum == None:
        h = "--.-"
    else:
        h = "%2.1f" %hum
    print("Temperature", t, "Humitity", h)
    ps.showText("t" + t[0] + t[1] + t[3], dp = [1, 0, 0]) # xxx
    time.sleep(3)
    ps.showText("h" + h[0] + h[1] + h[3], dp = [1, 0])