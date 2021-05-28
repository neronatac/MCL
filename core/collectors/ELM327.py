import logging
import time
import warnings
from typing import Union

from core.connection.abstract_conn import AbstractConnection
from core.connection.usb_serial import USBSerial

logger = logging.getLogger()


class VersionError(Exception):
    pass


class ELM327:
    """
    Driver of the ELM327 Interface product.
    """
    BAUD9_6K = (b'00', 9_600)
    BAUD19_2K = (b'D0', 19_200)
    BAUD38_4K = (b'68', 38_400)
    BAUD57_6K = (b'45', 57_600)
    BAUD115_2K = (b'23', 115_200)
    BAUD230_4K = (b'11', 230_400)
    BAUD500K = (b'08', 500_000)

    @property
    def baudrate(self):
        if not isinstance(self._conn, USBSerial):
            return self._baudrate

        raise AttributeError(f"No baudrate defined when connection is {type(self._conn)} (USBSerial needed)")

    @baudrate.setter
    def baudrate(self, value):
        warnings.warn("This method has not been tested in reality!")

        if not isinstance(self._conn, USBSerial):
            raise AttributeError(f"No baudrate defined when connection is {type(self._conn)} (USBSerial needed)")

        if value not in (self.BAUD9_6K, self.BAUD19_2K, self.BAUD38_4K, self.BAUD57_6K,
                         self.BAUD115_2K, self.BAUD230_4K, self.BAUD500K):
            raise ValueError(f"Baudrate must be one of the BAUDxxK constants")

        self._conn.write(b'AT BRD ' + value[0] + b'\r\n')

        time.sleep(0.03)
        rep = self._conn.read_all()
        if rep == b'AT BRD ' + value[0] + b'\r\n?\r\n\r\n>':
            raise VersionError(f"This ELM327 does not support the baudrate changing command (it is too old)")
        if not rep == b'OK':
            raise ConnectionError(f"Problem when testing the new baudrate ({value[1]})")

        self._conn.baud = value[1]

        rep = self._conn.read(4)
        if not rep == b'AT I':
            raise ConnectionError(f"Problem when testing the new baudrate ({value[1]})")

        self._conn.write(b'\n')

        rep = self._conn.read(2)
        if not rep == b'OK':
            raise ConnectionError(f"Problem when testing the new baudrate ({value[1]})")

        self._read()

    def __init__(self, connection):
        self.version_major: int = -1
        self.version_minor: int = -1

        self._baudrate = 38400

        self._conn: AbstractConnection = connection
        self.connect()

    def connect(self):
        self._conn.flush()
        self.reset()

    def reset(self):
        logger.info(f"ELM327 reset")
        ver = self.send_command(b'AT Z')
        if not ver.startswith("ELM327"):
            raise ConnectionError(f"Bad reset message received: {ver}")
        else:
            self.version_major, self.version_minor = (int(v) for v in ver[8:].split('.'))
            logger.info(f"ELM327 version: {self.version_major}.{self.version_minor}")

    def send_command(self, cmd: Union[bytes, str]):
        if isinstance(cmd, str):
            cmd = bytes(cmd, 'ASCII')

        if not cmd.startswith(b'AT'):
            cmd = b'AT ' + cmd

        self._conn.write(cmd + b'\r\n')
        return self._read()[len(cmd) + 2:]

    def _read(self):
        data = self._conn.read_until(b'>')

        assert data.endswith(b'\r\n\r\n>')
        data = data[:-5]  # delete b'\r\n\r\n>' at the end of received answer

        return data.decode('ascii')


if __name__ == '__main__':
    from core.utils.log import setup_log

    setup_log()

    conn = USBSerial()
    obd = ELM327(conn)
    print(obd.send_command('I'))
    print(obd.send_command('RV'))
    obd.baudrate = obd.BAUD57_6K
