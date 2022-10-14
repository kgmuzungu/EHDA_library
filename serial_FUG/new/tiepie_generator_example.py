#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
This example shows how to use both the oscilloscope and the generator
in the TiePie WS5.

To use LibTiePie SDK devices wrappers:

1. install the `hvl_ccb` package with a `tiepie` extra feature:

        $ pip install "hvl_ccb[tiepie]"

   this will install the Python bindings for the library.

2. install additional system library

    * on Linux: follow instructions in https://www.tiepie.com/en/libtiepie-sdk/linux ;
    * on Windows: the additional DLL is included in Python bindings package.
"""

import logging
import time
from pprint import pprint

import libtiepie as ltp
import numpy as np

from hvl_ccb.comm import NullCommunicationProtocol
from hvl_ccb.dev.tiepie import (
    TiePieWS5,
    TiePieOscilloscopeResolution,
    TiePieOscilloscopeChannelCoupling,
    TiePieOscilloscopeTriggerKind,
    TiePieOscilloscopeRange,
    TiePieOscilloscopeTriggerLevelMode,
    TiePieGeneratorSignalType,
    TiePieOscilloscopeAutoResolutionModes,
)

# Configure logger
logging.basicConfig(level=logging.INFO)

# Specify serial number of TiePie device
config = {"serial_number": 36307}

# Create null communication protocol
comm = NullCommunicationProtocol({})

# Open device
tp = TiePieWS5({}, config)

# Start device
tp.start()

# Customize default general oscilloscope configuration
tp.config_osc.resolution = TiePieOscilloscopeResolution.SIXTEEN_BIT
tp.config_osc.auto_resolution_mode = TiePieOscilloscopeAutoResolutionModes.DISABLED
tp.config_osc.pre_sample_ratio = 0.0
tp.config_osc.trigger_timeout = 8  # [s]
tp.config_osc.record_length = 1000
tp.config_osc.sample_frequency = 1e6  # [samples/s]

# print dynamic oscilloscope config to console
pprint(tp.config_osc)


# Customize default channel configurations as needed
# Channel 1
config_osc_ch1 = tp.config_osc_channel_dict[1]
config_osc_ch1.trigger_kind = TiePieOscilloscopeTriggerKind.ANY
config_osc_ch1.trigger_level_mode = TiePieOscilloscopeTriggerLevelMode.ABSOLUTE
config_osc_ch1.trigger_level = 0.5  # [V]
config_osc_ch1.trigger_enabled = True
config_osc_ch1.input_range = TiePieOscilloscopeRange.TWO_VOLT
config_osc_ch1.coupling = TiePieOscilloscopeChannelCoupling.DCV
config_osc_ch1.enabled = True
# Channel 2
config_osc_ch2 = tp.config_osc_channel_dict[2]
config_osc_ch2.enabled = False

# print dynamic channel configs to console
pprint(tp.config_osc_channel_dict)

# Customize default generator configuration
tp.config_gen.frequency = 1e3  # [Hz]
tp.config_gen.amplitude = 2  # [V]
tp.config_gen.offset = 0  # [V]
tp.config_gen.signal_type = TiePieGeneratorSignalType.ARBITRARY  # waveform
x_axis = np.linspace(0, 100, 8192)  # Create signal array
y_axis = np.sin(x_axis) * (
    1 - x_axis / 100
)  # waveform is automatically scaled to [-1, 1]
tp.config_gen.waveform = y_axis
tp.config_gen.enabled = True

# Example of direct manipulation of libtiepie handles (._osc, ._gen and _i2c)
# for more advanced settings

# Set scope trigger input to "generator start new period"
trigger_input = tp._osc.trigger_inputs.get_by_id(ltp.TIID_GENERATOR_NEW_PERIOD)
trigger_input.enabled = True

# Set trigger output "start new period" on extension connector pin 1 (EXT 1)
trigger_output = tp._gen.trigger_outputs.get_by_id(ltp.TOID_EXT1)
trigger_output.event = ltp.TOE_GENERATOR_NEWPERIOD
trigger_output.enabled = True

# print dynamic generator config to console
pprint(tp.config_gen)

# Start generator
tp.generator_start()

# Wait for generator output to stabilize
time.sleep(0.1)

# Start oscilloscope data acquisition
tp.start_measurement()
data_2 = tp.collect_measurement_data(timeout=5)

if data_2 is None:
    tp.force_trigger()
    data_2 = tp.collect_measurement_data(timeout=None)

# Wait for keystroke:
print("Press Enter to stop signal generation...")
input()

# Stop generator
tp.generator_stop()

# Close device
tp.stop()
