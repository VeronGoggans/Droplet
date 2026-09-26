from pathlib import Path
from typing import Union


####################### CUSTOM PARAM TYPES #######################
StringOrPath = str | Path
SupportedType = Union[str, int, float, bool]


####################### DATABASE SUPPORTED TYPES #######################
STRING = 1
INTEGER = 2
FLOAT = 3
BOOLEAN = 4

