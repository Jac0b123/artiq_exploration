from artiq.experiment import *

class DMAPulses(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl6")
        self.setattr_device("ttl7")

    @kernel
    def run(self):
        self.core.break_realtime()
        with parallel:
            for i in range(1000):
                self.ttl6.pulse(1 * ms)
                delay(1 * ms)
            for i in range(1000):
                self.ttl7.pulse(1 * ms)
                delay(1 * ms)

