import json
import numpy as np
# from scipy.signal import find_peaks_cwt
from scipy.signal import find_peaks
from scipy.signal import argrelextrema
from scipy.signal import hilbert
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter

# filename = 'test1 3_633kV fast single drop.json'
# filename = 'test3 4_38kV super fast dripping.json'
# filename = 'test4_5_12kV_pre_conejet.json'
filename = 'test5 5_41kV conejet.json'
# filename = 'test6 6_106kV unstable multijet.json'
# filename = 'test7 6_4kV corona noise.json'
# filename = 'measurement5kV_FR40uperl_100kSa.json'


# select find peak function
use_find_peaks = False
use_argrelextrema = True
data_collector_export = False
number_of_highest_peaks = 3
histogram_bins = np.arange(start=0, stop=1500, step=10)
result_sorted_indices = []

with open(filename) as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()


if not data_collector_export:
    data = np.array(jsonObject[0]['data']) * 1000  # values in nA
    print("scope name: ", jsonObject[0]['name'])
    print("bandwidth = ", jsonObject[0]['bandwidth'])
    print("sample frequency = ", jsonObject[0]['samplefrequency'])
    print("number data points = ", jsonObject[0]['datasize'])
    data_points = int(jsonObject[0]['datasize'])
    sampling_frequency = int(jsonObject[0]['samplefrequency'])
else:
    print("name = ", jsonObject[0]['name'])
    print("number data points = ", jsonObject[0]['outputs'][0]['datasize'])
    print("sample frequency: ", jsonObject[0]['outputs'][0]['samplefrequency'])
    data = np.array(jsonObject[0]['outputs'][0]['data']) * 1000  # values in nA
    data_points = int(jsonObject[0]['outputs'][0]['datasize'])
    sampling_frequency = int(jsonObject[0]['outputs'][0]['samplefrequency'])

time_step = 1 / sampling_frequency
time_max = time_step * data_points

# statistics
mean_value = np.mean(data)
variance = np.var(data)  # is a squared mean value of values of the average, square because it avoids cancellation of values below and above mean
stddev = np.std(data)  # is the sqrt(variance)

print("data mean: " + str(mean_value))
print("data variance: " + str(variance))
print("data std deviation: " + str(stddev))

# time axes
t = np.arange(0.0, time_max, time_step)  # time axes, time steps size is 1 / (sample frequences)

# low pass filter to flatten out noise
cutoff_freq_normalized = 1500 / (0.5 * sampling_frequency) #  in Hz
b, a = butter(6, Wn=cutoff_freq_normalized, btype='low', analog=False)  # first argument is the order of the filter
data_filtered = lfilter(b, a, data)
# check here to plot the transfer function of the filter
# https://stackoverflow.com/questions/25191620/creating-lowpass-filter-in-scipy-understanding-methods-and-units

# fourier transform, results in the complex discrete fourier coefficients
fourier_transform = np.fft.fft(data_filtered)
# fourier_transform = np.fft.fft(data_filtered)
freq = np.fft.fftfreq(data_points, d=time_step)  # better to use data.size
freq_step = freq[1] - freq[0]
# extracting coefficients
# print("peaks fourier: " + str(find_peaks(abs(fourier_transform)[0:500], threshold=1e5)))
# find_peaks uses wavelet convolution (implicit filtering) ... no idea how it works... :-)
# fourier_peaks = find_peaks_cwt(abs(fourier_transform[0:500]), np.arange(1, 69))
# gaussina blur first https://stackoverflow.com/questions/25571260/scipy-signal-find-peaks-cwt-not-finding-the-peaks-accurately
# argrelextrema uses trivial algorithm (no filtering). the order param provides some sort of filtering


