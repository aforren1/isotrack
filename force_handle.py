from ctypes import c_double
import numpy as np
from toon.input.base_input import BaseInput
import nidaqmx
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.constants import AcquisitionType, TerminalConfiguration


class ForceHandle(BaseInput):
    @staticmethod
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 250)

    @staticmethod
    def data_shapes(**kwargs):
        return [[8]]  # presumably x, y, z, rx, ry, rz

    @staticmethod
    def data_types(**kwargs):
        return [c_double]

    def __init__(self, **kwargs):
        super(ForceHandle, self).__init__(**kwargs)
        self.sampling_frequency = ForceHandle.samp_freq(**kwargs)
        self.period = 1/self.sampling_frequency
        self.t1 = 0
        self._time = None
        dims = ForceHandle.data_shapes(**kwargs)[0]
        dims2 = dims.copy()
        dims2[0] *= 2
        self._data_buffer = np.full(dims, np.nan)
        self._tmp_buffer = np.full(dims2, np.nan)

    def __enter__(self):
        self._device_name = nidaqmx.system.System.local().devices[0].name
        self.channels = [self._device_name + '/ai' + str(n) for n in
                         [0, 8, 1, 9, 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]] 
        # x is 7 - 8 (ai3 - ai11)
        # y may be 3 - 4 (ai1 - ai9)
        self._device = nidaqmx.Task()
        self._device.ai_channels.add_ai_voltage_chan(','.join(self.channels))
        self._reader = AnalogMultiChannelReader(self._device.in_stream)
        self._device.start()
        return self

    def read(self):
        self._reader.read_one_sample(self._tmp_buffer)
        time = self.clock()
        self._data_buffer = self._tmp_buffer[::2] - self._tmp_buffer[1::2]
        while self.clock() < self.t1:
            pass
        self.t1 = self.clock() + self.period
        return time, self._data_buffer

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._device.stop()
        self._device.close()
