import redis.asyncio as redis
from flou.conf import settings

redis_pool = redis.ConnectionPool.from_url(
    f"redis://{settings.redis.host}:{settings.redis.port}/{settings.redis.db}"
)


async def get_redis():
    """Get a new Redis connection."""
    redis_connection = await redis.Redis(connection_pool=redis_pool)
    try:
        yield redis_connection
    finally:
        await redis_connection.aclose()