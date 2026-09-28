import pytest

from pathlib import Path
from src.stashdb.database import Database


def test_init_with_none():
    """Test that passing None defaults to the current working directory."""
    db = Database()
    assert db.path == Path.cwd() / 'database.sdb'
    assert db.data == {}
    assert db.is_open is False


def test_init_with_string():
    """Test initializing with a string path."""
    db = Database("/temp/storage")
    assert db.path == Path("/temp/storage/database.sdb")
    assert db.data == {}
    assert db.is_open is False


def test_init_with_path_object():
    """Test initializing with a pathlib Path object."""
    custom_path = Path("/tmp/storage")
    db = Database(custom_path)
    assert db.path == custom_path / 'database.sdb'
    assert db.data == {}
    assert db.is_open is False


def test_init_with_invalid_type():
    """Test that passing an unsupported type (like an int) raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        Database(123)
    
    assert "expected StringOrPath" in str(exc_info.value)


def test_init_with_invalid_path():
    """Test that passing an unsupported path (with file as destination) raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        Database('/temp/database.sdb')
    
    assert "The database path should point to a folder, not a file" == str(exc_info.value)