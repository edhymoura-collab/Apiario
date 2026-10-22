import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from src.config.settings import get_settings

settings = get_settings()

client = AsyncIOMotorClient(settings.mongo_uri, serverSelectionTimeoutMS=2000)
database = client[settings.mongo_db]


async def ping_database() -> bool:
    try:
        await asyncio.wait_for(database.command("ping"), timeout=2.0)
        return True
    except (asyncio.TimeoutError, Exception):
        return False
