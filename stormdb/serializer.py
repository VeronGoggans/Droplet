import struct
import base64
from uuid import UUID
from stormdb.types import (
    SupportedType,
    STRING,
    INTEGER,
    FLOAT,
    BOOLEAN,
    NONE,
    UUID_TYPE,
    BYTES
)


SIGNED_64_BIT_INTEGER = '>q'
SIGNED_64_BIT_FLOAT = '>d'
UNSIGNED_CHAR = '>B'



def serialize(value: SupportedType) -> tuple[int, bytes]:
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


def json_serializer(obj):
    if isinstance(obj, UUID):
        return str(obj)

    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('ascii')

    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")