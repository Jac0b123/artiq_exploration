from artiq.experiment import *
import numpy as np
sample_rate = float(input("Enter sample rate: "))

class sampler(EnvExperiment):
    def export_data(self, data):
        f=open("data.txt", "w+")
        for d in data:
            f.write(str(d)+'\n')

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
            #delay(100*us)

        # This list holds all the sampled data for 2 channels, channel 6 and channel 7
        smp = [[int(0)]*8 for k in range(1000)]
        smp1 = [[int(0)]*2 for k in range(1000)]

        self.core.break_realtime()
        for k in range(1000):
            self.sampler0.sample_mu(smp[k])
            delay(float(1 / sample_rate) * ms)


        self.export_data(smp)



