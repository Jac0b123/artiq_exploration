from artiq.experiment import *
import numpy as np

frequency = float(input("Enter sinusoid frequency: "))
voltages = np.sin(np.linspace(0, 2*np.pi, 100))

class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("zotino0")
        self.zotino = self.zotino0

    @kernel
    def run(self):
        self.core.break_realtime()
        self.zotino.init()
        delay(1*ms)
        for k in range(1000):
            for voltage in voltages:
                self.zotino.write_dac(0, voltage)
                self.zotino.load()
                delay(10/frequency * ms)
