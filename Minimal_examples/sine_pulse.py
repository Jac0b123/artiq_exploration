from artiq.experiment import *
import numpy as np

frequency = float(input("Enter sinusoid frequency: "))
voltages = np.sin(np.linspace(0, 2*np.pi, 100))

class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.setattr_device("zotino0")
        self.zotino = self.zotino0

    @kernel
    def record(self):
        #self.core.break_realtime()
        #self.zotino.init()
        #delay(1*ms)
        with self.core_dma.record("pulse0"):
            for k in range(1):
                for voltage in voltages:
                    self.zotino.write_dac(0, voltage)
                    self.zotino.load()
                    # -0.0008 offset is the instruction duration
                    delay((10/frequency - 0.0008) * ms)

    @kernel
    def run(self):
        self.core.reset()
        self.record()
        pulses_handle = self.core_dma.get_handle("pulse0")
        self.core.break_realtime()
        self.zotino.init()
        self.core.break_realtime()

        for i in range(10000):
            self.core_dma.playback_handle(pulses_handle)