import logging
from typing import Union

import serial
from serial.tools.list_ports import comports

logger = logging.getLogger()


class ELM327:
    """
    Driver of the ELM327 Interface product.
    """

    @property
    def baud(self):
        return self._baud

    @baud.setter
    def baud(self, value):
        # TODO
        self._baud = value
        logger.debug(f"Baudrate set to {value}")

    def __init__(self, port=None, baud=38400):
        """
        Connects to the USB device and configures the baudrate
        :param port: USB port to connect to
        :type port: str
        :param baud: baudrate to use
        :type baud: int
        """
        self._baud: int = None
        self.version_major: int = None
        self.version_minor: int = None

        self._com: serial.Serial = None

        # Connection to USB device
        if port is None:
            port = self._search_port()
        self._connect(port)

        # Configure the baudrate
        self.baud = baud

    @staticmethod
    def _search_port():
        ports = comports()
        for p in ports:
            if p.vid == 0x0403 and p.pid == 0x6001:
                logger.debug(f"Found ELM327-USB: {p.device}")
                return p.device

    def _connect(self, port):
        self._com = serial.Serial(port, 38400)

        self._com.flush()

        ver = self.send_command(b'AT Z')
        if not ver.startswith("ELM327"):
            raise ConnectionError(f"Bad reset message received: {ver}")
        else:
            self.version_major, self.version_minor = (int(v) for v in ver[8:].split('.'))
            logger.debug(f"Version: {self.version_major}.{self.version_minor}")

    def send_command(self, cmd: Union[bytes, str]):
        if isinstance(cmd, str):
            cmd = bytes(cmd, 'ASCII')

        if not cmd.startswith(b'AT'):
            cmd = b'AT ' + cmd

        self._com.write(cmd + b'\r\n')
        return self._recv()[len(cmd) + 2:]

    def _recv(self):
        data = self._com.read_until(b'>')

        assert data.endswith(b'\r\n\r\n>')
        data = data[:-5]  # delete b'\r\n\r\n>' at the end of received answer

        logger.debug(f"RECV: {data.decode('ascii', 'ignore')}")

        return data.decode('ascii')


if __name__ == '__main__':
    obd = ELM327()
    print(obd.send_command('I'))
    print(obd.send_command('RV'))
