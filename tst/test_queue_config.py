""" Tests for utility functions related to manipulating and converting times. """

from importlib import reload
import os
from unittest.mock import Mock, MagicMock
import sys

from huey import SqliteHuey


def test_devo_huey_uses_sqlite():
    queue_config = __import__("queue_config")
    assert isinstance(queue_config.huey, SqliteHuey)


def test_devo_huey_raises_runtime_if_no_peewee():
    queue_config = __import__("queue_config")
    if 'peewee' in sys.modules:
        del sys.modules['peewee']
    reload(queue_config)
    __import__("queue_config")


def test_prod_huey_uses_redis():

    expected_redis_url = "da_redis_url"
    os.environ["REDIS_URL"] = expected_redis_url

    mock_redis_huey_instance = Mock()

    mock_redis_huey = Mock()
    mock_redis_huey.return_value = mock_redis_huey_instance

    mock_huey = MagicMock()
    mock_huey.RedisHuey = mock_redis_huey

    sys.modules['huey'] = mock_huey

    queue_config = __import__("queue_config")

    # Need to reload the module, in case the devo test above ran first and the module has already been imported.
    # If that happened, the setup above with mock huey, etc, wouldn't have happened.
    reload(queue_config)

    assert queue_config.huey == mock_redis_huey_instance
    mock_redis_huey.assert_called_once_with(url=expected_redis_url)
