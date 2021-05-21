import logging
from typing import Union

from core.connection.abstract_conn import AbstractConnection
from core.connection.usb_serial import USBSerial

logger = logging.getLogger()


class ELM327:
    """
    Driver of the ELM327 Interface product.
    """

    def __init__(self, connection):
        self.version_major: int = -1
        self.version_minor: int = -1

        self._conn: AbstractConnection = connection
        self.connect()

    def connect(self):
        self._conn.flush()

        ver = self.send_command(b'AT Z')
        if not ver.startswith("ELM327"):
            raise ConnectionError(f"Bad reset message received: {ver}")
        else:
            self.version_major, self.version_minor = (int(v) for v in ver[8:].split('.'))
            logger.debug(f"ELM327 version: {self.version_major}.{self.version_minor}")

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

        logger.debug(f"RECV: {data.decode('ascii', 'ignore')}")

        return data.decode('ascii')


if __name__ == '__main__':
    conn = USBSerial()
    obd = ELM327(conn)
    print(obd.send_command('I'))
    print(obd.send_command('RV'))
