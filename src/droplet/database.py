import os
import time
import struct

from pathlib import Path
from typing import Union
from dataclasses import asdict

from droplet.types import SupportedType, _MISSING, T, UUID
from droplet.serializer import serialize, deserialize
from droplet.exporter import export_to_json


ADD = 1
UPDATE = 2
DELETE = 3

# 1-byte unsigned int | 1-byte unsigned int | 4-byte unsigned int | 4-byte unsigned int | 8-byte unsigned int
#      operation      |       type_id       |      key_length     |     value_length    |      expiration
HEADER_FORMAT = '>BBIIQ'
HEADER_LENGTH = struct.calcsize(HEADER_FORMAT)

READ_BINARY = 'rb'
APPEND_BINARY = 'a+b'
WRITE_BINARY = 'w+b'



class Droplet:
    """
    A file-backed key-value database.

    Stores key-value pairs in an append-only binary file and rebuilds the
    in-memory database state when opened.
    """
    
    def __init__(self, path: Union[str, Path] = None) -> None:
        """
        Initialize a database.

        Args:
            path: Path to a directory or the database file.
                  Defaults to the current working directory.
        """
        self.file = None
        self.data = {}
        self.expirations = {}
        self.is_open = False
        self.path: Path = self.__init_path(path)



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

                    operation, type_id, key_length, value_length, expiration = struct.unpack(
                        HEADER_FORMAT,
                        header
                    )

                    key = file.read(key_length).decode("utf-8")
                    value_bytes = file.read(value_length)

                    value = deserialize(type_id, value_bytes)

                    if operation == ADD or operation == UPDATE:
                        # Expired
                        if expiration and expiration <= time.time():
                            self.data.pop(key, None)
                            self.expirations.pop(key, None)
                        # Valid
                        else:
                            self.data[key] = value

                            if expiration:
                                self.expirations[key] = expiration
                            else:
                                self.expirations.pop(key, None)

                    if operation == DELETE:
                        self.data.pop(key, None)
                        self.expirations.pop(key, None)

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



    def set(self, key: str, value: SupportedType, ttl: int = 0, namespace: str = '') -> SupportedType:
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
        self.__validate_input(ttl, namespace)
        key = self.__get_key(key, namespace)
        
        operation = UPDATE if key in self.data else ADD
        record = self.__create_record(key, value, operation, ttl)

        self.file.write(record)
        self.file.flush()

        self.data[key] = value

        if ttl > 0:
            self.expirations[key] = time.time() + ttl

        return value



    def set_as(self, key: str, cls: type[T], ttl: int = 0, namespace: str = '') -> T:
        """
        Stores a dataclass instance as a dictionary under the given key.

        Nested dataclasses are converted to nested dictionaries by ``asdict()``.

        Args:
            key: The key under which to store the dataclass.
            cls: The dataclass instance to store.

        Returns:
            The value returned by ``set()`` after storing the dataclass.

        Raises:
            TypeError: If the provided value is not a dataclass instance or
                contains unsupported nested dataclasses.
        """
        return self.set(key, asdict(cls), ttl, namespace)



    def set_batch_as(self, pairs: dict[str, type[T]], ttl: int = 0, namespace: str = '') -> dict[str, T]:
        """
        Set multiple key-value pairs.

        All records are written to the database in a single file write.

        Args:
            pairs: Dictionary containing the keys and values to store.

        Returns:
            The dictionary of key-value pairs that were stored.
        """
        self.__validate_input(ttl, namespace)
        buffer = bytearray()
        stored_items = {}

        for key, value in pairs.items():
            key = self.__get_key(key, namespace)
            operation = UPDATE if key in self.data else ADD
            
            stored_items[key] = asdict(value)
            buffer.extend(self.__create_record(key, asdict(value), operation, ttl))  
            
            if ttl > 0:
                self.expirations[key] = time.time() + ttl  

        self.file.write(buffer)
        self.file.flush()

        self.data.update(stored_items)        
        return stored_items



    def set_batch(self, pairs: dict[str, SupportedType], ttl: int = 0, namespace: str = '') -> dict[str, SupportedType]:
        """
        Set multiple key-value pairs.

        All records are written to the database in a single file write.

        Args:
            pairs: Dictionary containing the keys and values to store.

        Returns:
            The dictionary of key-value pairs that were stored.
        """
        self.__validate_input(ttl, namespace)
        buffer = bytearray()
        stored_items = {}

        for key, value in pairs.items():
            key = self.__get_key(key, namespace)
            operation = UPDATE if key in self.data else ADD

            buffer.extend(self.__create_record(key, value, operation, ttl))
            stored_items[key] = value
            
            if ttl > 0:
                self.expirations[key] = time.time() + ttl

        self.file.write(buffer)
        self.file.flush()

        self.data.update(stored_items)
        return stored_items



    def delete(self, key: str, namespace: str = '') -> SupportedType:
        """
        Delete a key from the database.

        Args:
            key: Key to delete.

        Returns:
            The value that was deleted, or False if the key does not exist.
        """
        self.__validate_input(0, namespace)
        key = self.__get_key(key, namespace)

        if not key in self.data:
            return False
        
        record = self.__create_record(key, None, DELETE)

        self.file.write(record)
        self.file.flush()

        self.expirations.pop(key, None)
        return self.data.pop(key, None)



    def delete_batch(self, keys: list[str], namespace: str = '') -> dict[str, SupportedType]:
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
        self.__validate_input(0, namespace)
        buffer = bytearray()
        deleted_items = {}
        
        for key in keys:
            key = self.__get_key(key, namespace)
            value = self.data.pop(key, _MISSING)
            self.expirations.pop(key, None)
            
            if value is _MISSING:
                continue
            
            deleted_items[key] = value
            buffer.extend(self.__create_record(key, None, DELETE))

        self.file.write(buffer)
        self.file.flush()            

        return deleted_items



    def clear(self) -> dict[str, SupportedType]:
        """
        Delete all key-value pairs from the database.

        Returns:
            A dictionary containing all keys and their values after
            deletion.
        """        
        self.data = {}
        self.expirations = {}
        try:
            temp_file_path = self.path.parent / 'database.droplet.tmp' 
            temp_file_path.write_bytes(b'')

            self.close()
            os.replace(temp_file_path, self.path)

            self.file = open(self.path, APPEND_BINARY)
            self.is_open = True

        except Exception as e:
            raise e



    def compact(self) -> None:
        """
        Compact the database by removing obsolete records from the log.

        Only records required to reconstruct the current database state
        are retained.
        """
        if not self.is_open:
            raise ValueError('The database needs to be open before compacting it')
        
        try:
            temp_file_path = self.path.parent / 'database.droplet.tmp' 
            
            with open(temp_file_path, WRITE_BINARY) as file:
                for key, value in self.data.items():
                    ttl = self.expirations.get(key, 0)
                    record = self.__create_record(key, value, ADD, ttl)
                    
                    file.write(record)
                    file.flush()

            self.close()
            os.replace(temp_file_path, self.path)

            self.file = open(self.path, APPEND_BINARY)
            self.is_open = True

        except Exception as e:
            raise e



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



    def view(self) -> dict:
        """
        Return all key-value pairs in the database.

        Returns:
            A view containing the database's key-value pairs.
        """
        return dict(self.data.items())



    def count(self) -> int:
        """
        Return the number of key-value pairs in the database.

        Returns:
            The number of keys currently stored in the database.
        """
        return len(list(self.data.keys()))



    def get_size(self) -> int:
        """
        Returns the current size of the database file in bytes.

        Returns:
            The size of the database file in bytes.
        """
        return self.path.stat().st_size
    


    def increment(self, key: str, amount: int = 1, namespace: str = '') -> int:
        """
        Increment an integer value by a given amount.

        Args:
            key: Key containing the integer value.
            amount: Amount to add to the current value. Defaults to 1.

        Returns:
            The new value after incrementing.
        """
        value = self.get(key, namespace)
        key = self.__get_key(key, namespace)

        if isinstance(value, int):
            new_value = self.data[key] + amount
            return self.set(key, new_value)



    def decrement(self, key: str, amount: int = 1, namespace: str = '') -> int:
        """
        Decrement an integer value by a given amount.

        Args:
            key: Key containing the integer value.
            amount: Amount to subtract from the current value. Defaults to 1.

        Returns:
            The new value after decrementing.

        """
        value = self.get(key, namespace)
        key = self.__get_key(key, namespace)

        if isinstance(value, int):
            new_value = self.data[key] - amount
            return self.set(key, new_value)



    def ttl(self, key: str, namespace: str = '') -> int:
        self.__validate_input(0, namespace)
        key = self.__get_key(key, namespace)
        
        expiration = self.expirations.get(key, 0)
        if expiration == 0:
            raise ValueError(f'{key} does not have an expiration.')

        now = time.time()
        if expiration < now:
            self.delete(key)
            raise KeyError(f'{key} has expired {now - expiration} seconds ago.')

        return expiration - now



    def compare_and_set(
            self, 
            key: str,
            expected: SupportedType, 
            new_value: SupportedType, 
            ttl: int = 0,
            namespace: str = ''
        ) -> SupportedType:
        """
        Set a value only if the current value matches the expected value.

        If the key exists and its current value equals `expected`, it is
        updated to `new_value`. Otherwise, the value is left unchanged.

        Args:
            key: The key to compare and potentially update.
            expected: The value currently expected for the key.
            new_value: The value to set if the comparison succeeds.

        Returns:
            The new value if the comparison succeeds, or False otherwise.
        """
        value = self.get(key, namespace)

        if value == expected:
            return self.set(key, new_value, ttl, namespace)
        return False



    def greater_than(self, value: Union[int, float]) -> dict[str, SupportedType]:
        self.__check_num_type(value)

        items: dict[str, SupportedType] = {}
        for k, v in self.data.items():
            if isinstance(v, (int, float)) and v > value:
                items[k] = v

        return items



    def less_than(self, value: Union[int, float]) -> dict[str, SupportedType]:
        self.__check_num_type(value)
        
        items: dict[str, SupportedType] = {}
        for k, v in self.data.items():
            if isinstance(v, (int, float)) and v < value:
                items[k] = v

        return items



    def greater_than_or_equal(self, value: Union[int, float]) -> dict[str, SupportedType]:
        self.__check_num_type(value)
                
        items: dict[str, SupportedType] = {}
        for k, v in self.data.items():
            if isinstance(v, (int, float)) and v >= value:
                items[k] = v

        return items
    
    
    
    def less_than_or_equal(self, value: Union[int, float]) -> dict[str, SupportedType]:
        self.__check_num_type(value)
        
        items: dict[str, SupportedType] = {}
        for k, v in self.data.items():
            if isinstance(v, (int, float)) and v <= value:
                items[k] = v

        return items



    def equal_to(self, value: Union[str, int, float, bool, UUID, bytes]) -> dict[str, SupportedType]:
        """
        Returns all key-value pairs whose value is equal to the given value.

        Args:
            value: The value to compare against.

        Returns:
            A dictionary containing the key-value pairs with matching values.

        Raises:
            ValueError: If the given value is not a supported type.
        """
        if not isinstance(value, (str, int, float, bool, UUID, bytes)):
            raise ValueError(f'Unsupported type: {type(value)}')

        items: dict[str, SupportedType] = {}
        for k, v in self.data.items():
            if type(v) == type(v) and v == value:
                items[k] = v
        return items



    def export_to_json(self, path: Path = Path.cwd()) -> None:
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



    def import_from_json(self, data: dict) -> None:
        """
        Imports data from a JSON-compatible dictionary into the database.

        The database must be open and empty before importing.

        Args:
            data: A dictionary containing the data to import.

        Raises:
            ValueError: If the database is not open, the data is not a dictionary,
                or the database is not empty.
        """
        if not self.is_open:
            raise ValueError('The database needs to be open before importing from JSON')

        if not isinstance(data, dict):
            raise ValueError('The JSON needs to be a valid dict')

        if self.data:
            raise ValueError('You can only import if the database is empty')

        self.set_batch(data)



    def get(self, key: str, namespace: str = '') -> SupportedType:
        """
        Get the value associated with a key.

        Args:
            key: Key whose value should be retrieved.
            default: Value to return if the key does not exist.

        Returns:
            The value associated with the key, or `default` if the key does not
            exist.
        """
        self.__validate_input(0, namespace)
        key = self.__get_key(key, namespace)

        if self.__is_expired(key):
            self.delete(key)
            raise KeyError(key)

        value = self.data.get(key, _MISSING)
        if value == _MISSING:
            raise KeyError(key)
        return value



    def get_namespace(self, namespace: str) -> dict[str, SupportedType]:
        self.__validate_input(0, namespace)
        items = {}

        for key, value in self.data.items():
            if ':' in key and key.split(':')[0] == namespace:
                items[key] = value

        return items



    def get_as(self, key: str, cls: type[T], namespace: str = '') -> T:
        """
        Retrieves a value by key and converts it into an instance of the given class.

        The stored value must be a dictionary whose keys match the parameters
        accepted by the class constructor.

        Args:
            key: The key of the value to retrieve.
            cls: The class to instantiate using the stored dictionary.

        Returns:
            An instance of the given class populated with the stored value.

        Raises:
            KeyError: If the key does not exist in the database.
            TypeError: If the stored value is not a dictionary or cannot be used
                to construct the given class.
        """
        return cls(**self.get(key, namespace))



    def get_batch_as(self, keys: list[str], cls: type[T], namespace: str = '') -> dict[str, T]:
        """
        Retrieves multiple values by key and converts them into instances of
        the given data class.

        Each stored value must be a dictionary whose keys match the parameters
        accepted by the class constructor.

        Args:
            keys: A list of keys to retrieve from the database.
            cls: The data class to instantiate using each stored value.

        Returns:
            A dictionary mapping each key to an instance of the given data class.

        Raises:
            KeyError: If any of the given keys do not exist in the database.
            TypeError: If a stored value cannot be used to construct the given class.
        """        
        items: dict[str, T] = {}
        for key in keys:
            items[key] = cls(**self.get(key, namespace))

        return items



    def get_batch(self, keys: list[str], namespace: str = '') -> dict[str, SupportedType]:
        """
        Retrieve multiple values from the database by their keys.

        Keys that do not exist in the database are omitted from the result.

        Args:
            keys: A list of keys to retrieve.

        Returns:
            A dictionary containing the requested keys and their values.
            Missing keys are not included.
        """
        items: dict[str, SupportedType] = {}
        for key in keys:
            key = self.__get_key(key, namespace)
            items[key] = self.get(key)
        
        return items


    def exists(self, key: str, namespace: str = '') -> bool:
        """
        Check whether a key exists in the database.

        Args:
            key: Key to check.

        Returns:
            True if the key exists, otherwise False.
        """
        self.__validate_input(0, namespace)
        key = self.__get_key(key, namespace)

        if self.__is_expired(key):
            self.delete(key)
            return False
        
        return key in self.data



    def __is_expired(self, key: str) -> bool:
        expiration = self.expirations.get(key, None)
        now = time.time()
        
        return False if expiration is None else expiration < now



    def __create_record(self, key: str, value: SupportedType, operation: int, ttl = 0) -> bytes:
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
        expiration = time.time() + ttl if ttl > 0 else 0

        if operation == DELETE:    
            return struct.pack(
                HEADER_FORMAT,
                DELETE,
                type_id,
                len(key_bytes),
                0,
                0
            ) + key_bytes
    
        if operation == ADD or operation == UPDATE:
            return struct.pack(
                HEADER_FORMAT,
                operation,
                type_id,
                len(key_bytes),
                len(value_bytes),
                int(expiration)
            ) + key_bytes + value_bytes



    def __check_num_type(self, value: Union[int, float]) -> None:
        if not isinstance(value, int) and not isinstance(value, float):
            raise ValueError(f'Unsupported type: {type(value)}')



    def __validate_input(self, ttl: int, namespace: str) -> None:
        if not isinstance(ttl, int):
            raise ValueError('ttl must be an int')

        if ttl < 0:
            raise ValueError('ttl must be a positive int')

        if not isinstance(namespace, str):
            raise ValueError('namespace must be a str')



    def __get_key(self, key: str, namespace: str) -> str:
        if not namespace:
            return key
        return f'{namespace}:{key}'



    def __init_path(self, path: str | Path | None = None) -> Path:
        """
        Resolve the database file path.

        Accepts:
            - None: Uses the current working directory.
            - Directory: Places database.droplet inside it.
            - .droplet file: Uses the specified database file path.

        Raises:
            ValueError: If the path is invalid.
        """
        if path is None:
            return Path.cwd() / 'database.droplet'

        if not isinstance(path, (str, Path)):
            raise ValueError(
                f"Expected str, Path or None, got {type(path).__name__}"
            )

        path = Path(path)

        if path.suffix == '.droplet':
            if path.is_dir():
                raise ValueError("Database file path points to a directory")
            return path

        if path.is_file():
            raise ValueError("The database path must be a directory or a .droplet file")

        return path / 'database.droplet'

