from artiq.experiment import *
import numpy as np

def input_voltage() -> TList(TFloat):
    voltage_str = input()
    if voltage_str == 'q':
        raise RuntimeError('Quitting')

    channel, voltage = voltage_str.split(' ')
    return [float(channel), float(voltage)]

class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("zotino0")
        self.zotino = self.zotino0
        self.setattr_device("sampler0")
        self.sampler = self.sampler0
        self.step = 0.002
        self.count = 2

    @kernel
    def run(self):
        self.set_dataset("sampler", np.full(self.count, np.nan),
                         broadcast=True)

        self.core.break_realtime()
        self.sampler.init()
        delay(5 * ms)
        for i in range(8):
            self.sampler.set_gain_mu(i, 0)  # Sets the gain
            delay(100 * us)

        while True:
            print('Please enter: channel input_voltage)' )

            channel_voltage = input_voltage()
            channel = int(channel_voltage[0])
            voltage = channel_voltage[1]
            print('channel:', channel, 'voltage:', voltage)

            self.core.break_realtime()
            d= self.zotino.init()
            delay(1 * ms)

            # for v in self.voltages:
            #     self.core.break_realtime()
            #     self.zotino.init()
            #     delay(1 * ms)
            #     self.zotino.write_dac(channel, v)
            #     self.zotino.load()

            self.zotino.write_dac(channel, voltage)
            self.zotino.load()

            delay(100 * ms)

            smp = [0.0] * 8

            self.core.break_realtime()
            for k in range(self.count):
                self.sampler.sample(smp)
                delay(300 * us)
                self.mutate_dataset("sampler", k, smp[2])
                print(smp[2])
                self.core.break_realtime()