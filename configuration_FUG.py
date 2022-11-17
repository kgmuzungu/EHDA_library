
# package needed to list available COM ports
import serial.tools.list_ports
# package needed for sleep
import time
import re
import sys


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
        try:
            if com_port.is_open:
                com_port.flushInput()
                com_port.flushOutput()
                print('FUG initialized!')
                print("FUG Opened Port: " + com_ports[com_port_idx].device)
                return com_port
        except Exception as e:
            print('Error FUG_initialize()')
            print('Exception: ' + e.message)
            return e.message
            sys.exit(1)

    else:
        print('Error FUG_initialize()')
        return None




# cmd, list of commands expected
def FUG_sendcommands(com_port, cmd):
    # cmd = ['I 6e-4', 'S0R 250', 'U 5e3', 'F1']
    # cmd = ['I 6e-4', 'S0R 50', 'U 1e4']
    # cmd = ['F0'] turn it off
    # cmd = ['>M0?'] readback the actual voltage
    responses = []
    try:
        for command in cmd:
            # print("cmd:" + command)
            com_port.write((command + '\r\n').encode())
            # send cmd to device # might not work with older devices -> "LF" only needed!
            time.sleep(0.1)  # small sleep for response
            response = ''
            while com_port.in_waiting > 0:
                response = com_port.readline()           # all characters received, read line till '\r\n'
            if response != '':
                responses.append(response.decode("utf-8"))
                # print("<<: " + response.decode("utf-8"))  # decode bytes received to string
            else:
                responses.append('')
                print("FUG ERROR: no Response!")
    except Exception as e:
        print('Error FUG_sendcommands()')
        print('Exception: ' + e.message)
        sys.exit(1)
        return sys.exit(1)
    return responses


def FUG_off():
    serial.Serial('COM8').close()


# obj_fug_com ... fug serial object
# step_size=300 ... in volt
# step_time=1 step time in seconds : sleep time in seconds
# step_slope=0 step slope in voltage per second
# voltage_start=0  ... in volt
# voltage_stop=100 ... in volt

def get_voltage_from_PS(obj_fug_com):
    try:
        voltage_reading = str.rstrip(str(FUG_sendcommands(obj_fug_com, ['>M0?'])[0]))
        numbers = (re.findall('[+,-][0-9].+E[+,-][0-9].', voltage_reading))
        print("Voltage from Power supply" + numbers[0])
    except:
        numbers = ["0"]
        print("Failed get Voltage from PS")
    return float(numbers[0])


def get_current_from_PS(obj_fug_com):
    try:
        current_reading = str.rstrip(str(FUG_sendcommands(obj_fug_com, ['>M1?'])[0]))
        numbers = (re.findall('[+,-][0-9].+E[+,-][0-9].', current_reading))
        print("Current from Power supply" + numbers[0])
    except:
        numbers = ["0"]
    return float(numbers[0])


def step_sequency(obj_fug_com, step_size=350, step_time=1, step_slope=0, voltage_start=3000, voltage_stop=100):
    """responses = FUG_sendcommands(obj_fug_com, ['F0', '>S1B 0', 'I 600e-6', '>S0B 2', '>S0R ' + str(step_slope),
                                               'U ' + str(voltage_start), 'F1'])"""
    responses = FUG_sendcommands(obj_fug_com, ['>S1B 0', 'I 600e-6', '>S0B 0', '>S0R ' + str(step_slope),
                                               'U ' + str(voltage_start), 'F1'])

    if (get_voltage_from_PS(obj_fug_com) < voltage_start or get_voltage_from_PS(obj_fug_com) > voltage_start):
        time.sleep(step_time)

    voltage = voltage_start
    while voltage < voltage_stop:
        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
        time.sleep(step_time)
        voltage += step_size

    responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage_stop)]))
    responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(0)]))

    print("Responses from step frequency : ", str(responses))



def ramp_sequency(obj_fug_com, ramp_slope=250, voltage_start=0, voltage_stop=100):
    responses = FUG_sendcommands(obj_fug_com, ['F0', '>S1B 0', 'I 600e-6', '>S0B 0', 'U ' + str(voltage_start), 'F1'])

    responses.append(FUG_sendcommands(obj_fug_com, ['>S0B 2', '>S0R ' + str(ramp_slope), 'U ' + str(voltage_stop)]))

    # FUG_sendcommands(obj_fug_com, ['U ' + str(voltage_stop)])

    return responses
