import pytest

from pathlib import Path
from stormdb.stormdb import StormDB


def test_init_with_none():
    """Test that passing None defaults to the current working directory."""
    db = StormDB()
    assert db.path == Path.cwd() / 'stormdb.storm'
    assert db.data == {}
    assert db.opened is False

def test_init_with_string():
    """Test initializing with a string path."""
    db = StormDB("my_database.storm")
    assert db.path == Path("my_database.storm")
    assert db.data == {}
    assert db.opened is False

def test_init_with_path_object():
    """Test initializing with a pathlib Path object."""
    custom_path = Path("/tmp/stormdb")
    db = StormDB(custom_path)
    assert db.path == custom_path
    assert db.data == {}
    assert db.opened is False

def test_init_with_invalid_type():
    """Test that passing an unsupported type (like an int) raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        StormDB(123)
    
    assert "expected StringOrPath" in str(exc_info.value)