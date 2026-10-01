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
    
    raise ValueError(
        f'Unsupported type: {type(value)}'
    )
    

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

    raise TypeError(
        f"Unknown type ID: {type_id}"
    )