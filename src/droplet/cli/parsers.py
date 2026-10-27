import json
from uuid import UUID
from typing import Any


def type_parser(value: str, value_type: str, iterable_type: str = 'str') -> Any:
    match value_type:
        case 'str':
            return value

        case 'int':
            return int(value)

        case 'float':
            return float(value)

        case 'bool':
            if value.lower() in ('true', '1'):
                return True
            if value.lower() in ('false', '0'):
                return False
            raise ValueError('Invalid boolean value')

        case 'json':
            return json.loads(value)

        case 'list':
            iterable = value.split(',')
            if iterable_type == 'str':
                return iterable
            return [type_parser(n, iterable_type) for n in iterable]

        case 'tuple':
            iterable = tuple(value.split(','))
            if iterable_type == 'str':
                return iterable
            return tuple([type_parser(n, iterable_type) for n in iterable])

        case 'uuid':
            return UUID(value)

        case _:
            raise ValueError(f'Unsupported type: {value_type}')
