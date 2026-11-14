class DropletError(Exception):
    """Base exception for Droplet."""


class DeserializationError(DropletError):
    """An error occured while deserializing a record"""


class CorruptedRecordError(DropletError):
    """A stored record is corrupted."""