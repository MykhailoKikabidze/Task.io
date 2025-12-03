import os
import redis

REDIS_URL = os.getenv("REDIS_URL")

if REDIS_URL:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
else:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB   = int(os.getenv("REDIS_DB", 0))
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True
    )

PROJECT_TTL = int(os.getenv("PROJECT_TTL", 3600))
USERS_TTL   = int(os.getenv("USERS_TTL",   300))
SPRINTS_TTL = int(os.getenv("SPRINTS_TTL",   1800))
EPICS_TTL   = int(os.getenv("EPICS_TTL",   1800))
