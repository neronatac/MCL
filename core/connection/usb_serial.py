import logging
from typing import Optional

import serial
from serial.tools.list_ports import comports

from core.connection.abstract_conn import AbstractConnection


class USBSerial(AbstractConnection):
    @property
    def baudrate(self):
        return self.com.baudrate

    @baudrate.setter
    def baudrate(self, value):
        self.com.baudrate = value
        self._baudrate = value
        self.logger.debug(f"Baudrate set to {value}")

    def __init__(self, port=None, baudrate: int = 38400):
        self.logger = logging.getLogger('MCL.USBSerial')

        self._baudrate: int = baudrate
        self.com: serial.Serial = None
        self.hw_ref = None

        # Connection to USB device
        if port is None:
            port = self._search_port()
        self.connect(port)
        self.logger.info("ELM327 connected!")

    def _search_port(self):
        ports = comports()
        for p in ports:
            if p.vid == 0x0403 and p.pid == 0x6001:
                self.hw_ref = 'FTDI'
                self.logger.debug(f"Found ELM327-USB (FTDI): {p.device}")
                return p.device
            elif p.vid == 0x1A86 and p.pid == 0x7523:
                self.hw_ref = 'CH340'
                self.logger.debug(f"Found ELM327-USB (CH340): {p.device}")
                return p.device
        self.logger.error("No ELM327-USB found!")
        raise ConnectionError("No ELM327-USB found!")

    def connect(self, port):
        self.com = serial.Serial(port, self._baudrate)

    def read(self, size: int):
        ret = self.com.read(size)
        self.logger.debug(f"read {ret}")
        return ret

    def read_all(self):
        ret = self.com.read_all()
        self.logger.debug(f"read {ret}")
        return ret

    def read_until(self, expected: bytes = b'\n', size: Optional[int] = None):
        ret = self.com.read_until(expected, size)
        self.logger.debug(f"read {ret}")
        return ret

    def flush(self):
        self.com.flush()

    def write(self, data: bytes):
        self.logger.debug(f"writing {data}")
        return self.com.write(data)
