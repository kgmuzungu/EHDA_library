#  *************************************
# 	Code for connect to arduino and send a analog signal trigger to make camera start reccording
# 	AUTHOR: 乔昂
# 	DATE: 26/10/2022
#  *************************************

import serial.tools.list_ports
import time


def activateTrigger(com_port_idx,finish_event, typeofmeasurement, number_camera_partitions):
    # Function to trigger Photron PFV4 with arduino Hardware Trigger INPUT
    # This functions needs at least 3 seconds in between each use so that the communication with arduino works.


    time_between_videos  = ((typeofmeasurement['voltage_stop'] - typeofmeasurement['voltage_start']) / typeofmeasurement['step_size']) * typeofmeasurement['step_time'] / number_camera_partitions

    print("[CAMERA THREAD] Time Between Videos: ", time_between_videos)


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
        print("[CAMERA THREAD] Arduino Port: " + com_ports[com_port_idx].device)
        print("[CAMERA THREAD] Arduino Camera Trigger Connected!")
    else:
        print("[CAMERA THREAD] ERROR: Communication to Arduino/camera failed!")

    #  THREAD LOOP
    i = 1
    for i in range(0, number_camera_partitions + 1):

        if com_port.is_open:
            com_port.flushInput()
            com_port.flushOutput()
            time.sleep(1)
            print("[CAMERA THREAD] Camera Trigger", i)
            com_port.write(bytes('1', 'utf-8'))
            time.sleep(2)
            # Fazer algoritmo de checar response
            response = com_port.readline()
            # print(response.decode())
            i += 1
        else:
            print("[CAMERA THREAD] ERROR: Communication to Arduino/camera failed!")

        # print()

        # fazer algoritmo para determinar frequencia do envio de sinal
        time.sleep(time_between_videos - 3)

    while not finish_event.is_set():
        time.sleep(3)

            

# Test
# activateTrigger(0)

