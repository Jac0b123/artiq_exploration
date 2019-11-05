from artiq.experiment import *

rate = float(input("Enter rate of V/s: "))

ramp_voltages = [k/100 for k in range(100)]


class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.setattr_device("zotino0")
        self.zotino = self.zotino0


    @kernel
    def record(self):
        with self.core_dma.record("pulse0"):
            for voltage in ramp_voltages:
                self.zotino.write_dac(0, voltage)
                self.zotino.load()
                delay((10/rate-0.0008) * ms)

    @kernel
    def run(self):
        self.core.reset()
        self.record()
        pulses_handle = self.core_dma.get_handle("pulse0")
        self.core.break_realtime()
        self.zotino.init()
        self.core.break_realtime()
        self.core_dma.playback_handle(pulses_handle)