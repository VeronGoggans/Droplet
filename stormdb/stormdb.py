import struct

from pathlib import Path

from stormdb.types import StringOrPath, SupportedType
from stormdb.serializer import serialize, deserialize
from stormdb.exporter import export_to_json


ADD = 1
UPDATE = 2
DELETE = 3

HEADER_LENGTH = 1 + 1 + 4 + 4
HEADER_FORMAT = '>BBII'

READ_BINARY = 'rb'
APPEND_BINARY = 'a+b'




class Database:
    
    def __init__(self, path: StringOrPath = None) -> None:
        self.path: Path = self.__init_path(path)
        self.file = None
        self.data = {}
        self.is_open = False
        


    def open(self) -> None:
        if self.is_open:
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

                    if operation == ADD or operation == UPDATE:
                        self.data[key] = value

                    if operation == DELETE:
                        del self.data[key]

        except FileNotFoundError:
            self.data = {}
        
        self.is_open = True



    def close(self) -> None:
        if not self.is_open:
            return

        self.file.close()
        self.is_open = False



    def set(self, key: str, value: SupportedType) -> SupportedType:
        operation = ADD
        if self.get(key) is not None:
            operation = UPDATE
        
        type_id, value_bytes = serialize(value)
        key_bytes: bytes = key.encode('utf-8')

        record = struct.pack(
            HEADER_FORMAT,
            operation,
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



    def delete(self, key: str) -> bool:
        old_value = self.get(key) 
        if old_value is None:
            return False
        
        type_id, _ = serialize(old_value)
        key_bytes: bytes = key.encode('utf-8')

        record = struct.pack(
            HEADER_FORMAT,
            DELETE,
            type_id,
            len(key_bytes),
            0
        )

        record += key_bytes

        self.file.write(record)
        self.file.flush()

        del self.data[key]
        return True



    def find(self) -> list[dict]:
        ...



    def export(self, path: Path = Path.cwd()) -> None:
        """Exports the database content to json"""
        if not self.is_open:
            raise ValueError('The database needs to be open before exporting to JSON')
        export_to_json(path, self.data)



    def get(self, key: str) -> str | None:
        return self.data.get(key)



    def exists(self, key: str) -> bool:
        return self.data.get(key) is not None



    def __init_path(self, path: Path = None) -> Path:
        filename = 'database.keys'
        if path is None:
            return Path.cwd() / filename
        
        if '.' in str(path):
            raise ValueError(
                'The database path should point to a folder, not a file'
            )
    
        if isinstance(path, str):
            return Path(path) / filename
        
        if isinstance(path, Path): 
            return path / filename

        raise ValueError(
            f'expected StringOrPath, not {type(path)}'
        )

