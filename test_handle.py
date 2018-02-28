from force_handle import ForceHandle
from toon.input.clock import mono_clock
import numpy as np
np.set_printoptions(precision=3, suppress=True)

if __name__ == '__main__':
    device = ForceHandle(sampling_frequency=60)

    t0 = mono_clock.get_time()
    t1 = t0 + 10
    t2 = 0
    with device as dev:
        while mono_clock.get_time() < t1:
            time, data = dev.read()
            print(data)
            while mono_clock.get_time() < t2:
                pass
            t2 = mono_clock.get_time() + (1/60)
