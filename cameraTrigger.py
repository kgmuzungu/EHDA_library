#  *************************************
# 	Camera trigger send code for arduino
# 	AUTHOR: 乔昂
# 	DATE: 26/10/2022
#  *************************************

import serial.tools.list_ports
import time


def activateTrigger(com_port_idx):
    # Function to trigger Photron PFV4 with arduino Hardware Trigger INPUT
    # This functions needs at least 3 seconds in between each use so that the communication with arduino works.

    n_camera_partitions = 10
    time_between_videos  = 10 #    minimum 3


    com_ports = list(serial.tools.list_ports.comports())
    com_port = serial.Serial(
        port=com_ports[com_port_idx].device,
        baudrate=9600,
        timeout=0.1
    )

    # # get number of available COM ports
    # no_com_ports = len(com_ports)
    #
    # if no_com_ports > 0:
    #     print("Total no. of available COM ports: " + str(no_com_ports))
    #     # show all available COM ports
    #     for idx, curr in enumerate(com_ports):
    #         print("  " + str(idx) + ".)  " + curr.description)
    #
    #     if com_port_idx > no_com_ports or com_port_idx < 0:
    #         print("Incorrect value for COM port! Enter a Number (0 - " + str(no_com_ports - 1) + ")")
    #         return None
    #
    #

    if com_port.is_open:
        print("Arduino Port: " + com_ports[com_port_idx].device)
        print("Arduino Camera Trigger Connected!")
    else:
        print("ERROR: Communication to Arduino/camera failed!")

    for i in range(0, n_camera_partitions + 1):

        if com_port.is_open:
            com_port.flushInput()
            com_port.flushOutput()
            time.sleep(1)
            print("Camera Trigger", i)
            com_port.write(bytes('1', 'utf-8'))
            time.sleep(2)
            # Fazer algoritmo de checar response
            response = com_port.readline()
            print(response.decode())
        else:
            print("ERROR: Communication to Arduino/camera failed!")

        print()

        # fazer algoritmo para determinar frequencia do envio de sinal
        time.sleep(time_between_videos - 3)


            

# Test
# activateTrigger(0)

