from FUG_functions import *
import time
import re

obj_fug_com = FUG_initialize(4)
FUG_sendcommands(obj_fug_com, ['>M1I 7'])
while True:
    FUG_sendcommands(obj_fug_com, ['>M1?'])
    time.sleep(0.5)
# FUG_sendcommands(obj_fug_com, ['>M1I?'])
# FUG_sendcommands(obj_fug_com, ['>S1B 0', 'I 600e-6', '>S0B 0', 'u 3000', 'F1'])
"""
FUG_sendcommands(obj_fug_com, ['F0'])
FUG_sendcommands(obj_fug_com, ['F0', '>S1B 0', 'I 600e-6', '>S0B 2', '>S0R 500', 'U 0', 'F1'])
FUG_sendcommands(obj_fug_com, ['>S0A?'])
time.sleep(3)
FUG_sendcommands(obj_fug_com, ['S0R 50', 'U 200'])
FUG_sendcommands(obj_fug_com, ['>S0A?'])
# FUG_sendcommands(obj_fug_com, ['F0'])
# FUG_off()  # closes serial connection


voltage = str.rstrip(str(FUG_sendcommands(obj_fug_com, ['>M1?'])[0]))
numbers = (re.findall('[+,-][0-9].+E[+,-][0-9].', voltage))
voltage = (numbers[0])
main_voltage = float(voltage)
"""
"""
voltage = 0
FUG_sendcommands(obj_fug_com, ['F0', '>S1B 0', 'I 600e-6', '>S0B 0', 'U 0', 'F1'])
time.sleep(3)
#for x in range(10):
while voltage < 3000:
    FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)])
    FUG_sendcommands(obj_fug_com, ['>M1?'])
    time.sleep(1)
    voltage += 300
"""


