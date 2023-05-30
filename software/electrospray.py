"""
TITLE: electrospray class functions
"""

import numpy as np
import csv
import json
from scipy.signal import argrelextrema
from scipy import signal
from scipy.signal import hilbert
from scipy.signal import butter, lfilter


class ElectrosprayConfig:
    def __init__(self, file_setup):
        self.file_setup = file_setup
        self.ki = 6.46  # no units

    def __repr__(self):
        """dictionary = {
            "electrical conductivity": str(self.k_electrical_conductivity),
            "flow_rate": str(self.q_flow_rate),
            "voltage": str(self.voltage),
            "setup": str(self.json_setup_obj)
        }
        return "config: %s " % (json.dumps(dictionary))"""
        d = dict(
            config=dict(comment=str(self.current_comment),
                        flow_rate_min=str(self.flow_rate_min), type_of_measurement=str(self.typeofmeasurement)))
        return json.dumps(d, sort_keys=True)

    def load_json_config_setup(self):

        print("load_json_config_setup")
        # print(self.file_setup)
        
        with open(self.file_setup, 'r') as file:
            # First we load existing data into a dict.
            self.json_setup_obj = json.load(file)
            # print(type(self.json_setup_obj))

        """with open(self.file_setup) as json_file:
            self.json_setup_obj = json.load(json_file)"""

    def load_json_config_liquid(self, file_liquid):

        print("load_json_config_liquid")

        with open(file_liquid, 'r') as file:
            # First we load existing data into a dict.
            self.json_liquid_obj = json.load(file)
            print(self.json_liquid_obj)

        """with open(self.file_liquid) as json_file:
            self.json_liquid_obj = json.load(json_file) # dictionary"""

    def get_json_liquid(self):
        return self.json_liquid_obj

    def get_json_setup(self):
        return self.json_setup_obj

    def set_comment_current(self, current_comment):
        self.current_comment = current_comment

    def set_type_of_measurement(self, typeofmeasurement):
        self.type_of_measurement = typeofmeasurement

    def get_dict_config(self):
        dictionary = {
            "voltage regime": self.type_of_measurement
        }
        return dictionary

    def get_alpha_chen_pui(self):
        return ((self.γ * self.k_electrical_conductivity * self.q_flow_rate / self.k) ** (.5))

    # def get_cone_jet_current_est_chen_pui(self):
    # b = i_actual / ((self.γ * self.k_electrical_conductivity * self.q_flow_rate) ** .5)
    def get_flow_rate_min_ian(self):
        # print("\nconfig liquid:", self.data_dict['config']['liquid'])
        dieletric_const = self.json_liquid_obj['dielectric const']
        electrical_conductivity = self.json_liquid_obj['electrical conductivity']
        permitivity = self.json_liquid_obj['vacuum permitivity']
        surface_tension = self.json_liquid_obj['surface tension']
        rho = self.json_liquid_obj['density']
        self.flow_rate_min_ian = (permitivity * surface_tension / (rho * electrical_conductivity))
        return self.flow_rate_min_ian

    def flow_rate_min_est_chen_pui(self):
        # print("\nconfig liquid:", self.data_dict['config']['liquid'])
        dieletric_const = self.json_liquid_obj['dielectric const']
        electrical_conductivity = self.json_liquid_obj['electrical conductivity']
        permitivity = self.json_liquid_obj['vacuum permitivity']
        surface_tension = self.json_liquid_obj['surface tension']
        rho = self.json_liquid_obj['density']
        self.flow_rate_chen_pui = (
                (dieletric_const ** 0.5) * permitivity * surface_tension / (rho * electrical_conductivity))

    def get_flow_rate_min_est_chen_pui(self): 
        return self.flow_rate_chen_pui 
 
    def get_dict_flow_rate_min_est_chen_pui(self): 
        dictionary = { 
            "flow_rate_chen_pui": self.flow_rate_chen_pui 
        } 
        return dictionary 
 
    def get_cone_jet_current_est_hartman(self, i_actual): 
        b = i_actual / ((self.γ * self.k_electrical_conductivity * self.q_flow_rate) ** .5) 
        # b = I_actual/pow((y * K * Q), (1/2)) 
        I_hartman = b * ((self.γ * self.k_electrical_conductivity * self.q_flow_rate) ** .5) 
        b = 0.5 
        I_hartman_05 = b * ((self.γ * self.k_electrical_conductivity * self.q_flow_rate) ** .5) 
        b = 2 
        I_hartman_2 = b * ((self.γ * self.k_electrical_conductivity * self.q_flow_rate) ** .5) 
        return I_hartman, I_hartman_05, I_hartman_2 


# *****************************************
#             MEASUREMENTS
# *****************************************

