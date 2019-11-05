from artiq.experiment import *
import numpy as np
from matplotlib import pyplot as plt

def plot_results(samples):
    samples_array = np.array(samples).transpose()

    fig, axes = plt.subplots(len(samples_array), 1)
    for ax, samples_channel in zip(axes, samples_array):
        ax.plot(samples_channel)

    plt.show()

class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.setattr_device("ttl4")
        self.setattr_device("zotino0")
        self.zotino = self.zotino0
        self.setattr_device("sampler0")
        self.sampler = self.sampler0

        N = int(1000)
        self.voltages = np.sin(2*np.pi*np.arange(N) / float(N))


        self.Nsamples = 500
        self.samples = [[int(0)] * 2 for k in range(self.Nsamples)]

    @kernel
    def record(self):
        dt = 500*us
        with self.core_dma.record("pulse0"):
            for voltage in self.voltages:
                delay(dt)
                self.zotino.write_dac(0, voltage)
                self.zotino.write_dac(1, voltage)
                self.zotino.load()

    @kernel
    def acquire_me_please(self):
        self.core.break_realtime()
        for k in range(self.Nsamples):
            delay(0.1 * ms)
            self.sampler0.sample_mu(self.samples[k])

    @kernel
    def run(self):
        self.core.reset()

        self.record()
        pulses_handle = self.core_dma.get_handle("pulse0")
        self.core.break_realtime()

        self.zotino.init()
        self.core.break_realtime()

        self.sampler.init()
        self.core.break_realtime()

        with parallel:
            with sequential:
                for k in range(300):
                    self.ttl4.pulse(3*ms)
                    delay(3*ms)
                    rtio_log("ttl4", "k", k)
                self.core.break_realtime()
            # self.core_dma.playback_handle(pulses_handle)


            # self.acquire_me_please()


        # plot_results(self.samples)