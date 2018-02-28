from ctypes import c_double
import numpy as np
from toon.input.base_input import BaseInput
import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.errors import DaqError

class ForceHandle(BaseInput):
    @staticmethod
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 240)
    
    @staticmethod
    def data_shapes(**kwargs):
        return [[5, kwargs.get('sampling_frequency')/60]]
    
    @staticmethod
    def data_types(**kwargs):
        return [c_double]
    
    def __init__(self, **kwargs):
        super(ForceHandle, self).__init__(**kwargs)
        self.sampling_frequency = ForceHandle.samp_freq(**kwargs)
        self.period = 1/self.sampling_frequency
        self._data_buffer = np.full(ForceHandle.data_shapes(**kwargs)[0], np.nan)
        self._tmp_buffer = np.copy(np.transpose(self._data_buffer)) # nidaqmx expects different shape
        self._time = None
    
    def __enter__(self):
        self._device_name = nidaqmx.system.System.local().devices[0].name
        self.channels = [self._device_name + '/ai' + str(n) for n in
                         [1, 2, 3, 4, 5]]  # todo: check
        self._device = nidaqmx.Task()
        self._device.ai_channels.add_ai_voltage_chan(','.join(self.channels),
                                                     terminal_config=TerminalConfiguration.DIFFERENTIAL,
                                                     min_val=-10.0, max_val=10.0)
        self._device.timing.cfg_samp_clk_timing(self.sampling_frequency,
                                                sample_mode=AcquisitionType.CONTINUOUS)
        self._reader = AnalogMultiChannelReader(self._device.in_stream)
        self._device.register_every_n_samples_acquired_into_buffer_event(self._data_buffer.shape[1], self.callback)
        self._device.start()
        return self

    def callback(self, task_handle, every_n_samples_event_type, number_of_samples, callback_data):
        self._reader.read_many_sample(self._tmp_buffer, 
                                      number_of_samples_per_channel=self._data_buffer.shape[1],
                                      timeout=0)
        self._time = self.clock()
        return 0
    
    def read(self):
        if not self._time:
            return None, None
        np.copyto(self._data_buffer, np.transpose(self._tmp_buffer))
        tmptime = self._time
        self._time = None
        self._data_buffer.fill(np.nan)
        return tmptime, self._data_buffer

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._device.stop()
        self._device.close()