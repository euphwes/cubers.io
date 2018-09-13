""" TODO: module doc """

MAIN_POST_BODY = """
Hello, and welcome to the /r/cubers weekly competition! If you're new, please read the entire post before competing.
This is competition #{comp_num}, and will run until {due_date}.

We'll hold (almost) every WCA event weekly. We are not currently holding 4BLD, 5BLD, and MBLD, but if there
is enough interest we will add them. We'll rotate through a list of bonus events every week.

For a streamlined competition experience, please visit [cubers.io](https://www.cubers.io)! This app comes with a timer and Reddit
integration, and will post a comment below on your behalf with your completed events.

If you want to still compete and manually enter your times, please follow the instructions below:

> 1. For each event, scramble your cube with the scrambles provided. For COLL, perform the algorithm 5 times.
> 1. Post your results down below in a format such as this:
    **10x10: 0.41** = 0.37, 0.62, 0.23, (0.07), (1.13)
> 1. Common mistakes with formatting include adding a space at the beginning of a line, not writing event names as they appear in the post, and bolding event name and average separately. Try to avoid these mistakes.

Competition results are taken by 10 PM EDT on Sunday nights, so make sure to submit your times by then!

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
