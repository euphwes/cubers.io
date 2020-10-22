""" Tasks related to SCS gift code and recipient management. """

from huey import crontab

from app import app
from app.persistence.comp_manager import get_random_reddit_participant_for_competition,\
    get_competition
from app.persistence.gift_code_manager import create_confirm_deny_record, get_gift_code_by_id,\
    get_unused_gift_code, get_unused_gift_code_count
from app.persistence.user_manager import get_user_by_id
from app.util.reddit import send_PM_to_user_with_title_and_body

from . import huey

# -------------------------------------------------------------------------------------------------

# The min threshold of gift codes we should have "in stock", and the Reddit user to notify if they
# are too low.
__CODE_TOP_OFF_REDDIT_USER = app.config['CODE_TOP_OFF_REDDIT_USER']
__CODE_TOP_OFF_THRESHOLD   = app.config['CODE_TOP_OFF_THRESHOLD']

__CODE_REFILL_ADMIN_URL = app.config['APP_URL'] + 'admin/codes/add/'

__CODES_REFILL_TITLE = 'cubers.io gift codes alert'
__CODES_REFILL_TEMPLATE = '''There are only {codes_left} SCS gift codes left!

[Click here]({code_refill_url}) to add more gift codes.'''

# -------------------------------------------------------------------------------------------------

__CODE_CONFIRM_REDDIT_USER = app.config['CODE_CONFIRM_REDDIT_USER']

__DENY_URL_TEMPLATE    = app.config['APP_URL'] + 'admin/deny_code/{deny_code}/'
__CONFIRM_URL_TEMPLATE = app.config['APP_URL'] + 'admin/confirm_code/{confirm_code}/'
__USER_PROFILE_URL     = app.config['APP_URL'] + 'u/{username}/'

__CODE_CONFIRM_DENY_TITLE = 'Confirm cubers.io gift code recipient'
__CODE_CONFIRM_DENY_MSG_TEMPLATE = '''/u/{reddit_id} ([cubers.io profile]({user_profile_url})) was
randomly selected as the SCS gift code recipient for {comp_title}.

To send this user their gift code, [click here to confirm.]({confirm_url})

To select a different participant, [click here to deny.]({deny_url})

There are currently {unused_codes_count} unused gift codes (including the one about to be sent).
'''

# -------------------------------------------------------------------------------------------------

__GIFT_CODE_RECIPIENT_TITLE = "You won a SpeedCubeShop gift code from cubers.io!"
__GIFT_CODE_RECIPIENT_TEMPLATE = """Congratulations, {username}!

You were randomly selected as the winner of a SpeedCubeShop gift code for participating in
{comp_title}. The gift code is `{gift_code}`.

Thanks for participating in [cubers.io](https://www.cubers.io) weekly competitions! We hope to see
you again soon."""

# -------------------------------------------------------------------------------------------------

__NO_CODES_LEFT_TITLE = "No cubers.io gift codes remaining!"
__NO_CODES_LEFT_TEMPLATE = """Can't choose a winner for {comp_title} because there are no codes
left, but we'll retry soon.

[Click here]({code_refill_url}) to add more gift codes."""

# -------------------------------------------------------------------------------------------------

# In devo, run the task to check the gift code pool every 5 minutes. In prod, run it every day.
if app.config['IS_DEVO']:
    CHECK_GIFT_CODE_POOL_SCHEDULE = crontab(minute="*/5")
else:
    CHECK_GIFT_CODE_POOL_SCHEDULE = crontab(day="*/1", hour="0", minute="0")


# Retry a failed gift code winner selection in 5 minutes. In prod, retry in 1 day.
if app.config['IS_DEVO']:
    __GIFT_CODE_SELECTION_RETRY_DELAY = 60 * 5
else:
    __GIFT_CODE_SELECTION_RETRY_DELAY = 60 * 60 * 24

# -------------------------------------------------------------------------------------------------

@huey.periodic_task(CHECK_GIFT_CODE_POOL_SCHEDULE)
def check_gift_code_pool():
    """ Periodically checks the available gift code count and if it's too low, send a PM to a
    configurable user to top it off. """

    available_code_count = get_unused_gift_code_count()
    if available_code_count < __CODE_TOP_OFF_THRESHOLD:
        msg = __CODES_REFILL_TEMPLATE.format(
            codes_left      = available_code_count,
            code_refill_url = __CODE_REFILL_ADMIN_URL
        )
        send_PM_to_user_with_title_and_body(__CODE_TOP_OFF_REDDIT_USER, __CODES_REFILL_TITLE, msg)


@huey.task()
def send_gift_code_winner_approval_pm(comp_id):
    """ Chooses a random participant from the competition provided, and builds a
    WeeklyCodeRecipientConfirmDeny record. Sends a PM to the configured admin user to approve or
    deny that user. """

    winner      = get_random_reddit_participant_for_competition(comp_id)
    competition = get_competition(comp_id)
    gift_code   = get_unused_gift_code()

    if not gift_code:
        msg = __NO_CODES_LEFT_TEMPLATE.format(
            comp_title      = competition.title,
            code_refill_url = __CODE_REFILL_ADMIN_URL
        )
        send_PM_to_user_with_title_and_body(__CODE_TOP_OFF_REDDIT_USER, __NO_CODES_LEFT_TITLE, msg)
        send_gift_code_winner_approval_pm.schedule((comp_id,), delay=__GIFT_CODE_SELECTION_RETRY_DELAY)
        return

    confirm_deny_record = create_confirm_deny_record(gift_code.id, winner.id, comp_id)

    msg = __CODE_CONFIRM_DENY_MSG_TEMPLATE.format(
        reddit_id          = winner.reddit_id,
        comp_title         = competition.title,
        user_profile_url   = __USER_PROFILE_URL.format(username=winner.username),
        confirm_url        = __CONFIRM_URL_TEMPLATE.format(confirm_code=confirm_deny_record.confirm_code),
        deny_url           = __DENY_URL_TEMPLATE.format(deny_code=confirm_deny_record.deny_code),
        unused_codes_count = get_unused_gift_code_count()
    )

    send_PM_to_user_with_title_and_body(__CODE_CONFIRM_REDDIT_USER, __CODE_CONFIRM_DENY_TITLE, msg)


@huey.task()
def send_gift_code_to_winner(user_id: int, gift_code_id: int, comp_id: int) -> None:
    """ Sends a PM to recipient of a weekly SCS gift code. """

    user = get_user_by_id(user_id)
    msg  = __GIFT_CODE_RECIPIENT_TEMPLATE.format(
        username   = user.reddit_id,
        gift_code  = get_gift_code_by_id(gift_code_id).gift_code,
        comp_title = get_competition(comp_id).title
    )

    send_PM_to_user_with_title_and_body(user.reddit_id, __GIFT_CODE_RECIPIENT_TITLE, msg)
