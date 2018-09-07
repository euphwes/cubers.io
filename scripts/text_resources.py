""" TODO: module doc """

MAIN_POST_BODY = """
Hello, and welcome to the /r/cubers weekly competitions! If you're new, please read the entire post before competing.
This is competition #{comp_num}, and will run until {due_date}.

We'll hold (almost) every WCA event weekly. We are not currently holding 4BLD, 5BLD, and MBLD, but if there
is enough interest we will add them.

To compete:

> 1. For each event, scramble your cube with the scrambles provided. For OLL, perform the algorithm 5 times.

TODO: rewrite the section below, including talking about cubers.io

> 1. Using a timer, such as [cstimer](http://cstimer.net/timer.php) or [qqtimer](http://www.qqtimer.net/), time your 5 solves and record the results. You are given up to 15 seconds to inspect the cube for each event.
> 1. Post your results down below in a format such as this:
    **10x10: 0.41** = 0.37, 0.62, 0.23, (0.07), (1.13)
> 1. Common mistakes with formatting include adding a space at the beginning of a line, not writing event names as they appear in the post, and bolding event name and average separately. Try to avoid these mistakes.
> 1. Competition results are taken by 10 PM EDT on Sunday nights, so make sure to submit your times by then!

**Weekly WCA Events**:

{formatted_wca_events_list}

**Current Bonus Events**:

{formatted_current_non_wca_events_list}

**Bonus Events In The Queue**:

{formatted_upcoming_non_wca_events_list}

Good luck to all competitors!
"""

SCRAMBLE_ROW_TEMPLATE = "> 1. {scramble}\n\n"

def build_event_scramble_section(event, scrambles_list):
    """ TODO: doc """
    pass
