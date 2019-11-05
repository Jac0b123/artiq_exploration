from artiq.experiment import *

import numpy as np
import sys
import time

sample_rate = int(input("Enter sample rate: "))

class sampler(EnvExperiment):
    def export_data(self, data):
        f=open("data.txt", "w+")
        for d in data:
            f.write(str(d)+'\n')

    def build(self):
        self.setattr_device("core")
        self.setattr_device("sampler0")
        self.sampler = self.sampler0
        self.count = 100
        self.core.reset()

    @kernel
    def run(self):
        self.set_dataset("sampler", np.full(self.count, np.nan), broadcast=True)
        self.core.break_realtime()
        self.sampler.init()
        delay(5*ms)
        for i in range(8):
            self.sampler0.set_gain_mu(i, 0)         # Set the gain of each channel to 1
            delay(100*us)

        smp = [[float(0)]*16 for k in range(100)]    # This list holds all the sampled data for each channel

        self.core.break_realtime()
        for k in range(self.count):
            self.sampler0.sample(smp[k])
            #delay(0.2 * ms)
            delay(float(1/sample_rate) * s)
        self.export_data(smp)



