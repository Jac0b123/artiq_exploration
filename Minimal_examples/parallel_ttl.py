from artiq.experiment import*


class Tutorial(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl6")
        self.setattr_device("ttl7")

    @kernel
    def run(self):
        self.core.reset()
        for i in range(3000):
            with parallel:
                for x in range(4):
                    delay(1*ms)
                    self.ttl6.pulse(1*ms)
                self.ttl7.pulse(5*ms)
            delay(2*ms)