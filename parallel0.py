from artiq.experiment import *

class DMAPulses(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl6")
        self.setattr_device("ttl7")

    @kernel
    def run(self):
        self.core.break_realtime()
        for i in range(1000):
            with parallel:
                self.ttl6.pulse(1 * ms)
                self.ttl7.pulse(1 * ms)
            delay(1 * ms)

