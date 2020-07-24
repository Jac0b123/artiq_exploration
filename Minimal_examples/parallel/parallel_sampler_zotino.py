from artiq.experiment import *
import numpy as np
from matplotlib import pyplot as plt


# sample_rate = float(input("Enter sample rate: "))
# frequency = float(input("Enter sinusoid frequency: "))

sample_rate = 10e3
frequency = .1e2
points = 200
total_duration = 2  # seconds
Nsamples = int(total_duration * frequency * points)
voltages = np.sin(np.linspace(0, 2*np.pi, points))

print('Nsamples:', Nsamples)


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
        self.setattr_device("zotino0")
        self.zotino = self.zotino0

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        self.sampler0.init()
        delay(1*ms)
        for i in range(8):
            self.sampler0.set_gain_mu(i, 0)         # Set the gain of each channel to 1
            delay(1*ms)

        # This list holds all the sampled data for 2 channels, channel 6 and channel 7
        samples = [[int(0)]*2 for k in range(Nsamples)]
        k = 0

        self.core.break_realtime()
        for j in range(int(total_duration * frequency)):
            for voltage in voltages:
                with parallel:
                    with sequential:
                        self.zotino0.write_dac(0, voltage)
                        self.zotino0.write_dac(1, voltage)
                        self.zotino0.load()
                    with sequential:
                        self.sampler0.sample_mu(samples[k])
                delay(0.5*ms)
                k = k + 1


        self.export_data(samples)
        self.plot(samples)




