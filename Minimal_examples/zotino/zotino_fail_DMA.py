""" This file shows that the Zotino DMA cannot be used in parallel if the DMA
    pulse exceeds a certain number of instructions

Here we apply a ramping pulse to a Zotino output.
The ramp pulse is stored in the DMA and consists of a fixed number of points.
When the number of points composing the ramp pulse exceeds 85, the machine RTIO
counter suddenly increases from hundreds of microseconds to ~1 second.
Note that the increased duration depends on the delays set in the DMA pulse.

It seems the number of instructions in a DMA pulse has a maximum, and it isn't high...
"""

points = 85 # Number of points for the zotino ramping pulse
# Choosing 86 points or higher causes an RTIOunderflow error.

from artiq.experiment import *

class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.setattr_device("zotino0")
        self.zotino = self.zotino0

    @kernel
    def record(self):
        with self.core_dma.record("pulse0"):
            for k in range(points):
                self.zotino.write_dac(0, float(k / points))  # ramping pulse
                self.zotino.load()
                delay(10*ms)
    @kernel
    def run(self):
        # Initialize instruments
        self.core.reset()
        self.core.break_realtime()
        self.zotino0.init()
        delay(5*ms)

        # Load Zotino pulses
        self.record()
        pulses_handle0 = self.core_dma.get_handle("pulse0")
        self.core.break_realtime()

        T0 = self.core.get_rtio_counter_mu()
        t0 = now_mu()   # time before entering parallel statement

        # Need to measure the time to execute this playback_handle
        # And it's effect on the timeline cursor
        self.core_dma.playback_handle(pulses_handle0)
        T1 = self.core.get_rtio_counter_mu()
        t1 = now_mu()

        print("Timeline cursor increased by", self.core.mu_to_seconds(t1 - t0), "seconds")
        print("RTIO counter increased by", self.core.mu_to_seconds(T1 - T0), "seconds")
        print("timeline cursor - RTIO counter = ", self.core.mu_to_seconds(t1 - T1))

