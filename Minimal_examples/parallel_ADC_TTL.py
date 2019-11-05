from artiq.experiment import *
import numpy as np
sample_rate = float(input("Enter sample rate: "))

class sampler(EnvExperiment):
    def export_data(self, data):
        # Convert data using code in adc_mu_to_volt
        scale = 20./(1 << 16)
        data_scaled = np.array(data) * scale

        f=open("data.txt", "w+")
        for d in data_scaled:
            f.write(str(d)+'\n')

    def build(self):
        self.setattr_device("core")
        self.setattr_device("sampler0")
        self.sampler = self.sampler0
        self.setattr_device("ttl6")
        self.setattr_device("ttl7")
        self.core.reset()

    @kernel
    def run(self):
        self.core.break_realtime()
        self.sampler.init()
        delay(1*ms)
        for i in range(8):
            self.sampler0.set_gain_mu(i, 0)         # Set the gain of each channel to 1

        # This list holds all the sampled data for 2 channels, channel 6 and channel 7
        smp = [[int(0)]*8 for k in range(100000)]
        smp1 = [[int(0)]*2 for k in range(100000)]

        self.core.break_realtime()

        for k in range(9999):
            with parallel:
                self.ttl7.pulse(0.1*ms)
                self.sampler0.sample_mu(smp1[2*k])
            with parallel:
                delay(0.1*ms)
                self.sampler0.sample_mu(smp[2*k+1])
            #delay(1*ms)
                #for j in range(5):
                #    self.ttl6.pulse(3*ms)
                #    self.ttl7.pulse(3*ms)
                #    delay(1 * ms)
                #for j in range(97):
                #    self.sampler0.sample_mu(smp1[j * (k + 1)])
                #    delay(0.1*ms)

        self.export_data(smp1)



