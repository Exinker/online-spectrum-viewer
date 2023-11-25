import numpy as np

from libspectrum2_wrapper.alias import Array
from libspectrum2_wrapper.device import Device
from libspectrum2_wrapper.storage import BufferDeviceStorage


class Signal():

    def __init__(self, __data: Array[float]):
        assert __data.ndim == 2, 'Two dimential data are supported only!'

        self._data = __data

    # --------        number        --------
    @property
    def n_numbers(self) -> int:
        return self._data.shape[1]

    @property
    def number(self) -> Array[int]:
        return np.arange(self.n_numbers)

    # --------        value        --------
    @property
    def value(self) -> Array[int]:
        return self._data[0,:]


def await_read_signal(device: Device) -> Signal:
    """Read (blocking) output signal from device."""

    value = device.await_read()

    return Signal(value)


def read_signal(storage: BufferDeviceStorage) -> Signal | None:
    """Read (non-blocking) output signal from device."""

    if len(storage.data) == 0:
        return None

    value = storage.data[-1]
    value = value.reshape(1,-1)

    return Signal(value)
