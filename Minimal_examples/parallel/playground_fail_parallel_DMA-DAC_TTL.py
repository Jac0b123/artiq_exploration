""" This file simultaneously applies a zotino ramp pulse and TTL pulses
The Zotino ramp pulse is stored in the DMA.
When the number of points composing the ramp pulse exceeds ~80, an RTIOUnderflow
error is always raised.

It seems the number of DMA pulses has a maximum, and it isn't high...
"""

points = 100 # Number of points for the zotino ramping pulse
# Choosing ~90 points or higher causes an RTIOunderflow error.

import sys
from artiq.experiment import *
import numpy as np
from matplotlib import pyplot as plt

class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.setattr_device("zotino0")
        self.zotino = self.zotino0
        self.setattr_device("ttl6")

    @kernel
    def record(self):
        with self.core_dma.record("pulse0"):
            # at_mu(now_mu() + int(10*1e9))        # push the timeline cursor into the future
            for k in range(points):
                self.zotino.write_dac(0, float(k / points))  # ramping pulse
                #self.zotino.write_dac(1, float(k / points))
                self.zotino.load()
                delay(50*ms)

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
        t1 = 0
        t2 = 0
        T1 = 0
        t3 = 0
        T3 = 0
        try:
            with parallel:
                with sequential:
                    # Need to measure the time to execute this playback_handle
                    # And it's effect on the timeline cursor
                    self.core_dma.playback_handle(pulses_handle0)
                    T1 = self.core.get_rtio_counter_mu()
                    t1 = now_mu()
                with sequential:
                    t3 = now_mu()
                    T3 = self.core.get_rtio_counter_mu()
                    t2 = now_mu()
                    for k in range(100):
                        delay(10*ms)
                        self.ttl6.pulse(0.1*ms)

        except RTIOUnderflow:
            print("RTIO UNDERFLOW")

        print("timeline cursor = ", self.core.mu_to_seconds(t1 - t0))
        print("wall clock time elapsed during playback = ", self.core.mu_to_seconds(T1 - T0))
        print("timeline cursor - wall clock = ",
              self.core.mu_to_seconds(t1 - T1))
        print(
            "After at_mu intruction, then timeline cursor - wall clock = ",
            self.core.mu_to_seconds(t2 - T1))

        print('t3 - t0 = ', self.core.mu_to_seconds(t3 - t0))
        print('T3 - T0 = ', self.core.mu_to_seconds(T3 - T0)*1e6, 'us')


