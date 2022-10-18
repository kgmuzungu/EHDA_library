# OscilloscopeBlock.py
# This example performs a block mode measurement and writes the data to OscilloscopeBlock.csv.
# Find more information on http://www.tiepie.com/LibTiePie .


from __future__ import print_function
import time
import threading
import sys
import libtiepie
from tests.printinfo import *
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.signal import butter, lfilter
from scipy.signal import argrelextrema

multiplier_for_nA = 500


def do_validation():
    y = 0.04737     # N/m : surface tension
    # K = 0.000034 # EG
    K = 0.000026  # pure ethanol; S/m : electrical conductivity
    Q = 0.01389  # cm3/s : flow rate  **** ml/h to cm3/h : * 0.000277778
    ki = 6.46  # no units
    k = 37.7
    # kd = 1.66
    # Todo change
    I_actual = 0

    alpha = pow((y * K * Q), (1/2))
    print(" alpha = %f" % alpha)
    b = I_actual / (y * K * Q) ** (1 / 2)
    # b = I_actual/pow((y * K * Q), (1/2))
    I_hartman = b*pow((y * K * Q), (1/2))

    b = 0.5
    I_hartman_05 = b*pow((y * K * Q), (1/2))

    b = 2
    I_hartman_2 = b*pow((y * K * Q), (1/2))

    print(" I_hartman [nA] with b calculated : %f ; b = 0.5 : %f ; with b = 2 : %f" % (I_hartman, I_hartman_05, I_hartman_2))
    I_chen_pui = ki * k^(1/4) * (y*K*Q / k)^(1/2)
    print(" I_chen_pui [nA] = %f" % I_chen_pui)


def do_statistics (data_array, data_filtered_array, fourier_peaks_array):
    mean_value = np.mean(data_array)
    I_actual = mean_value
    std_dev = np.std(data_array)  # standard deviation
    med = np.median(data_array)  # mediana
    inf = np.percentile(data_array, 2.5)
    sup = np.percentile(data_array, 97.5)
    #   Range = Highest_value – Lowest_value
    rang_confidence = sup - inf
    freqs, psd = signal.welch(data_filtered_array)

    sum_tvd = 0
    data_points = int(len(data_array))
    # Total Variation Distance (TVD)
    for i in range(0, data_points):
        sum_tvd = sum_tvd + abs(data_array[i] - data_filtered_array[i])
    proportional_sum = sum_tvd / 2

    print("mean=%f ; std=%f ; TVD=%f " % (mean_value, std_dev, proportional_sum))
    print("freqs = max: %s, min: %s X; psd = max: %s, mean: %s, min: %s, elevado: %s  " % (freqs.max(), freqs.min(), psd.max(), psd.mean(), psd.min(), pow(fourier_peaks_array, 2)))

    try:
        print(" std/mean = %f ;" % (std_dev / mean_value) )
    except ZeroDivisionError:
        print('Error: Invalid argument.')
    try:
        print("mean-median = %f ;" % (mean_value/med) )
    except ZeroDivisionError:
        print('Error: Invalid argument.')
    try:
        print("avarage development-relaxation ratios = %f ;" % (mean_value / med ))
    except ZeroDivisionError:
        print('Error: Invalid argument.')

    len_fourier_peaks_array = len(fourier_peaks_array)
    do_classification(mean_value, std_dev, med, psd, proportional_sum, sup, len_fourier_peaks_array)
    I_actual = mean_value
    # do_validation()
    return I_actual

    # Compute and plot the power spectral density (PSD)


