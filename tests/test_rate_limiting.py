
import time
import pytest

from droplet import Droplet


@pytest.fixture
def db():
    return Droplet(mode='memory')



def test_create_rate_limit(db):
    db.rate_limit("api", limit=5, window=60)

    data = db.rate_limits["api"]

    assert data["count"] == 0
    assert data["limit"] == 5
    assert data["window"] == 60
    assert data["exp"] > time.time()


@pytest.mark.parametrize(
    ("limit", "window"),
    [
        (0, 60),
        (5, 0),
        (0, 0),
        (-1, 60),
        (5, -1),
    ],
)
def test_create_rate_limit_invalid_values(db, limit, window):
    with pytest.raises(ValueError):
        db.rate_limit("api", limit, window)


@pytest.mark.parametrize(
    ("limit", "window"),
    [
        ("5", 60),
        (5, "60"),
        (5.5, 60),
        (5, 60.5),
    ],
)
def test_create_rate_limit_invalid_types(db, limit, window):
    with pytest.raises(ValueError):
        db.rate_limit("api", limit, window)



def test_increment_rate_limit(db):
    db.rate_limit("api", limit=5, window=60)
    db.increment_rate_limit("api")

    assert db.rate_limits["api"]["count"] == 1


def test_increment_rate_limit_multiple_times(db):
    db.rate_limit("api", limit=5, window=60)

    for _ in range(3):
        db.increment_rate_limit("api")

    assert db.rate_limits["api"]["count"] == 3


def test_increment_nonexistent_rate_limit(db):
    with pytest.raises(ValueError, match="does not have a rate limit"):
        db.increment_rate_limit("missing")


def test_increment_exceeding_limit(db):
    db.rate_limit("api", limit=2, window=60)

    db.increment_rate_limit("api")
    db.increment_rate_limit("api")

    with pytest.raises(ValueError, match="exceeded"):
        db.increment_rate_limit("api")

    assert db.rate_limits["api"]["count"] == 2


def test_increment_after_window_expiration(db, monkeypatch):
    current_time = 1000.0

    monkeypatch.setattr(time, "time", lambda: current_time)

    db.rate_limit("api", limit=2, window=60)
    db.increment_rate_limit("api")
    db.increment_rate_limit("api")

    assert db.rate_limits["api"]["count"] == 2

    current_time += 61

    db.increment_rate_limit("api")

    data = db.rate_limits["api"]

    assert data["count"] == 1
    assert data["exp"] == current_time + 60


def test_increment_before_window_expiration(db, monkeypatch):
    current_time = 1000.0

    monkeypatch.setattr(time, "time", lambda: current_time)

    db.rate_limit("api", limit=5, window=60)
    db.increment_rate_limit("api")

    current_time += 30
    db.increment_rate_limit("api")

    assert db.rate_limits["api"]["count"] == 2
