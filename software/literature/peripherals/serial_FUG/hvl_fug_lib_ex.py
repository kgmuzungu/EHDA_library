#  Copyright (c) 2020-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Example script for the device FuG
"""

from time import sleep
import serial
from hvl_ccb.dev import FuG, FuGDigitalVal, FuGError



# create device object
hv = FuG({"port": "COM9"})

# start the device
hv.start(max_voltage=1e3, max_current=10e-3)

# give the device some time to apply hv.set_number_of_recordings()
# that was called during hv.start()
sleep(0.5)

# print the nominal voltage and current
print(
    f"This power supply can apply {hv.max_voltage_hardware} V "
    f"and {hv.max_current_hardware} A"
)
print(f"In this setup the limits are at {hv.max_voltage} V and {hv.max_current} A")


# apply a current limitation
hv.current = 3.5e-3

sleep(0.5)

# turn on the output
hv.on = FuGDigitalVal.YES
sleep(0.5)

# Try to apply a voltage which is to high
try:
    hv.voltage = 50000000
except FuGError:
    print(f"You can't set a voltage higher than {hv.max_voltage} V.")

# apply a (normal) voltage
setVoltage = 250
hv.voltage = setVoltage

sleep(0.5)  # give the device some time to apply the voltage

# check the set voltage
commandVoltage = hv.voltage.actualsetvalue

print("Charging...")

# measure the output voltage
max_n = 25
while hv.current_monitor.value >= 1e-3 and max_n >= 0:
    print(f"still charging: {hv.voltage_monitor.value} V")
    max_n -= 1
    sleep(1)


# print the result
print(
    f"I wanted to set {setVoltage} V, the command set {commandVoltage} V, "
    f"and I finally measured {hv.voltage_monitor.value} V"
)

# stop the device (this also turns off the output)
hv.stop()
