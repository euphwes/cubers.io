""" Tasks related to SCS gift code and recipient management. """

from huey import crontab

from app import app
from app.persistence.gift_code_manager import get_unused_gift_code_count
from app.util.reddit import send_PM_to_user_with_title_and_body

from . import huey

# -------------------------------------------------------------------------------------------------

# CODE_CONFIRM_REDDIT_USER
# CODE_TOP_OFF_REDDIT_USER
# CODE_TOP_OFF_THRESHOLD

# The min threshold of gift codes we should have "in stock", and the Reddit user to notify if they
# are too low.
CODE_TOP_OFF_REDDIT_USER = app.config['CODE_TOP_OFF_REDDIT_USER']
CODE_TOP_OFF_THRESHOLD   = app.config['CODE_TOP_OFF_THRESHOLD']

CODES_REFILL_TITLE = 'cubers.io gift codes alert'
CODES_REFILL_TEMPLATE = 'There are only {} SCS gift codes left! Please top off the codes soon.'

# -------------------------------------------------------------------------------------------------

# In dev environments, run the task to check the gift code pool every minute.
# In prod, run it every day.
if app.config['IS_DEVO']:
    CHECK_GIFT_CODE_POOL_SCHEDULE = crontab(minute="*/1")
else:
    CHECK_GIFT_CODE_POOL_SCHEDULE = crontab(day="*/1", hour="0", minute="0")

# -------------------------------------------------------------------------------------------------

@huey.periodic_task(CHECK_GIFT_CODE_POOL_SCHEDULE)
def check_gift_code_pool():
    """ Periodically checks the available gift code count and if it's too low, send a PM to a
    configurable user to top it off. """

    available_code_count = get_unused_gift_code_count()
    if available_code_count < CODE_TOP_OFF_THRESHOLD:
        msg = CODES_REFILL_TEMPLATE.format(available_code_count)
        send_PM_to_user_with_title_and_body(CODE_TOP_OFF_REDDIT_USER, CODES_REFILL_TITLE, msg)
