""" Acquires sinusoidal signal with sampler while simultaneously applying
zotino output pulse.

This is a modified version of sampler/test_consistent_sampler_rate.py
Here we test if simultaneously applying a DMA pulse via the Zotino affects
the sample rate.

At the moment this script raises an RTIOUnderflow error because we cannot make
the Zotino output a DMA pulse with more than ~80 instructions.
"""

from artiq.experiment import *
from matplotlib import pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


# plt.ion()

target_frequency = 2e3  # Known sinusoidal input signal
sample_rates = np.linspace(10e3, 20e3, 3)
samples = 5000
channels = 2  # Number of channels to acquire
sampler_sine_channel = -1  # Sinusoidal input channel in sampler
sampler_zotino_channel = -2  # Channel at which the sampler measures the zotino sine

zotino_output_channel = 0  # Channel at which the zotino outputs a sine
zotino_sample_rate = int(1e3)
zotino_frequency = 1e2
zotino_points = int(zotino_sample_rate / zotino_frequency)

zotino_duration = 0.5  # seconds
zotino_repetitions = int(zotino_duration * zotino_frequency)
print('Zotino repetitions:', zotino_repetitions)


def calculate_sample_interval(sample_rate) -> TFloat:
    return float(1 / sample_rate) * s  - 2.6 * us  - 0.01255 / sample_rate * s


def find_initial_sine_fit_parameters(trace, sample_interval):
    """ Estimate initial fitting parameters for a sinusoidal signal """
    A_init = (np.max(trace) - np.min(trace)) / 2

    # Find frequency and phase from a Fourier transform of data
    fft_flips = np.fft.fft(trace)
    fft_flips_abs = np.abs(fft_flips)[:int(len(fft_flips) / 2)]
    fft_freqs = np.fft.fftfreq(len(fft_flips), sample_interval)[
                :int(len(fft_flips) / 2)]
    frequency_idx = np.argmax(fft_flips_abs[1:]) + 1

    f_init = fft_freqs[frequency_idx]
    phase_init = np.pi / 2 + np.angle(fft_flips[frequency_idx])

    init_params = [A_init, f_init, phase_init]

    return init_params


def fit_sine(trace, sample_rate):
    """ Fit results to a sine wave """

    def sine_func(x, A, f, phase):
        return A * np.sin(2 * np.pi * f * x + phase)

    sample_interval = float(1 / sample_rate)

    t_list = np.arange(0, samples * sample_interval, sample_interval)
    t_list = t_list[:samples]

    init_params = find_initial_sine_fit_parameters(trace, sample_interval)
    print('Initial parameters:', init_params)

    bounds = ([500, init_params[1] * 0.7, -np.pi],
              [1000, init_params[1] * 1.5, 2 * np.pi])

    # Perform fitting routine
    try:
        params, params_covariance = curve_fit(sine_func,
                                              t_list, trace,
                                              p0=init_params,
                                              bounds=bounds)
    except ValueError:
        raise ValueError('Init params out of bounds', init_params, '\n', bounds)

    # print('Fitted params:', params)
    print('Estimated frequency: {} kHz'.format(params[1] / 1e3))

    return {'fit_params': params,
            'initial_fit_data': sine_func(t_list, *init_params),
            'fit_data': sine_func(t_list, *params)}


def plot_trace(trace, sample_rate, fit=False):
    sample_interval = calculate_sample_interval(sample_rate)
    t_list = np.arange(0, samples * sample_interval, sample_interval)[:samples]

    plt.figure(figsize=(15, 5))
    plt.plot(t_list, trace, 'o')

    if fit:
        plt.plot(t_list, fit['initial_fit_data'], '--')
        plt.plot(t_list, fit['fit_data'], '-')

    plt.show()

def plot_traces(traces):
    plt.figure()
    plt.plot(traces)
    plt.show()


def plot_measured_frequencies(sample_rates, measured_frequencies):
    fig, axes = plt.subplots(3, 1, sharex=True)

    ax = axes[0]
    ax.plot(sample_rates/1e3, measured_frequencies, 'o')
    ax.set_ylabel('Measured frequencies (Hz)')

    ax = axes[1]
    frequency_offset = np.array(measured_frequencies) - target_frequency
    ax.plot(sample_rates/1e3, frequency_offset, 'o')
    ax.set_ylabel('Frequency offset (Hz)')

    ax = axes[2]
    instruction_duration = (-frequency_offset) / measured_frequencies / sample_rates
    # instruction_duration = frequency_offset / sample_rates
    ax.plot(sample_rates/1e3, instruction_duration * 1e6)
    ax.set_xlabel('Sample rate(kS/s)')
    ax.set_ylabel('instruction duration (us)')

    plt.show()

    input('Finished. Press enter to continue')


