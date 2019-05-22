""" Routes related to displaying competition results. """

from random import choice

from flask import render_template, redirect, abort, request
from flask_login import current_user

from app import app

# -------------------------------------------------------------------------------------------------

TIMER_TEMPLATE_MOBILE_MAP = {
    True:  'timer/mobile/timer_page.html',
    False: 'timer/timer_page.html',
}

# -------------------------------------------------------------------------------------------------

@app.route('/timer/<int:comp_event_id>')
def timer_page(comp_event_id):
    """ TODO: fill this for real.
    A temp route for working on timer page redesign outside of the real timer page. """

    scramble = choice([
        # "D' B2 L2 D R2 F2 D2 U' R2 F2 D2 L B R2 U' L2 D2 F U' B2 L'",
        "3Fw2 Bw Dw L2 U' Fw Uw R2 U' 3Lw2 L2 Uw 3Lw2 3Uw' Uw D' B2 Rw2 L' 3Dw Bw Uw 3Fw B' Bw' 3Uw 3Rw' 3Uw2 U 3Bw2 D 3Lw 3Rw Rw 3Bw2 D2 B2 U' Uw' Rw2 3Bw2 3Rw Dw' 3Bw' 3Lw2 Bw' 3Bw' U' 3Dw Rw Fw' Rw Bw L F2 3Lw2 3Uw2 Lw Fw2 D Fw2 3Lw' Fw L Dw 3Bw2 Dw' 3Lw2 3Fw' Uw2 3Rw2 U2 Rw2 Bw 3Fw Uw L Fw2 Uw' L Fw2 B' Bw' 3Lw' Fw' B F' 3Dw2 R' 3Bw' D' Lw D2 U' Uw 3Bw' F2 3Rw L' Fw2",
    ])

    alternative_title = "7x7 - May 2019 Week 2"

    return render_template(TIMER_TEMPLATE_MOBILE_MAP[request.MOBILE], scramble=scramble,
        alternative_title=alternative_title)
