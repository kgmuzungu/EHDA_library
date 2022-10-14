#  Copyright (c) 2020-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
This example shows how to use the oscilloscope in the TiePie HS6 device,
once with a blocking and once with a non-blocking measurement request.

To use LibTiePie SDK devices wrappers:

1. install the `hvl_ccb` package with a `tiepie` extra feature:

        $ pip install "hvl_ccb[tiepie]"

   this will install the Python bindings for the library.

2. install additional system library

    * on Linux: follow instructions in https://www.tiepie.com/en/libtiepie-sdk/linux ;
    * on Windows: the additional DLL is included in Python bindings package.
"""

import logging
from time import sleep

from hvl_ccb.comm import NullCommunicationProtocol
from hvl_ccb.dev.tiepie import (
    TiePieHS6,
    TiePieOscilloscopeResolution,
    TiePieOscilloscopeChannelCoupling,
    TiePieOscilloscopeTriggerKind,
    TiePieOscilloscopeRange,
    TiePieOscilloscopeTriggerLevelMode,
    TiePieOscilloscopeAutoResolutionModes,
    TiePieOscilloscope,
)

# configure logger
logging.basicConfig(level=logging.INFO)

#######################################################################################
"""
Configure the device if you know the serial_number
"""
#######################################################################################
# specify serial number of TiePie
config = {"serial_number": 37289}

# create null communication protocol
comm = NullCommunicationProtocol({})

# open device
# (available: TiePieHS6, TiePieHS5 and TiePieWS5)
tp = TiePieHS6(comm, config)

#######################################################################################
"""
If you do not know the serial number you can first search for available devices
and select one from the list, here the first one (index 0) is taken.
This can be useful, when you are sure you only have one TiePie connected to the computer.
The program will then also work if you change the hardware (and therefore the serial number).
"""
#######################################################################################
devList = TiePieOscilloscope.list_devices()
tp = TiePieOscilloscope(
    comm, {"serial_number": devList.get_item_by_index(0).serial_number}
)

#######################################################################################

# start device
tp.start()

# Customize default general oscilloscope configuration
tp.config_osc.resolution = TiePieOscilloscopeResolution.SIXTEEN_BIT
tp.config_osc.auto_resolution_mode = TiePieOscilloscopeAutoResolutionModes.DISABLED
tp.config_osc.pre_sample_ratio = 0.5  # between 0 and 1
tp.config_osc.trigger_timeout = 0.2  # in s
tp.config_osc.sample_frequency = 3.125e6  # in samples/s
tp.config_osc.record_length = 18e6  # in sample

# Customize default channel configurations as needed
# Channel 1
config_osc_ch1 = tp.config_osc_channel_dict[1]
config_osc_ch1.enabled = True
# Channel 2
config_osc_ch2 = tp.config_osc_channel_dict[2]
config_osc_ch2.enabled = False
# Channel 3
config_osc_ch3 = tp.config_osc_channel_dict[3]
config_osc_ch3.enabled = False
# Channel 4
config_osc_ch4 = tp.config_osc_channel_dict[4]
config_osc_ch4.enabled = False

config_osc_ch1.input_range = TiePieOscilloscopeRange.EIGHT_VOLT
config_osc_ch1.trigger_kind = TiePieOscilloscopeTriggerKind.ANY
config_osc_ch1.trigger_level_mode = TiePieOscilloscopeTriggerLevelMode.ABSOLUTE
config_osc_ch1.trigger_level = 0.0  # in V
config_osc_ch1.trigger_hysteresis = 0.01
config_osc_ch1.trigger_enabled = True
config_osc_ch1.coupling = TiePieOscilloscopeChannelCoupling.DCV

#######################################################################################
"""
non blocking call of collect_measurement_data()
"""
#######################################################################################
print(f"TiePie is armed: {tp.is_measurement_running()}")
tp.start_measurement()

# do other stuff here

print(f"TiePie is armed: {tp.is_measurement_running()}")
while not tp.is_measurement_data_ready():
    print(f"TiePie has triggered: {tp.is_triggered()}")
    print(f"TiePie is armed: {tp.is_measurement_running()}")
    print(f"TiePie has measurement data ready: {tp.is_measurement_data_ready()}")
    sleep(0.1)
print(f"TiePie has measurement data ready: {tp.is_measurement_data_ready()}")
data_1 = tp.collect_measurement_data(timeout=0)

#######################################################################################
"""
blocking call of collect_measurement_data with force trigger
"""
#######################################################################################

config_osc_ch1.trigger_level = 2
tp.config_osc.trigger_timeout = None

tp.start_measurement()
data_2 = tp.collect_measurement_data(timeout=5)

if data_2 is None:
    tp.force_trigger()
    data_2 = tp.collect_measurement_data(timeout=None)

# close oscilloscope
tp.stop()
