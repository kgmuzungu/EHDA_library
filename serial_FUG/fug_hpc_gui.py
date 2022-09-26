#!/usr/bin/env python3


import argparse
import time

import PySimpleGUI as sg
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import serial

import fug_hpc

sg_theme = "Black"
plt_style = "dark_background"
color_u = "blue"
color_i = "red"
font = ("Courier", 20)
# On gryphon a 1ms timeout leads to a cycle duration of ~50ms, i.e. a buffer size of 12000 corresponds to ~10min
win_timeout_ms = 1
down_sampling = 1
buffer_size = 12000
supported_interfaces = ("serial", "usb")
ramp_behaviour_dict = {
    "off": 0,
    "up/down": 1,
    "up": 2
}
ramp_behaviour_inv = {v: k for k, v in ramp_behaviour_dict.items()}


def float_format(num_or_string):
    return f"{float(num_or_string):.3e}"


def software_trip(i_setpoint, i_actual, u, fug):
    if abs(i_actual) > i_setpoint:
        fug.kill()
        sg.popup_error(
            f"Software trip at {time.asctime(time.localtime(time.time()))} with {float_format(u)}V and {float_format(i_actual)}A",
            title=fug_hpc.model)


def fill_buffer(buffer, u, i):
    if not buffer["counter"]:
        buffer["t"][buffer["idx"]] = time.time()
        buffer["u"][buffer["idx"]] = u
        buffer["i"][buffer["idx"]] = i
        buffer["idx"] = (buffer["idx"] + 1) % buffer_size
    buffer["counter"] = (buffer["counter"] + 1) % down_sampling


def plot_buffer(buffer):
    plt.close("all")
    t = np.roll(buffer["t"], -buffer["idx"]) - np.nanmax(buffer["t"])
    u = np.roll(buffer["u"], -buffer["idx"]) / 1e3
    i = np.roll(buffer["i"], -buffer["idx"]) * 1e6
    fig = plt.figure()
    ax_u = fig.add_subplot(111)
    ax_u.plot(t, u, color_u)
    ax_u.set_xlabel("t [s]")
    ax_u.set_ylabel("U [kV]", color=color_u)
    ax_u.tick_params(axis="y", labelcolor=color_u)
    ax_u.grid(which="both")
    ax_i = ax_u.twinx()
    ax_i.plot(t, i, color_i)
    ax_i.set_ylabel("I [uA]", color=color_i)
    ax_i.tick_params(axis="y", labelcolor=color_i)
    plt.show(block=False)


