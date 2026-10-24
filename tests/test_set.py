
import time
import pytest

from dataclasses import dataclass, asdict
from src.droplet.database import Droplet


@dataclass
class User:
    name: str
    age: int


@dataclass
class Product:
    name: str
    price: float


@dataclass
class Address:
    city: str
    country: str


@dataclass
class Person:
    name: str
    address: Address


@pytest.fixture
def db(tmp_path):
    database = Droplet(tmp_path)
    database.open()

    yield database

    database.close()


# -------------------------
# SET
# -------------------------

@pytest.mark.parametrize("key,value", [
    ("name", "John"),
    ("age", 25),
    ("active", True),
    ("score", 99.5),
    ("nothing", None),
    ("data", {"name": "Alice", "age": 30}),
    ("numbers", [1, 2, 3]),
    ("empty_string", ""),
    ("empty_dict", {}),
    ("empty_list", []),
])
def test_set_supported_values(db, key, value):
    result = db.set(key, value)

    assert result == value
    assert db.data[key] == value
    assert db.get(key) == value


def test_set_new_key(db):
    result = db.set("name", "Alice")

    assert result == "Alice"
    assert db.data["name"] == "Alice"


def test_set_existing_key(db):
    db.set("name", "Alice")
    result = db.set("name", "Bob")

    assert result == "Bob"
    assert db.get("name") == "Bob"


def test_set_with_namespace(db):
    db.set("1", {"name": "Alice"}, namespace="user")

    assert db.data["user:1"] == {"name": "Alice"}
    assert db.get("1", namespace="user") == {"name": "Alice"}


def test_set_same_key_different_namespaces(db):
    db.set("1", "Alice", namespace="user")
    db.set("1", "Laptop", namespace="product")

    assert db.get("1", namespace="user") == "Alice"
    assert db.get("1", namespace="product") == "Laptop"


def test_set_with_ttl(db):
    before = time.time()
    db.set("session", "token", ttl=60)
    after = time.time()

    assert "session" in db.expirations
    assert before + 60 <= db.expirations["session"] <= after + 60


def test_set_with_namespace_and_ttl(db):
    db.set("1", "Alice", ttl=60, namespace="user")

    assert "user:1" in db.expirations


def test_set_without_ttl(db):
    db.set("name", "Alice")

    assert "name" not in db.expirations


def test_set_invalid_ttl(db):
    with pytest.raises((ValueError, TypeError)):
        db.set("name", "Alice", ttl=-1)


def test_set_invalid_namespace(db):
    with pytest.raises((ValueError, TypeError)):
        db.set("name", "Alice", namespace=123)


# -------------------------
# SET AS
# -------------------------

def test_set_as_dataclass(db):
    user = User("Alice", 30)

    result = db.set_as("1", user)

    assert result == asdict(user)
    assert db.get("1") == {
        "name": "Alice",
        "age": 30,
    }


def test_set_as_with_namespace(db):
    user = User("Alice", 30)

    db.set_as("1", user, namespace="user")

    assert db.get("1", namespace="user") == asdict(user)


def test_set_as_nested_dataclass(db):
    person = Person(
        name="Alice",
        address=Address("Amsterdam", "Netherlands")
    )

    db.set_as("person", person)

    assert db.get("person") == {
        "name": "Alice",
        "address": {
            "city": "Amsterdam",
            "country": "Netherlands",
        },
    }


def test_set_as_with_ttl(db):
    user = User("Alice", 30)

    db.set_as("1", user, ttl=60, namespace="user")

    assert "user:1" in db.expirations


def test_set_as_invalid_value(db):
    with pytest.raises(TypeError):
        db.set_as("1", {"name": "Alice"})


def test_set_as_overwrite(db):
    db.set_as("1", User("Alice", 30))
    db.set_as("1", User("Bob", 25))

    assert db.get("1") == {
        "name": "Bob",
        "age": 25,
    }


# -------------------------
# SET BATCH
# -------------------------

def test_set_batch(db):
    pairs = {
        "name": "Alice",
        "age": 30,
        "active": True,
    }

    result = db.set_batch(pairs)

    assert result == pairs

    for key, value in pairs.items():
        assert db.get(key) == value


def test_set_batch_empty(db):
    result = db.set_batch({})

    assert result == {}


def test_set_batch_with_namespace(db):
    pairs = {
        "1": "Alice",
        "2": "Bob",
    }

    result = db.set_batch(pairs, namespace="user")

    assert result == {
        "user:1": "Alice",
        "user:2": "Bob",
    }


