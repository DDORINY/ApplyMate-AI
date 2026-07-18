from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


async def check_database() -> str:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return "UP"
    except Exception:
        return "DOWN"


async def check_redis() -> str:
    try:
        from redis.asyncio import Redis

        redis = Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1)
        await redis.ping()
        await redis.aclose()
        return "UP"
    except Exception:
        return "DOWN"
