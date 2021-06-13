import logging
from typing import Union

from core.connection.abstract_conn import AbstractConnection
from core.connection.usb_serial import USBSerial


class ELM327Error(Exception):
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
        if not isinstance(self._conn, USBSerial):
            raise AttributeError(f"No baudrate defined when connection is {type(self._conn)} (USBSerial needed)")

        if value not in (self.BAUD9_6K, self.BAUD19_2K, self.BAUD38_4K, self.BAUD57_6K,
                         self.BAUD115_2K, self.BAUD230_4K, self.BAUD500K):
            raise ValueError(f"Baudrate must be one of the BAUDxxK constants")

        self._conn.write(b'AT BRD ' + value[0] + self._suffix)

        # time.sleep(0.03)
        # rep = self._conn.read_all().split(self._suffix)
        rep = self._conn.read_until(self._suffix)
        rep += self._conn.read_until(self._suffix)
        rep = rep.split(self._suffix)
        if rep[1] == b'?':
            raise ELM327Error(f"This ELM327 does not support the baudrate changing command (it is too old)")
        if not rep[1] == b'OK':
            raise ConnectionError(f"Problem when testing the new baudrate ({value[1]})")

        self._conn.baudrate = value[1]

        rep = self._conn.read_until(self._suffix)
        if not rep.endswith(self._ati + self._suffix):
            raise ConnectionError(f"Problem when testing the new baudrate ({value[1]})")

        self._conn.write(b'\r')

        rep = self._conn.read(2)
        if not rep == b'OK':
            raise ConnectionError(f"Problem when testing the new baudrate ({value[1]})")

        self._read()

        self.logger.info(f"Baudrate set to {value[1]} (not permanent)")

    def __init__(self, connection):
        self.logger = logging.getLogger('MCL.ELM327')

        self._ati = None
        self.version_major: int = -1
        self.version_minor: int = -1

        self._baudrate = 38400
        self._suffix = None

        self._conn: AbstractConnection = connection
        self.connect()

    def connect(self):
        self._conn.flush()
        self.reset()

    def reset(self):
        self.logger.info(f"reset")
        ver = self.send_command(b'AT Z')
        self._ati = ver
        ver = ver.decode('ascii', 'ignore')
        if not ver.startswith("ELM327"):
            raise ConnectionError(f"Bad reset message received: {ver}")
        else:
            self.version_major, self.version_minor = (int(v) for v in ver[8:].split('.'))
            self.logger.info(f"AT I string: {self._ati}")
            self.logger.info(f"version: {self.version_major}.{self.version_minor}")

    def send_command(self, cmd: Union[bytes, str]):
        if isinstance(cmd, str):
            cmd = bytes(cmd, 'ASCII')

        if not cmd.startswith(b'AT'):
            cmd = b'AT ' + cmd

        self._conn.write(cmd + (self._suffix or b'\r\n'))
        return self._read().split(self._suffix)[-1]

    def _read(self):
        data = self._conn.read_until(b'>')

        # define the suffix if its the first time a answer is got
        if self._suffix is None:
            if data.endswith(b'\r\n\r\n>'):
                self._suffix = b'\r\n'
            elif data.endswith(b'\r\r>'):
                self._suffix = b'\r'
            else:
                raise ELM327Error(r"Suffix not recognized ('\r\n\r\n' and '\r\r' tested)")

        assert data.endswith(self._suffix + b'>')
        data = data[:-(len(self._suffix) * 2 + 1)]  # delete the suffix at the end of received answer

        return data


if __name__ == '__main__':
    from core.utils.log import setup_log, set_console_log_level

    setup_log()
    set_console_log_level(logging.DEBUG)

    conn = USBSerial()
    obd = ELM327(conn)
    print(obd.send_command('I'))
    print(obd.send_command('RV'))
    obd.baudrate = obd.BAUD57_6K
