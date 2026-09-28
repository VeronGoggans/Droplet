import pytest
import uuid

from src.stashdb.serializer import serialize, deserialize


@pytest.mark.parametrize(
    "value",
    [
        "Binary",
        10,
        100,
        1000,
        10000,
        100000,
        1000000,
        -1000000,
        -100000,
        -10000,
        -1000,
        -100,
        -10
        -1,
        3.14,
        -3.14,
        True,
        False,
        None,
        uuid.uuid4(),
        uuid.uuid4().bytes,
        'bytes string'.encode('utf-8')
    ],
)
def test_serialize_deserialize(value):
    type_id, data = serialize(value)

    result = deserialize(type_id, data)

    assert result == value
    assert type(result) is type(value)