import logging
from typing import Optional

import serial
from serial.tools.list_ports import comports

from core.connection.abstract_conn import AbstractConnection

logger = logging.getLogger()


class USBSerial(AbstractConnection):
    @property
    def baudrate(self):
        return self.com.baudrate

    @baudrate.setter
    def baudrate(self, value):
        self.com.baudrate = value
        self._baudrate = value
        logger.debug(f"Baudrate set to {value}")

    def __init__(self, port=None, baudrate: int = 38400):
        self._baudrate: int = baudrate
        self.com: serial.Serial = None

        # Connection to USB device
        if port is None:
            port = self._search_port()
        self.connect(port)

    @staticmethod
    def _search_port():
        ports = comports()
        for p in ports:
            if p.vid == 0x0403 and p.pid == 0x6001:
                logger.debug(f"Found ELM327-USB: {p.device}")
                return p.device

    def connect(self, port):
        self.com = serial.Serial(port, self._baudrate)

    def read(self, size: int):
        return self.com.read(size)

    def read_all(self):
        return self.com.read_all()

    def read_until(self, expected: bytes = b'\n', size: Optional[int] = None):
        return self.com.read_until(expected, size)

    def flush(self):
        self.com.flush()

    def write(self, data: bytes):
        return self.com.write(data)
