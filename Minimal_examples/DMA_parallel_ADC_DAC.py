import sys
from artiq.experiment import *
import numpy as np
from matplotlib import pyplot as plt


frequency = 2e2  # Sine wave frequency
points = 50  # points per period
total_duration = 0.01  # seconds per period

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
        k = 0
        t0 = t1 = t2 = t3 = 0
        try:
            for j in range(int(Nperiods)):
                with parallel:
                    t0 = now_mu()
                    #delay(0.7*ms)
                    self.core_dma.playback_handle(pulses_handle0)
                    t1 = now_mu()
                    #self.core_dma.playback_handle(pulses_handle1)
                    with sequential:
                        t2 = now_mu()
                        delay(sample_rate / acquisition_rate_scale * s*3)
                        #t2 = now_mu()
                        for k in range(points):
                            delay(sample_rate / acquisition_rate_scale * s - 2.5*us)
                            self.sampler0.sample_mu(self.samples[j * points + k])
                        t3 = now_mu()
                            # Subtract 2.5 us, i.e. the sample instruction duraction
                        # We need a small delay here, probably a combination of
                        # the sampler needing a small delay and exiting a for loop
                        delay(0.54*ms)
        except RTIOUnderflow:
            print('j =', j, 'k =', k)
            print(self.core.mu_to_seconds(t1 - t0) * 1000,self.core.mu_to_seconds(t3 - t2) * 1000)
            raise

        print(self.core.mu_to_seconds(t1 - t0)*1000, self.core.mu_to_seconds(t3 - t2)*1000)
        # Plot all sampler channels
        self.plot(self.samples)
