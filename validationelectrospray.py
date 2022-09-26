import numpy as np
import json


class ElectrosprayValidation:
    def __init__(self, name_liquid):
        self.name_liquid = name_liquid

        self.all_data = []
        self.flow_rate_chen_pui = []
        self.alpha_chen_pui = []
        self.I_emitted_chen_pui = []
        self.I_hartman = []
        self.sjaak_std_mean_array = []
        self.sjaak_mean_median_array = []
        self.med_value_array = []
        self.mean_value_array = []
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
            "all data": self.all_data.tolist(),
            "mean_value_array": self.mean_value_array.tolist(),
            "flow rate chen pui": self.flow_rate_chen_pui.tolist(),
            "alpha_chen_pui": self.alpha_chen_pui.tolist(),
            "I_emitted_chen_pui": self.I_emitted_chen_pui.tolist(),
            "I_hartman": self.I_hartman.tolist()
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
            self.min_fr_chen_pui = self.data_dict['config']['liquid']['actual measurement']['flow rate chen pui']
            self.data_dict['config']['liquid']['surface tension']
            self.dieletric_const = self.data_dict['config']['liquid']['dielectric const']
            self.electrical_conductivity = electrical_conductivity
            self.permitivity = self.data_dict['vacuum permitivity']
            self.rho = self.data_dict['config']['liquid']['rho density']
        """
    def calculate_scaling_laws_cone_jet(self, data, mean, flow_rate):
        ki = 6.46

        print("\nprocessing_mean:", mean)
        data_points_np = np.array(data)
        self.data_points_list = data.tolist()
        print("\nmeasurements list:", self.data_points_list)
        self.mean_value_array.append(mean)


        for i in range(len(self.data_points_list)):
            self.flow_rate_chen_pui.append(flow_rate)
            flow_rate_aux = self.flow_rate_chen_pui[i]
            if flow_rate_aux == 0.0:
                flow_rate_aux = i + 1

            self.alpha_chen_pui.append(
                (self.surface_tension * self.electrical_conductivity * self.flow_rate_chen_pui[i] / self.dieletric_const) ** (.5))

            self.I_emitted_chen_pui.append(ki * self.dieletric_const ** (.25) * self.alpha_chen_pui[i] ** (.5))
            i_actual = data[i]

            b_hartman = i_actual / ((self.surface_tension * self.electrical_conductivity * flow_rate_aux) ** .5)
            self.I_hartman.append(b_hartman * ((self.surface_tension * self.electrical_conductivity * flow_rate_aux) ** .5))

            if self.electrical_conductivity == 0.0 or self.rho == 0.0:
                self.flow_rate_chen_pui.append(0.0)
            else:
                self.flow_rate_chen_pui.append(
                    (self.dieletric_const ** 0.5) * self.permitivity * self.surface_tension / (self.rho * self.electrical_conductivity))
