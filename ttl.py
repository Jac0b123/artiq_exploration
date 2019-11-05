from artiq.experiment import *

frequency = float(input("Enter desired frequency in MHz: "))

class DMAPulses(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.setattr_device("ttl7")

    @kernel
    def run(self):
        self.core.reset()
        for i in range(1000000):
            self.ttl7.pulse(1/(2*frequency) * us)
            delay(1/(2*frequency) * us)