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
    
    def open_load_json_data(self, filename): 
        with open(filename) as json_file: 
            self.data_dict = json.load(json_file) 
            print("\nconfig liquid:", self.data_dict['config']['liquid']) 


    def open_load_cone_jet(self, filename): 
        with open(filename) as json_file: 
            self.data_dict = json.load(json_file) 
            print("\nconfig liquid coned jet:", self.data_dict['config']['liquid']) 
 
    def set_data_from_dict_liquid(self, dict_liquid): 
        self.surface_tension = dict_liquid['surface tension'] 
        self.dieletric_const = dict_liquid['dielectric const'] 
        self.electrical_conductivity = dict_liquid['electrical conductivity'] 
        self.permitivity = dict_liquid['vacuum permitivity'] 
        self.rho = dict_liquid['density'] 
        self.density = dict_liquid['density'] 
        """ 
        def validation_data(self, current_comment, manual_shape, electrical_conductivity): 
            self.min_fr_chen_pui = self.data_dict['config']['liquid']['actual measurement']['flow_rate chen pui'] 
            self.data_dict['config']['liquid']['surface tension'] 
            self.dieletric_const = self.data_dict['config']['liquid']['dielectric const'] 
            self.electrical_conductivity = electrical_conductivity 
            self.permitivity = self.data_dict['vacuum permitivity'] 
            self.rho = self.data_dict['config']['liquid']['rho density'] 
        """ 

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


