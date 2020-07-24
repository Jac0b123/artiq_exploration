import sys
from artiq.experiment import *
import numpy as np
from matplotlib import pyplot as plt


frequency = 1  # Sine wave frequency
points = 50 # points per period
total_duration = 1  # seconds per period

Nsamples = int(total_duration * frequency * points)
sample_rate = 1 / (frequency * points)
Nperiods = total_duration * frequency

acquisition_rate_scale = 1
Nsamples_acquisition = int(Nsamples * acquisition_rate_scale)

print('Nsamples:', Nsamples)
print('sample_rate:', 1 / sample_rate / 1e3, 'kHz')
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
        self.sinevoltages = np.sin(np.linspace(0, 2*np.pi, points))
        self.rampvoltages = [k/points for k in range(points)]


    @kernel
    def record(self):
        with self.core_dma.record("pulse0"):
            for k in range(points):
                self.zotino0.write_dac(0, self.sinevoltages[k])
                self.zotino0.write_dac(1, self.sinevoltages[k])
                self.zotino0.load()

                # Subtract 800 ns, i.e. the zotino load duration
                delay(sample_rate * s - 0.8*us)

        with self.core_dma.record("pulse1"):
            for k in range(points):
                self.zotino0.write_dac(2, self.rampvoltages[k])
                self.zotino0.load()
                # Subtract 800 ns, i.e. the zotino load duration
                delay(sample_rate * s - 0.8 * us)

    @kernel
    def run(self):
        # Initialize instruments
        self.core.reset()
        self.core.break_realtime()
        self.sampler0.init()
        self.core.break_realtime()
        self.zotino0.init()
        delay(5*ms)
        for i in range(8):
            self.sampler0.set_gain_mu(i,0)  # Set the gain of each channel to 1
            delay(1*us)

        # Load Zotino pulses
        self.record()
        pulses_handle0 = self.core_dma.get_handle("pulse0")
        pulses_handle1 = self.core_dma.get_handle("pulse1")
        self.core.break_realtime()

        # Simultaneously emit Zotino pulses and acquire with digitizer
        t1 = T1 = k = 0
        T0 = self.core.get_rtio_counter_mu()
        t0 = now_mu()
        try:
            for j in range(int(Nperiods)):
                with parallel:
                    with sequential:
                        self.core_dma.playback_handle(pulses_handle0)
                        T1 = self.core.get_rtio_counter_mu()
                        t1 = now_mu()
                    with sequential:
                        for k in range(points):
                            delay(sample_rate / acquisition_rate_scale * s - 2.5*us)
                            self.sampler0.sample_mu(self.samples[j * points + k])

        except RTIOUnderflow:
            print('j =', j, 'k =', k)
            print("RTIO clock advanced by ", self.core.mu_to_seconds(T1 - T0))
            print("timeline cursor advanced by ", self.core.mu_to_seconds(t1 - t0))
            raise

        print("RTIO clock advanced by ",self.core.mu_to_seconds(T1 - T0))
        print("timeline cursor advanced by ",self.core.mu_to_seconds(t1 - t0))
        self.plot(self.samples)
