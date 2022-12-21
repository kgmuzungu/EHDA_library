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
"""
repeat = "VER"

command_sequence = ["00PHN", "00STP", "*BUZ12", "0BUZ12", "00RUN", "00VOL", "00DIR", "00RAT",
                    "00FUN", "00TIM", "00PHN", "00STP"]

command_sequence_run = ["00PHN", "00STP", "*BUZ12", "0BUZ12", "00RUN", "00VOL", "00DIR", "00RAT",
                    "00FUN", "00TIM", "00PHN", ]

command_sequence_verify_how_much_dispensed = ["00PHN", "00STP", "*BUZ12", "0BUZ12", "00RUN", "00VOL", "00DIR", "00RAT",
                    "00FUN", "00TIM", "00PHN", "00STP"]

command_sequence_stop = ["00STP"]

command_diameter_double_check = ["00dia1.3", "00.dia"] # response should be 00S1.300

command_sequence_defining_step_rate = ["dia 1.3", "al 1", "bp 1", "PF 0", "phase START",
                                       "fun rat", "rat5uh", "vol1", "00dir", "dir inf",
                                       "phase", "fun rat", "rat5.5uh", "vol 5", "dir inf",
                                       "phase", "fun stp"]

command_sequence = ["00PHN", "00DIA1.3", "00DIA", "00VOL", "00PHN", "*ADR0", "00RATE2.5UH", "00RUN",
                    "00RAT", "00VOL", "00DIS", "00RAT", "00PHN", "00VOL", "00FUN", "00PHN", "00DIS",
                    "00VOL", "00PHN", "00DIS", "00RAT", "00VOL", "00STP"]


com_port = serial.Serial(
    port="/dev/cu.usbserial-AL00KSTG",  # chosen COM port
    baudrate=19200,  #
    bytesize=serial.EIGHTBITS,  # 8
    parity=serial.PARITY_NONE,  # N
    stopbits=serial.STOPBITS_ONE,  # 1
    timeout = 1
)
print("name: " + com_port.name)

# time.sleep(10)  # seconds to start the serial monitor

if com_port.is_open:
    com_port.flushInput()
    com_port.flushOutput()
    print("Opened Port: COM6")
    for command in command_sequence:
        com_port.write((command + '\r\n').encode())
        print("command sending: " + command)
        time.sleep(0.5)
        response = ''
        # while com_port.in_waiting > 0:
        response = com_port.readline()
        """for x in range(10):
        response = response + com_port.read().decode()"""
        print("response: " + response.decode("utf-8"))
        time.sleep(0.5)
else:
    print("port not open")

com_port.close()




