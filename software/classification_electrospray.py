import itertools
import os
import re
from typing import TextIO
import logging
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

        self.data_points_list = 0
        self.electrical_conductivity = 0
        self.surface_tension = 0
        self.dieletric_const = 0
        self.electrical_conductivity = 0
        self.permitivity = 0
        self.rho = 0
        self.density = 0


    def do_sjaak(self, mean, median, stddeviation, psd_values, variance):
        self.med_value_array.append(median)
        sjaak_classification_txt = ""

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
        # if mean <= 5:
        if self.sjaak_std_mean > 2.5:
            sjaak_classification_txt = "Dripping"
            if (self.sjaak_mean_median) < 0.9 or (self.sjaak_mean_median) > 1.1:
                # logging.info("Dripping Sjaak")
                # print("classification dripping confirmed!")
                sjaak_classification_txt = "Dripping"

        # classification for intermittent
        # if mean > 5:
        if (self.sjaak_std_mean) < 2.5 and self.sjaak_std_mean > 0.5:
            # print("intermittent Sjaak!")
            sjaak_classification_txt = "Intermittent"
            if (self.sjaak_mean_median) < 0.9 or (self.sjaak_mean_median) > 1.1:
                sjaak_classification_txt = "Intermittent"

            # ToDo: check this value different conditions
            """if psd_values.any() > 0.2 and psd_values.any() < 0.75:
                logging.info("Intermittent psd Sjaak")
                #logging.info("************")"""

        # classification for cone-jet
        # if mean > 10:  # ToDo replace absolut value with cone-jet current estimation by laMora/Calvo
        if self.sjaak_std_mean < 0.3:
            sjaak_classification_txt = "Cone Jet"
            if (self.sjaak_mean_median) > 0.9 or (self.sjaak_mean_median) < 1.1:
                sjaak_classification_txt = "Cone Jet"
        # print("Sjaak txt do_sjaak = ", sjaak_classification_txt)

        return sjaak_classification_txt

    @staticmethod
    def do_monica(max_value_of_the_data, quantity_max_data, percentage_max, flow_rate, fft_max_peaks_array,
                  cont_fft_max_peaks):
        # todo: use of fft_max_peaks_array (defined in the function calculate_peaks_fft of electrospray.py)
        # PEAKS SIGNAL
        # print("****************** MAX = " + str(max_value_of_the_data))
        if float(max_value_of_the_data) >= 900.0:
            if (flow_rate / (2.7778e-7 * 10e-6)) <= 200.0:  # uL/h
                if float(max_value_of_the_data)>= 2000.0:
                    return "streamer onset"
                if percentage_max >= 0.0001:
                    return "streamer onset"
                if quantity_max_data >= 5.0:
                    return "streamer onset"

            if (flow_rate / (2.7778e-7 * 10e-6)) >= 200.0:  # uL/h
                if float(max_value_of_the_data)>= 2000.0:
                    return "streamer onset"
                if percentage_max >= 0.5:
                    return "streamer onset"
                if quantity_max_data >= 10.0:
                    return "streamer onset"

        else:
            return "no streamer onset"

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

        """sd0 = a.std(axis=0, ddof=0)
        SNR0 = np.where(sd0 == 0, 0, mean_value / sd0)
        return ("Signal to Noise Ratio : %s" % SNR0)"""

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


    """
    def plot_sjaak_cone_jet(self):
        values = ["sjaak_std_mean_array ]2.5", "sjaak_mean_median_array ]0.9,1.1[", "mean_value_array ]1",
                  "med_value_array ]0"]
        fig, axs = plt.subplots(6)
        data = [self.sjaak_std_mean_array, self.sjaak_mean_median_array, self.mean_value_array,
                self.sjaak_std_mean_array]
        axs[0].set(xlabel=values)
        axs[0].set_title(self.name_liquid)
        axs[0].boxplot(data)

        x0 = []
        for i in range(len(self.sjaak_std_mean_array)):
            x0.append(i)
        colors = 'black'
        axs[1].scatter(x0, self.sjaak_std_mean_array, c=colors, marker='^',
                       label="sjaak_std_mean_array %s" % self.name_liquid)
        axs[1].axhline(2.5, color=colors, lw=2, alpha=0.5)
        axs[1].legend(loc='best')

        colors = 'green'
        axs[2].scatter(x0, self.sjaak_mean_median_array, c=colors, marker="s",
                       label="sjaak_mean_median_array %s" % (self.name_liquid))
        # sjaak_mean_median cone jet values
        axs[2].axhline(0.9, color=colors, lw=2, alpha=0.5)
        axs[2].axhline(1.1, color=colors, lw=2, alpha=0.5)
        axs[2].legend(loc='best')

        x0 = []
        for i in range(len(self.mean_value_array)):
            x0.append(i)
        colors = 'blue'
        axs[3].scatter(x0, self.mean_value_array, c=colors, marker=">", label="mean_value_array %s" % self.name_liquid)
        axs[3].axhline(1, color=colors, lw=2, alpha=0.5)
        axs[3].legend(loc='best')

        x0 = []
        for i in range(len(self.med_value_array)):
            x0.append(i)
        colors = 'yellow'
        # for i in range(len(med_value_array[j])):
        axs[4].scatter(x0, self.med_value_array, c=colors, marker="<", label="med_value_array %s" % (self.name_liquid))
        axs[4].axhline(0, color=colors, lw=2, alpha=0.5)
        axs[4].legend(loc='best')

        x0 = []
        for i in range(len(self.med_value_array)):
            x0.append(i)
        axs[5].scatter(x0, self.med_value_array, c=colors, marker="<", label="med_value_array %s" % (self.name_liquid))
        # plt.scatter([pt[i] for pt in x0[j]], [pt[i] for pt in med_value_array[j]], c=colors, marker="<")
        # med_value
        axs[5].axhline(0, color=colors, lw=2, alpha=0.5)
        x0.append([])
        axs[5].legend(loc='best')

    def plot_sjaak_classification(self):
        values = ["sjaak_std_mean_array", "sjaak_mean_median_array", "mean_value_array",
                  "med_value_array"]
        fig, axs = plt.subplots(2)
        # for j in range(1):
        data_1 = np.array(self.sjaak_std_mean_array)
        data_2 = np.array(self.sjaak_mean_median_array)  # , 0.99, 0.9, 1.1))
        data_3 = np.array(self.mean_value_array)  # , stddev_value_array[j])
        data_4 = np.array(self.med_value_array)
        data = [data_1, data_2, data_3, data_4]
        axs[0].set(xlabel=values)
        axs[0].set_title(self.name_liquid)
        axs[0].boxplot(data, vert=True)

        nbins = [0, 1]
        colors = ['Red', 'Lime']
        labels = ['Sjaak classified false', 'Sjaak classified true']
        bars = ["0/False" + self.name_liquid, "1/True" + self.name_liquid]
        sjaak_verified_true_aux = (np.ones(len(self.sjaak_verified_true)))
        sjaak_verified_false_aux = (np.zeros(len(self.sjaak_verified_false)))
        x = [sjaak_verified_false_aux, sjaak_verified_true_aux]
        axs[1].hist(x, nbins, density=True, histtype='bar', color=colors, label=labels)
        axs[1].grid(axis='y', alpha=0.75)
        axs[1].set(xlabel=bars, ylabel=nbins, title='%s' % self.name_liquid)
        plt.hold(True)

        axs[2].set(xlabel=values[2])
        axs[2].boxplot(data_2, vert=True)
        axs[3].set(xlabel=values[3])
        axs[3].boxplot(data_3, vert=True)
        plt.show()
        
    def plot_mean(self, mean_value, datapoints):
        # Display mean_value
        # mean_value_plotrealtime = np.full(datapoints, mean_value)  # create a mean value line
        # plt.plot(mean_value_plotrealtime)
        plt.text(0.01, 0.01, 'mean = ' + str(np.round("mean_value_plotrealtime", 1)), fontsize=16, color='C1')

"""
