# ListDevices.py
#
# This example prints all the available devices to the screen.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
import sys
import time
import libtiepie
from printinfo import *

# Print library info:
print_library_info()
"""
    Name: WiFiScope WS6 DIFF-1000XMSG
    Serial number  : 37427
    Available types: Oscilloscope
    Server         : 192.168.255.1:5450 (WiFiScope WS6 DIFF-1000XMSG)
"""
# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

if len(libtiepie.device_list) > 0:
    print()
    print('Available devices:')

    for item in libtiepie.device_list:
        print('  Name: ' + item.name)
        print('    Serial number  : ' + str(item.serial_number))
        print('    Available types: ' + libtiepie.device_type_str(item.types))

        if item.has_server:
            print('    Server         : ' + item.server.url + ' (' + item.server.name + ')')
else:
    print('No devices found!')

sys.exit(0)
