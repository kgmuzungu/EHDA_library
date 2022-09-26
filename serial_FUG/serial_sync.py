##
 # @file serial_com.py
 #
 # @author Birkmaier Thomas
 #
 # @version v0.00
 #
 # @par Development System
 # - Hardware: --
 # - IDE     : Microsoft Visual Studio Code
 #
 # @brief Example program to send commands using a COM Port.
 #
 # @details How to use this example:
 #  - Use this link to set up Visual Studio Code for Python:
 #    https://code.visualstudio.com/docs/python/python-tutorial
 #  - Use information provided by this link to install pySerial library
 #  - Run this Python script
 #  - Program shows you available COM ports
 #  - Choose the port you want to send commands to
 #  - Example command ">S0 10.00"
 #  - Device responds "#0 >S0:1.000000E+1"
 #  - Example command ">S0?"
 #  - Device responds "#1 >S0:0.000000E+00"
 #  - Type "exit" to exit the program
 #
 # @note This is just an example to show how to create a connection. Be aware
 # that This is not production ready code!
 #
 # @copyright
 # THIS DOCUMENT/MEDIA IS THE PERSONAL PROPERTY OF FuG GMBH
 # AND WAS CREATED AND COPYRIGHTED BY FuG GMBH IN 2018. ALL
 # RIGHTS TO ITS USE ARE RESERVED.  THIS  MATERIAL  MAY NOT BE USED,
 # COPIED OR DISCLOSED  TO ANY THIRD PARTY WITHOUT THE PRIOR WRITTEN
 # AGREEMENT OF FuG GMBH. (c) 2019 FuG GMBH.
 #
 ##

# package needed to list available COM ports
import serial.tools.list_ports

# package needed for sleep
import time


def FUG_initialize(com_port_idx):
    # print out user information
    # get available COM ports and store as list
    com_ports = list(serial.tools.list_ports.comports())
    # get number of available COM ports
    no_com_ports = len(com_ports)

    if no_com_ports > 0:
        print("Total no. of available COM ports: " + str(no_com_ports))
        # show all available COM ports
        for idx, curr in enumerate(com_ports):
            print("  " + str(idx) + ".)  " + curr.description)

        if com_port_idx > no_com_ports or com_port_idx < 0:
            print("Incorrect value for COM port! Enter a Number (0 - " + str(no_com_ports - 1) + ")")
            return None

        # configure the COM port to talk to. Default values: 115200,8,N,1
        com_port = serial.Serial(
            port=com_ports[com_port_idx].device,  # chosen COM port
            baudrate=115200,  # 115200
            bytesize=serial.EIGHTBITS,  # 8
            parity=serial.PARITY_NONE,  # N
            stopbits=serial.STOPBITS_ONE,  # 1
            timeout=0
        )
        if com_port.is_open:
            com_port.flushInput()
            com_port.flushOutput()
            print("Opened Port: " + com_ports[com_port_idx].device)
    return com_port


# cmd, list of commands expected
def FUG_sendcommands(com_port, cmd):
    # cmd = ['I 6e-4', 'S0R 250', 'U 5e3', 'F1']
    # cmd = ['I 6e-4', 'S0R 50', 'U 1e4']
    # cmd = ['F0'] turn it off
    # cmd = ['>M0?'] readback the actual voltage
    responses = []
    for command in cmd:
        print("cmd:" + command)
        com_port.write((command + '\r\n').encode())
        # send cmd to device # might not work with older devices -> "LF" only needed!
        time.sleep(0.1)  # small sleep for response
        response = ''
        while com_port.in_waiting > 0:
            response = com_port.readline()           # all characters received, read line till '\r\n'
        if response != '':
            responses.append(response.decode("utf-8"))
            print("<<: " + response.decode("utf-8"))  # decode bytes received to string
        else:
            responses.append('')
            print("<< Error, no Response!")
    return responses


def FUG_off():
    serial.Serial('COM8').close()

