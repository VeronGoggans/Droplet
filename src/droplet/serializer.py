import struct
from uuid import UUID
from droplet.types import (
    SupportedType,
    STRING,
    INTEGER,
    FLOAT,
    BOOLEAN,
    NONE,
    UUID_TYPE,
    BYTES, 
    TUPLE,
    LIST,
    DICT
)


SIGNED_64_BIT_INTEGER = '>q'
SIGNED_64_BIT_FLOAT = '>d'
UNSIGNED_CHAR = '>B'
UNSIGNED_INT = '>I'



def serialize(value: SupportedType) -> tuple[int, bytes]:
    """
    Serialize a supported value into a type ID and binary representation.

    Args:
        value: Value to serialize. Supported values include strings,
            booleans, UUIDs, None, bytes, integers, and floats.

    Returns:
        A tuple containing the type ID and the serialized binary value.

    Raises:
        ValueError: If the value's type is not supported.
    """
    if isinstance(value, str):
        return STRING, value.encode("utf-8")

    if isinstance(value, bool):
        return BOOLEAN, struct.pack(UNSIGNED_CHAR, value)

    if isinstance(value, UUID):
        return UUID_TYPE, value.bytes

    if value is None:
        return NONE, b""

    if isinstance(value, bytes):
        return BYTES, value
    
    if isinstance(value, int):
        return INTEGER, struct.pack(SIGNED_64_BIT_INTEGER, value)

    if isinstance(value, float):
        return FLOAT, struct.pack(SIGNED_64_BIT_FLOAT, value)

    if isinstance(value, dict):
        # Number of key/value pairs
        dict_bytes = struct.pack(UNSIGNED_INT, len(value))

        for key, item in value.items():
            key_type_id, key_bytes = serialize(key)
            value_type_id, value_bytes = serialize(item)

            # The key type id
            dict_bytes += struct.pack(UNSIGNED_CHAR, key_type_id)
            
            # The length of the key 
            dict_bytes += struct.pack(UNSIGNED_INT, len(key_bytes))

            # The key bytes
            dict_bytes += key_bytes

            # The value type id
            dict_bytes += struct.pack(UNSIGNED_CHAR, value_type_id)

            # The length of the value
            dict_bytes += struct.pack(UNSIGNED_INT, len(value_bytes))

            # The value bytes
            dict_bytes += value_bytes

        return DICT, dict_bytes

    if isinstance(value, list) or isinstance(value, tuple):
        # Number of items in the iterable
        iterable_bytes = struct.pack(UNSIGNED_INT, len(value))

        for v in value:
            value_type_id, value_bytes = serialize(v)

            # The value type id
            iterable_bytes += struct.pack(UNSIGNED_CHAR, value_type_id)

            # The value length
            iterable_bytes += struct.pack(UNSIGNED_INT, len(value_bytes))

            # The value bytes
            iterable_bytes += value_bytes

        data_type = LIST if isinstance(value, list) else TUPLE
        return data_type, iterable_bytes
    
    raise ValueError(f'Unsupported type: {type(value)}')
    

def deserialize(type_id: int, value: bytes) -> SupportedType:
    """
    Deserialize binary data into a supported Python value.

    Args:
        type_id: Identifier specifying the type of the serialized value.
        value: Binary data to deserialize.

    Returns:
        The deserialized Python value.

    Raises:
        TypeError: If the type ID is unknown.
    """
    
    if type_id == STRING:
        return value.decode("utf-8")

    if type_id == BOOLEAN:
        return bool(struct.unpack(UNSIGNED_CHAR, value)[0])

    if type_id == UUID_TYPE:
        return UUID(bytes=value)

    if type_id == NONE:
        return None

    if type_id == BYTES:
        return value

    if type_id == INTEGER:
        return struct.unpack(SIGNED_64_BIT_INTEGER, value)[0]

    if type_id == FLOAT:
        return struct.unpack(SIGNED_64_BIT_FLOAT, value)[0]

    if type_id == DICT:
        offset = 0

        # Number of key/value pairs in the dict
        entry_count = struct.unpack_from(UNSIGNED_INT, value, offset)[0]

        # Move offset to the next piece of data
        offset += struct.calcsize(UNSIGNED_INT)

        result = {}

        for _ in range(entry_count):

            # Read the key type id 
            key_type = struct.unpack_from(UNSIGNED_CHAR, value, offset)[0]

            # Move the offset to the key length
            offset += struct.calcsize(UNSIGNED_CHAR)

            # Read the key length
            key_length = struct.unpack_from(UNSIGNED_INT, value, offset)[0]

            # Move the offset to the actual key data
            offset += struct.calcsize(UNSIGNED_INT)

            # Read the key bytes
            key_data = value[offset:offset + key_length]
            
            # Move the offset to the 
            offset += key_length

            item_type = struct.unpack_from(UNSIGNED_CHAR, value, offset)[0]

            offset += struct.calcsize(UNSIGNED_CHAR)

            item_length = struct.unpack_from(UNSIGNED_INT, value, offset)[0]

            offset += struct.calcsize(UNSIGNED_INT)

            item_data = value[offset:offset + item_length]
            offset += item_length

            key = deserialize(key_type, key_data)
            item = deserialize(item_type, item_data)

            result[key] = item

        return result

    if type_id == LIST or type_id == TUPLE:
        offset = 0

        # Number of items in the iterable
        entry_count = struct.unpack_from(UNSIGNED_INT, value, offset)[0]

        # Move offset to the next piece of data
        offset += struct.calcsize(UNSIGNED_INT)

        result = []

        for _ in range(entry_count):
            # Read the value type id 
            value_type_id = struct.unpack_from(UNSIGNED_CHAR, value, offset)[0]

            # Move the offset to the key length
            offset += struct.calcsize(UNSIGNED_CHAR)

            # Read the value length
            value_length = struct.unpack_from(UNSIGNED_INT, value, offset)[0]

            # Move the offset to the actual value data
            offset += struct.calcsize(UNSIGNED_INT)

            value_data = value[offset:offset + value_length]
            offset += value_length

            d_value = deserialize(value_type_id, value_data)
            result.append(d_value)


        if type_id == TUPLE:
            result = tuple(result)
        
        return result

    raise TypeError(f"Unknown type ID: {type_id}")


