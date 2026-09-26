import struct

from pathlib import Path
from stormdb.types import StringOrPath


ADD = 1
UPDATE = 2
DELETE = 3
HEADER_LENGTH = 9
READ_BINARY = 'rb'
APPEND_BINARY = 'a+b'


class StormDB:
    
    def __init__(self, path: StringOrPath = None) -> None:
        self.path: Path = self.__init_path(path)
        self.file = None
        self.data = {}
        self.opened = False


    def open(self) -> None:
        if self.opened:
            return

        self.data = {}
        self.file = open(self.path, APPEND_BINARY)
        
        try:
            with open(self.path, READ_BINARY) as file:

                while True:
                    header = file.read(HEADER_LENGTH)

                    if not header:
                        break

                    operation, key_length, value_length = struct.unpack(
                        ">BII",
                        header
                    )

                    key = file.read(key_length).decode("utf-8")
                    value = file.read(value_length).decode("utf-8")

                    if operation == ADD:
                        self.data[key] = value

        except FileNotFoundError:
            self.data = {}
        
        self.opened = True


    def close(self) -> None:
        if not self.opened:
            return

        self.file.close()
        self.opened = False


    def add(self, key: str, value: str) -> None:
        key_bytes: bytes = key.encode('utf-8')
        value_bytes: bytes = value.encode('utf-8')

        record = struct.pack(
            ">BII",
            ADD,
            len(key_bytes),
            len(value_bytes)
        )

        record += key_bytes
        record += value_bytes

        self.file.write(record)
        self.file.flush()

        self.data[key] = value
        


    def update(self, key: str, value: str) -> None:
        if key not in self.data:
            raise KeyError(f"Key '{key}' does not exist")

        self.data[key] = value


    def delete(self, key: str) -> None:
        if key not in self.data:
            raise KeyError(f"Key '{key}' does not exist")

        del self.data[key]


    def get(self, key: str) -> str:
        return self.data.get(key)


    def __init_path(self, path) -> Path:
        if path is None:
            return Path.cwd() / 'stormdb.storm'
        
        if isinstance(path, str):
            return Path(path)
        
        if isinstance(path, Path):
            return path

        raise ValueError(
            f'expected StringOrPath, not {type(path)}'
        )

