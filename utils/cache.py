import redis
import json
import functools
from typing import Optional, Any
from app.config import get_settings
from app.utils.logging import logging_config
from fastapi.responses import JSONResponse
from fastapi import status

logger = logging_config.getLogger(__name__)

settings = get_settings()

# Create redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
    username=settings.REDIS_USR,
    password=settings.REDIS_PWD,
)

def cache_response(expire: int = 300):
    """
    Decorator for caching API responses in Redis.
    
    Args:
        expire: Cache expiration time in seconds (default 5 minutes)
    
    Example:
        @cache_response(expire=600)
        async def get_user(user_id: int):
            return db.query(User).filter(User.id == user_id).first()
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Cache keys
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            try:
                cached = redis_client.get(cache_key)
                
                if cached:
                    cached_data = json.loads(cached)
                    logger.info('Lodaing from the cache')
                    responses_content = {'status_code': status.HTTP_200_OK,
                                            'data': cached_data,
                                            'message': 'User Found'
                                                }
                    return JSONResponse(content=responses_content, status_code=status.HTTP_200_OK)
            except redis.RedisError as e:
                logger.error(f"Redis error: {e}")

            #Execute fuction and cache result
            result = await func(*args, **kwargs)
            responses_content = {'status_code': status.HTTP_200_OK,
                                    'data': result,
                                    'message': 'User Found'
                                }

            try:
                redis_client.setex(
                    cache_key,
                    expire,
                    json.dumps(result, default=str)
                )
            except redis.RedisError as e:
                logger.error(f"Redis caching error: {e}")

            return JSONResponse(content=responses_content, status_code=status.HTTP_200_OK)
        return wrapper
    return decorator

def invalidate_cache(pattern:str) -> None:
    """
    Invalidate all cache keys matching a pattern.
    Useful when data is updated and cache needs to be cleared.
    
    Args:
        pattern: Redis key pattern (e.g., "get_user:*")
    """
    try:
        keys = redis_client.keys(pattern=pattern)
        if keys:
            logger.info('Invalidating the existing cache')
            redis_client.delete(*keys)
    except redis.RedisError as e:
        logger.error(f"Cache invalidation error: {e}")