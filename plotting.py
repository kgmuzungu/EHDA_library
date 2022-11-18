from simple_pid import PID
import os
import re
import numpy as np
import json
import logging
import pylab
import numpy as np
import plotting
import libtiepie
from configuration_FUG import *
import configuration_tiepie
from scipy.signal import butter, lfilter
from time import gmtime, strftime
from electrospray import ElectrosprayDataProcessing, ElectrosprayConfig, ElectrosprayMeasurements
from validation_electrospray import ElectrosprayValidation
from classification_electrospray import ElectrosprayClassification
import matplotlib.pyplot as plt




def real_time_plot(queue, event, fig, ax, ln0, ln1, ln2, bg):
    # real time plotting loop event for iterable plotting

    while not event.is_set() or not queue.empty():

        print('[PLOTTING] plot event')
        message = queue.get()

        datapoints, datapoints_filtered, time_step, electrospray_data, electrospray_processing, txt_sjaak_str, txt_monica_str, txt_max_peaks, voltage_from_PS, current_from_PS = message
        logging.info(
            "Consumer got message: %s (queue size=%d)", message, queue.qsize()
            )
        logging.info("Consumer received event. Exiting")

        try:

            # reset the background back in the canvas state, screen unchange
            fig.canvas.restore_region(bg)

            ln0.set_ydata(electrospray_data.data)
            ln1.set_ydata(electrospray_processing.datapoints_filtered)
            ln2.set_ydata(
                (electrospray_processing.fourier_transform[0:500]))
            ax[0].legend(bbox_to_anchor=(1.05, 1),
                         loc='upper left', borderaxespad=0.)

            # re-render the artist, updating the canvas state, but not the screen
            ax[0].draw_artist(ln0)
            ax[1].draw_artist(ln1)
            ax[2].draw_artist(ln2)

            fig.canvas.manager.set_window_title('Sjaak: ' + txt_sjaak_str + 'monnica' + txt_monica_str + '; Peaks:' + txt_max_peaks +
                                                " voltage_PS= " + str(voltage_from_PS) + " current_PS= " + str(
                                                    current_from_PS * 1e6) + " current mean osci= " + str(electrospray_processing.mean_value))

            """df = pd.DataFrame({str(j): ['Sjaak: ' + txt_sjaak_str + ' ; Peaks:' + txt_max_peaks +
                                                " voltage_PS= " + str(voltage_from_PS) + " current_PS= " + str(
                current_from_PS * 1e6) + " current mean osci= " + str(electrospray_processing.mean_value) ] } ) """

            # copy the image to the GUI state, but screen might not be changed yet
            fig.canvas.blit(fig.bbox)
            # flush any pending GUI events, re-painting the screen if needed
            fig.canvas.flush_events()

        except:
            print("[PLOTTING] Failed to plot values!")
            sys.exit(1)




def start_plot(queue, event):

    # wait for first value
    print("[PLOTTING] No values in the data_queue yet")
    while queue.empty():
        time.sleep(0.1)

    message = queue.get()

    print("[PLOTTING] got values on data_queue")

    datapoints, datapoints_filtered, time_step, electrospray_data, electrospray_processing, txt_sjaak_str, txt_monica_str, txt_max_peaks, voltage_from_PS, current_from_PS = message

    plt.style.use('seaborn-colorblind')
    plt.ion()

    logging.info(
        "Consumer got: %s (queue size=%d)", message, queue.qsize()
    )
    logging.info("Consumer received event. Exiting")

    fig, ax = plt.subplots(3)


    try:

        #     # check here to plot the transfer function of the filter
        #     # https://stackoverflow.com/questions/25191620/creating-lowpass-filter-in-scipy-understanding-methods-and-units
        #     # ax[0].text(.5, .5, 'blabla', animated=True)

        # animated=True tells matplotlib to only draw the artist when we explicitly request it
        (ln0,) = ax[0].plot(np.arange(0, len(datapoints) * time_step, time_step), datapoints, animated=True)

        (ln1,) = ax[1].plot(np.arange(0, len(datapoints_filtered) * time_step, time_step), datapoints_filtered,
                            animated=True)
        freq = np.fft.fftfreq(len(datapoints_filtered), d=time_step)

        (ln2,) = ax[2].plot(freq[0:500], np.zeros(500), animated=True)

        ax[0].set(xlabel='time [s]', ylabel='current (nA)',
                  title='osci reading', ylim=[-3e2, 3e2])
        ax[1].set(xlabel='time', ylabel='nA',
                  title='LP filtered', ylim=[-1e1, 5e2])
        ax[2].set(xlabel='Frequency [Hz]', ylabel='mag',
                  title='fourier transform', ylim=[0, 1e6])
        # freqs_psd, psd = signal.welch(datapoints)
        # (ln3,) = ax[3].semilogx(freqs_psd, psd)
        # ax[3].set(xlabel='Frequency [Hz]', ylabel='Power', title='power spectral density')
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()

        # make sure the window is raised, but the script keeps going
        plt.show(block=False)
        plt.pause(0.1)

        # get copy of entire figure (everything inside fig.bbox) sans animated artist
        bg = fig.canvas.copy_from_bbox(fig.bbox)
        # draw the animated artist, this uses a cached renderer
        ax[0].draw_artist(ln0)
        ax[1].draw_artist(ln1)
        ax[2].draw_artist(ln2)

        fig.canvas.blit(fig.bbox)

        return fig, ax, ln0, ln1, ln2, bg

    except:
        print("[PLOTTING] Failed make iterable plot")
        return sys.exit(1)