def test_set_batch_overwrite(db):
    db.set_batch({
        "name": "Alice",
        "age": 30,
    })

    db.set_batch({
        "name": "Bob",
        "age": 25,
    })

    assert db.get("name") == "Bob"
    assert db.get("age") == 25


def test_set_batch_mixed_new_and_existing(db):
    db.set("name", "Alice")

    db.set_batch({
        "name": "Bob",
        "age": 25,
    })

    assert db.get("name") == "Bob"
    assert db.get("age") == 25


def test_set_batch_with_ttl(db):
    db.set_batch({
        "1": "Alice",
        "2": "Bob",
    }, ttl=60, namespace="user")

    assert "user:1" in db.expirations
    assert "user:2" in db.expirations


def test_set_batch_invalid_ttl(db):
    with pytest.raises((ValueError, TypeError)):
        db.set_batch({"name": "Alice"}, ttl=-1)


def test_set_batch_invalid_namespace(db):
    with pytest.raises((ValueError, TypeError)):
        db.set_batch({"name": "Alice"}, namespace=123)


# -------------------------
# SET BATCH AS
# -------------------------

def test_set_batch_as(db):
    pairs = {
        "1": User("Alice", 30),
        "2": User("Bob", 25),
    }

    db.set_batch_as(pairs)

    assert db.get("1") == asdict(pairs["1"])
    assert db.get("2") == asdict(pairs["2"])


def test_set_batch_as_with_namespace(db):
    pairs = {
        "1": User("Alice", 30),
        "2": User("Bob", 25),
    }

    result = db.set_batch_as(pairs, namespace="user")

    assert result == {
        "user:1": asdict(pairs["1"]),
        "user:2": asdict(pairs["2"]),
    }


def test_set_batch_as_empty(db):
    assert db.set_batch_as({}) == {}


def test_set_batch_as_with_ttl(db):
    pairs = {
        "1": User("Alice", 30),
        "2": User("Bob", 25),
    }

    db.set_batch_as(pairs, ttl=60, namespace="user")

    assert "user:1" in db.expirations
    assert "user:2" in db.expirations


def test_set_batch_as_nested_dataclass(db):
    person = Person(
        "Alice",
        Address("Amsterdam", "Netherlands")
    )

    db.set_batch_as({"1": person})

    assert db.get("1") == asdict(person)


def test_set_batch_as_invalid_value(db):
    with pytest.raises(TypeError):
        db.set_batch_as({
            "1": {"name": "Alice"}
        })


def test_set_batch_as_overwrite(db):
    db.set_batch_as({
        "1": User("Alice", 30)
    })

    db.set_batch_as({
        "1": User("Bob", 25)
    })

    assert db.get("1") == {
        "name": "Bob",
        "age": 25,
    }


# -------------------------
# PERSISTENCE
# -------------------------

def test_set_persistence(tmp_path):
    db = Droplet(tmp_path, mode='persistent')
    db.open()
    db.set("name", "Alice")
    db.close()

    reopened = Droplet(tmp_path, mode='persistent')
    reopened.open()

    try:
        assert reopened.get("name") == "Alice"
    finally:
        reopened.close()


def test_set_batch_persistence(tmp_path):
    db = Droplet(tmp_path, mode='persistent')
    db.open()

    db.set_batch({
        "name": "Alice",
        "age": 30,
        "active": True,
    })

    db.close()

    reopened = Droplet(tmp_path, mode='persistent')
    reopened.open()

    try:
        assert reopened.get("name") == "Alice"
        assert reopened.get("age") == 30
        assert reopened.get("active") is True
    finally:
        reopened.close()


def test_set_as_persistence(tmp_path):
    db = Droplet(tmp_path, mode='persistent')
    db.open()
    db.set_as("1", User("Alice", 30), namespace="user")
    db.close()

    reopened = Droplet(tmp_path, mode='persistent')
    reopened.open()

    try:
        assert reopened.get_as("1", User, namespace="user") == User("Alice", 30)
    finally:
        reopened.close()


def test_set_batch_as_persistence(tmp_path):
    db = Droplet(tmp_path, mode='persistent')
    db.open()

    db.set_batch_as({
        "1": User("Alice", 30),
        "2": User("Bob", 25),
    }, namespace="user")

    db.close()

    reopened = Droplet(tmp_path, mode='persistent')
    reopened.open()

    try:
        assert reopened.get_as("1", User, namespace="user") == User("Alice", 30)
        assert reopened.get_as("2", User, namespace="user") == User("Bob", 25)
    finally:
        reopened.close()
