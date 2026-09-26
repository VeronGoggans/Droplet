import struct

from pathlib import Path
from stormdb.types import StringOrPath, SupportedType
from stormdb.serializer import serialize, deserialize

ADD = 1
UPDATE = 2
DELETE = 3

HEADER_LENGTH = 1 + 1 + 4 + 4
HEADER_FORMAT = '>BBII'

READ_BINARY = 'rb'
APPEND_BINARY = 'a+b'


"""
>: endian
B: unsigned 1-byte integer
I: unsigned 4-byte integer
"""



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

                    operation, type_id, key_length, value_length = struct.unpack(
                        HEADER_FORMAT,
                        header
                    )

                    key = file.read(key_length).decode("utf-8")
                    value_bytes = file.read(value_length)

                    value = deserialize(type_id, value_bytes)

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



    def add(self, key: str, value: SupportedType) -> SupportedType:
        stored_value = self.data.get(key, None)
        if stored_value:
            return stored_value
        
        type_id, value_bytes = serialize(value)
        key_bytes: bytes = key.encode('utf-8')
        
        record = struct.pack(
            HEADER_FORMAT,
            ADD,
            type_id,
            len(key_bytes),
            len(value_bytes)
        )

        record += key_bytes
        record += value_bytes

        self.file.write(record)
        self.file.flush()

        self.data[key] = value
        return value



    def get(self, key: str) -> str:
        return self.data.get(key)



    def __init_path(self, path) -> Path:
        if path is None:
            return Path.cwd() / 'database.stormdb'
        
        if isinstance(path, str):
            return Path(path)
        
        if isinstance(path, Path):
            return path

        raise ValueError(
            f'expected StringOrPath, not {type(path)}'
        )

