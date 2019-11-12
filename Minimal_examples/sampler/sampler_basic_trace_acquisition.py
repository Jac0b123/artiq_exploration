""" Acquires single trace with variable sample rate, samples, and channels
After acquiring, data is plotted and saved to

TODO:
  - Subtract sampler.sample() instruction duration from delay
"""

from artiq.experiment import *
from matplotlib import pyplot as plt


sample_rate = float(input("Enter sample rate:"))
samples = int(float(input("Enter number of samples:")))
channels = int(input("Enter number of channels:"))

filename = "data.txt"


class sampler(EnvExperiment):
    def export_data(self, data):
        f=open(filename, "w+")
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

    @kernel
    def run(self):
        self.core.break_realtime()
        self.sampler.init()
        delay(5*ms)

        for i in range(channels):
            self.sampler0.set_gain_mu(i, 0)         # Set the gain of each channel to 1
            delay(100*us)

        # Generate sample trace list for multiple channels
        trace_data = [[int(0)]*channels for k in range(samples)]

        self.core.break_realtime()
        for k in range(samples):
            self.sampler0.sample_mu(trace_data[k])
            # Note that this delay does not yet incorporate the instruction
            # duration of sampler0.sample()
            delay(float(1/sample_rate) * s)

        self.export_data(trace_data)
        self.plot(trace_data)


