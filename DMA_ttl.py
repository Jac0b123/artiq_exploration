from artiq.experiment import *

frequency = float(input("Enter desired frequency in MHz: "))

class DMAPulses(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.setattr_device("ttl7")

    @kernel
    def record(self):
        with self.core_dma.record("pulses"):
            for i in range(100):
                self.ttl7.pulse(1/(2*frequency) * us)
                delay(1/(2*frequency) * us)

    @kernel
    def run(self):
        self.core.reset()
        self.record()
        pulses_handle = self.core_dma.get_handle("pulses")
        self.core.break_realtime()
        for i in range(100000):
            #self.core.break_realtime()
            self.core_dma.playback_handle(pulses_handle)