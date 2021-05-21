from abc import ABCMeta, abstractmethod
from typing import Optional


class AbstractConnection(metaclass=ABCMeta):
    @abstractmethod
    def connect(self, port):
        pass

    @abstractmethod
    def read(self, size: int):
        pass

    @abstractmethod
    def read_all(self):
        pass

    @abstractmethod
    def read_until(self, expected: bytes = b'\n', size: Optional[int] = None):
        pass

    @abstractmethod
    def flush(self):
        pass

    @abstractmethod
    def write(self, data: bytes):
        pass
