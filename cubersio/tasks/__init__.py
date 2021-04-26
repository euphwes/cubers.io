""" Core task setup. """

from huey.signals import SIGNAL_ERROR

from queue_config import huey

from cubersio import app
from cubersio.tasks.gift_code_management import *
from cubersio.tasks.competition_management import *
from cubersio.tasks.reddit import *
from cubersio.tasks.scramble_generation import *


__TASK_STATUS_REDDIT_USER = app.config['TASK_STATUS_REDDIT_USER']

__TASK_FAILED_BODY  = 'Task {task_name}({task_args}) failed due to the following error: {error}'
__TASK_FAILED_TITLE = 'Task {task_name} failed'


@huey.signal(SIGNAL_ERROR)
def __task_error_handler(_, task, exc):
    """ Handles when a task fails due to unhandled exceptions. """

    if app.config['IS_DEVO']:
        return

    body = __TASK_FAILED_BODY.format(task_name=task.name, task_args=task.args, error=str(exc))
    title = __TASK_FAILED_TITLE.format(task_name=task.name)

    send_pm_to_user(__TASK_STATUS_REDDIT_USER, title, body)