def config_TiePieScope(scp):
    # ToDo set input to single ended or differential
    # in oscilloscopechannel.py _get_is_differential or _get_impedance ... investigate further
    """print("SCP is differential: %s" % scp.channels[0].is_differential)
    print("SCP impedance: %s" % scp.channels[0].impedance)
    print("SCP is safe_ground: %s" % scp.channels[0].safe_ground_enabled)"""
    # !!!! input impedance by default is 2MOhm ... is in differential mode
    scp.measure_mode = libtiepie.MM_BLOCK
    scp.sample_frequency = sampling_frequency
    scp.record_length = 50000  # 10000 samples
    scp.pre_sample_ratio = 0  # 0 %
    scp.channels[0].enabled = True
    scp.channels[0].range = 4  # range in V
    # ToDo using autoranging would be an advantage?
    scp.channels[0].coupling = libtiepie.CK_DCV  # DC Volt
    scp.channels[0].trigger.enabled = True
    scp.channels[0].trigger.kind = libtiepie.TK_RISINGEDGE
    scp.channels[1].enabled = False
    scp.channels[2].enabled = False
    scp.channels[3].enabled = False
    scp.trigger_time_out = 100e-3  # 100 ms
    # Disable all channel trigger sources:
    for ch in scp.channels:
        ch.trigger.enabled = False
    # Setup channel trigger:
    ch = scp.channels[0]  # Ch 1
    # Enable trigger source:
    ch.trigger.enabled = True
    ch.trigger.kind = libtiepie.TK_RISINGEDGE  # Rising edge
    ch.trigger.levels[0] = 0.5  # 50 %
    ch.trigger.hystereses[0] = 0.05  # 5 %
    return scp


def do_classification (mean_value_var, std_dev_var,  med_var, psd_var, proportional_sum_var, sup_var, len_fourier_peaks_var):
    if mean_value_var < 0.5 or mean_value_var == 0.5:
        if (std_dev_var / mean_value_var) > 2.5:
            if (mean_value_var/med_var) < 0.9 or (mean_value_var/med_var) > 1.1:
                if psd_var.any() < 0.2:
                    print("Dripping Sjaak")
                    print("************")
        # mean_value - med < 1
        # mean_Value < 1
    elif mean_value_var > 0.5:
        if (std_dev_var / mean_value_var) > 2.5:
            try:
                if (mean_value_var / med_var) < 0.9 or (mean_value_var / med_var) > 1.1:
                    if psd_var.any() > 0.2 and psd_var.any() < 0.75:
                        print("Intermittent Sjaak")
                        print("************")
                    if len_fourier_peaks_var < 15:
                        print("Intermittent Monica")
                        print("************")
            except ZeroDivisionError:
                print('Error: Invalid argument.')

    elif mean_value_var > 0.5:
        try:
            if (mean_value_var / med_var) > 0.9 or (mean_value_var / med_var) < 1.1:
                if psd_var.any() > 0.0075: # 0.75
                    print("Cone jet Sjaak")
                    print("************")

                if psd_var.any() > 0.0009: # check !!!!!!
                    print("Cone jet Monica")
                    print("************")
                    if med_var > 50:
                        if len_fourier_peaks_var > 15:
                            print("Cone jet Monica")
                            print("************")
        except ZeroDivisionError:
            print('Error: Invalid argument.')

    elif mean_value_var > 0.5:
        print("Multi-jet Sjaak")
        print("************")

        if std_dev_var > 300:
            if sup_var > 1e3:
                if proportional_sum_var > 1e6:
                    if mean_value_var > 100:
                        print("Multi-jet Monica")
                        print("************")


# Print library info:
print_library_info()

sampling_frequency = 1e5
time_step = 1 / sampling_frequency

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# Semaphore to do the orchestra:
sem = threading.Semaphore()

fig, ax = plt.subplots(3)


# Try to open an oscilloscope with block measurement support:
scp = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):
        scp = item.open_oscilloscope()