class ElectrosprayMeasurements:
    """ Electrospray setup representation """

    def __init__(self, name, data, voltage, flow_rate, temperature, humidity, day_measurement, current, target_voltage):
        self.name = name  # name of liquid
        self.data = data  # array nA
        self.flow_rate = flow_rate  # m3/s
        self.voltage = voltage  # Volt
        self.temperature = temperature  # degree Celsius
        self.humidity = humidity  # relative percentage
        self.day_measurement = day_measurement  # date
        # self.gas_coflow_rate  = gas_coflow_rate
        self.current = current
        self.target_voltage = target_voltage

    def __repr__(self):
        dictionary = {
            "current": str(self.data.tolist()),  # array nA
            "flow_rate": self.flow_rate,
            "voltage": self.voltage,
            "current_PS": self.current,
            "temperature": self.temperature,  # graus Celsius
            "humidity": self.humidity,  # percentage
            "date_and_time": self.day_measurement,
            "target_voltage": self.target_voltage
        }

        return (json.dumps(dictionary))

    def get_measurements_dictionary(self):
        dictionary = {
            "name": self.name,
            "current": self.data.tolist(),  # array nA
            "flow_rate": self.flow_rate,
            "voltage": str(self.voltage),
            "current_PS": str(self.current),
            "temperature": str(self.temperature),  # graus Celsius
            "humidity": str(self.humidity),  # percentage
            "date_and_time": str(self.day_measurement),
            "target_voltage": self.target_voltage
        }
        # self.json_measurements_obj.write(json.dumps((dictionary), sort_keys=True, indent=4, separators=(". ", " = ")))
        return dictionary

    def get_flow_rate_actual(self):
        return self.flow_rate

    def get_measurements(self):
        return self.name, self.data, self.voltage,  self.flow_rate, self.impedance, self.temperature, self.humidity, self.current, self.shape_current, self.target_voltage

    def set_data(self, data_update):
        self.data = data_update  # array nA

    def set_voltage(self, voltage_update):
        self.voltage = voltage_update



# *****************************************
#             PROCESSING
# *****************************************


