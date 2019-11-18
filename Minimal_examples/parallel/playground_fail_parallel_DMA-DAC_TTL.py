""" This file simultaneously applies a zotino ramp pulse and TTL pulses
The Zotino ramp pulse is stored in the DMA.
When the number of points composing the ramp pulse exceeds ~80, an RTIOUnderflow
error is always raised.

It seems the number of DMA pulses has a maximum, and it isn't high...
"""

points = 70 # Number of points for the zotino ramping pulse
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
            #at_mu(now_mu() + int(10*1e9))        # push the timeline cursor into the future
            for k in range(points):
                self.zotino.write_dac(0, float(k / points))  # ramping pulse
                #self.zotino.write_dac(1, float(k / points))
                self.zotino.load()
                delay(30*ms)

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
        t0 = now_mu()   # time before entering parallel statement
        T0 = self.core.get_rtio_counter_mu()
        t1 = 0
        T1 = 0
        try:
            with parallel:
                self.core_dma.playback_handle(pulses_handle0)
                #at_mu(now_mu() + int(2*1e9))
                t1 = now_mu()
                T1 = self.core.get_rtio_counter_mu()
                with sequential:
                    #self.core.break_realtime()
                    t2 = now_mu()
                    for k in range(100):
                        delay(10*ms)
                        self.ttl6.pulse(0.1*ms)

            print("timeline cursor = ", self.core.mu_to_seconds(t1 - t0))
            print("wall clock = ", self.core.mu_to_seconds(T1-T0))
            print("timeline cursor - wall clock = ",self.core.mu_to_seconds(t1 - T1))
        except RTIOUnderflow:
            # print the timeline cursor and also the wall clock

            print("timeline cursor = ", self.core.mu_to_seconds(t1 - t0))
            print("wall clock = ", self.core.mu_to_seconds(T1 - T0))
            print("timeline cursor - wall clock = ", self.core.mu_to_seconds(t1 - T1))


