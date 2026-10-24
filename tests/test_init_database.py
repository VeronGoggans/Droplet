import pytest

from pathlib import Path
from src.droplet.database import Droplet



def test_init_with_none():
    db = Droplet()

    assert db.path == Path.cwd() / 'database.droplet'
    assert db.data == {}
    assert db.is_open is False


def test_init_with_existing_directory(tmp_path):
    db = Droplet(tmp_path)

    assert db.path == tmp_path / 'database.droplet'


def test_init_with_nonexistent_directory(tmp_path):
    path = tmp_path / 'storage'
    db = Droplet(path)

    assert db.path == path / 'database.droplet'


def test_init_with_existing_database_file(tmp_path):
    path = tmp_path / 'custom.droplet'
    path.touch()

    db = Droplet(path)

    assert db.path == path


def test_init_with_nonexistent_database_file(tmp_path):
    path = tmp_path / 'custom.droplet'
    db = Droplet(path)

    assert db.path == path


def test_init_with_string_directory(tmp_path):
    db = Droplet(str(tmp_path))

    assert db.path == tmp_path / 'database.droplet'


def test_init_with_invalid_type():
    with pytest.raises(ValueError, match="Expected str, Path or None"):
        Droplet(123)


def test_init_with_invalid_file(tmp_path):
    path = tmp_path / 'invalid.txt'
    path.touch()

    with pytest.raises(ValueError, match="must be a directory or a .droplet file"):
        Droplet(path)


def test_init_with_directory_named_droplet(tmp_path):
    path = tmp_path / 'storage.droplet'
    path.mkdir()

    with pytest.raises(ValueError, match="points to a directory"):
        Droplet(path)