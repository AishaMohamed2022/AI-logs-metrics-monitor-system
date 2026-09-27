from typing import Optional
import redis
from app.config import get_settings
from app.logger import logger

settings = get_settings()

_redis_instance: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """Returns a singleton Redis client instance with connection pooling."""
    global _redis_instance
    if _redis_instance is None:
        try:
            _redis_instance = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_SOCKET_TIMEOUT,
            )
        except Exception as exc:
            logger.error(f"Failed to initialize Redis client: {exc}")
            return None
    return _redis_instance


def check_redis_connection() -> tuple[bool, str]:
    """Verifies that Redis responds to a PING command."""
    client = get_redis_client()
    if client is None:
        return False, "Redis client not initialized"
    try:
        if client.ping():
            return True, "Redis connection OK"
        return False, "Redis ping returned false"
    except Exception as exc:
        logger.error(f"Redis health check failed: {exc}", extra={"error_type": "redis_conn_error"})
        return False, str(exc)
