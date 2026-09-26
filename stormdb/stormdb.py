import os
import json

from pathlib import Path
from stormdb.types import StringOrPath




class StormDB:
    
    def __init__(self, path: StringOrPath) -> None:
        self.path: Path = self.__init_path(path)
        self.data = {}
        self.opened = False


    def open(self) -> None:
        if self.opened:
            return

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = {}
        
        self.opened = True


    def close(self) -> None:
        if not self.opened:
            return

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4)

        self.opened = False


    def add(self, key: str, value: str) -> None:
        self.data[key] = value


    def update(self, key: str, value: str) -> None:
        if key not in self.data:
            raise KeyError(f"Key '{key}' does not exist")

        self.data[key] = value


    def delete(self, key: str) -> None:
        if key not in self.data:
            raise KeyError(f"Key '{key}' does not exist")

        del self.data[key]


    def get(self, key: str) -> str:
        return self.data.get(key)


    def __init_path(self, path) -> Path:
        if path is None:
            return Path(os.getcwd())
        
        elif isinstance(path, str):
            return Path(path)
        
        elif isinstance(path, Path):
            return path

        else:
            raise ValueError(f'expected StringOrPath, not {type(path)}')

