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
        a[k] = int(0)
    if k%2 == 1:
        a[k] = int(1)

class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("zotino0")
        self.zotino = self.zotino0

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        self.zotino.init()
        delay(5*ms)

        self.zotino.write_dac(0, 1)
        # for i in range(30000):
        #     self.zotino.write_dac(0, 0)
        #     self.zotino.load()
        #     delay(0.1*ms)
        #
        #     self.zotino.write_dac(0, 1)
        #     self.zotino.load()
        #     delay(0.1*ms)
