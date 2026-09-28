import json
import base64
from uuid import UUID
from pathlib import Path




def export_to_json(path: Path, data: dict) -> None:
    """
    Export database data to a JSON file.

    The exported file is named ``database_export.json`` and is created
    inside the specified directory. UUID and bytes values are converted
    using ``json_serializer``.

    Args:
        path: Directory where the JSON export should be created.
        data: Dictionary containing the data to export.

    Raises:
        TypeError: If a value in the data cannot be serialized to JSON.
    """
    export_path = path / "database_export.json"
    with open(export_path, 'w') as file:
        json.dump(
            data, 
            file, 
            indent=4,
            default=json_serializer
        )


def json_serializer(obj) -> str:
    """
    Convert non-standard Python objects into JSON-compatible values.

    UUID objects are converted to strings and bytes objects are encoded
    using Base64 and returned as ASCII strings.

    Args:
        obj: Python object to convert for JSON serialization.

    Returns:
        A JSON-compatible string representation of the object.

    Raises:
        TypeError: If the object cannot be converted to a JSON-compatible
        representation.
    """
    if isinstance(obj, UUID):
        return str(obj)

    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('ascii')

    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")