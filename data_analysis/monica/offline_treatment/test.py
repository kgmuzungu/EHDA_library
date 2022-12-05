import json
import os
import re
import numpy as np
from scipy import signal
import scipy.fftpack
from scipy.fft import fftshift
from scipy.signal import find_peaks_cwt
from scipy.signal import argrelextrema
from scipy.fft import irfft
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from scipy.signal import find_peaks
from matplotlib import pyplot
from scipy import stats
import time


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
        data = load(filename)

        """
        >> mat2json('teste.mat', 'out.json')
        Unrecognized function or variable 'mat2json'.
         
        >> mat2json('teste.mat')
        Unrecognized function or variable 'mat2json'.
         
        >> txt = jsonencode(a)
        """

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
            variance = np.var(
                data)  # is a squared mean value of values of the average, square because it avoids cancellation of values below and above mean
            stddev = np.std(data)  # is the sqrt(variance)
            med = np.median(data)  # mediana

            inf = np.percentile(data, 2.5)
            sup = np.percentile(data, 97.5)
            #   Range = Highest_value – Lowest_value
            data_max = max(data)
            data_min = min(data)
            rang = data_max - data_min
            rang_confidence = sup - inf

            print('confidence interval, with 95% confidence inf, sup limits =')
            print(inf, sup)
            print(
                'data_points, bandwidth, sampling_frequency, time_step, mean_value, variance, desvio, mediana, range, rangconfidence')
            print(data_points, bandwidth, sampling_frequency, time_step, mean_value, variance, stddev, med, rang,
                  rang_confidence)

            # time axes
            t = np.arange(0.0, time_max, time_step)  # time axes, time steps size is 1 / (sample frequences)

            # low pass filter to flatten out noise
            cutoff_freq_normalized = 1500 / (0.5 * sampling_frequency)  # in Hz
            b, a = butter(6, Wn=cutoff_freq_normalized, btype='low',
                          analog=False)  # first argument is the order of the filter
            data_filtered = lfilter(b, a, data)
            # check here to plot the transfer function of the filter
            # https://stackoverflow.com/questions/25191620/creating-lowpass-filter-in-scipy-understanding-methods-and-units

            sum_tvd = 0
            # Total Variation Distance (TVD)
            for i in range(0, data_points):
                sum_tvd = sum_tvd + abs(data[i] - data_filtered[i])
            proportional_sum = sum_tvd/2
            print('Total Variation Distance (TVD) = %f ' % proportional_sum)

            # fourier transform, results in the complex discrete fourier coefficients
            fourier_transform = np.fft.fft(data)
            # fourier_transform = np.fft.fft(data_filtered)
            freq = np.fft.fftfreq(data_points, d=time_step)
            # print("peaks fourier: " + str(find_peaks(abs(fourier_transform)[0:500], threshold=1e5)))
            # find_peaks uses wavelet convolution (implicit filtering)
            # fourier_snippet = abs(fourier_transform[0:500])
            # fourier_peaks = argrelextrema(abs(fourier_transform), comparator=np.greater, order=20)
            fourier_peaks = argrelextrema(abs(fourier_transform[0:500]), comparator=np.greater, order=15)[0]

            start = time.time()
            freqs_welch, psd_welch = signal.welch(data, sampling_frequency)
            # print("freqs = max: %s, min: %s X; psd = max: %s, mean: %s, min: %s, elevado: %s  " % (freqs.max(), freqs.min(), psd.max(), psd.mean(), psd.min(), pow(fourier_peaks,2)))
            end = time.time()
            print(end - start)

            start = time.time()
            freqs_periodogram, psd_periodogram = signal.periodogram(data, sampling_frequency)
            # print("freqs = max: %s, min: %s X; psd = max: %s, mean: %s, min: %s, elevado: %s  " % (freqs.max(), freqs.min(), psd.max(), psd.mean(), psd.min(), pow(fourier_peaks,2)))
            end = time.time()
            print(end - start)

            print("rel max fourier: %s" % fourier_peaks)
            # argrelextrema uses trivial algorithm (no filtering). the order param provides some sort of filtering
            # abs_fourier_values = abs(fourier_transform)

            # gradient data set needs to be filtered first
            # gradient = np.gradient(data)
            gradient = np.gradient(data_filtered)
            gradient_variance = np.var(gradient)
            gradient_stddev = np.std(gradient)
            print("gradient var = %f" % gradient_variance)
            print("gradient stddev = %f" % gradient_stddev)
            # gradient = np.diff(data, n=1)  # basically the same as gradient, n= order of derivative
            print(" std/mean = %f ;" % (stddev/mean_value))
            print("mean-median = %f ;" % (mean_value/med))
            print("avarage development-relaxation ratios = %f ;" % (mean_value/med))

            # peakidx = signal.find_peaks_cwt(y_array, np.arange(10, 15), noise_perc=0.1)
            # plot
            print(type(mean_value))
            mean_value_plot = np.full(data_points, mean_value)  # create a mean value line

            # s = 1 + np.sin(2 * np.pi * t)
            # ----------------------------------------------
            number_subplots = 8
            fig, axs = plt.subplots(number_subplots)

            axs[0].plot(t, data)
            axs[0].plot(t, mean_value_plot)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.text.html#matplotlib.pyplot.text
            fig.text(0.01, 0.01, 'mean = ' + str(np.round(mean_value, 1)), fontsize=16, color='C1')
            axs[0].set(xlabel='time [s]', ylabel='current (nA)', title='osci reading')
            axs[0].grid()


            axs[1].plot(t, data_filtered)
            axs[1].set(xlabel='time', ylabel='nA', title='LP filtered')
            axs[1].grid()


            axs[2].set(xlabel='frequency [Hz]', ylabel='mag', title='fourier transform')
            axs[2].plot(freq, abs(fourier_transform))
            # axs[2].plot(freq[50000:50500], abs(fourier_transform[50000:50500]))  # freq????
            # axs[2].plot(freq[(int(len(freq)/2)):(int(len(freq)/2) + 500)], abs(fourier_transform[0:500]))  # freq????
            # print(abs(fourier_transform[100]))
            for i in fourier_peaks:  # mais que 50k
                # print(abs(fourier_transform[i]))
                axs[2].scatter(freq[i], abs(fourier_transform[i]), s=50, c='r', marker='x')  # set a marker

            # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.dbode.html
            # bode das equacoes do gradiente
            axs[3].plot(t, gradient)
            axs[3].set(xlabel='time', ylabel='values', title='gradient')
            axs[3].grid()


            #   axs[4].plot(t, data)
            axs[4].hist(data, density=True)
            res_relfreq = stats.relfreq(data, numbins = data_points)
            x = res_relfreq.lowerlimit + np.linspace(0, res_relfreq.binsize * res_relfreq.frequency.size,
                                             res_relfreq.frequency.size)
            print(res_relfreq, x)
            #axs[4].twinx()
            #axs[4].bar(x, res_relfreq.frequency, width=res.binsize)
            axs[4].set(xlabel='values', ylabel='quantity', title='Histogram')


            # high-pitch tone as unwanted noise, so it gets multiplied by 0.3 to reduce its power
            noise_tone = data * 0.3
            mixed_tone = data_filtered + noise_tone
            normalized_tone = np.int16((mixed_tone / mixed_tone.max()) * rang)
            axs[5].set(xlabel='t', ylabel='nA', title='Normalization')
            axs[5].plot(t, normalized_tone[:data_points])
            axs[5].grid()


            # Estimate the magnitude squared coherence estimate, Cxy, of discrete-time signals X and Y using Welch’s method.
            # f, Cxy = signal.coherence(t, data_filtered, sampling_frequency)
            axs[6].set(xlabel='frequency [Hz]', ylabel='psd welch', title='psd welch')
            axs[6].semilogy(freqs_welch, psd_welch)

            # print(len(i))
            # axes = axs[2].gca(projection='polar')
            # https://github.com/mwaskom/seaborn/issues/576
            y_min, y_max = axs[2].get_ylim()
            print("tracking axis range ymin and ymax : %s , %s " % (y_min, y_max))

            # ---------------------------
            """
            generate and apply a window function to avoid spectral leakage. This method is often used before any spectrum computations
            frames  (array) : array including the overlapping frames.
            frame_len (int) : frame length.
            win_type  (str) : type of window to use.Default is "hamming". https://superkogito.github.io/blog/SpectralLeakageWindowing.html
            """
            win_type = "kaiser"
            beta = 4
            if win_type == "hamming":
                windows = np.hamming(data_points)
            elif win_type == "hanning":
                windows = np.hanning(data_points)
            elif win_type == "bartlet":
                windows = np.bartlett(data_points)
            elif win_type == "kaiser":
                windows = np.kaiser(data_points, beta)
            elif win_type == "blackman":
                windows = np.blackman(data_points)
            windowed_frames = data_filtered * windows

            f2 = np.arange(-sampling_frequency / 2, sampling_frequency / 2, sampling_frequency / data_points)  # the frequency axis including negative frequencies
            #plt.subplot(132)
            #plt.plot(f2, np.fft.fftshift(abs(fourier_transform)))



            axs[7].set(xlabel='time', ylabel='amplitude', title='Magnitude specgram')
            axs[7].angle_spectrum(filtered, Fs=sampling_frequency)
            # csd
            # Plots the spectral density between two signals.
            #axs[7].specgram(filtered, Fs=sampling_frequency)
            #axs[7].specgram(filtered, Fs=sampling_frequency,  cmap = plt.cm.bone)
            # Can plot the angle spectrum of segments within the signal in a colormap.
            #axs[7].magnitude_spectrum(filtered, Fs=sampling_frequency)
            # Plots the magnitudes of the corresponding frequencies.


            a = np.asanyarray(data)
            sd0 = a.std(axis=0, ddof=0)
            SNR0 = np.where(sd0 == 0, 0, mean_value / sd0)
            print("Signal to Noise Ratio : %s" % SNR0)

            window = signal.general_gaussian(data_points, p=0.5,
                                             sig=stddev)  # The Gaussian window is defined with scipy's signal.general_gaussian, which requires the number of points of the window, the shape p of the window (for example, p=1 for a Gaussian and p=0.5 for a Laplace distribution) and the standard deviation sig of the window
            filtered = signal.fftconvolve(window, data)
            filtered = (np.average(data) / np.average(filtered)) * filtered
            filtered = np.roll(filtered, -25)
            axs[7].set(xlabel='time', ylabel='amplitude', title='Laplace convolution')
            axs[7].plot(filtered, color='green')
            """  
            window = np.bartlett(data_points)

            Y = scipy.fftpack.fftshift(scipy.fftpack.fft(data_filtered))
            f = scipy.fftpack.fftshift(scipy.fftpack.fftfreq(len(t)))

            p = np.angle(Y)
            p[np.abs(fourier_transform) < 1] = 0
            axs[7].plot(f, p)
            axs[7].set(xlabel='time', ylabel='values', title='fft')
            
            
            1/T = bandwidth/spectral lines = sampling_frequency/blocksize = delta_Frequency 
                        
            each sine wave will have more than a single peak (like you've noticed). You need to identify the peak 
            in the magnitude plot, and look only at the phase there. You should always use a suitable windowing function
            
            
            https://en.wikipedia.org/wiki/Window_function
            N = len(data_filtered)
            
            n = np.arange(N)
            k = n.reshape((N, 1))
            e = np.exp(-2j * np.pi * k * n / N)
            X = np.dot(e, data_filtered)
            # calculate the frequency
            N = len(X)
            n = np.arange(N)
            T = N / sampling_frequency
            freq = n / T

            axs[6].stem(freq, abs(X), 'b', markerfmt=" ", basefmt="-b")
            axs[6].xlabel('Freq (Hz)')
            axs[6].ylabel('DFT Amplitude |X(freq)|')
            
                     
            Scipy.signal's find_peaks should return the amplitudes of the peaks that find_peaks finds.
        
                For each amp in the returned peaks array you can find the index in the np_array where the value 
                at that index is this max amp. This index should give you the index at which to find the time
                stamp of the peak.
                
                Note, you may need to threshold the peaks returned to return only the tallest peaks. 
                If this cuts off too many peaks you can iterate through and ignore peaks that are x 
                distance close to the previous peak (don't label one hill as multiple peaks).
        
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.spectrogram.html

            axs[6].set(xlabel='t', ylabel='kHz', title='Spectogram')
            f, t, Sxx = signal.spectrogram(data, freq, return_onesided=False)
            axs[6].pcolormesh(t, fftshift(f), fftshift(Sxx), fftshift(Sxx, axes=0), shading='gouraud')

            https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.spectrogram.html
            
            # Interquartile Range to Test Normality
            mapping coefficient in a plot python matplotlib
            
            # inverse FFT ********* verify - plots dont have harmony
            axs[6].set(xlabel='t', ylabel='nA', title='Inverse FT')
            new_sig = irfft(data)
            axs[6].plot(new_sig[:data_points])
            axs[6].grid()
           
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
            
            error to quantify how close an estimate is to that true value
            error = estimate - correct 
            percent_error = error / correct * 100
            """
            plt.show()

        except KeyError:
            print("we need more data to classify")