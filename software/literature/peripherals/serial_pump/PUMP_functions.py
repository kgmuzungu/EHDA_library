import time
import serial

"""
VER The pump type and software version
DIA Diameter of the syringe or tubing - Use quick set area to set syringe 
DIR The current pumping direction.
PHN The current phase number
RAT The current pumping rate.
FUN The current pump function.
DIS The Infusion and Withdrawal counter values from the pump.
AL Alarms on/off use manual command
00AL1 will turn alarms on for the pump at address 0
PF Power fail on/off 
TRG Trigger type
DIN Digital input state 
ROM Pump motor operating TTL out signal
LOC Keypad lockout 
BUZ Buzzer on/off
SAF Safe mode on/off 
BP Keypad beeping on/off
IN2 Digital input #2 
IN4 Digital input #3
IN4 Digital input #4 
IN6 Digital input #6


prompt:
    I W S P T U
Infusing
Withdrawing
Pumping Program Stopped Pumping Program Paused
Timed Pause Phase
Operational trigger wait (user wait)

ALARMs:
    R S T E O
Pump was reset (power was interrupted) Pump motor stalled
Safe mode communications time out Pumping Program error
Pumping Program Phase is out of range
"""
repeat = "VER"

command_sequence = ["00PHN", "00STP", "*BUZ12", "0BUZ12", "00RUN", "00VOL", "00DIR", "00RAT",
                    "00FUN", "00TIM", "00PHN", "00STP"]

command_sequence_run = ["00PHN", "00STP", "*BUZ12", "0BUZ12", "00RUN", "00VOL", "00DIR", "00RAT",
                    "00FUN", "00TIM", "00PHN", ]

command_sequence_verify_how_much_dispensed = ["00PHN", "00STP", "*BUZ12", "0BUZ12", "00RUN", "00VOL", "00DIR", "00RAT",
                    "00FUN", "00TIM", "00PHN", "00STP"]

command_diameter_double_check = ["00dia1.3", "00.dia"] # response should be 00S1.300

command_sequence_defining_step_rate = ["dia 1.3", "al 1", "bp 1", "PF 0", "phase START",
                                       "fun rat", "rat5uh", "vol1", "00dir", "dir inf",
                                       "phase", "fun rat", "rat5.5uh", "vol 5", "dir inf",
                                       "phase", "fun stp"]

command_sequence = ["00PHN", "00DIA1.3", "00DIA", "00VOL", "00PHN", "*ADR0", "00RATE2.5UH", "00RUN",
                    "00RAT", "00VOL", "00DIS", "00RAT", "00PHN", "00VOL", "00FUN", "00PHN", "00DIS",
                    "00VOL", "00PHN", "00DIS", "00RAT", "00VOL", "00STP"]



def set_pump_direction(com_port, dir):
    """ 
    DIR 
    [ INF | WDR | REV | STK ] Set/query pumping direction
    INF = Infuse
    WDR = Withdraw
    REV = Reverse pumping direction
    STK = “Sticky Direction” (See “Sticky Direction”, sec: .6.8.1)
    """
    command = "DIR" + dir
    com_port.write((command + '\r\n').encode())
    print("[PUMP] command sending: set inner direction to " + dir)
    time.sleep(0.5)
    response = ''
    response = com_port.readline()
    print("[PUMP] response: " + response.decode("utf-8"))



def set_inner_diameter(com_port, dia):
    command = "DIA" + dia
    com_port.write((command + '\r\n').encode())
    print("[PUMP] command sending: set inner diameter to " + dia)
    time.sleep(0.5)
    response = ''
    response = com_port.readline()
    print("[PUMP] response: " + response.decode("utf-8"))


def get_volume(com_port):
    command = "VOL"
    com_port.write((command + '\r\n').encode())
    print("[PUMP] get volume: " + command)
    time.sleep(0.5)
    response = ''
    response = com_port.readline()
    print("[PUMP] response: " + response.decode("utf-8"))


def set_flowrate(com_port, fr, unit):
    """"
    UM = μL/min 
    MM = mL/min
    UH = μL/hr 
    MH = mL/hr
    """
    command = "RAT" + fr + unit
    com_port.write((command + '\r\n').encode())
    print("[PUMP] command sending: set flowrate to " + fr + unit)
    time.sleep(0.5)
    response = ''
    response = com_port.readline()
    print("[PUMP] response: " + response.decode("utf-8"))


def start_pumping(com_port):
    command = "RUN"
    com_port.write((command + '\r\n').encode())
    print("[PUMP] command sending: START")
    time.sleep(0.5)
    response = ''
    response = com_port.readline()
    print("[PUMP] response: " + response.decode("utf-8"))

def low_motor_noize(com_port):
    command = "LN1"
    com_port.write((command + '\r\n').encode())
    print("[PUMP] command sending: Low Motor Noise")
    time.sleep(0.5)
    response = ''
    response = com_port.readline()
    print("[PUMP] response: " + response.decode("utf-8"))


def stop_pumping(com_port):
    command = "STP"
    com_port.write((command + '\r\n').encode())
    print("[PUMP] command sending: STOP")
    time.sleep(0.5)
    response = ''
    response = com_port.readline()
    print("[PUMP] response: " + response.decode("utf-8"))


def increase_flowrate(com_port):
    command = "INC"
    com_port.write((command + '\r\n').encode())
    print("[PUMP] command sending: increase flowrate")
    time.sleep(0.5)
    response = ''
    response = com_port.readline()
    print("[PUMP] response: " + response.decode("utf-8"))


def beep_command(com_port):
    command = "BUZ1"
    com_port.write((command + '\r\n').encode())
    print("[PUMP] command sending: BEP")
    time.sleep(0.5)
    command = "BUZ0"
    com_port.write((command + '\r\n').encode())
    time.sleep(0.1)
    response = ''
    response = com_port.readline()
    print("[PUMP] response: " + response.decode("utf-8"))




com_port = serial.Serial(
    port="/dev/cu.usbserial-AL00KSTG",  # chosen COM port
    baudrate=19200,  #
    bytesize=serial.EIGHTBITS,  # 8
    parity=serial.PARITY_NONE,  # N
    stopbits=serial.STOPBITS_ONE,  # 1
    timeout = 1
)
print("name: " + com_port.name)


if com_port.is_open:
    com_port.flushInput()
    com_port.flushOutput()
    print("Opened Port: COM6")

    set_pump_direction(com_port, "INF")
    set_inner_diameter(com_port, "1.7")
    get_volume(com_port)
    set_flowrate(com_port, "1.5", "UM")
    low_motor_noize(com_port)

    beep_command(com_port)
    start_pumping(com_port)
    time.sleep(5)
    increase_flowrate(com_port)
    stop_pumping(com_port)
    beep_command(com_port)


else:
    print("port not open")


com_port.close()




