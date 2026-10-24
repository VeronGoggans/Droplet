
import pytest

from src.droplet.database import Droplet


@pytest.fixture
def db(tmp_path):
    database = Droplet(tmp_path)
    database.open()

    yield database

    database.close()


# -------------------------
# DELETE
# -------------------------

def test_delete_existing_key(db):
    db.set("name", "Alice")

    result = db.delete("name")

    assert result == "Alice"
    assert "name" not in db.data


def test_delete_missing_key(db):
    result = db.delete("missing")

    assert result is False


def test_delete_integer(db):
    db.set("age", 25)

    result = db.delete("age")

    assert result == 25
    assert "age" not in db.data


def test_delete_none_value(db):
    db.set("nothing", None)

    result = db.delete("nothing")

    assert result is None
    assert "nothing" not in db.data


def test_delete_false_value(db):
    db.set("active", False)

    result = db.delete("active")

    assert result is False
    assert "active" not in db.data


def test_delete_with_namespace(db):
    db.set("1", "Alice", namespace="user")

    result = db.delete("1", namespace="user")

    assert result == "Alice"
    assert "user:1" not in db.data


def test_delete_namespace_isolation(db):
    db.set("1", "Alice", namespace="user")
    db.set("1", "Laptop", namespace="product")

    db.delete("1", namespace="user")

    assert "user:1" not in db.data
    assert db.get("1", namespace="product") == "Laptop"


def test_delete_removes_expiration(db):
    db.set("session", "token", ttl=60)

    assert "session" in db.expirations

    db.delete("session")

    assert "session" not in db.expirations
    assert "session" not in db.data


def test_delete_with_namespace_removes_expiration(db):
    db.set("1", "Alice", ttl=60, namespace="user")

    db.delete("1", namespace="user")

    assert "user:1" not in db.expirations


def test_delete_same_key_twice(db):
    db.set("name", "Alice")

    first = db.delete("name")
    second = db.delete("name")

    assert first == "Alice"
    assert second is False


def test_delete_invalid_namespace(db):
    db.set("name", "Alice")

    with pytest.raises((ValueError, TypeError)):
        db.delete("name", namespace=123)

    assert db.get("name") == "Alice"


# -------------------------
# DELETE BATCH
# -------------------------

def test_delete_batch(db):
    db.set_batch({
        "name": "Alice",
        "age": 30,
        "active": True,
    })

    result = db.delete_batch(["name", "age"])

    assert result == {
        "name": "Alice",
        "age": 30,
    }

    assert "name" not in db.data
    assert "age" not in db.data
    assert db.get("active") is True


def test_delete_batch_empty(db):
    result = db.delete_batch([])

    assert result == {}


def test_delete_batch_missing_keys(db):
    result = db.delete_batch(["missing1", "missing2"])

    assert result == {}


def test_delete_batch_mixed_existing_and_missing(db):
    db.set_batch({
        "name": "Alice",
        "age": 30,
    })

    result = db.delete_batch(["name", "missing", "age"])

    assert result == {
        "name": "Alice",
        "age": 30,
    }


def test_delete_batch_with_namespace(db):
    db.set_batch({
        "1": "Alice",
        "2": "Bob",
        "3": "Charlie",
    }, namespace="user")

    result = db.delete_batch(["1", "2"], namespace="user")

    assert result == {
        "user:1": "Alice",
        "user:2": "Bob",
    }

    assert "user:1" not in db.data
    assert "user:2" not in db.data
    assert db.get("3", namespace="user") == "Charlie"


def test_delete_batch_namespace_isolation(db):
    db.set("1", "Alice", namespace="user")
    db.set("1", "Laptop", namespace="product")

    db.delete_batch(["1"], namespace="user")

    assert db.get("1", namespace="product") == "Laptop"


def test_delete_batch_removes_expirations(db):
    db.set_batch({
        "1": "Alice",
        "2": "Bob",
        "3": "Charlie",
    }, ttl=60, namespace="user")

    db.delete_batch(["1", "2"], namespace="user")

    assert "user:1" not in db.expirations
    assert "user:2" not in db.expirations
    assert "user:3" in db.expirations


def test_delete_batch_duplicate_keys(db):
    db.set("name", "Alice")

    result = db.delete_batch(["name", "name"])

    assert result == {"name": "Alice"}
    assert "name" not in db.data


def test_delete_batch_all_keys(db):
    db.set_batch({
        "a": 1,
        "b": 2,
        "c": 3,
    })

    result = db.delete_batch(["a", "b", "c"])

    assert result == {
        "a": 1,
        "b": 2,
        "c": 3,
    }

    assert db.data == {}


def test_delete_batch_invalid_namespace(db):
    db.set("name", "Alice")

    with pytest.raises((ValueError, TypeError)):
        db.delete_batch(["name"], namespace=123)

    assert db.get("name") == "Alice"


# -------------------------
# PERSISTENCE
# -------------------------

def test_delete_persistence(tmp_path):
    db = Droplet(tmp_path, mode='persistent')
    db.open()

    db.set("name", "Alice")
    db.set("age", 30)
    db.delete("name")

    db.close()

    reopened = Droplet(tmp_path, mode='persistent')
    reopened.open()

    try:
        with pytest.raises(KeyError):
            reopened.get("name")

        assert reopened.get("age") == 30
    finally:
        reopened.close()


def test_delete_batch_persistence(tmp_path):
    db = Droplet(tmp_path, mode='persistent')
    db.open()

    db.set_batch({
        "name": "Alice",
        "age": 30,
        "active": True,
    })

    db.delete_batch(["name", "age"])
    db.close()

    reopened = Droplet(tmp_path, mode='persistent')
    reopened.open()

    try:
        with pytest.raises(KeyError):
            reopened.get("name")

        with pytest.raises(KeyError):
            reopened.get("age")

        assert reopened.get("active") is True
    finally:
        reopened.close()


def test_delete_then_reinsert_persistence(tmp_path):
    db = Droplet(tmp_path, mode='persistent')
    db.open()

    db.set("name", "Alice")
    db.delete("name")
    db.set("name", "Bob")

    db.close()

    reopened = Droplet(tmp_path, mode='persistent')
    reopened.open()

    try:
        assert reopened.get("name") == "Bob"
    finally:
        reopened.close()


def test_delete_batch_then_reinsert_persistence(tmp_path):
    db = Droplet(tmp_path, mode='persistent')
    db.open()

    db.set_batch({
        "a": 1,
        "b": 2,
    })

    db.delete_batch(["a", "b"])

    db.set_batch({
        "a": 10,
        "b": 20,
    })

    db.close()

    reopened = Droplet(tmp_path, mode='persistent')
    reopened.open()

    try:
        assert reopened.get("a") == 10
        assert reopened.get("b") == 20
    finally:
        reopened.close()
