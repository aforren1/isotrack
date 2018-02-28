from ctypes import c_int32
from toon.input.base_input import BaseInput
from psychopy.event import Mouse as ms


class Mouse(BaseInput):
    """Sham interface for debugging."""
    @staticmethod
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 100)

    @staticmethod
    def data_shapes(**kwargs):
        return [[2]]

    @staticmethod
    def data_types(**kwargs):
        return [c_int32]
    
    def __init__(self, **kwargs):
        super(Mouse, self).__init__(**kwargs)
    
    def __enter__(self):
        self.dev = ms()
        return self
    
    def __exit__(self, x, y, z):
        pass
    
    def read(self):
        time = self.clock()
        pos = self.dev.getPos()
        return time, pos

