import os
import json
from typing import Any, Optional
from datetime import datetime
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_EXPIRY = 3600  # 1 hour default cache expiry

# Create Redis connection
redis_client = redis.from_url(REDIS_URL)

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def get_cache(key: str) -> Optional[Any]:
    """
    Get value from cache
    """
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def set_cache(key: str, value: Any, expiry: int = DEFAULT_EXPIRY) -> None:
    """
    Set value in cache with expiry time
    """
    redis_client.setex(key, expiry, json.dumps(value, cls=DateTimeEncoder))

def delete_cache(key: str) -> None:
    """
    Delete value from cache
    """
    redis_client.delete(key)

def clear_cache_pattern(pattern: str) -> None:
    """
    Clear all cache keys matching pattern
    """
    for key in redis_client.scan_iter(f"{pattern}*"):
        redis_client.delete(key) 