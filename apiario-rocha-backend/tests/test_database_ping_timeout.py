import asyncio
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
    assert elapsed < 3