class sampler(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.setattr_device("sampler0")
        self.sampler = self.sampler0
        self.setattr_device("zotino0")
        self.zotino = self.zotino0

        self.core.reset()

        self.measured_frequencies = [0. for _ in sample_rates]
        self.traces_data = [[int(0)] * channels for _ in range(samples)]
        self.sine_voltages = np.sin(np.linspace(0, 2 * np.pi, zotino_points))

    @rpc(flags={"async"})
    def print(self, msg, *args):
        print(msg.format(*args))

    def analyze_traces(self, traces_data, sample_rate, plot=False) -> TFloat:
        print('sample_interval without instruction_delay: {:.1f} us'.format(
            calculate_sample_interval(sample_rate)*1e6))

        trace = [sample[sampler_sine_channel] for sample in traces_data]
        fit = fit_sine(trace, sample_rate)

        if plot:
            plot_trace(trace, sample_rate, fit=fit)

        measured_frequency = fit['fit_params'][1]
        return measured_frequency

    @kernel
    def initialize(self):
        self.core.break_realtime()
        self.sampler.init()
        delay(5*ms)

        for i in range(channels):
            self.sampler.set_gain_mu(i, 0)  # Set the gain of each channel to 1
            delay(100*us)

        self.zotino.init()

    @kernel
    def acquire_trace(self, samples, sample_rate):
        sample_interval = calculate_sample_interval(sample_rate)

        k = 0
        try:
            self.core.break_realtime()
            t0 = now_mu()
            for k in range(samples):
                self.sampler.sample_mu(self.traces_data[k])
                delay(sample_interval)
        except RTIOUnderflow as e:
            print('Failed at index', k)
            raise

        # Perform timing analysis
        t1 = now_mu()
        acquisition_time = self.core.mu_to_seconds(t1 - t0)
        calculated_sample_rate = samples / acquisition_time
        self.print('Acquisition time: {:.2f} ms, '
                   '\tMeasured sample_rate: {:.1f} kS/s,'
                   '\t Measured sample_interval: {:.1f} us',
                   acquisition_time*1e3,
                   calculated_sample_rate / 1e3,
                   1/calculated_sample_rate * 1e6)
        self.core.break_realtime()

    @kernel
    def record(self):
        with self.core_dma.record("pulse0"):
            N = 50
            for k in range(N):
                voltage = float(-0.5 + k / N)
                self.zotino.write_dac(0, voltage)
                self.zotino.write_dac(1, voltage)
                self.zotino.load()

                # Subtract 800 ns, i.e. the zotino load duration
                delay(1 / zotino_sample_rate * s - 0.8*us)
        with self.core_dma.record("pulse1"):
            N = 50
            for k in range(N):
                voltage = float(0.5 - k / N)
                self.zotino.write_dac(0, voltage)
                self.zotino.write_dac(1, voltage)
                self.zotino.load()

                # Subtract 800 ns, i.e. the zotino load duration
                delay(1 / zotino_sample_rate * s - 0.8*us)

    @kernel
    def acquire_trace_simple(self, samples, sample_interval):
        delay(1 * ms)
        for k in range(samples):
            self.sampler.sample_mu(self.traces_data[k])
            delay(sample_interval)
        delay(1 * ms)

    @kernel
    def run(self):
        self.initialize()

        self.record()
        pulses_handle0 = self.core_dma.get_handle("pulse0")
        pulses_handle1 = self.core_dma.get_handle("pulse1")

        self.core.break_realtime()

        sample_rate = 50e3
        sample_interval = calculate_sample_interval(sample_rate)
        self.core.break_realtime()

        with parallel:
            # Generate sample trace list for multiple channels
            # self.acquire_trace(samples, sample_rate)
            # with sequential:
                # for k in range(zotino_repetitions):
            with sequential:
                self.core_dma.playback_handle(pulses_handle0)
                self.core_dma.playback_handle(pulses_handle0)
            with sequential:
                # self.core.break_realtime()
                delay(2*ms)
                self.acquire_trace_simple(samples, sample_interval)
                delay(400*ms)
                self.acquire_trace_simple(samples, sample_interval)
                delay(400*ms)

        # self.core.break_realtime()
        # delay(1*s)
        # plot_traces(self.traces_data)

        # k = 0
        # for sample_rate in sample_rates:
        #     self.print('\nSample rate: {:.1f} kS/s', sample_rate/1e3)
        #     sample_interval = calculate_sample_interval(sample_rate)
        #     self.core.break_realtime()
        #
        #
        #     for k in range(zotino_repetitions):
        #         self.core_dma.playback_handle(pulses_handle0)
            # try:
            #     with parallel:
            #         # Generate sample trace list for multiple channels
            #         # self.acquire_trace(samples, sample_rate)
            #         self.core_dma.playback_handle(pulses_handle0)
            #         with sequential:
            #             self.acquire_trace_simple(samples, sample_interval)
            # except RTIOUnderflow:
            #     raise


            # Analyze results
            # self.core.break_realtime()
            # frequency = self.analyze_traces(self.traces_data, sample_rate)#, plot=True)
            # self.measured_frequencies[k] = frequency

            # k += 1

        # plot_measured_frequencies(sample_rates, self.measured_frequencies)


