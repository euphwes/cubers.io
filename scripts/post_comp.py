""" module doc here """

from arrow import utcnow

# -------------------------------------------------------------------------------------------------

POST_TEMPLATE = """Hello, and welcome to the /r/cubers weekly competition! If you're new, please
read the entire post before competing. This is competition #{comp_num}, and will run until {due_date}.

We'll hold (almost) every WCA event weekly. We are not currently holding 4BLD, 5BLD, and MBLD, but
if there is enough interest we will add them. We'll rotate through a list of bonus events every week.

For a streamlined experience, please visit [cubers.io](https://www.cubers.io)! This app is focused
directly on the weekly competition, with a timer and features Reddit integration. If you log in to
compete, it can post a comment below on your behalf with your completed events.

If you want to still compete by manually entering your times, please follow the instructions below:

> 1. For each event, scramble your cube with the scrambles provided. For COLL, perform the algorithm 5 times.
> 1. Post your results down below in a format such as this:
    **10x10: 0.41** = 0.37, 0.62, 0.23, (0.07), (1.13)
> 1. Common mistakes with formatting include adding a space at the beginning of a line, not writing event
names as they appear in the post, and bolding event name and average separately. Try to avoid these mistakes.

**Current Bonus Events**:

{curr_bonus_events}

**Bonus Events In The Queue**:

{upcoming_bonus_events}

Good luck to all competitors!

{formatted_events_with_scrambles}"""

SCRAMBLE_LINE_TEMPLATE   = '> 1. {}\n\n'
EVENT_NAME_LINE_TEMPLATE = '**{}:**\n\n'

# -------------------------------------------------------------------------------------------------

def post_competition(comp_title, comp_num, event_data, curr_bonus, upcoming_bonus):
    """ Post the competition to Reddit and return the Reddit ID. """

    due_date = utcnow().to('US/Eastern').format('hh:MM A on dddd, MMMM Do YYYY US/Eastern time')

    curr_bonus_events     = '\n\n> * '.join(curr_bonus)
    upcoming_bonus_events = '\n\n> * '.join(upcoming_bonus)

    event_section = ''
    for event in event_data:
        event_section += EVENT_NAME_LINE_TEMPLATE.format(event['name'])
        for scramble in event['scrambles']:
            event_section += SCRAMBLE_LINE_TEMPLATE.format(scramble)

    post_body = POST_TEMPLATE.format(
        due_date = due_date,
        comp_num = comp_num,
        curr_bonus_events = curr_bonus_events,
        upcoming_bonus_events = upcoming_bonus_events,
        formatted_events_with_scrambles = event_section
    )

    #new_comp = r.subreddit('cubers').submit(title="Cubing Competition " + str(data[3]) + "!", selftext=post, send_replies=False)
    #return new_comp.id
    return 1