from artiq.experiment import *
import numpy as np
from time import clock
from matplotlib import pyplot as plt


# sample_rate = float(input("Enter sample rate: "))
sample_rate = 80e3
channels = 8
Nsamples = int(1e5)


class sampler(EnvExperiment):
    def export_data(self, data):
        f=open("data.txt", "w+")
        for d in data:
            f.write(str(d)+'\n')

    def plot(self, data):
        plt.figure()
        plt.plot(data)
        plt.show()

    def build(self):
        self.setattr_device("core")
        self.setattr_device("sampler0")
        self.sampler = self.sampler0
        self.core.reset()

        # This list holds all the sampled data for all channels
        # self.samples = [[int(0)] * channels for k in range(Nsamples)]

    @kernel
    def run(self):
        self.core.break_realtime()
        self.sampler.init()
        delay(1*ms)
        for i in range(8):
            self.sampler0.set_gain_mu(i, 0)         # Set the gain of each channel to 1
            delay(100*us)

        samples = [[int(0)] * channels for k in range(Nsamples)]

        print('Starting acquisition')
        self.core.break_realtime()
        try:
            for k in range(Nsamples):
                self.sampler0.sample_mu(samples[k])
                delay(float(1 / sample_rate) * s)
        except RTIOUnderflow:
            print('Failed at k =', k)
            raise

        self.plot(samples)
        self.export_data(samples)


        # self.export_data(self.samples)



