import json
import base64
from uuid import UUID
from pathlib import Path




def export_to_json(path: Path, data: dict) -> None:
    try:
        export_path = path / "database_export.json"
        with open(export_path, 'w') as file:
            json.dump(
                data, 
                file, 
                indent=4,
                default=json_serializer
            )
    except TypeError as e:
        print(f'An error occured while exporting: {str(e)}')



def json_serializer(obj) -> str:
    if isinstance(obj, UUID):
        return str(obj)

    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('ascii')

    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")