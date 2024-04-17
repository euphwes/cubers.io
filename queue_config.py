""" Setup for the Huey task queue. """
# pylint: disable=invalid-name,ungrouped-imports,unused-import

from os import environ
from huey import RedisHuey, SqliteHuey

# run consumer via:
# huey_consumer.py app.huey
# from the root of the app directory

# ------------------------------------------------------
# Huey task config
# ------------------------------------------------------

# Redis is the preferred Huey backend
REDIS_URL = environ.get('REDIS_URL', None)
if REDIS_URL:
    huey = RedisHuey(url=REDIS_URL)

# But in dev environments, fall back to SqliteHuey if Redis is not available
else:
    # peewee is required for SqliteHuey
    # If this import fails, install peewee directly. Don't add to requirements.txt.
    import peewee
    huey = SqliteHuey(filename='huey.db', immediate=True)
