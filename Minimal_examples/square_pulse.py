from artiq.experiment import *

frequency = float(input("Enter square pulse frequency in kHz: "))

class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("zotino0")
        self.zotino = self.zotino0

    @kernel
    def run(self):
        self.core.break_realtime()
        self.zotino.init()
        delay(1 * ms)
        for k in range(30000):
            self.zotino.write_dac(0, 1)
            self.zotino.load()
            delay(1/(2*frequency) * ms)

            self.zotino.write_dac(0, 0)
            self.zotino.load()
            delay(1/(2*frequency) * ms)
