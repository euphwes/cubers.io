""" Admin routes for confirmation or denial of randomly-selected winners of the SCS gift code. """

from typing import Text

from flask import render_template, request
from flask_login import current_user

from cubersio import app
from cubersio.persistence.models import WeeklyCodeRecipientResolution
from cubersio.persistence.gift_code_manager import bulk_add_gift_codes,\
    get_pending_confirm_deny_record_by_confirm_code, get_pending_confirm_deny_record_by_deny_code,\
    get_unused_gift_code_count, mark_gift_code_used, update_confirm_deny_record
from cubersio.tasks.gift_code_management import send_gift_code_to_winner,\
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


@app.route("/admin/codes/add/", methods=['GET', 'POST'])
def add_gift_codes():
    """ Admin route for adding SCS gift codes to the gift code pool in the database. """

    # TODO this better
    if not (current_user.is_authenticated and current_user.is_admin):
        return ("Hey, you're not allowed to do that.", 403)

    if request.method == 'POST':
        return __handle_add_gift_codes(request.form)

    return render_template("admin/gift_codes/gift_code_topoff.html")


def __handle_add_gift_codes(form: dict) -> Text:
    """ Handles the form submission, parses SCS gift codes from the input, and adds them to the
    gift code pool database. """

    new_codes = [code.strip() for code in form['code_list'].split()]
    bulk_add_gift_codes(new_codes)

    new_codes_count    = len(new_codes)
    unused_codes_count = get_unused_gift_code_count()

    return 'Successfully added {} new gift codes. There are now {} unused codes in the pool.'.format(new_codes_count, unused_codes_count)
