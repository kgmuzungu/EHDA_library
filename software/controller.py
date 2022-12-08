
from FUG_functions import *


def controller(typeofmeasurement, finish_event, fug_values_queue, fug_COM_port, feedback_queue):

    #              FUG INIT
    obj_fug_com = FUG_initialize(fug_COM_port)  # parameter: COM port idx
    print("[FUG] obj_fug_com: ", obj_fug_com)
    get_voltage_from_PS(obj_fug_com)
    voltage = typeofmeasurement['voltage_start']


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
            fug_values = [get_voltage_from_PS(obj_fug_com), get_current_from_PS(obj_fug_com), voltage]
            voltage += typeofmeasurement['step_size']
            fug_values_queue.put(fug_values)
            # print("[FUG THREAD] put values in fug_values_queue")

        finish_event.set()

        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(typeofmeasurement['voltage_stop'])]))
        time.sleep(typeofmeasurement['step_time'])
        responses.append(FUG_sendcommands(obj_fug_com, ['U ' + str(0)]))

        print("[FUG THREAD] Responses from step sequence: ", str(responses))


#                   RAMP SEQUENCE
    elif typeofmeasurement['sequence'] == "ramp":
        responses = FUG_sendcommands(obj_fug_com, ['F0', '>S1B 0', 'I 600e-6', '>S0B 0', 'U ' + str(typeofmeasurement['voltage_start']), 'F1'])

        responses.append(FUG_sendcommands(obj_fug_com, ['>S0B 2', '>S0R ' + str(typeofmeasurement['slope']), 'U ' + str(typeofmeasurement['voltage_stop'])]))

        while get_voltage_from_PS(obj_fug_com) < typeofmeasurement['voltage_stop']:
            fug_values = [get_voltage_from_PS(obj_fug_com), get_current_from_PS(obj_fug_com)]
            fug_values_queue.put(fug_values)
            time.sleep(0.5)


    #             CONTROL SEQUENCE
    elif typeofmeasurement['sequence'] == "control":


        responses = FUG_sendcommands(obj_fug_com, ['>S1B 0', 'I 600e-6', '>S0B 0', '>S0R ' + str(typeofmeasurement['slope']), 'U ' + str(typeofmeasurement['voltage_start']), 'F1'])
        current_state = "Dripping"
        fug_values = [get_voltage_from_PS(obj_fug_com), get_current_from_PS(obj_fug_com), voltage]
        fug_values_queue.put(fug_values)


        while not finish_event.is_set():

            try:
                if not feedback_queue.empty():
                    current_state = feedback_queue.get()
                    print("[FUG THREAD]:current state: ", current_state)

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

                    fug_values = [get_voltage_from_PS(obj_fug_com), get_current_from_PS(obj_fug_com), voltage]
                    fug_values_queue.put(fug_values)

            except:
                print("[CONTROLLER THREAD] ERROR!")
                sys.exit(1)
            


    else:
        print("[FUG THREAD] Mode not available")


