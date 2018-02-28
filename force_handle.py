from ctypes import c_double
import numpy as np
from toon.input.base_input import BaseInput
import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration


class ForceHandle(BaseInput):
    @staticmethod
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 240)

    @staticmethod
    def data_shapes(**kwargs):
        return [[5]]  # presumably x, y, z, rx, ry, rz

    @staticmethod
    def data_types(**kwargs):
        return [c_double]

    def __init__(self, **kwargs):
        super(ForceHandle, self).__init__(**kwargs)
        self.sampling_frequency = ForceHandle.samp_freq(**kwargs)
        self.period = 1/self.sampling_frequency
        self.t1 = 0
        self._time = None
        self._data_buffer = np.full(ForceHandle.data_shapes(**kwargs)[0], np.nan)

    def __enter__(self):
        self._device_name = nidaqmx.system.System.local().devices[0].name
        self.channels = [self._device_name + '/ai' + str(n) for n in
                         [1, 2, 3, 4, 5]]  # todo: check
        # x is 7 - 8 (ai3 - ai11)
        # y may be 3 - 4 (ai1 - ai9)
        self._device = nidaqmx.Task()
        self._device.ai_channels.add_ai_voltage_chan(','.join(self.channels),
                                                     terminal_config=TerminalConfiguration.DIFFERENTIAL,
                                                     min_val=-10.0, max_val=10.0)
        self._device.timing.cfg_samp_clk_timing(self.sampling_frequency,
                                                sample_mode=AcquisitionType.CONTINUOUS,
                                                samps_per_chan=1)
        self._device.start()
        return self

    def read(self):
        data = self._device.read()
        time = self.clock()
        np.copyto(self._data_buffer, data)
        # while self.clock() < self.t1:
        #     pass
        # self.t1 = self.clock() + self.period
        return time, self._data_buffer

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._device.stop()
        self._device.close()