if scp:
    try:
        scp = config_TiePieScope(scp)

        # Print oscilloscope info:
        print_device_info(scp)

        # Start measurement:
        scp.start()

        # Wait for measurement to complete:
        while not scp.is_data_ready:
            time.sleep(0.05)  # 50 ms delay, to save CPU time

        # Get data:
        data = scp.get_data()
        time_start = time.time()
        # datapoints = np.array(data[0]) * 1000 # 1Mohm input resistance when in single ended input mode
        datapoints = np.array(data[0]) * multiplier_for_nA  # 2Mohm default input resistance

        # low pass filter to flatten out noise
        cutoff_freq_normalized = 3000 / (0.5 * sampling_frequency)  # in Hz
        b, a = butter(6, Wn=cutoff_freq_normalized, btype='low',
                      analog=False)  # first argument is the order of the filter
        datapoints_filtered = lfilter(b, a, datapoints)
        # check here to plot the transfer function of the filter
        # https://stackoverflow.com/questions/25191620/creating-lowpass-filter-in-scipy-understanding-methods-and-units


        # animated=True tells matplotlib to only draw the artist when we
        # explicitly request it
        ax[0].set(xlabel='time [s]', ylabel='current (nA)', title='osci reading', ylim=[-3e2, 3e2])

        (ln0,) = ax[0].plot(np.arange(0, len(datapoints) * time_step, time_step), datapoints, animated=True)
        (ln1,) = ax[1].plot(np.arange(0, len(datapoints_filtered) * time_step, time_step), datapoints_filtered, animated=True)
        freq = np.fft.fftfreq(len(datapoints_filtered), d=time_step)
        ax[1].set(xlabel='time', ylabel='nA', title='LP filtered', ylim=[-1e1, 5e2])
        (ln2,) = ax[2].plot(freq[0:500], np.zeros(500), animated=True)
        # (ln2,) = ax[2].plot(freq, np.zeros(len(datapoints_filtered)), animated=True)
        ax[2].set(xlabel='frequency [Hz]', ylabel='mag', title='fourier transform', ylim=[0, 1e6])

        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()

        # make sure the window is raised, but the script keeps going
        plt.show(block=False)
        plt.pause(0.1)

        # get copy of entire figure (everything inside fig.bbox) sans animated artist
        bg = fig.canvas.copy_from_bbox(fig.bbox)
        # draw the animated artist, this uses a cached renderer
        # ax[0].autoscale()

        ax[0].draw_artist(ln0)
        ax[1].draw_artist(ln1)
        ax[2].draw_artist(ln2)

        # show the result to the screen, this pushes the updated RGBA buffer from the
        # renderer to the GUI framework so you can see it
        fig.canvas.blit(fig.bbox)

        j = 0
        for j in range(10000):
            # reset the background back in the canvas state, screen unchanged
            fig.canvas.restore_region(bg)
            # update the artist, neither the canvas state nor the screen have changed

            # Start measurement:
            scp.start()

            # Wait for measurement to complete:
            while not scp.is_data_ready:
                time.sleep(0.05)  # 50 ms delay, to save CPU time

            # Get data:
            data = scp.get_data()
            datapoints = np.array(data[0]) * multiplier_for_nA

            # mean_value_plot = np.full(datapoints, mean_value)  # create a mean value line

            # low pass filter to flatten out noise
            datapoints_filtered = lfilter(b, a, datapoints)

            # fourier transform, results in the complex discrete fourier coefficients
            fourier_transform = np.fft.fft(datapoints_filtered)
            # fourier_transform = np.fft.fft(data_filtered)
            # freq = np.fft.fftfreq(len(datapoints_filtered), d=time_step)
            # print("peaks fourier: " + str(find_peaks(abs(fourier_transform)[0:500], threshold=1e5)))
            # find_peaks uses wavelet convolution (implicit filtering)
            # fourier_snippet = abs(fourier_transform[0:500])
            # fourier_peaks = argrelextrema(abs(fourier_transform), comparator=np.greater, order=20)
            fourier_peaks = argrelextrema(abs(fourier_transform[0:500]), comparator=np.greater, order=15)[0]
            print("rel max fourier: %s" % fourier_peaks)
            # argrelextrema uses trivial algorithm (no filtering). the order param provides some sort of filtering
            # abs_fourier_values = abs(fourier_transform)


            time_end = time.time() - time_start
            ln0.set_ydata(datapoints)
            ln1.set_ydata(datapoints_filtered)
            ln2.set_ydata(abs(fourier_transform[0:500]))

            # re-render the artist, updating the canvas state, but not the screen
            ax[0].draw_artist(ln0)
            ax[1].draw_artist(ln1)
            ax[2].draw_artist(ln2)

            # copy the image to the GUI state, but screen might not be changed yet
            fig.canvas.blit(fig.bbox)
            # flush any pending GUI events, re-painting the screen if needed
            fig.canvas.flush_events()
            # you can put a pause in if you want to slow thi
            # ngs down
            # plt.pause(.1)

            # statistics
            do_statistics(datapoints, datapoints_filtered, fourier_peaks)
            # validation
            # do_validation()


    except Exception as e:
        print('Exception: ' + e.message)
        sys.exit(1)

    # Close oscilloscope:
    del scp

else:
    print('No oscilloscope available with block measurement support!')
    sys.exit(1)

sys.exit(0)