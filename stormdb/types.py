from pathlib import Path
from typing import Union


####################### CUSTOM PARAM TYPES #######################
StringOrPath = str | Path
SupportedType = Union[str, int, float, bool]


####################### DATABASE SUPPORTED TYPES #######################
NONE = 0
STRING = 1
INTEGER = 2
FLOAT = 3
BOOLEAN = 4
LIST = 5
DICT = 6
UUID_TYPE = 7



