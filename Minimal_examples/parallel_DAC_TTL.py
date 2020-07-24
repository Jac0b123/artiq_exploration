from artiq.experiment import*

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

class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("zotino0")
        self.setattr_device("ttl7")
        self.setattr_device("ttl6")
        self.zotino = self.zotino0

        self.setattr_device("sampler0")

    @kernel
    def run(self):
        d = int(0)
        self.core.reset()
        self.core.break_realtime()
        self.zotino.init()

        self.sampler0.init()
        delay(1*ms)
        for i in range(8):
            self.sampler0.set_gain_mu(i, 0)         # Set the gain of each channel to 1

        self.core.break_realtime()

        delay(5*ms)

        #for i in range(300):
        #with parallel:
            for j in range(5):
                self.zotino.write_dac(0,1)
                self.zotino.write_dac(1,0)
                self.zotino.load()
                delay(1*ms)
                self.zotino.write_dac(0,0)
                self.zotino.write_dac(1,1)
                self.zotino.load()
                delay(1*ms)

            #with sequential:
                self.core.break_realtime()
                for j in range(5):
                    self.ttl7.pulse(1*ms)
                    self.sampler0.sample_mu([int(0), int(0)])
                    delay(1*ms)

