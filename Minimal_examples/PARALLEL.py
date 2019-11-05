from artiq.experiment import*
import numpy as np

a = [int(0)]*1000
for k in range(len(a)):
    if k%2 == 0:
        a[k] = int(0)
    if k%2 == 1:
        a[k] = int(1)

b = [int(0)]*1000
for k in range(len(b)):
    if k%2 == 0:
        b[k] = int(1)
    if k%2 == 1:
        b[k] = int(0)

ramp = [float(k/1000) for k in range(1000)]
sine = np.sin(np.linspace(0, 2*np.pi, 100))

class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("zotino0")
        self.setattr_device("ttl7")
        self.setattr_device("ttl6")
        self.zotino = self.zotino0

    @kernel
    def run(self):
        d = int(0)
        self.core.reset()
        self.core.break_realtime()
        self.zotino.init()
        delay(5*ms)
        for i in range(5000):
            with parallel:
                for j in range(10):
                    self.zotino.write_dac(0, sine[d % 100])
                    self.zotino.load()
                    delay(1 * ms)
                    d = d + 1

                for j in range(5):
                    self.ttl7.pulse(1*ms)
                    delay(1*ms)
