from artiq.experiment import *

import numpy as np

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
        self.core.break_realtime()
        self.sampler.init()
        delay(5*ms)

        for i in range(8):
            self.sampler0.set_gain_mu(i, 0)         # Set the gain of each channel to 1
            delay(100*us)

        # Generate sample trace list for multiple channels
        channels = 2
        smp = [[float(0)]*channels for k in range(100)]

        self.core.break_realtime()
        for k in range(self.count):
            self.sampler0.sample(smp[k])
            delay(float(1/sample_rate) * s)

        self.export_data(smp)



