
import pytest

from dataclasses import dataclass
from src.droplet.database import Droplet


@dataclass
class User:
    name: str
    age: int


@dataclass
class Product:
    name: str
    price: float


@pytest.fixture
def db():
    database = Droplet()
    database.data = {
        "name": "John",
        "age": 25,
        "active": True,
        "score": 99.5,
        "nothing": None,
        "user:1": {"name": "Alice", "age": 30},
        "user:2": {"name": "Bob", "age": 22},
        "product:1": {"name": "Laptop", "price": 999.99},
        "product:2": {"name": "Mouse", "price": 29.99},
    }
    return database


# -------------------------
# GET
# -------------------------

def test_get_string(db):
    assert db.get("name") == "John"


def test_get_integer(db):
    assert db.get("age") == 25


def test_get_boolean(db):
    assert db.get("active") is True


def test_get_float(db):
    assert db.get("score") == 99.5


def test_get_none(db):
    assert db.get("nothing") is None


def test_get_missing_key(db):
    with pytest.raises(KeyError):
        db.get("missing")


def test_get_with_namespace(db):
    assert db.get("1", namespace="user") == {
        "name": "Alice",
        "age": 30
    }


def test_get_missing_namespace_key(db):
    with pytest.raises(KeyError):
        db.get("999", namespace="user")


# -------------------------
# GET NAMESPACE
# -------------------------

def test_get_namespace(db):
    result = db.get_namespace("user")

    assert result == {
        "user:1": {"name": "Alice", "age": 30},
        "user:2": {"name": "Bob", "age": 22},
    }


def test_get_namespace_products(db):
    result = db.get_namespace("product")

    assert len(result) == 2
    assert result["product:1"]["name"] == "Laptop"


def test_get_namespace_missing(db):
    assert db.get_namespace("missing") == {}


def test_get_namespace_excludes_other_keys(db):
    result = db.get_namespace("user")

    assert "name" not in result
    assert "product:1" not in result


# -------------------------
# GET AS
# -------------------------

def test_get_as_dataclass(db):
    user = db.get_as("1", User, namespace="user")

    assert isinstance(user, User)
    assert user.name == "Alice"
    assert user.age == 30


def test_get_as_product(db):
    product = db.get_as("1", Product, namespace="product")

    assert isinstance(product, Product)
    assert product.name == "Laptop"
    assert product.price == 999.99


def test_get_as_missing_key(db):
    with pytest.raises(KeyError):
        db.get_as("999", User, namespace="user")


def test_get_as_invalid_value(db):
    with pytest.raises(TypeError):
        db.get_as("name", User)


def test_get_as_invalid_dataclass_fields(db):
    db.data["user:3"] = {"invalid": "value"}

    with pytest.raises(TypeError):
        db.get_as("3", User, namespace="user")


# -------------------------
# GET BATCH AS
# -------------------------

def test_get_batch_as(db):
    users = db.get_batch_as(["1", "2"], User, namespace="user")

    assert len(users) == 2
    assert isinstance(users["1"], User)
    assert isinstance(users["2"], User)
    assert users["1"].name == "Alice"
    assert users["2"].name == "Bob"


def test_get_batch_as_empty(db):
    assert db.get_batch_as([], User, namespace="user") == {}


def test_get_batch_as_missing_key(db):
    with pytest.raises(KeyError):
        db.get_batch_as(["1", "999"], User, namespace="user")


def test_get_batch_as_invalid_value(db):
    db.data["user:3"] = "invalid"

    with pytest.raises(TypeError):
        db.get_batch_as(["1", "3"], User, namespace="user")


# -------------------------
# GET BATCH
# -------------------------

def test_get_batch(db):
    result = db.get_batch(["name", "age", "active"])

    assert result == {
        "name": "John",
        "age": 25,
        "active": True,
    }


def test_get_batch_with_namespace(db):
    result = db.get_batch(["1", "2"], namespace="user")

    assert result == {
        "user:1": {"name": "Alice", "age": 30},
        "user:2": {"name": "Bob", "age": 22},
    }


def test_get_batch_empty(db):
    assert db.get_batch([]) == {}


def test_get_batch_missing_key(db):
    with pytest.raises(KeyError):
        db.get_batch(["name", "missing"])


def test_get_batch_single_key(db):
    assert db.get_batch(["name"]) == {
        "name": "John"
    }
