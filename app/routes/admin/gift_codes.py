""" Admin routes for confirmation or denial of randomly-selected winners of the SCS gift code. """

from app import app
from app.persistence.models import WeeklyCodeRecipientResolution
from app.persistence.gift_code_manager import get_pending_confirm_deny_record_by_confirm_code,\
    get_pending_confirm_deny_record_by_deny_code, mark_gift_code_used, update_confirm_deny_record
from app.tasks.gift_code_management import send_gift_code_to_winner,\
    send_gift_code_winner_approval_pm

# -------------------------------------------------------------------------------------------------

@app.route("/admin/confirm_code/<confirm_code>/")
def confirm_gift_code_recipient(confirm_code):
    """ Admin route for confirming the recipient of a weekly SCS gift code. """

    confirm_deny_record = get_pending_confirm_deny_record_by_confirm_code(confirm_code)
    if not confirm_deny_record:
        return "The provided code doesn't match any pending gift codes."

    confirm_deny_record.resolution = WeeklyCodeRecipientResolution.Confirmed
    update_confirm_deny_record(confirm_deny_record)

    mark_gift_code_used(confirm_deny_record.gift_code_id)

    send_gift_code_to_winner(confirm_deny_record.user_id,
                             confirm_deny_record.gift_code_id,
                             confirm_deny_record.comp_id)

    return "Thank you for confirming, the gift code has been sent."


@app.route("/admin/deny_code/<deny_code>/")
def deny_gift_code_recipient(deny_code):
    """ Admin route for denying the chosen recipient of a weekly SCS gift code, and randomly
    choosing another. """

    confirm_deny_record = get_pending_confirm_deny_record_by_deny_code(deny_code)
    if not confirm_deny_record:
        return "The provided code doesn't match any pending gift codes."

    confirm_deny_record.resolution = WeeklyCodeRecipientResolution.Denied
    update_confirm_deny_record(confirm_deny_record)

    send_gift_code_winner_approval_pm(confirm_deny_record.comp_id)

    return "Another recipient will randomly selected. Expect a new confirmation PM shortly."