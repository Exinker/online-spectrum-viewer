import dataclasses
import json
import os
from dataclasses import dataclass
from functools import partial

import numpy as np

from libspectrum2_wrapper.device import Device, DeviceEthernetConfig, DeviceStatusCode
from libspectrum2_wrapper.storage import BufferDeviceStorage


BUFFER_HANDLER = {
    'average': partial(np.mean, axis=0),
}


# --------        experiment        --------
@dataclass
class Config:
    ip: str
    exposure: float
    buffer_size: int
    buffer_handler: str

    @classmethod
    def default(cls) -> 'Config':
        """Get config from defalut."""

        config = Config(
            ip='10.116.220.2',
            exposure=2,
            buffer_size=1,
            buffer_handler='average',
        )
        config.to_json()

        return config

    @classmethod
    def from_json(cls, filepath: str = os.path.join('config.json')):
        """Load config from json."""

        if os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                config = Config(**json.load(file))
        else:
            config = cls.default()

        return config

    def to_json(self) -> None:
        """Save config to json."""

        filepath = os.path.join('config.json')
        with open(filepath, 'w') as file:
            json.dump(dataclasses.asdict(self), file)


def setup_experiment() -> Device:
    """Setup an experiment by config."""

    # load config
    config = Config.from_json()

    # setup device
    device =  Device(
        config=DeviceEthernetConfig(
            ip=config.ip,
        ),
        storage=BufferDeviceStorage(
            buffer_size=config.buffer_size,
            buffer_handler=BUFFER_HANDLER[config.buffer_handler],
        ),
    )
    try:
        device = device.connect()
        device = device.set_exposure(config.exposure)
    except AssertionError as error:
        print(error)

    #
    return device


def is_device_ready(device: Device) -> bool:
    """Check device connection and exposure."""

    is_connected = device.is_status(
        codes=(DeviceStatusCode.CONNECTED, DeviceStatusCode.DONE_READING),
    )

    return (device.storage is not None) and (device.exposure is not None) and is_connected