def update_actual_values(win, fug, sw_trip, buffer):
    u = fug.get_u(silent=True)
    i = fug.get_i(silent=True)
    state = fug.get_output_state(silent=True)
    if state and (sw_trip is not None):
        software_trip(sw_trip, i, u, fug)
    win["-TUA-"].update(float_format(u))
    win["-TIA-"].update(float_format(i))
    if state:
        win["-TO-"].update("ON", text_color="red")
    else:
        win["-TO-"].update("OFF", text_color="green")
    fill_buffer(buffer, u, i)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("interface", help=str(supported_interfaces))
    parser.add_argument("port")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-r", "--no-reset", action="store_true", help=f"Don't reset {fug_hpc.model}")
    args = parser.parse_args()
    interface = args.interface
    port = args.port
    verbose = args.verbose
    reset = not args.no_reset

    if interface in supported_interfaces[:2]:
        fug = fug_hpc.FugHpcSerial(port, verbose=verbose)
    else:
        raise RuntimeError(f"Interface {interface} not supported. Supported interfaces are: {supported_interfaces}")
    if reset:
        fug.reset()
    sw_trip_current = 0.

    buffer = {
        "idx": 0,
        "counter": 0,
        "t": np.full(buffer_size, np.NaN, dtype=np.longdouble),
        "u": np.full(buffer_size, np.NaN, dtype=np.double),
        "i": np.full(buffer_size, np.NaN, dtype=np.double)
    }

    # Plot will not show up without this
    matplotlib.use("TkAgg")
    plt.style.use(plt_style)

    sg.theme(sg_theme)
    sg.set_options(font=font)
    layout = [
        [
            sg.T("Voltage [V]", size=(12, 1)),
            sg.T("-", key="-TUA-", size=(11, 1)),
            sg.T("Setpoint:", size=(10, 1)),
            sg.T(float_format(fug.get_u_set()), key="-TUS-", size=(11, 1)),
            sg.B("Set", key="-BUS-", size=(4, 1)),
            sg.I(key="-IUS-", size=(11, 1))
        ],
        [
            sg.T("Current [A]", size=(12, 1)),
            sg.T("-", key="-TIA-", size=(11, 1)),
            sg.T("Setpoint:", size=(10, 1)),
            sg.T(float_format(fug.get_i_set()), key="-TIS-", size=(11, 1)),
            sg.B("Set", key="-BIS-", size=(4, 1)),
            sg.I(key="-IIS-", size=(11, 1))
        ],
        [
            sg.T("Trip [A]", size=(12, 1)),
            sg.CB("Arm", key="-CTS-", size=(8, 1)),
            sg.T("Setpoint:", size=(10, 1)),
            sg.T(float_format(sw_trip_current), key="-TTS-", size=(11, 1)),
            sg.B("Set", key="-BTS-", size=(4, 1)),
            sg.I(key="-ITS-", size=(11, 1))
        ],
        [
            sg.T("Ramp [V/s]", size=(12, 1)),
            sg.DD(tuple(ramp_behaviour_dict), key="-DRB-", enable_events=True,
                  default_value=ramp_behaviour_inv[fug.get_ramp_behaviour()], size=(10, 1)),
            sg.T("Setpoint:", size=(10, 1)),
            sg.T(float_format(fug.get_ramp_speed()), key="-TRS-", size=(11, 1)),
            sg.B("Set", key="-BRS-", size=(4, 1)),
            sg.I(key="-IRS-", size=(11, 1))
        ],
        [
            sg.T("Output", size=(12, 1)),
            sg.T("-", key="-TO-", size=(11, 1)),
            sg.B("On", key="-BOO-", size=(8, 1)),
            sg.B("KILL", key="-BOK-", button_color="red", size=(10, 1)),
            sg.T("Polarity", size=(8, 1)),
            sg.DD(tuple(fug_hpc.pol_dict.keys()), key="-DP-", enable_events=True, default_value=fug.get_polarity_set(),
                  size=(2, 1))
        ],
        [sg.B("Exit", key="-BE-"), sg.B("History", key="-BH-")]
    ]

    win = sg.Window(fug_hpc.model, layout)

    last_event = None
    while True:
        try:
            event, values = win.read(win_timeout_ms)
            update_actual_values(win, fug, (sw_trip_current if values["-CTS-"] else None), buffer)
            if (verbose and (event != "__TIMEOUT__")) or (verbose > 2):
                print(f"Processing event {event}...")
            if event != last_event:
                last_event = event
                if event == "-BOK-":
                    fug.kill()
                elif event in ("-BE-", sg.WIN_CLOSED):
                    break
                elif event == "-BUS-":
                    win["-TUS-"].update(float_format(fug.set_u(abs(float(values['-IUS-'])))))
                elif event == "-BIS-":
                    win["-TIS-"].update(float_format(fug.set_i(abs(float(values['-IIS-'])))))
                elif event == "-BRS-":
                    win["-TRS-"].update(float_format(fug.set_ramp_speed(abs(float(values['-IRS-'])))))
                elif event == "-BTS-":
                    sw_trip_current = abs(float(values["-ITS-"]))
                    win["-TTS-"].update(float_format(sw_trip_current))
                elif event == "-DRB-":
                    fug.set_ramp_behaviour(ramp_behaviour_dict[values["-DRB-"]])
                elif event == "-DP-":
                    fug.set_polarity(values["-DP-"])
                elif event == "-BOO-":
                    fug.set_output_state(1)
                elif event == "-BH-":
                    plot_buffer(buffer)
        except (fug_hpc.Error, serial.SerialException) as exc:
            sg.popup_error(f"{fug_hpc.model} exception: {exc}")
        except ValueError as exc:
            sg.popup_error(f"Invalid input: {exc}")
        except KeyboardInterrupt:
            break
    win.close()


if __name__ == "__main__":
    main()
