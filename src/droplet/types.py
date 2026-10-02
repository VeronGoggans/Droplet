from typing import Union, TypeVar
from uuid import UUID


####################### CUSTOM PARAM TYPES #######################
SupportedType = Union[str, int, float, bool, bytes, UUID, dict, list, tuple]


####################### DATABASE SUPPORTED TYPES #######################
NONE = 0
STRING = 1
INTEGER = 2
FLOAT = 3
BOOLEAN = 4
BYTES = 5
LIST = 6
TUPLE = 7
DICT = 8
UUID_TYPE = 9


####################### SPECIAL TYPES #######################
_MISSING = object()
T = TypeVar('T')



