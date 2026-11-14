from pathlib import Path
from dataclasses import asdict


from droplet.core.types import SupportedType, T
from droplet.core.exporter import export_to_json


class Namespace:
    def __init__(self, db, name: str):
        self._db = db
        self.name = name


    def set(self, key: str, value: SupportedType, ttl: int = 0) -> SupportedType:
        return self._db.set(key, value, ttl, self.name)


    def set_as(self, key: str, cls: type[T], ttl: int = 0) -> T:
        return self._db.set(key, asdict(cls), ttl, self.name)


    def set_batch_as(self, pairs: dict[str, type[T]], ttl: int = 0) -> dict[str, T]:
        return self._db.set_batch_as(pairs, ttl, self.name)


    def set_batch(self, pairs: dict[str, SupportedType], ttl: int = 0) -> dict[str, SupportedType]:
        return self._db.set_batch(pairs, ttl, self.name)


    def delete(self, key: str) -> SupportedType:
        return self._db.delete(key, self.name)


    def delete_batch(self, keys: list[str]) -> dict[str, SupportedType]:
        return self._db.delete_batch(keys, self.name)


    def keys(self) -> list[str]:
        pairs = self._db.get_namespace(self.name)
        return list(pairs.keys())


    def values(self) -> list[SupportedType]:
        pairs = self._db.get_namespace(self.name)
        return list(pairs.values())


    def view(self) -> dict:
        pairs = self._db.get_namespace(self.name)
        return dict(pairs.items())


    def count(self) -> int:
        pairs = self._db.get_namespace(self.name)
        return len(list(pairs.keys()))


    def rate_limit(self, key: str, limit: int = 0, window: int = 0) -> None:
        self._db.rate_limit(key, limit, window, self.name)


    def increment_rate_limit(self, key: str) -> None:
        self._db.increment_rate_limit(key, self.name)


    def increment(self, key: str, amount: int = 1) -> int:
        return self._db.increment(key, amount, self.name)


    def decrement(self, key: str, amount: int = 1) -> int:
        return self._db.decrement(key, amount, self.name)


    def ttl(self, key: str) -> int:
        return self._db.ttl(key, self.name)


    def compare_and_set(self, key: str, expected: SupportedType, new_value: SupportedType, ttl: int = 0) -> SupportedType:
        return self._db.compare_and_set(key, expected, new_value, ttl, self.name)


    def get(self, key: str) -> SupportedType:
        return self._db.get(key, self.name)


    def get_as(self, key: str, cls: type[T]) -> T:
        return self._db.get_as(key, cls, self.name)


    def get_batch_as(self, keys: list[str], cls: type[T]) -> dict[str, T]:
        return self._db.get_batch_as(keys, cls, self.name)


    def get_batch(self, keys: list[str]) -> dict[str, SupportedType]:
        return self._db.get_batch(keys, self.name)


    def exists(self, key: str) -> bool:
        return self._db.exists(key, self.name)


    def export_to_json(self, path: Path = Path.cwd()) -> None:
        pairs = self._db.get_namespace(self.name)
        
        if not self._db.is_open:
            raise ValueError('The database needs to be open before exporting to JSON')
        
        export_to_json(path, pairs)
    