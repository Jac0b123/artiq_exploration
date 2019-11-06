from artiq.experiment import *
import numpy as np
from time import clock
from matplotlib import pyplot as plt


Nsamples = int(1e3)
channel_list = [2, 4, 6, 8]
sample_rate_list = [k for k in range(int(50e3), int(140e3), int(5e3))]
print('Acquiring a total', Nsamples, 'samples')


class sampler(EnvExperiment):
    def analyze_acquisitions(self, acquire_success):
        for line in acquire_success:
            print(line)
        for k in range(len(acquire_success)):
            idx_max = np.argmin(acquire_success[k])
            max_sample_rate = sample_rate_list[idx_max-1]
            print('Channel', channel_list[k], 'Max sample rate:', max_sample_rate/1e3, 'kHz')

    def build(self):
        self.setattr_device("core")
        self.setattr_device("sampler0")
        self.sampler = self.sampler0
        self.core.reset()

    @kernel
    def run(self):
        self.core.break_realtime()
        self.sampler.init()
        delay(1*ms)
        for i in range(8):
            self.sampler0.set_gain_mu(i, 0)         # Set the gain of each channel to 1
            delay(100*us)


        acquire_success = [[0] * len(sample_rate_list) for _ in channel_list]
        k1 = 0
        for channels in channel_list:
            k2 = 0
            for sample_rate in sample_rate_list:
                # This list holds all the sampled data for all channels
                samples = [[int(0)] * channels for _ in range(Nsamples)]

                print('Starting acquisition for',
                      channels, 'channels\t',
                      sample_rate, 'sample rate')

                instruction_duration = [2.6, 4.7, 6.8, 8.9][k1]  # us
                sample_delay = float(1 / sample_rate) * s - instruction_duration * us
                k3 = 0
                self.core.break_realtime()
                delay(1*ms)
                try:
                    for k3 in range(Nsamples):
                        self.sampler0.sample_mu(samples[k3])
                        delay(sample_delay)
                    # print('Success')
                    acquire_success[k1][k2] = 1
                except RTIOUnderflow:
                    print('Failed at k =', k3)
                    acquire_success[k1][k2] = 0

                k2 = k2 + 1
            k1 = k1 + 1

        self.analyze_acquisitions(acquire_success)