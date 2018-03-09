from ctypes import c_double
import numpy as np
from toon.input.base_input import BaseInput
import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration
from nidaqmx.stream_readers import AnalogMultiChannelReader


class ForceHandle(BaseInput):
    @staticmethod
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 240)

    @staticmethod
    def data_shapes(**kwargs):
        return [[int(kwargs.get('sampling_frequency', 240)/60.0), 8]]

    @staticmethod
    def data_types(**kwargs):
        return [c_double]

    def __init__(self, **kwargs):
        super(ForceHandle, self).__init__(**kwargs)
        self.sampling_frequency = ForceHandle.samp_freq(**kwargs)
        self.period = 1/self.sampling_frequency
        shape = ForceHandle.data_shapes(**kwargs)[0]
        shape_ext = shape.copy()
        shape_ext[1] *= 2
        self._data_buffer = np.full(shape, np.nan)
        # nidaqmx expects different shape
        self._tmp_buffer = np.full(shape_ext[::-1], np.nan)
        self._tmp_buffer_2 = np.full(shape_ext, np.nan)
        self._time = None

    def __enter__(self):
        self._device_name = nidaqmx.system.System.local().devices[0].name
        self.channels = [self._device_name + '/ai' + str(n) for n in
                         [0, 8, 1, 9, 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]]  # todo: check
        self._device = nidaqmx.Task()
        self._device.ai_channels.add_ai_voltage_chan(','.join(self.channels))
        self._device.timing.cfg_samp_clk_timing(self.sampling_frequency,
                                                sample_mode=AcquisitionType.CONTINUOUS)
        self._reader = AnalogMultiChannelReader(self._device.in_stream)
        self._device.register_every_n_samples_acquired_into_buffer_event(
            self._data_buffer.shape[0], self.callback)
        self._device.start()
        return self

    def callback(self, task_handle, every_n_samples_event_type, number_of_samples, callback_data):
        self._time = self.clock()
        self._reader.read_many_sample(self._tmp_buffer,
                                      number_of_samples_per_channel=number_of_samples,
                                      timeout=0)
        return 0

    def read(self):
        if not self._time:
            return None, None
        tmptime = self._time
        self._time = None
        np.copyto(self._tmp_buffer_2, np.transpose(self._tmp_buffer))
        self._data_buffer = self._tmp_buffer_2[:, ::2] - self._tmp_buffer_2[:, 1::2]
        return tmptime, self._data_buffer

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._device.stop()
        self._device.close()
