from typing import *
import redis
import os

IN_MEMORY_REDIS = {}

def get(key) -> Optional[str]:
    if os.environ.get('REDIS_URL'):
        value: bytes = redis.Redis.from_url(os.environ.get('REDIS_URL')).get(key)
        return str(value)
        
    return IN_MEMORY_REDIS.get(key, None)

def set(key, value) -> None:
    if os.environ.get('REDIS_URL'):
        redis.Redis.from_url(os.environ.get('REDIS_URL')).set(key, value)
    else:
        IN_MEMORY_REDIS[key] = value

    return None