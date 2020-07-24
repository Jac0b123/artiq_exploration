from artiq.experiment import *

frequency = float(input("Enter square pulse frequency in kHz: "))

class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.setattr_device("zotino0")
        self.zotino = self.zotino0

    @kernel
    def record(self):
        with self.core_dma.record("pulse0"):
            for i in range(100):
                self.zotino.write_dac(0, float(1))
                self.zotino.load()
                delay((1/(2*frequency) - 0.0008) * ms)

                self.zotino.write_dac(0, float(0))
                self.zotino.load()
                delay((1/(2*frequency) - 0.0008) * ms)

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