class ElectrosprayDataProcessing:
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.mean_value = 0
        self.variance = 0
        # is a squared mean value of values of the average,
        # square because it avoids cancellation of values below and above mean
        self.stddev = 0  # is the sqrt(variance)
        self.med = 0
        self.rms = 0
        self.psd_welch = 0
        self.datapoints_filtered = []
        self.fourier_transform = []
        self.fourier_transform_filtered = []
        self.freq = []
        self.fourier_peaks = []
        self.all_fourier_peaks = []
        self.shape_current = ""


    # expected are the polinominal coef for denominator and numerator for filter function
    def calculate_filter(self, a_coef, b_coef, datapoints):
        # low pass filter to flatten out noise
        self.datapoints_filtered = lfilter(b_coef, a_coef, datapoints)

    def calculate_fft_raw(self, datapoints):
        # low pass filter to flatten out noise
        # self.datapoints_filtered = lfilter(b, a, self.data)
        # fourier transform, results in the complex discrete fourier coefficients
        time_step = 1 / self.sample_rate
        self.fourier_transform = np.fft.fft(datapoints)
        # fourier_transform = np.fft.fft(data_filtered)
        self.freq = np.fft.fftfreq(datapoints.size, d=time_step)

    def calculate_fft_filtered(self):
        # low pass filter to flatten out noise
        # fourier transform, results in the complex discrete fourier coefficients
        time_step = 1 / self.sample_rate
        self.fourier_transform_filtered = np.fft.fft(self.datapoints_filtered)
        self.freq = np.fft.fftfreq(self.datapoints_filtered.size, d=time_step)  # better to use data.size

    def calculate_fft_peaks(self):
        # order – How many points on each side to use for the comparison to consider ``comparator(n, n+x)`` to be True.
        # mode – How the edges of the vector are treated. 'wrap' (wrap around) or 'clip' (treat overflow as the same as the last (or first) element). Default is 'clip'. See `numpy.take`.
        self.all_fourier_peaks = \
            argrelextrema(abs(self.fourier_transform[0:200]), comparator=np.greater, order=3, mode='wrap')[
                0]  # returns indices

        if len(self.all_fourier_peaks) > 0:
            # print("rel max fourier: %s" % self.fourier_peaks)
            sorted_indices = np.argsort(abs(self.fourier_transform[self.all_fourier_peaks]))

            freq_step = self.freq[1] - self.freq[0]
            self.fourier_peaks.append("1st: ")
            self.fourier_peaks.append([abs(self.fourier_transform[self.all_fourier_peaks[sorted_indices[-1]]]),
                                       freq_step * self.all_fourier_peaks[sorted_indices[-1]]])
        if len(self.all_fourier_peaks) > 1:
            self.fourier_peaks.append("2nd: ")
            self.fourier_peaks.append([abs(self.fourier_transform[self.all_fourier_peaks[sorted_indices[-2]]]),
                                       freq_step * self.all_fourier_peaks[sorted_indices[-2]]])

        if len(self.all_fourier_peaks) > 2:
            self.fourier_peaks.append("3rd: ")
            self.fourier_peaks.append([abs(self.fourier_transform[self.all_fourier_peaks[sorted_indices[-3]]]),
                                       freq_step * self.all_fourier_peaks[sorted_indices[-3]]])
        """
        # height = fourier_peaks_find_peaks[1]['peak_heights']  # list containing the height of the peaks
        # peak_pos = fourier_peaks_find_peaks[0] 
         # list containing the positions of the peaks
        """

    def calculate_statistics(self, data):
        self.mean_value = np.mean(data)
        self.variance = np.var(data)
        # is a squared mean value of values of the average,
        # square because it avoids cancellation of values below and above mean
        self.stddev = np.std(data)  # is the sqrt(variance)
        self.med = np.median(data)
        self.rms = np.sqrt(np.mean(data ** 2))

        
    def calculate_peaks_fft(self, data):
        sorted_indices = np.argsort(abs(self.fourier_transform[self.all_fourier_peaks]))
        freq_step = self.freq[1] - self.freq[0]
        cont = 0
        fourier_peaks_array = []
        # if abs(self.fourier_transform[self.all_fourier_peaks[sorted_indices[-1]]])

        for i in range(len(self.all_fourier_peaks)):
            # above 50 Hz
            if (freq_step * self.all_fourier_peaks[sorted_indices[-i]]) > 50:

                if (abs(self.fourier_transform[self.all_fourier_peaks[sorted_indices[-i]]])) > 1500:
                    cont = cont + 1
                    fourier_peaks_array.append([abs(self.fourier_transform[self.all_fourier_peaks[sorted_indices[-i]]]),
                                                freq_step * self.all_fourier_peaks[sorted_indices[-i]]])

        return fourier_peaks_array, cont

    def calculate_peaks_signal(self, data):
        quantity_max_data = 0
        max_data = max(data)
        for i in range(0, int(len(data))):
            if data[i] == max_data:
                quantity_max_data = quantity_max_data + 1
        percentage_max = (quantity_max_data / 50000) * 100
        # print(max_data)
        # print(quantity_max_data)
        # print(percentage_max)
        # print("*************")
        return max_data, quantity_max_data, percentage_max

    def calculate_power_spectral_density(self, data):
        """
        # The above definition of energy spectral density is suitable for
         transients (pulse-like signals) whose energy is concentrated
          around one time window; then the Fourier transforms of the
          signals generally exist. For continuous signals over all time,
          one must rather define the power spectral density (PSD) which
          exists for stationary processes; this describes how power of
          a signal or time series is distributed over frequency, as in
          the simple example given previously. Here, power can be the
          actual physical power, or more often, for convenience with
          abstract signals, is simply identified with the squared value
          of the signal. For example, statisticians study the variance
          of a function over time {\displaystyle x(t)}x(t) (or over
          another independent variable), and using an analogy with
          electrical signals (among other physical processes), it is
          customary to refer to it as the power spectrum even when there
          is no physical power involved.

          The spectrum analyzer measures the magnitude of the short-time
          Fourier transform (STFT) of an input signal. If the signal being
          analyzed can be considered a stationary process, the STFT is a
          good smoothed estimate of its power spectral density.
       """
        freqs, self.psd_welch = signal.welch(data)
        
        return freqs, self.psd_welch

    # string representation of this class
    def __repr__(self):
        d = dict(mean=str(self.mean_value),
                variance=str(self.variance),
                deviation=str(self.stddev),
                median=str(self.med),
                rms=str(self.rms),
                shape_current=self.shape_current,
                #  psd_welch=str(self.psd_welch.tolist()),
                # fourier_transform=str(self.fourier_transform),
                # total_variation_distance=str(self.total_variation_distance),
                freq=str(self.freq.tolist()),
                fourier_peaks=str(self.fourier_peaks))
        return (json.dumps(d, sort_keys=True))

    def get_statistics_dictionary(self):
        dictionary = {
            "mean": np.float64(self.mean_value),
            "variance": np.float64(self.variance),
            "deviation": np.float64(self.stddev),
            "median": np.float64(self.med),
            "rms": np.float64(self.rms),
            "spray_mode": self.shape_current[0],
            # "psd welch": self.psd_welch.tolist(),
            # "fourier peaks": self.fourier_peaks,
            # "maximum variation distance": np.float64(self.total_variation_distance),
            # "freq": self.freq.tolist()
        }
        return dictionary

    def set_electrical_conductivity(self, K):
        self.k_electrical_conductivity = K

    def set_flow_rate(self, Q):
        self.q_flow_rate = Q

    def set_voltage(self, voltage):
        self.voltage = voltage

    def set_shape(self, shape_current):
        self.shape_current = shape_current