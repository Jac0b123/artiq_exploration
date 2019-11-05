from artiq.experiment import *


class UrukulTest(EnvExperiment):
    def build(self):

        self.setattr_device("core")
        # self.setattr_device("fmcdio_dirctl")
        self.setattr_device("urukul0_cpld")
        self.setattr_device("urukul0_ch0")
        self.setattr_device("urukul0_ch1")
        self.setattr_device("urukul0_ch2")
        self.setattr_device("urukul0_ch3")
        self.setattr_device("led0")

    @kernel
    def run(self):
        self.core.reset()
        delay(5*ms)
        # Zotino plus Urukul (MISO, IO_UPDATE_RET)
        # self.fmcdio_dirctl.set(0x0A008800)

        self.urukul0_cpld.init()
        self.urukul0_ch0.init()
        self.urukul0_ch1.init()
        self.urukul0_ch2.init()
        self.urukul0_ch3.init()

        delay(1000*us)
        #self.urukul0_ch0.set_frequency(1*kHz)
        self.urukul0_ch0.set(1000)
        self.urukul0_ch0.sw.on()
        self.urukul0_ch0.set_att(0.)