""" Core task setup. """

from os import getpid

from queue_config import huey

# -------------------------------------------------------------------------------------------------

@huey.task()
def test_print(value):
    """ Prints a value as a background task, along with the PID. """
    pid = str(getpid())
    print("'{}' on PID {}".format(value, pid))
