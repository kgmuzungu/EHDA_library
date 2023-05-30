"""
TITLE: class for validation functions
"""

import numpy as np
import json
import time
import datetime


class ElectrosprayValidation:
    def __init__(self, name_liquid):
        self.name_liquid = name_liquid

        self.sjaak_verified = []
        self.sjaak_verified_false = []
        self.sjaak_verified_true = []

        self.data_points_list = 0
        self.electrical_conductivity = 0
        self.surface_tension = 0
        self.dieletric_const = 0
        self.electrical_conductivity = 0
        self.permitivity = 0
        self.rho = 0
        self.density = 0
        self.manual_shape = ""
        self.current_comment = ""

    def get_validation_dictionary(self):
        dictionary = {
            "mean_value_array": self.mean_value_array,
            "flow_rate chen pui": self.flow_rate_chen_pui,
            "alpha_chen_pui": self.alpha_chen_pui,
            "I_emitted_chen_pui": self.I_emitted_chen_pui,
            "I_hartman": self.I_hartman
        }
        return dictionary


    def calculate_scaling_laws_cone_jet(self, data, mean, flow_rate):
        # ki = 6.46
        ki = 1

        # print("\nprocessing_mean:", mean)
        self.mean_value_array = mean
        self.flow_rate_chen_pui = float(flow_rate) * 16e-12 # converting uL/min to m^3/s

        self.alpha_chen_pui =  (self.surface_tension * self.electrical_conductivity * self.flow_rate_chen_pui / self.dieletric_const) ** (.5)

        self.I_emitted_chen_pui = ki * self.dieletric_const ** (.25) * self.alpha_chen_pui ** (.5)
        self.I_emitted_chen_pui = self.I_emitted_chen_pui*10e5 / 2  # divided by two because of oscilloscope internal impedance
        # i_actual = data
        #
        # b_hartman = i_actual / ((self.surface_tension * self.electrical_conductivity * flow_rate) ** .5)
        # self.I_hartman = b_hartman * ((self.surface_tension * self.electrical_conductivity * flow_rate) ** .5)

        self.I_hartman = "Unknown"


