
from FUG_functions import *
from PUMP_functions import *
import keyboard


def controller(typeofmeasurement, finish_event, controller_output_queue, fug_COM_port, pump_COM_port, feedback_queue):

    #              FUG INIT
    obj_fug_com = FUG_initialize(fug_COM_port)  # parameter: COM port idx
    print("[FUG] obj_fug_com: ", obj_fug_com)
    get_voltage_from_PS(obj_fug_com)
    voltage = typeofmeasurement['voltage_start']

    #              FUG INIT
    obj_pump_com = PUMP_initialize(pump_COM_port)  # parameter: COM port idx
    print("[PUMP] obj_pump_com: ", obj_pump_com)
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
        set_inner_diameter(obj_pump_com, "1.7")
        # get_volume(obj_pump_com)
        low_motor_noize(obj_pump_com)

        flow_rate = ["0.01","0.03", "0.05" ,"0.1", "0.15", "0.2", "0.3", "0.35", "0.5", "0.55", "0.6", "0.7", "0.8", "0.85", "0.9", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5"]

        for fr in flow_rate:
            print("\n Starting experiment with flowrate:", fr)
            set_flowrate(obj_pump_com, fr, "UM")
            start_pumping(obj_pump_com)
            beep_command(obj_pump_com)
            while voltage < typeofmeasurement['voltage_stop']:
                responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                time.sleep(typeofmeasurement['step_time']/2)
                controller_output = [get_voltage_from_PS(obj_fug_com), get_current_from_PS(obj_fug_com), voltage, fr]
                time.sleep(typeofmeasurement['step_time']/2)
                voltage += typeofmeasurement['step_size']
                controller_output_queue.put(controller_output)
                # print("[FUG THREAD] put values in controller_output_queue")
            stop_pumping(obj_pump_com)
            voltage = typeofmeasurement['voltage_start']
            responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)])) # turn voltage to zero
            beep_command(obj_pump_com)
            time.sleep(5)


        finish_event.set()
        time.sleep(typeofmeasurement['step_time'])
        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(0)]))

        # print("[FUG THREAD] Responses from MAP sequence: ", str(responses))


    #             CONTROL SEQUENCE
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

                    elif current_state == "Multi Jet" or current_state == "Corona Sparks":
                        voltage -= 100
                        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))
                        print("[FUG THREAD] Decreasing voltage")

                    elif current_state == "Cone Jet":
                        print("[FUG THREAD] Stable in Cone Jet")

                    else:
                        print("[FUG THREAD] current state not known")

                    previous_state = current_state

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

            except:
                print("[CONTROLLER THREAD] ERROR!")
                sys.exit(1)

    # Closing FUG
    voltage = 0
    responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(voltage)]))

