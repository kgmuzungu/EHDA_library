#  *************************************
# 	Camera trigger send code for arduino
# 	AUTHOR: 乔昂
# 	DATE: 26/10/2022
#  *************************************

import serial.tools.list_ports
import time


def activateTrigger(com_port_idx):
    # Function to trigger Photron PFV4 with arduino Hardware Trigger INPUT
    # This functions needs 3 seconds in between each use so that the communication with arduino works.

    com_ports = list(serial.tools.list_ports.comports())
    no_com_ports = len(com_ports)

    if no_com_ports > 0:
        print("Total no. of available COM ports: " + str(no_com_ports))
        for idx, curr in enumerate(com_ports):
            print("  " + str(idx) + ".)  " + curr.description)

        if com_port_idx > no_com_ports or com_port_idx < 0:
            print("Incorrect value for COM port! Enter a Number (0 - " +
                  str(no_com_ports - 1) + ")")
            return None

        com_port = serial.Serial(
            port=com_ports[com_port_idx].device,  
            baudrate=9600,
            timeout=0.1
        )

        for i in range(10):
            if com_port.is_open:
                com_port.flushInput()
                com_port.flushOutput()
                time.sleep(2)
                print("Arduino Port: " + com_ports[com_port_idx].device)
                print("Arduino Camera Trigger Connected!")
                com_port.write(bytes('5', 'utf-8'))
                time.sleep(1)
                # Fazer algoritmo de checar response
                response = com_port.readline()
                print(response)
            else:
                print("ERROR: Communication to camera failed!")
            time.sleep(10)
            


# Test
# activateTrigger(2)

