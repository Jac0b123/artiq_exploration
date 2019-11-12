""" Alternate TTL output at given frequency

TODO
  - Subtract instruction duration `ttl.pulse` from delay
"""

from artiq.experiment import *

frequency = float(input("Enter desired frequency in MHz: "))
duration = float(input("Enter total duration in seconds: "))
channel = int(input("Enter channel: "))

repetitions = duration * (frequency * 1e6)

class DMAPulses(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.setattr_device("ttl" + str(channel))
        self.ttl = getattr(self, 'ttl' + str(channel))

    @kernel
    def run(self):
        self.core.reset()
        for i in range(repetitions):
            self.ttl.pulse(1/(2*frequency) * us)
            delay(1/(2*frequency) * us)