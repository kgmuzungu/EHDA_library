
from FUG_functions import *
from PUMP_functions import *
import keyboard


def controller(typeofmeasurement, finish_event, controller_output_queue, fug_COM_port, pump_COM_port, feedback_queue, syringe_diameter):

    #              FUG INIT
    obj_fug_com = FUG_initialize(fug_COM_port)  # parameter: COM port idx
    try:
        get_voltage_from_PS(obj_fug_com)
    except Exception as e:
        print("ERROR: ", str(e))
        print("[CONTROLLER THREAD] FAILED TO COMMUNICATE WITH POWER SUPPLY!")
        sys.exit(1)

    voltage = typeofmeasurement['voltage_start']

    #              PUMP INIT
    obj_pump_com = PUMP_initialize(pump_COM_port)  # parameter: COM port idx
    flow_rate = typeofmeasurement['flow_rate']


    #           STEP SEQUENCE
    if typeofmeasurement['sequence'] == "step":
        """responses = FUG_sendcommands(obj_fug_com, ['F0', '>S1B 0', 'I 600e-6', '>S0B 2', '>S0R ' + str(step_slope),
                                                'U ' + str(voltage_start), 'F1'])"""
        responses = FUG_sendcommands(obj_fug_com, ['>S1B 0', 'I 600e-6', '>S0B 0', '>S0R ' + str(typeofmeasurement['slope']),
                                                'U ' + str(typeofmeasurement['voltage_start']), 'F1'])

        if (get_voltage_from_PS(obj_fug_com) < typeofmeasurement['voltage_start'] or get_voltage_from_PS(obj_fug_com) > typeofmeasurement['voltage_start']):
            time.sleep(typeofmeasurement['step_time'])

        while voltage < typeofmeasurement['voltage_stop']:
            responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
            time.sleep(typeofmeasurement['step_time'])
            controller_output = [get_voltage_from_PS(obj_fug_com), get_current_from_PS(obj_fug_com), voltage, flow_rate]
            voltage += typeofmeasurement['step_size']
            controller_output_queue.put(controller_output)
            # print("[FUG THREAD] put values in controller_output_queue")

        finish_event.set()

        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(typeofmeasurement['voltage_stop'])]))
        time.sleep(typeofmeasurement['step_time'])
        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(0)]))

        # print("[FUG THREAD] Responses from step sequence: ", str(responses))


    #            RAMP SEQUENCE
    elif typeofmeasurement['sequence'] == "ramp":
        responses = FUG_sendcommands(obj_fug_com, ['F0', '>S1B 0', 'I 600e-6', '>S0B 0', 'U ' + str(typeofmeasurement['voltage_start']), 'F1'])

        responses.append(FUG_sendcommands(obj_fug_com, ['>S0B 2', '>S0R ' + str(typeofmeasurement['slope']), 'U ' + str(typeofmeasurement['voltage_stop'])]))

        while get_voltage_from_PS(obj_fug_com) < typeofmeasurement['voltage_stop']:
            controller_output = [get_voltage_from_PS(obj_fug_com), get_current_from_PS(obj_fug_com), 0, flow_rate]
            controller_output_queue.put(controller_output)
            time.sleep(0.5)

        finish_event.set()


    #            MAP SEQUENCE
    elif typeofmeasurement['sequence'] == "map":
        """responses = FUG_sendcommands(obj_fug_com, ['F0', '>S1B 0', 'I 600e-6', '>S0B 2', '>S0R ' + str(step_slope),
                                                'U ' + str(voltage_start), 'F1'])"""
        responses = FUG_sendcommands(obj_fug_com, ['>S1B 0', 'I 600e-6', '>S0B 0', '>S0R ' + str(typeofmeasurement['slope']),
                                                'U ' + str(typeofmeasurement['voltage_start']), 'F1'])

        if (get_voltage_from_PS(obj_fug_com) < typeofmeasurement['voltage_start'] or get_voltage_from_PS(obj_fug_com) > typeofmeasurement['voltage_start']):
            time.sleep(typeofmeasurement['step_time'])


        set_pump_direction(obj_pump_com, "INF")
        set_inner_diameter(obj_pump_com, syringe_diameter)
        # get_volume(obj_pump_com)
        low_motor_noize(obj_pump_com)


        for fr in flow_rate:

            print("\n Starting experiment with flowrate:", fr)
            set_flowrate(obj_pump_com, fr, "UM")
            time.sleep(1)
            start_pumping(obj_pump_com)
            voltage = typeofmeasurement['voltage_start']
            responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)])) # turn voltage to zero
            time.sleep(5)
            beep_command(obj_pump_com)

            # Voltage loop
            while voltage < typeofmeasurement['voltage_stop']:

                responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                time.sleep(typeofmeasurement['step_time']/2)
                controller_output = [get_voltage_from_PS(obj_fug_com), get_current_from_PS(obj_fug_com), voltage, fr]
                time.sleep(typeofmeasurement['step_time']/2)
                voltage += typeofmeasurement['step_size']
                controller_output_queue.put(controller_output)
                # print("[FUG THREAD] put values in controller_output_queue")
                # EXIT CONTROL SEQUENCE
                if keyboard.is_pressed("q"):
                    print("You pressed q")
                    finish_event.set()

            stop_pumping(obj_pump_com)
            time.sleep(0.5)



        finish_event.set()
        stop_pumping(obj_pump_com)
        time.sleep(typeofmeasurement['step_time'])
        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(0)]))

        # print("[FUG THREAD] Responses from MAP sequence: ", str(responses))


    #            SIMPLE CONTROL SEQUENCE
    elif typeofmeasurement['sequence'] == "control":


        responses = FUG_sendcommands(obj_fug_com, ['>S1B 0', 'I 600e-6', '>S0B 0', '>S0R ' + str(typeofmeasurement['slope']), 'U ' + str(typeofmeasurement['voltage_start']), 'F1'])
        current_state = "Dripping"

        controller_output = controller_output = [get_voltage_from_PS(obj_fug_com), get_current_from_PS(obj_fug_com), voltage, flow_rate]
        controller_output_queue.put(controller_output)


        while not finish_event.is_set():

            try:
                if not feedback_queue.empty():

                    current_state = feedback_queue.get()
                    print("[FUG THREAD] current state: ", current_state)

                    # CONTROL ALGORITHM
                    if current_state == "Dripping" or current_state == "Intermittent":
                        voltage += 100
                        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                        print("[FUG THREAD] Increasing Voltage")

                    elif current_state == "Multi Jet" or current_state == "Corona":
                        voltage -= 100
                        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                        print("[FUG THREAD] Decreasing voltage")

                    elif current_state == "Cone Jet":
                        print("[FUG THREAD] Stable in Cone Jet")

                    else:
                        print("[FUG THREAD] current state not known")

                    # SAFETY VOLTAGE LIMITS
                    if voltage > typeofmeasurement['voltage_stop']:
                        voltage = typeofmeasurement['voltage_stop']
                        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                    elif voltage < typeofmeasurement['voltage_start']:
                        voltage = typeofmeasurement['voltage_start']
                        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))

                    controller_output = controller_output = [get_voltage_from_PS(obj_fug_com), get_current_from_PS(obj_fug_com), voltage, flow_rate]
                    controller_output_queue.put(controller_output)

                    # EXIT CONTROL SEQUENCE
                    if keyboard.is_pressed("q"):
                        print("You pressed q")
                        finish_event.set()

            except Exception as e:
                print("ERROR: ", str(e))
                print("[CONTROLLER THREAD] ERROR!")
                sys.exit(1)


    #            ROBUST CONTROL SEQUENCE
    elif typeofmeasurement['sequence'] == "robust_control":


        responses = FUG_sendcommands(obj_fug_com, ['>S1B 0', 'I 600e-6', '>S0B 0', '>S0R ' + str(typeofmeasurement['slope']), 'U ' + str(typeofmeasurement['voltage_start']), 'F1'])
        current_state = "Dripping"

        controller_output = controller_output = [get_voltage_from_PS(obj_fug_com), get_current_from_PS(obj_fug_com), voltage, flow_rate]
        controller_output_queue.put(controller_output)

        previous_state = []


        while not finish_event.is_set():

            try:
                if not feedback_queue.empty():

                    current_state = feedback_queue.get()
                    print("[FUG THREAD] current state: ", current_state)
                    previous_state.append(current_state)

                    # CONTROL ALGORITHM

                    if current_state == "Dripping":
                        voltage += 200
                        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                        print("[FUG THREAD] Increasing Voltage")

                    elif current_state == "Intermittent":
                        if previous_state[-1] == "Dripping":
                            voltage += 200
                            responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                            print("[FUG THREAD] Increasing Voltage")
                        else:
                            voltage += 100
                            responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                            print("[FUG THREAD] Increasing Voltage")

                    elif current_state == "Cone Jet":
                        if previous_state[-5:].count("Intermittent") > 2:
                            voltage += 100
                            responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                            print("[FUG THREAD] Increasing Voltage")

                        elif previous_state[-5:].count("Intermittent") > 1:
                            voltage += 50
                            responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                            print("[FUG THREAD] Increasing Voltage")

                        elif previous_state[-5:].count("Cone Jet") == 5:
                            print("[FUG THREAD] Stable in Cone Jet")

                        elif previous_state[-5:].count("Multi Jet") > 1:
                            voltage -= 50
                            responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                            print("[FUG THREAD] Decreasing Voltage")

                        elif previous_state[-5:].count("Multi Jet") > 2:
                            voltage -= 100
                            responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                            print("[FUG THREAD] Decreasing Voltage")

                    elif current_state == "Multi Jet":
                        if previous_state[-1] == "Corona":
                            voltage -= 200
                            responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                            print("[FUG THREAD] Decreasing Voltage")
                        else:
                            voltage -= 100
                            responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                            print("[FUG THREAD] Decreasing Voltage")

                    elif current_state == "Corona":
                        voltage -= 200
                        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                        print("[FUG THREAD] Decreasing Voltage")

                    else:
                        print("[FUG THREAD] controller will wait more info of the system")

                    # SAFETY VOLTAGE LIMITS
                    if voltage > typeofmeasurement['voltage_stop']:
                        voltage = typeofmeasurement['voltage_stop']
                        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                    elif voltage < typeofmeasurement['voltage_start']:
                        voltage = typeofmeasurement['voltage_start']
                        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))

                    controller_output = controller_output = [get_voltage_from_PS(obj_fug_com), get_current_from_PS(obj_fug_com), voltage, flow_rate]
                    controller_output_queue.put(controller_output)

                    # EXIT CONTROL SEQUENCE
                    if keyboard.is_pressed("q"):
                        print("You pressed q")
                        finish_event.set()

            except Exception as e:
                print("ERROR: ", str(e))
                print("[CONTROLLER THREAD] ERROR!")
                sys.exit(1)


    # Closing FUG
    voltage = 0
    responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))

