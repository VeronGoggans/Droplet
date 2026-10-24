
import pytest

from src.droplet.database import Droplet


@pytest.fixture
def db(tmp_path):
    database = Droplet(tmp_path)
    database.open()

    yield database

    database.close()


# -------------------------
# KEYS
# -------------------------

def test_keys_empty(db):
    assert db.keys() == []


def test_keys(db):
    db.set_batch({
        "name": "Alice",
        "age": 30,
        "active": True,
    })

    assert db.keys() == ["name", "age", "active"]


def test_keys_with_namespace(db):
    db.set("1", "Alice", namespace="user")
    db.set("1", "Laptop", namespace="product")

    assert db.keys() == ["user:1", "product:1"]


def test_keys_after_delete(db):
    db.set_batch({"a": 1, "b": 2})
    db.delete("a")

    assert db.keys() == ["b"]


# -------------------------
# VALUES
# -------------------------

def test_values_empty(db):
    assert db.values() == []


def test_values(db):
    db.set_batch({
        "name": "Alice",
        "age": 30,
        "active": True,
    })

    assert db.values() == ["Alice", 30, True]


def test_values_with_none(db):
    db.set("nothing", None)

    assert db.values() == [None]


def test_values_after_update(db):
    db.set("name", "Alice")
    db.set("name", "Bob")

    assert db.values() == ["Bob"]


# -------------------------
# VIEW
# -------------------------

def test_view_empty(db):
    assert dict(db.view()) == {}


def test_view(db):
    pairs = {
        "name": "Alice",
        "age": 30,
        "active": True,
    }

    db.set_batch(pairs)

    assert db.view() == pairs


def test_view_with_namespace(db):
    db.set("1", "Alice", namespace="user")

    assert db.view() == {"user:1": "Alice"}


def test_view_reflects_updates(db):
    db.set("name", "Alice")
    db.set("name", "Bob")

    result = db.view()
    assert result == {"name": "Bob"}


def test_view_reflects_deletions(db):
    db.set_batch({"a": 1, "b": 2})
    db.delete("a")

    result = db.view()
    assert result == {"b": 2}


# -------------------------
# COUNT
# -------------------------

def test_count_empty(db):
    assert db.count() == 0


def test_count(db):
    db.set_batch({"a": 1, "b": 2, "c": 3})

    assert db.count() == 3


def test_count_after_update(db):
    db.set("name", "Alice")
    db.set("name", "Bob")

    assert db.count() == 1


def test_count_after_delete(db):
    db.set_batch({"a": 1, "b": 2})
    db.delete("a")

    assert db.count() == 1


def test_count_with_namespaces(db):
    db.set("1", "Alice", namespace="user")
    db.set("1", "Laptop", namespace="product")

    assert db.count() == 2


# -------------------------
# INCREMENT
# -------------------------

def test_increment_default(db):
    db.set("counter", 10)

    result = db.increment("counter")

    assert result == 11
    assert db.get("counter") == 11


def test_increment_custom_amount(db):
    db.set("counter", 10)

    result = db.increment("counter", 5)

    assert result == 15


def test_increment_negative_amount(db):
    db.set("counter", 10)

    result = db.increment("counter", -3)

    assert result == 7


def test_increment_zero(db):
    db.set("counter", 10)

    assert db.increment("counter", 0) == 10


def test_increment_negative_value(db):
    db.set("counter", -10)

    assert db.increment("counter", 5) == -5


def test_increment_with_namespace(db):
    db.set("counter", 10, namespace="stats")

    result = db.increment("counter", 5, namespace="stats")

    assert result == 15
    assert db.get("counter", namespace="stats") == 15


def test_increment_missing_key(db):
    with pytest.raises(KeyError):
        db.increment("missing")


def test_increment_non_integer(db):
    db.set("name", "Alice")

    assert db.increment("name") is None
    assert db.get("name") == "Alice"


def test_increment_float(db):
    db.set("score", 10.5)

    assert db.increment("score") is None
    assert db.get("score") == 10.5


def test_increment_boolean(db):
    db.set("active", True)

    # bool is a subclass of int in Python.
    assert db.increment("active") == 2


# -------------------------
# DECREMENT
# -------------------------

def test_decrement_default(db):
    db.set("counter", 10)

    result = db.decrement("counter")

    assert result == 9
    assert db.get("counter") == 9


def test_decrement_custom_amount(db):
    db.set("counter", 10)

    assert db.decrement("counter", 5) == 5


def test_decrement_negative_amount(db):
    db.set("counter", 10)

    assert db.decrement("counter", -3) == 13


def test_decrement_zero(db):
    db.set("counter", 10)

    assert db.decrement("counter", 0) == 10


def test_decrement_below_zero(db):
    db.set("counter", 0)

    assert db.decrement("counter", 5) == -5


def test_decrement_with_namespace(db):
    db.set("counter", 10, namespace="stats")

    result = db.decrement("counter", 3, namespace="stats")

    assert result == 7
    assert db.get("counter", namespace="stats") == 7


def test_decrement_missing_key(db):
    with pytest.raises(KeyError):
        db.decrement("missing")


def test_decrement_non_integer(db):
    db.set("name", "Alice")

    assert db.decrement("name") is None
    assert db.get("name") == "Alice"


def test_decrement_float(db):
    db.set("score", 10.5)

    assert db.decrement("score") is None


def test_decrement_boolean(db):
    db.set("active", True)

    assert db.decrement("active") == 0


# -------------------------
# PERSISTENCE
# -------------------------

def test_increment_persistence(tmp_path):
    db = Droplet(tmp_path)
    db.open()

    db.set("counter", 10)
    db.increment("counter", 5)
    db.close()

    reopened = Droplet(tmp_path)
    reopened.open()

    try:
        assert reopened.get("counter") == 15
    finally:
        reopened.close()


def test_decrement_persistence(tmp_path):
    db = Droplet(tmp_path)
    db.open()

    db.set("counter", 10)
    db.decrement("counter", 3)
    db.close()

    reopened = Droplet(tmp_path)
    reopened.open()

    try:
        assert reopened.get("counter") == 7
    finally:
        reopened.close()


def test_multiple_increments(db):
    db.set("counter", 0)

    for _ in range(100):
        db.increment("counter")

    assert db.get("counter") == 100


def test_multiple_decrements(db):
    db.set("counter", 100)

    for _ in range(100):
        db.decrement("counter")

    assert db.get("counter") == 0
