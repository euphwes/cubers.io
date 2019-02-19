""" Setup for the Huey task queue. """
# pylint: disable=invalid-name,ungrouped-imports,unused-import

from os import environ

# run consumer via:
# huey_consumer.py app.huey
# from the root of the app directory

# ------------------------------------------------------
# Huey task config
# ------------------------------------------------------

# Redis is the preferred Huey backend
REDIS_URL = environ.get('REDIS_URL', None)
if REDIS_URL:
    from huey import RedisHuey
    huey = RedisHuey(url=REDIS_URL)

# But in dev environments, fall back to SqliteHuey if Redis is not available
else:
    try:
        import peewee
    except ImportError:
        MSG =  "peewee is required for SqliteHuey."
        MSG += "Install peewee directly, don't add to requirements.txt"
        raise RuntimeError(MSG)

    from huey.contrib.sqlitedb import SqliteHuey
    huey = SqliteHuey(filename='huey.db')
