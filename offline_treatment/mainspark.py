import json
import os
import re
import json
import numpy as np
from scipy.signal import find_peaks_cwt
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from scipy.signal import find_peaks


res = ""
listdir = os.listdir()
j = 0
plt.style.use('seaborn-colorblind')
plt.ion()

for i in listdir:
    res = re.search("json", i)
    if res == None:
        continue
    else:
        # print(i)
        filename = i
        print(filename)

        j = j + 1
        if j == 1:
            print("fast single drop")
            print("************")
            # mean_value - med < 1
            # mean_Value < 1

        elif j == 3:
            c = "fast dripping"
            print("fast dripping")
            print("************")
        elif j == 4:
            c = "pre cone jet"
            print("pre cone jet")
            print("************")
        elif j == 5:
            # stddev < 4

            c = "cone jet"
            print("cone jet")
            print("************")
        elif j == 6:
            c = "multi jet"
            print("multi jet")
            print("************")
        elif j == 7:
            c = "corona noise"
            print("corona noise")
            print("************")
        else:
            print("we need more data to classify")


        with open(filename) as jsonFile:
            jsonObject = json.load(jsonFile)
            jsonFile.close()

        try:
            data = np.array(jsonObject[0]['data']) * 1000  # values in nA
            bandwidth = int(jsonObject[0]['bandwidth'])
            data_points = int(jsonObject[0]['datasize'])
            sampling_frequency = int(jsonObject[0]['samplefrequency'])

            time_step = 1 / sampling_frequency
            time_max = time_step * data_points

        #   statistics
            mean_value = np.mean(data)
            variance = np.var(data)  # is a squared mean value of values of the average, square because it avoids cancellation of values below and above mean
            stddev = np.std(data)  # is the sqrt(variance)
            med = np.median(data)  # mediana


            inf = np.percentile(data, 2.5)
            sup = np.percentile(data, 97.5)
        #   Range = Highest_value – Lowest_value
            rang_confidence = sup - inf
            # rang = range(data)

            print('confidence interval, with 95% confidence inf, sup limits =')
            print(inf, sup)
            print('data_points, bandwidth, sampling_frequency, time_step, mean_value, variance, desvio, mediana, rangconfidence')
            print(data_points, bandwidth, sampling_frequency, time_step, mean_value, variance, stddev, med,  rang_confidence)

            # time axes
            t = np.arange(0.0, time_max, time_step)  # time axes, time steps size is 1 / (sample frequences)

            # low pass filter to flatten out noise
            cutoff_freq_normalized = 1500 / (0.5 * sampling_frequency)  # in Hz
            b, a = butter(6, Wn=cutoff_freq_normalized, btype='low',
                          analog=False)  # first argument is the order of the filter
            data_filtered = lfilter(b, a, data)
            # check here to plot the transfer function of the filter
            # https://stackoverflow.com/questions/25191620/creating-lowpass-filter-in-scipy-understanding-methods-and-units

            # fourier transform, results in the complex discrete fourier coefficients
            fourier_transform = np.fft.fft(data)
            # fourier_transform = np.fft.fft(data_filtered)
            freq = np.fft.fftfreq(data_points, d=time_step)
            # print("peaks fourier: " + str(find_peaks(abs(fourier_transform)[0:500], threshold=1e5)))
            # find_peaks uses wavelet convolution (implicit filtering)
            # fourier_snippet = abs(fourier_transform[0:500])
            # fourier_peaks = argrelextrema(abs(fourier_transform), comparator=np.greater, order=20)
            fourier_peaks = argrelextrema(abs(fourier_transform[0:500]), comparator=np.greater, order=15)[0]
            print("rel max fourier: %s" % fourier_peaks)
            # argrelextrema uses trivial algorithm (no filtering). the order param provides some sort of filtering
            # abs_fourier_values = abs(fourier_transform)

            # gradient
            # data set needs to be filtered first
            # gradient = np.gradient(data)
            gradient = np.gradient(data_filtered)
            gradient_variance = np.var(gradient)
            gradient_stddev = np.std(gradient)

            print("gradient var = %f" % gradient_variance)
            print("gradient stddev = %f" % gradient_stddev)
            # gradient = np.diff(data, n=1)  # basically the same as gradient, n= order of derivative

            #peakidx = signal.find_peaks_cwt(y_array, np.arange(10, 15), noise_perc=0.1)
            # plot
            mean_value_plot = np.full(data_points, mean_value)  # create a mean value line
            # s = 1 + np.sin(2 * np.pi * t)
            fig, axs = plt.subplots(5)

            axs[0].plot(t, data)
            axs[0].plot(t, mean_value_plot)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.text.html#matplotlib.pyplot.text
            fig.text(0.01, 0.01, 'mean = ' + str(np.round(mean_value, 1)), fontsize=16, color='C1')
            axs[0].set(xlabel='time [s]', ylabel='current (nA)', title='osci reading')
            axs[0].grid()


            axs[2].set(xlabel='frequency [Hz]', ylabel='mag', title='fourier transform')
            axs[2].plot(freq, abs(fourier_transform))
            # axs[2].plot(freq[50000:50500], abs(fourier_transform[50000:50500]))  # freq????
            # axs[2].plot(freq[(int(len(freq)/2)):(int(len(freq)/2) + 500)], abs(fourier_transform[0:500]))  # freq????
            # print(abs(fourier_transform[100]))
            for i in fourier_peaks:  # mais que 50k
                # print(abs(fourier_transform[i]))
                axs[2].scatter(freq[i], abs(fourier_transform[i]), s=50, c='r', marker='x')  # set a marker
            # print(len(i))


            axs[3].plot(t, gradient)
            axs[3].set(xlabel='time', ylabel='values', title='gradient')
            axs[3].grid()


            axs[1].plot(t, data_filtered)
            axs[1].set(xlabel='time', ylabel='nA', title='LP filtered')
            axs[1].grid()
            # fig.savefig("test.png")


            # axs[4].plot(t, data)
            axs[4].hist(data, density=True)
            axs[4].set(xlabel='quantity', ylabel='values in data', title='histogram')

            """
            
            PASSBAND
            
            
            TRANSIENT
            
            STOPBAND
            
            SIGNAL PROCESSING PYTHON
            
            
            
            # detection of local minimums and maximums
            # simple one-step differencing will detect a sudden drop from a previous value
            # y_a' = y_a - y_(a-n)
            # n = size period
    
            a = np.diff(np.sign(np.diff(data))).nonzero()[0] + 1  # local min & max
            b = (np.diff(np.sign(np.diff(data))) > 0).nonzero()[0] + 1  # local min
            c = (np.diff(np.sign(np.diff(data))) < 0).nonzero()[0] + 1  # local max
            # +1 due to the fact that diff reduces the original index number
    
            axs[4].plot(t, data)
            axs[4].plot(t, data, color='grey')
            # plt.plot(x[b], data[b], "o", label="min", color='r')
            axs[4].plot(t[c], data[c], "o", label="max", color='b')
            """
            plt.show()

        except KeyError:
            print("we need more data to classify")



