import struct

from pathlib import Path
from typing import Union

from stormdb.types import SupportedType
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
    """
    A file-backed key-value database.

    Stores key-value pairs in an append-only binary file and rebuilds the
    in-memory database state when opened.
    """
    
    def __init__(self, path: Union[str, Path] = None) -> None:
        """
        Initialize a database.

        Args:
            path: Directory where the database file should be stored.
                  Defaults to the current working directory.
        """
        self.path: Path = self.__init_path(path)
        self.file = None
        self.data = {}
        self.is_open = False
        


    def open(self) -> None:
        """
        Open the database and load its contents into memory.

        Replays all stored records from the database file to reconstruct
        the current key-value state. Does nothing if the database is
        already open.
        """
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
        """
        Close the database file.

        Does nothing if the database is already closed.
        """
        if not self.is_open:
            return

        self.file.close()
        self.is_open = False



    def set(self, key: str, value: SupportedType) -> SupportedType:
        """
        Set a key to a value.

        Creates an ADD record when the key does not exist or an UPDATE
        record when the key already exists.

        Args:
            key: Key to set.
            value: Value to store.

        Returns:
            The value that was stored.
        """
        operation = self.__get_set_operation(key)
        
        record = self.__create_record(key, value, operation)

        self.file.write(record)
        self.file.flush()

        self.data[key] = value
        return value



    def set_many(self, pairs: dict[str, SupportedType]) -> dict[str, SupportedType]:
        """
        Set multiple key-value pairs.

        All records are written to the database in a single file write.

        Args:
            pairs: Dictionary containing the keys and values to store.

        Returns:
            The dictionary of key-value pairs that were stored.
        """
        buffer = bytearray()

        for key, value in pairs.items():
            operation = self.__get_set_operation(key)
            buffer.extend(self.__create_record(key, value, operation))    

        self.file.write(buffer)
        self.file.flush()

        self.data = self.data | pairs
        return pairs



    def delete(self, key: str) -> SupportedType:
        """
        Delete a key from the database.

        Args:
            key: Key to delete.

        Returns:
            The value that was deleted, or False if the key does not exist.
        """
        if not key in self.data:
            return False
        
        record = self.__create_record(key, None, DELETE)

        self.file.write(record)
        self.file.flush()

        return self.data.pop(key, None)



    def delete_many(self, keys: list[str]) -> dict[str, SupportedType]:
        """
        Delete multiple keys from the database.

        Keys that do not exist are ignored. All deletion records are
        written to the database in a single file write.

        Args:
            keys: List of keys to delete.

        Returns:
            A dictionary containing the requested keys and their previous
            values. Keys that did not exist, are not included.
        """
        buffer = bytearray()
        deleted_items = {}
        
        for key in keys:
            if not self.exists(key):
                continue

            deleted_items[key] = self.data.pop(key, None)
            buffer.extend(self.__create_record(key, None, DELETE))

        self.file.write(buffer)
        self.file.flush()            

        return deleted_items



    def delete_all(self) -> dict[str, SupportedType]:
        """
        Delete all key-value pairs from the database.

        Returns:
            A dictionary containing all keys and their values after
            deletion.
        """
        return self.delete_many(list(self.data.keys()))
        


    def keys(self) -> list[str]:
        """
        Return all keys in the database.

        Returns:
            A list containing the keys currently stored in the database.
        """
        return list(self.data.keys())



    def values(self) -> list[SupportedType]:
        """
        Return all values in the database.

        Returns:
            A list containing the values currently stored in the database.
        """
        return list(self.data.values())



    def view(self):
        """
        Return all key-value pairs in the database.

        Returns:
            A view containing the database's key-value pairs.
        """
        return self.data.items()



    def count(self) -> int:
        """
        Return the number of key-value pairs in the database.

        Returns:
            The number of keys currently stored in the database.
        """
        return len(list(self.data.keys()))
    


    def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment an integer value by a given amount.

        Args:
            key: Key containing the integer value.
            amount: Amount to add to the current value. Defaults to 1.

        Returns:
            The new value after incrementing.

        """
        value = self.get(key)

        if isinstance(value, int):
            new_value = self.data[key] + amount
            return self.set(key, new_value)



    def decrement(self, key: str, amount: int = 1) -> int:
        """
        Decrement an integer value by a given amount.

        Args:
            key: Key containing the integer value.
            amount: Amount to subtract from the current value. Defaults to 1.

        Returns:
            The new value after decrementing.

        """
        value = self.get(key)

        if isinstance(value, int):
            new_value = self.data[key] - amount
            return self.set(key, new_value)



    def find(self) -> list[dict]:
        """
        Find key-value pairs matching the given criteria.

        Returns:
            A list of matching key-value pairs.
        """
        ...



    def export(self, path: Path = Path.cwd()) -> None:
        """
        Export the database contents to a JSON file.

        Args:
            path: Directory or path where the JSON export should be stored.

        Raises:
            ValueError: If the database is not open.
        """
        if not self.is_open:
            raise ValueError('The database needs to be open before exporting to JSON')
        export_to_json(path, self.data)



    def get(self, key: str) -> SupportedType:
        """
        Get the value associated with a key.

        Args:
            key: Key whose value should be retrieved.

        Returns:
            The value associated with the key, or None if the key does not
            exist.
        """
        return self.data.get(key)



    def exists(self, key: str) -> bool:
        """
        Check whether a key exists in the database.

        Args:
            key: Key to check.

        Returns:
            True if the key exists, otherwise False.
        """
        return key in self.data



    def __create_record(self, key: str, value: SupportedType, operation: int) -> bytes:
        """
        Create a binary database record.

        Args:
            key: Key to include in the record.
            value: Value to serialize into the record.
            operation: Operation type, such as ADD, UPDATE, or DELETE.

        Returns:
            The serialized binary database record.
        """
        type_id, value_bytes = serialize(value)
        key_bytes: bytes = key.encode('utf-8')

        if operation == DELETE:    
            record = struct.pack(
                HEADER_FORMAT,
                DELETE,
                type_id,
                len(key_bytes),
                0
            )
    
            record += key_bytes
        
        if operation == ADD or operation == UPDATE:
            record = struct.pack(
                HEADER_FORMAT,
                operation,
                type_id,
                len(key_bytes),
                len(value_bytes)
            )

            record += key_bytes
            record += value_bytes

        return record



    def __get_set_operation(self, key: str) -> int:
        """
        Determine whether setting a key requires an ADD or UPDATE operation.

        Args:
            key: Key whose existence should be checked.

        Returns:
            ADD if the key does not exist, otherwise UPDATE.
        """
        operation = ADD
        if key in self.data:
            operation = UPDATE
        return operation



    def __init_path(self, path: Path = None) -> Path:
        """
        Create the database file path from a directory path.

        Args:
            path: Directory where the database file should be stored.
                Defaults to the current working directory.

        Returns:
            The complete path to the database file.

        Raises:
            ValueError: If the provided path appears to point to a file
                or is not a supported path type.
        """
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

