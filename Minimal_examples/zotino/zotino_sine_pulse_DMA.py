""" Run a sine wave from DMA for variable frequency and duration """

from artiq.experiment import *
import numpy as np

frequency = float(input("Enter sinusoid frequency in Hz: "))
duration = float(input("Enter total duration in seconds: "))
channel = int(input("Enter channel: "))

Npoints = 100  # Number of points per sine pulse
voltages = np.sin(np.linspace(0, 2*np.pi, Npoints))
repetitions = int(duration * frequency)
print('Sample rate:', Npoints * frequency / 1e3, 'kS/s')


class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.setattr_device("zotino0")
        self.zotino = self.zotino0

    @kernel
    def record(self):
        with self.core_dma.record("pulse0"):
            for voltage in voltages:
                self.zotino.write_dac(channel, voltage)
                self.zotino.load()
                # -0.0008 offset is the instruction duration
                delay(1 / (frequency * Npoints) * s - 0.8 * us)

    @kernel
    def run(self):
        self.core.reset()
        self.record()
        pulses_handle = self.core_dma.get_handle("pulse0")
        self.core.break_realtime()
        self.zotino.init()
        self.core.break_realtime()

        for i in range(repetitions):
            self.core_dma.playback_handle(pulses_handle)