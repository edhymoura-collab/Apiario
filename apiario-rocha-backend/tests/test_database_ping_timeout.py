import asyncio
import sqlite3
import time

from src.config import database


def test_ping_database_does_not_block_startup(monkeypatch):
    async def slow_command(*args, **kwargs):
        await asyncio.sleep(10)
        return {"ok": 1}

    fake_db = type("FakeDb", (), {"command": staticmethod(slow_command)})()
    monkeypatch.setattr(database, "database", fake_db)

    started = time.monotonic()
    result = asyncio.run(database.ping_database())
    elapsed = time.monotonic() - started

    assert result is False
    assert elapsed < 1.5


def test_ping_database_returns_false_on_sqlite_error(monkeypatch):
    async def failing_command(*args, **kwargs):
        raise sqlite3.OperationalError("database unavailable")

    fake_db = type("FakeDb", (), {"command": staticmethod(failing_command)})()
    monkeypatch.setattr(database, "database", fake_db)

    assert asyncio.run(database.ping_database()) is False
