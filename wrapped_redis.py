import redis
import os

IN_MEMORY_REDIS = {}

def get(key) -> str:
    if os.environ.get('REDIS_URL'):
        return redis.Redis.from_url(os.environ.get('REDIS_URL')).get(key)
    return IN_MEMORY_REDIS[key]

def set(key, value) -> None:
    if os.environ.get('REDIS_URL'):
        redis.Redis.from_url(os.environ.get('REDIS_URL')).set(key, value)
    else:
        IN_MEMORY_REDIS[key] = value

    return None