from force_handle import ForceHandle
from toon.input import MultiprocessInput as MpI
from toon.input.clock import mono_clock
import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(precision=4, suppress=True)

if __name__ == '__main__':
    lst = list()
    device = MpI(ForceHandle, clock=mono_clock.get_time, sampling_frequency=200)
    #device = ForceHandle(clock=mono_clock.get_time)
    t0 = mono_clock.get_time()
    t1 = t0 + 15
    t2 = 0
    time2 = 0
    with device as dev:
        while mono_clock.get_time() < t1:
            time, data = dev.read()
            if time is not None:
                print(data)
                dff = np.diff(time)
                #print(dff)
                lst.append(dff)
            while mono_clock.get_time() < t2:
                pass
            t2 = mono_clock.get_time() + (1/60)
    
    lst = np.concatenate(lst)
    #plt.plot(lst)
    #plt.show()