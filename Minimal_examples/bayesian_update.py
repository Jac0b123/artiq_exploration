import sys
from artiq.experiment import *
import numpy as np
from matplotlib import pyplot as plt
from random import random

Nsamples = 500      # number of samples
total_duration = 5  # duration
sample_rate = total_duration/Nsamples

voltages = [0 for k in range(Nsamples)]
random_array = [np.random.random() for k in range(10)]


class Tutorial(EnvExperiment):
    def plot(self, data):
        plt.figure()
        plt.plot(data)
        plt.show()

    def build(self):
        self.setattr_device("core")
        self.setattr_device("sampler0")
        self.setattr_device("zotino0")
        self.zotino = self.zotino0

    @kernel
    def run(self):
        # This list holds all the sampled data for 2 channels, channel 6 and channel 7
        samples = [[int(0)] * 2 for k in range(8000)]
        self.core.reset()
        self.core.break_realtime()
        self.sampler0.init()
        self.zotino0.init()

        delay(1 * ms)
        for i in range(8):
            self.sampler0.set_gain_mu(i,0)  # Set the gain of each channel to 1
            delay(10 * us)

        sample_counter = 0
        # Define high and low voltages
        V_high = 3
        V_low = 0

        # Voltage and time thresholds
        V_threshold = 2*(1<<16)/20
        t_threshold = 0.6

        blip_duration = float(0.1)   # Set blip to 100ms
        t0 = now_mu()
        t_last_blip = now_mu()
        t_wait = float(random_array[0])
        V = V_low
        for k in range(len(random_array)):

            dt = self.core.mu_to_seconds(now_mu() - t0)

            # generate the pulses while dt < t_wait
            while dt < t_wait:
                with parallel:
                    with sequential:
                        self.zotino0.write_dac(0, V)
                        self.zotino0.write_dac(1, V)
                        self.zotino0.load()
                    with sequential:
                        self.sampler0.sa mple_mu(samples[sample_counter])
                delay(1 * ms)
                dt = self.core.mu_to_seconds(now_mu() - t0)
                sample_counter = sample_counter + 1

            # Set high or low voltage as necessary
            if V == V_high:
                t_wait = float(random_array[k])    # Set time until next blip
                V = V_low
            if V == V_low:
                t_wait = blip_duration      # Set time for blip
                V = V_high

            # Acquire sample and perform EPR sequence if necessary
            if samples[sample_counter-50][1] > V_threshold:
                t_last_blip = now_mu()
            if samples[sample_counter-50][1] < V_threshold:
                if (self.core.mu_to_seconds(now_mu() - t_last_blip) > t_threshold):
                    self.zotino0.write_dac(3, 1)
                    self.zotino0.load()
                    delay(1 * s)
                    self.zotino0.write_dac(3, -1)
                    self.zotino0.load()
                    delay(1 * s)
            t0 = now_mu()

        print(random_array)

        #self.plot(samples)
