# GeneratorGatedBurst.py
#
# This example generates a 100 kHz square waveform, 25% duty cycle, 0..5 V, 20 periods, this waveform is triggered by the external trigger (EXT 1).
# Connect EXT 1 to GND to trigger the burst.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
import sys
import libtiepie
from printinfo import *

# Print library info:
print_library_info()

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# Try to open a generator with triggered burst support:
gen = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_GENERATOR):
        gen = item.open_generator()
        if (gen.modes_native & libtiepie.GM_BURST_COUNT) and len(gen.trigger_inputs) > 0:
            break
        else:
            gen = None

if gen:
    try:
        # Set signal type:
        gen.signal_type = libtiepie.ST_SQUARE

        # Set frequency:
        gen.frequency = 100e3  # 100 kHz

        # Set amplitude:
        gen.amplitude = 2.5  # 2.5 V

        # Set offset:
        gen.offset = 2.5  # 2.5 V

        # Set symmetry (duty cycle):
        gen.symmetry = 0.25  # 25 %

        # Set mode:
        gen.mode = libtiepie.GM_BURST_COUNT

        # Set burst count:
        gen.burst_count = 20  # 20 periods

        # Locate trigger input:
        trigger_input = gen.trigger_inputs.get_by_id(libtiepie.TIID_EXT1)

        if trigger_input is None:
            trigger_input = gen.trigger_inputs.get_by_id(libtiepie.TIID_EXT2)

        if trigger_input is None:
            raise Exception('Unknown trigger input!')

        # Enable trigger input:
        trigger_input.enabled = True

        # Set trigger input kind:
        trigger_input.kind = libtiepie.TK_FALLINGEDGE

        # Enable output:
        gen.output_on = True

        # Print generator info:
        print_device_info(gen)

        # Start signal burst:
        gen.start()

        # Wait for keystroke:
        print('Press Enter to stop signal generation...')
        if sys.version_info < (3, 0):  # Python 2.x
            raw_input()
        else:  # Python 3.x
            input()

        # Stop generator:
        gen.stop()

        # Disable output:
        gen.output_on = False

    except Exception as e:
        print('Exception: ' + e.message)
        sys.exit(1)

    # Close generator:
    del gen

else:
    print('No generator available with triggererd burst support!')
    sys.exit(1)

sys.exit(0)