from artiq.experiment import *
import numpy as np
from matplotlib import pyplot as plt

sample_rate = 10e3
frequency = 1e2
points = 50
total_duration = 0.1  # seconds
Nsamples = int(total_duration * frequency * points)



class Tutorial(EnvExperiment):
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
        self.setattr_device("core_dma")
        self.setattr_device("sampler0")
        self.setattr_device("zotino0")
        self.zotino = self.zotino0
        self.samples = [[int(0)] * 2 for k in range(Nsamples)]
        self.voltages = np.sin(np.linspace(0, 2*np.pi, points))


    @kernel
    def record(self):
        with self.core_dma.record("pulse0"):
            for k in range(len(self.voltages)):
                # with parallel:
                #     with sequential:
                self.zotino0.write_dac(0, self.voltages[k])
                self.zotino0.write_dac(1, self.voltages[k])
                self.zotino0.load()
                    # with sequential:
                    #     self.sampler0.sample_mu(self.samples[k])
                delay(1*ms)

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        self.sampler0.init()
        delay(5 * ms)
        for i in range(8):
            self.sampler0.set_gain_mu(i,0)  # Set the gain of each channel to 1
            delay(1 * ms)

        # This list holds all the sampled data for 2 channels, channel 6 and channel 7
        self.record()
        pulses_handle = self.core_dma.get_handle("pulse0")
        self.core.break_realtime()
        self.zotino0.init()
        self.core.break_realtime()
        for j in range(200):
            with parallel:
                self.core_dma.playback_handle(pulses_handle)
                with sequential:
                    delay(1*ms)
                    self.sampler0.sample_mu(self.samples[j])