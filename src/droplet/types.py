from typing import Union
from uuid import UUID


####################### CUSTOM PARAM TYPES #######################
SupportedType = Union[str, int, float, bool, bytes, UUID]


####################### DATABASE SUPPORTED TYPES #######################
NONE = 0
STRING = 1
INTEGER = 2
FLOAT = 3
BOOLEAN = 4
BYTES = 5
LIST = 6
DICT = 7
UUID_TYPE = 8



