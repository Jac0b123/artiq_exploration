from artiq.experiment import *

class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("zotino0")
        self.zotino = self.zotino0

    @kernel
    def run(self):
        t1 = now_mu()
        #k = 0
        #for i in range(1000000):
        #    k = k + 1
        #print(k)

        delay(1*s)

        t2 = now_mu()
        print(self.core.mu_to_seconds(t2-t1))