if use_argrelextrema:
    # order – How many points on each side to use for the comparison to consider ``comparator(n, n+x)`` to be True.
    # mode – How the edges of the vector are treated. 'wrap' (wrap around) or 'clip' (treat overflow as the same as the last (or first) element). Default is 'clip'. See `numpy.take`.
    fourier_peaks = argrelextrema(abs(fourier_transform[0:100]), comparator=np.greater, order=3, mode='wrap')[0]  #  returns indices
    # test = abs(fourier_transform[fourier_peaks])  # values at indices
    sorted_indices = np.argsort(abs(fourier_transform[fourier_peaks]))
    print(sorted_indices)
    print(fourier_peaks)

    # result_sorted_indices[np.in1d(int(sorted_indices), fourier_transform)]
    # print(result_sorted_indices)
    # print(" TEST " + str(test/1e6))
    # sorted_argsort = np.argsort(test)  # returns sorted indices
    # sorted_sort = np.sort(test)  # returns the sorted array
    # argpartition seems to be a faster sort algorithm under some circumstances that I havent looked up yet
    # if you give the index of the biggest value then the resulting array will be sorted
    # sorted_argpartition = np.argpartition(test, kth=0)
    print("max=%f frequency=%d" % (abs(fourier_transform[fourier_peaks[sorted_indices[-1]]]) / 1e6, freq_step * fourier_peaks[sorted_indices[-1]]))
    print("max=%f frequency=%d" % (abs(fourier_transform[fourier_peaks[sorted_indices[-2]]]) / 1e6, freq_step * fourier_peaks[sorted_indices[-2]]))
    print("max=%f frequency=%d" % (abs(fourier_transform[fourier_peaks[sorted_indices[-3]]]) / 1e6, freq_step * fourier_peaks[sorted_indices[-3]]))
    print("max=%f frequency=%d" % (abs(fourier_transform[fourier_peaks[sorted_indices[-4]]]) / 1e6, freq_step * fourier_peaks[sorted_indices[-4]]))
    print("max=%f frequency=%d" % (abs(fourier_transform[fourier_peaks[sorted_indices[-5]]]) / 1e6, freq_step * fourier_peaks[sorted_indices[-4]]))

if use_find_peaks:
    fourier_peaks = find_peaks(abs(fourier_transform[0:100]), height=5e3, threshold=100, distance=1)
    height = fourier_peaks[1]['peak_heights']  # list containing the height of the peaks
    peak_pos = fourier_peaks[0]   # list containing the positions of the peaks
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

# histogram
hist, bins = np.histogram(data, histogram_bins)
print("histogram: " + str(hist))
# hist, bins = np.histogram(data_filtered, )


# ToDo probability density function
# approximation / probability density estimation ... machine learning

# ToDo convolution
# convolute with a similar wave form as the corona-current-shape ... but probably shooting with canons on sparrows

# ToDo autocorrelation gets any useful information here?
# I dont think so...
# can be used to estimate frequencies or the fundamental frequency

# filter 50Hz via inverse FFT
fourier_transform_modified = np.copy(fourier_transform)
# np.where(freq,  # where is 50Hz
index = int(50 / freq_step)
fourier_transform_modified[index] = 0
fourier_transform_modified[-index] = 0
data_iFFT = np.fft.ifft(fourier_transform_modified)

# hilbert transform: real-valued function to analytic function. only positive values in fourier transform
hilbert_transform = hilbert(data)

# plot
mean_value_plot = np.full(data_points, mean_value)  # create a mean value line
# s = 1 + np.sin(2 * np.pi * t)
fig, axs = plt.subplots(6)
axs[0].plot(t, data)
axs[0].plot(t, mean_value_plot)
# https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.text.html#matplotlib.pyplot.text
fig.text(0.01, 0.01, 'mean = ' + str(np.round(mean_value, 1)), fontsize=16, color='C1')
axs[0].set(xlabel='time [s]', ylabel='current (nA)', title='osci reading')
axs[0].grid()
axs[2].set(xlabel='frequency [Hz]', ylabel='mag', title='fourier transform')
# axs[2].set_yscale('log')
axs[2].plot(freq[0:200], abs(fourier_transform[0:200]))

if use_argrelextrema:
    for i in fourier_peaks:
        axs[2].scatter(freq[i], abs(fourier_transform[i]), s=50, c='r', marker='x')  # set a marker
if use_find_peaks:
    for pos, height in zip(fourier_peaks[0], fourier_peaks[1]['peak_heights']) :
        axs[2].scatter(freq[pos], height, s=50, c='r', marker='x')  # set a marker

axs[3].plot(t, gradient)
axs[3].set(xlabel='time', ylabel='values', title='gradient')
axs[3].grid()
axs[1].grid()
axs[1].plot(t, data_filtered)
axs[1].set(xlabel='time', ylabel='nA', title='LP filtered')
axs[4].grid()
axs[4].hist(data_filtered, histogram_bins)
axs[4].set(title='histogram')
axs[5].grid()
# axs[5].plot(t, abs(hilbert_transform))
axs[5].plot(t, data_iFFT.real, t, data_iFFT.imag)
# fig.savefig("test.png")
plt.show()
