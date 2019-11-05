from artiq.experiment import *
import numpy as np
from matplotlib import pyplot as plt


frequency = 1e2  # Sine wave frequency
points = 50  # points per period
total_duration = 0.1  # seconds per period

Nsamples = int(total_duration * frequency * points)
sample_rate = 1 / frequency / points
Nperiods = total_duration * frequency

acquisition_rate_scale = 1
Nsamples_acquisition = int(Nsamples * acquisition_rate_scale)

print('Nsamples:', Nsamples)
print('sample_rate:', sample_rate, 's')
print('Nsamples_acquisition', Nsamples_acquisition)
print('Nperiods', Nperiods)


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

        # This list holds all the sampled data for 2 channels, channel 6 and channel 7
        self.samples = [[int(0)] * 2 for k in range(Nsamples_acquisition)]
        self.voltages = np.sin(np.linspace(0, 2*np.pi, points))


    @kernel
    def record(self):
        with self.core_dma.record("pulse0"):
            for k in range(points):
                # with parallel:
                #     with sequential:
                self.zotino0.write_dac(0, self.voltages[k])
                self.zotino0.write_dac(1, self.voltages[k])
                self.zotino0.load()
                    # with sequential:
                    #     self.sampler0.sample_mu(self.samples[k])
                delay(sample_rate * s)

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        self.sampler0.init()
        delay(5 * ms)
        for i in range(8):
            self.sampler0.set_gain_mu(i,0)  # Set the gain of each channel to 1
            delay(1 * ms)

        self.record()
        pulses_handle = self.core_dma.get_handle("pulse0")
        self.core.break_realtime()
        self.zotino0.init()
        self.core.break_realtime()

        k = 0
        for j in range(int(Nperiods)):
            with parallel:
                self.core_dma.playback_handle(pulses_handle)
                with sequential:
                    for k in range(points):
                        idx = j * points + k
                        # idx = j
                        delay(sample_rate / acquisition_rate_scale * s)
                        self.sampler0.sample_mu(self.samples[idx])

        print(k)
        self.plot(self.samples)