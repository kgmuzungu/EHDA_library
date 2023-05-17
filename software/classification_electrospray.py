import itertools
import os
import re
from typing import TextIO
import numpy as np
import json
import math


class ElectrosprayClassification:
    
    def __init__(self, name_liquid):
        self.name_liquid = name_liquid
        self.all_data = []
        self.sjaak_std_mean_array = []
        self.sjaak_mean_median_array = []
        self.med_value_array = []
        self.mean_value_array = []
        self.sjaak_verified = []
        self.sjaak_verified_false = []
        self.sjaak_verified_true = []
        self.previous_states = []

        self.data_points_list = 0
        self.electrical_conductivity = 0
        self.surface_tension = 0
        self.dieletric_const = 0
        self.electrical_conductivity = 0
        self.permitivity = 0
        self.rho = 0
        self.density = 0




    def do_classification(
            self,
            mean,
            median,
            stddeviation,
            psd_values,
            variance,
            max_value_of_the_data,
            quantity_max_data,
            percentage_max,
            flow_rate,
            fft_max_peaks_array,
            cont_fft_max_peaks,
            I_chen_pui):

        self.med_value_array.append(median)
        classification_txt = "Undefined"


        #
        #       SJAAKS  -> Is capable of classifiying Dripping, Intermittent and Cone Jet
        #

        try:
                
            if mean != 0:
                self.sjaak_std_mean = (stddeviation / mean)
                # print("std/mean = %f ;" % (self.sjaak_std_mean))
            else:
                self.sjaak_std_mean = 0
            self.sjaak_std_mean_array.append(self.sjaak_std_mean)

            if median != 0:
                self.sjaak_mean_median = (mean / median)
                # print('sjaak_mean_median: ', self.sjaak_mean_median)
            else:
                self.sjaak_mean_median = 0
            self.sjaak_mean_median_array.append(self.sjaak_mean_median)

            # classification for dripping
            if mean <= 5:
                if self.sjaak_std_mean > 2.5:
                    #classification_txt = "Dripping"
                    if (self.sjaak_mean_median) < 0.9 or (self.sjaak_mean_median) > 1.1:
                        # print("classification dripping confirmed!")
                        classification_txt = "Dripping"

            # classification for intermittent
            if mean > 5:
                if (self.sjaak_std_mean) < 2.5 and self.sjaak_std_mean > 0.5:
                    # print("intermittent Sjaak!")
                    #classification_txt = "Intermittent"
                    if (self.sjaak_mean_median) < 0.9 or (self.sjaak_mean_median) > 1.1:
                        classification_txt = "Intermittent"

            # classification for cone-jet
            if mean > 5:  # replace absolut value with cone-jet current estimation by laMora/Calvo
                if self.sjaak_std_mean < 0.5:
                    #classification_txt = "Cone Jet"
                    if (self.sjaak_mean_median) > 0.9 and (self.sjaak_mean_median) < 1.1:
                        classification_txt = "Cone Jet"
                # print("Sjaak txt do_sjaak = ", classification_txt)

        except Exception as e:
            print("ERROR: ", str(e)) 
            print("Error on Sjaaks classification")


        #
        #       MONICA   -> Is capable of classifiying Corona Discharges
        #

        try:
            # use of fft_max_peaks_array (defined in the function calculate_peaks_fft of electrospray.py)
            # PEAKS SIGNAL
            # print("****************** MAX = " + str(max_value_of_the_data))

            if float(max_value_of_the_data) >= 900.0:
                if (float(flow_rate) / (2.7778e-7 * 10e-6)) <= 200.0:  # uL/h
                    if float(max_value_of_the_data) >= 2000.0:
                        classification_txt =  "Corona"
                    if percentage_max >= 0.0001:
                        classification_txt =  "Corona"
                    if quantity_max_data >= 5.0:
                        classification_txt =  "Corona"

                if (float(flow_rate) / (2.7778e-7 * 10e-6)) >= 200.0:  # uL/h
                    if float(max_value_of_the_data) >= 2000.0:
                        classification_txt =  "Corona"
                    if percentage_max >= 0.5:
                        classification_txt =  "Corona"
                    if quantity_max_data >= 10.0:
                        classification_txt =  "Corona"

            # PEAKS FFT
            # fft_max_peaks_array has info about the frequency and amplitude
            """
            if (flow_rate / (2.7778e-7 * 10e-6)) < 100:  # uL/h
                if cont_fft_max_peaks > 2:
                    return "streamer onset"
            if (flow_rate / (2.7778e-7 * 10e-6)) > 100:  # uL/h
                if cont_fft_max_peaks > 5:
                    return "streamer onset"""
            # a = np.asanyarray(data)
            # a = np.asanyarray(data)

            """sd0 = a.std(axis=0, ddof=0)
            SNR0 = np.where(sd0 == 0, 0, mean_value / sd0)
            return ("Signal to Noise Ratio : %s" % SNR0)"""

        except Exception as e:
            print("ERROR: ", str(e)) 
            print("Error on monica classification")


        # #
        # #       JOAO 乔昂   -> Is capable of classifiying Multi Jet

        print("current mean [nA]: ", mean)
        print("current std deviation [nA]:", stddeviation)

        # try:
        #     print("I chen pui:", I_chen_pui)  # Cone Jet mean current calculated by Chen&Pui Scaling Laws (See the formula in validation_electrospray file)
        #     if(classification_txt == "Cone Jet"):
        #         if(mean > 1.14 * I_chen_pui):   # 1.14 above was calculated experimentally for pure ethanol
        #             classification_txt = "Multi Jet"
        #
        #
        # except Exception as e:
        #     print("ERROR: ", str(e))
        #     print("Error on João classification")







        self.previous_states.append(classification_txt)

        return classification_txt






    def open_load_json_data(self, filename):
        with open(filename) as json_file:
            self.data_dict = json.load(json_file)
            print("\nconfig liquid:", self.data_dict['config']['liquid'])

    def read_print_json(liquid):
        f = open(liquid + ".json")
        # returns JSON object as a dictionary
        data = json.load(f)
        # Iterating through the json list
        for i in data['liquid']:
            print(i)

    def avg(self, xs):
        sum = 0
        for i in xs:
            sum += i
        return round((sum / len(xs)), 4)

    def estimate_avg(self, data):
        estimativas = []
        for i in range(0, len(data), 5):
            sample = data[i:i + 5]
            mean = self.avg(sample)
            estimativas.append(mean)

        #     plt.plot(estimativas)
        return self.avg(estimativas)

    def estimate_std(self, data):
        mean = self.estimate_avg(data)
        sum_aux = 0
        for i in data:
            sum_aux += ((i - mean) ** 2)

        var = (sum_aux / (len(data) - 1))
        return round(math.sqrt(var), 4)

