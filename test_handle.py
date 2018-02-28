from force_handle import ForceHandle
from toon.input import MultiprocessInput as MpI
from toon.input.clock import mono_clock
import numpy as np
np.set_printoptions(precision=5, suppress=True)

if __name__ == '__main__':
    device = MpI(ForceHandle, sampling_frequency=200)

    t0 = mono_clock.get_time()
    t1 = t0 + 10
    t2 = 0
    with device as dev:
        while mono_clock.get_time() < t1:
            time, data = dev.read()
            if time is not None:
                print(data)
                #print(np.diff(time))
                while mono_clock.get_time() < t2:
                    pass
                t2 = mono_clock.get_time() + (1/60)
