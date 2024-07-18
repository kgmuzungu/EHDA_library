#  *************************************
# 	Class classification
#  *************************************

import itertools
import os
import re
from typing import TextIO
import numpy as np
import json
import math

import pandas as pd


class ElectrosprayClassification:

    def __init__(self, name_liquid):
        self.ml_median = 0.0
        self.nn_median = 0.0
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
        self.cone_jet_mean = 0
        self.nozzle_outer_radius = 0.00068

        f = open("../software/setup/liquid/" + self.name_liquid + ".json")
        data_dict = json.load(f)
        self.surface_tension = data_dict['surface tension']
        self.permitivity_of_vacum = data_dict['vacuum permitivity']
        self.density = data_dict['density']
        self.conductivity = data_dict['electrical conductivity']

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
                    # classification_txt = "Dripping"
                    if (self.sjaak_mean_median) < 0.9 or (self.sjaak_mean_median) > 1.1:
                        # print("classification dripping confirmed!")
                        classification_txt = "Dripping"

            # classification for intermittent
            if mean > 5:
                if (self.sjaak_std_mean) < 2.5 and self.sjaak_std_mean > 0.5:
                    # print("intermittent Sjaak!")
                    # classification_txt = "Intermittent"
                    if (self.sjaak_mean_median) < 0.9 or (self.sjaak_mean_median) > 1.1:
                        classification_txt = "Intermittent"

            # classification for cone-jet
            if mean > 5:  # replace absolut value with cone-jet current estimation by laMora/Calvo
                if self.sjaak_std_mean < 0.5:
                    # classification_txt = "Cone Jet"
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

            # if float(max_value_of_the_data) >= 2000.0:  # if a single data point is equal or greater than 2microAmp = 2000
            # classification_txt =  "Corona"
            if percentage_max >= .5:  # percentage of values >= 2000.0nA in one data set of 50kpts, like 10.4 for 10.4%
                classification_txt = "Corona"
            # if quantity_max_data >= 5.0:
            # classification_txt =  "Corona"

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

        if False:
            try:
                print("I chen pui:",
                      I_chen_pui)  # Cone Jet mean current calculated by Chen&Pui Scaling Laws (See the formula in validation_electrospray file)
                if (classification_txt == "Cone Jet"):
                    if (mean > 1.14 * I_chen_pui):  # 1.14 above was calculated experimentally for pure ethanol
                        classification_txt = "Multi Jet"
            except Exception as e:
                print("ERROR: ", str(e))
                print("Error on João classification")

        if False:  # classifiying Multi jet by cone jet mean of previous classifications
            try:
                # print(self.previous_states[-5:])
                if (classification_txt == "Cone Jet") and self.cone_jet_mean == 0 and (
                        self.previous_states[-5:] == ['Cone Jet', 'Cone Jet', 'Cone Jet', 'Cone Jet', 'Cone Jet']):
                    self.cone_jet_mean = mean

                if (classification_txt == "Cone Jet") and self.cone_jet_mean != 0:
                    if (mean > 1.14 * self.cone_jet_mean):
                        classification_txt = "Multi Jet"


            except Exception as e:
                print("ERROR: ", str(e))
                print("Error on João classification")

        #
        #       Correcting some wrongly classified modes by the system knowledge and memory
        #
        # try:
        #     if(classification_txt == "Dripping") and (self.previous_states[-1] == "Cone Jet" or self.previous_states[-1] == "Multi Jet"):
        #         classification_txt = "Undefined"
        # except Exception as e:
        #     print("ERROR: ", str(e))
        #     print("Error on correcting classification")

        self.previous_states.append(classification_txt)

        return classification_txt

    def do_generalist_ml_classification(
            self,
            model,
            mean,
            variance,
            std_dev,
            median,
            rms,
            voltage,
            flow_rate
    ):

        classification_txt = "Undefined"

        ulmin_to_m3s = 1.67E-11

        qzero = ((self.surface_tension * self.permitivity_of_vacum) / (self.density * self.conductivity)) * 10000000000

        vzero = (2 * self.surface_tension * self.nozzle_outer_radius)

        flow_rate = float(flow_rate)

        try:
            if median == 0:
                self.ml_median = 1e-323
            else:
                self.ml_median = median

            mean_over_median = mean / self.ml_median

            std_dev_over_median = std_dev / self.ml_median

            undimensional_flowrate = flow_rate * ulmin_to_m3s / qzero

            undimensional_voltage = (voltage ** 2 * self.permitivity_of_vacum) / vzero

            classification_txt = model.predict([[mean, variance, std_dev, self.ml_median, rms, voltage, flow_rate,
                                                 undimensional_flowrate, undimensional_voltage, mean_over_median,
                                                 std_dev_over_median]])

            if classification_txt == 0:
                classification_txt = "Cone Jet"
            elif classification_txt == 1:
                classification_txt = "Corona"
            elif classification_txt == 2:
                classification_txt = "Dripping"
            elif classification_txt == 3:
                classification_txt = "Intermittent"
            elif classification_txt == 4:
                classification_txt = "Multi Jet"
            else:
                classification_txt = "Undefined"

            return classification_txt

        except Exception as e:
            print("ERROR: ", str(e))
            print("Error on Generalist Machine Learning Model classification")

    def do_ml_classification(
            self,
            model,
            mean,
            variance,
            std_dev,
            median,
            rms,
            voltage,
            flow_rate,
            temperature,
            humidity
    ):

        classification_txt = "Undefined"

        ulmin_to_m3s = 1.67E-11

        qzero = ((self.surface_tension * self.permitivity_of_vacum) / (self.density * self.conductivity)) * 10000000000

        vzero = (2 * self.surface_tension * self.nozzle_outer_radius)

        flow_rate = float(flow_rate)

        try:
            if median == 0:
                self.ml_median = 1e-323
            else:
                self.ml_median = median

            mean_over_median = mean / self.ml_median

            std_dev_over_median = std_dev / self.ml_median

            undimensional_flowrate = flow_rate * ulmin_to_m3s / qzero

            undimensional_voltage = (voltage ** 2 * self.permitivity_of_vacum) / vzero

            classification_txt = model.predict([[mean, variance, std_dev, self.ml_median, rms, voltage, flow_rate,
                                                 undimensional_flowrate, undimensional_voltage, temperature, humidity,
                                                 mean_over_median, std_dev_over_median]])

            if classification_txt == 0:
                classification_txt = "Cone Jet"
            elif classification_txt == 1:
                classification_txt = "Dripping"
            elif classification_txt == 2:
                classification_txt = "Intermittent"
            elif classification_txt == 3:
                classification_txt = "Multi Jet"
            else:
                classification_txt = "Undefined"

            return classification_txt

        except Exception as e:
            print("ERROR: ", str(e))
            print("Error on Machine Learning Model classification")

    def do_nn_classification(
            self,
            model,
            mean,
            variance,
            std_dev,
            median,
            rms,
            voltage,
            flow_rate,
            temperature,
            humidity
    ):

        classification_txt = "Undefined"

        ulmin_to_m3s = 1.67E-11

        qzero = ((self.surface_tension * self.permitivity_of_vacum) / (self.density * self.conductivity)) * 10000000000

        vzero = (2 * self.surface_tension * self.nozzle_outer_radius)

        flow_rate = float(flow_rate)

        try:
            if median == 0:
                self.nn_median = 1e-323
            else:
                self.nn_median = median

            mean_over_median = mean / self.nn_median

            std_dev_over_median = std_dev / self.nn_median

            undimensional_flowrate = flow_rate * ulmin_to_m3s / qzero

            undimensional_voltage = (voltage ** 2 * self.permitivity_of_vacum) / vzero

            classification_txt = model.predict([[mean, variance, std_dev, self.nn_median, rms, voltage, flow_rate,
                                                 undimensional_flowrate, undimensional_voltage, temperature, humidity,
                                                 mean_over_median, std_dev_over_median]])

            return classification_txt[0]

        except Exception as e:
            print("ERROR: ", str(e))
            print("Error on Neural Network classification")

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
