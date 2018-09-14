""" Utility functions for dealing with PRAW Reddit instances. """
#pylint: disable=C0103

import re
from sys import maxsize as MAX

from praw import Reddit

from app import CUBERS_APP
from app.persistence.models import EventFormat
from app.persistence.comp_manager import get_comp_event_by_id
from app.util.times_util import convert_centiseconds_to_friendly_time, convert_min_sec
from app.util import events_util

REDIRECT      = CUBERS_APP.config['REDDIT_REDIRECT_URI']
USER_AGENT    = 'web:rcubersComps:v0.01 by /u/euphwes'
CLIENT_ID     = CUBERS_APP.config['REDDIT_CLIENT_ID']
CLIENT_SECRET = CUBERS_APP.config['REDDIT_CLIENT_SECRET']
APP_URL       = '({})'.format(CUBERS_APP.config['APP_URL'])

TARGET_SUBREDDIT     = CUBERS_APP.config['TARGET_SUBREDDIT']
CUBERS_IO_ACCT_TOKEN = CUBERS_APP.config['CUBERS_IO_REFRESH_TOKEN']

COMMENT_FOOTER = '\n'.join([
    '',
    '----',
    '^^^Submitted ^^^by [ ^^^cubers.io ]' + APP_URL,
    # possible future stuff linking to the user's profile or competition history?
])

REDDIT_URL_ROOT = 'http://www.reddit.com'

# -------------------------------------------------------------------------------------------------

#pylint: disable=C0103
def build_comment_source_from_events_results(events_results):
    """ Builds the source of a Reddit comment that meets the formatting requirements of the
    /r/cubers weekly competition scoring script. """

    comment_source = ''
    event_line_template = '**{}: {}** = {}\n{}'

    convert_to_friendly = convert_centiseconds_to_friendly_time

    complete_events = [results for results in events_results if results.is_complete()]
    for results in complete_events:
        comp_event   = get_comp_event_by_id(results.comp_event_id)
        event_name   = comp_event.Event.name
        event_format = comp_event.Event.eventFormat
        isFMC        = event_name == 'FMC'
        times_string = build_times_string(results.solves, event_format, isFMC)
        comment      = '\n' if not results.comment else '>' + results.comment + '\n\n'

        if results.average == 'DNF':
            average = 'DNF'
        elif event_format in [EventFormat.Bo3, EventFormat.Bo1]:
            average = convert_to_friendly(results.single)
        else:
            average = results.average if isFMC else convert_to_friendly(results.average)

        line = event_line_template.format(event_name, average, times_string, comment)
        comment_source += line

    comment_source += COMMENT_FOOTER
    return comment_source


def build_times_string(solves, event_format, isFMC=False):
    """ Builds a list of individual times, with best/worst times in parens if appropriate
    for the given event format. """

    time_convert = convert_centiseconds_to_friendly_time

    # Bo1 is special, just return the friendly representation of the one time
    if event_format == EventFormat.Bo1:
        return 'DNF' if solves[0].is_dnf else time_convert(solves[0].get_total_time())

    # FMC is special, the 'time' is actually the number of moves, not number of centiseconds
    # so don't convert to "friendly times" because that makes no sense
    if not isFMC:
        friendly_times = [time_convert(solve.get_total_time()) for solve in solves]
    else:
        friendly_times = [str(solve.get_total_time()) for solve in solves]

    for i, solve in enumerate(solves):
        if solve.is_plus_two:
            friendly_times[i] = friendly_times[i] + "+"

    curr_best   = MAX
    curr_worst  = -1
    best_index  = -1
    worst_index = -1

    dnf_indicies   = list()
    have_found_dnf = False

    for i, solve in enumerate(solves):
        if (not solve.is_dnf) and (solve.get_total_time() < curr_best):
            best_index = i
            curr_best  = solve.get_total_time()

        if (not have_found_dnf) and (solve.get_total_time() > curr_worst):
            worst_index = i
            curr_worst  = solve.get_total_time()

        if solve.is_dnf:
            if not have_found_dnf:
                worst_index = i
                have_found_dnf = True
            dnf_indicies.append(i)

    for i in dnf_indicies:
        friendly_times[i] = 'DNF'

    if event_format in [EventFormat.Bo3, EventFormat.Mo3]:
        return ', '.join(friendly_times)

    friendly_times[best_index] = '({})'.format(friendly_times[best_index])
    friendly_times[worst_index] = '({})'.format(friendly_times[worst_index])
    return ', '.join(friendly_times)


def get_new_reddit():
    """ Returns a new, unauthenticated Reddit instance. """
    return Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT,
                  user_agent=USER_AGENT)


def get_authed_reddit_for_cubersio_acct():
    """ Returns a PRAW instance for the cubers_io Reddit account. """
    return Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                  refresh_token=CUBERS_IO_ACCT_TOKEN, user_agent=USER_AGENT)


def get_authed_reddit_for_user(user):
    """ Returns a PRAW instance for this user using their refresh token. """
    return Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                  refresh_token=user.refresh_token, user_agent=USER_AGENT)


def get_non_user_reddit():
    """ Returns a PRAW instance for cases where we do not need to be authed as a user. """
    return Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT,
                  user_agent=USER_AGENT)


def submit_comment_for_user(user, reddit_thread_id, comment_body):
    """ Submits the comment with the specified body on behalf of the user and returns a URL
    for the comment. """
    comp_submission = get_authed_reddit_for_user(user).submission(id=reddit_thread_id)
    comment = comp_submission.reply(comment_body)
    return (REDDIT_URL_ROOT + comment.permalink), comment.id


def update_comment_for_user(user, comment_thread_id, comment_body):
    """ Updates the comment with the specified body on behalf of the user and returns a URL
    for the comment. """
    r = get_authed_reddit_for_user(user)
    comment = r.comment(id=comment_thread_id)
    comment.edit(comment_body)
    return (REDDIT_URL_ROOT + comment.permalink), comment.id


def submit_competition_post(title, post_body):
    """ Posts a Submission for the competition, and returns a Reddit submission ID. """
    r = get_authed_reddit_for_cubersio_acct()
    cubers = r.subreddit(TARGET_SUBREDDIT)
    return cubers.submit(title=title, selftext=post_body, send_replies=False).id


def get_permalink_for_comp_thread(reddit_thread_id):
    """ Returns the permalink for the competition thread specified by the ID above. """
    comp = get_non_user_reddit().submission(id=reddit_thread_id)
    return REDDIT_URL_ROOT + comp.permalink


def get_username_refresh_token_from_code(code):
    """ Returns the username and current refresh token for a given Reddit auth code. """
    reddit = get_new_reddit()
    refresh_token = reddit.auth.authorize(code)
    username = reddit.user.me().name
    return username, refresh_token


def get_user_auth_url(state='...'):
    """ Returns a url for authenticating with Reddit. """
    return get_new_reddit().auth.url(['identity', 'read', 'submit', 'edit'], state, 'permanent')


# -------------------------------------------------------------------------------------------------
# TODO: Figure out if stuff below is needed. Does it belong in the scripts source? If so, doesn't
# belong directly here in the web app
# -------------------------------------------------------------------------------------------------

BLACKLIST = ["CaptainCockmunch", "LorettAttran", "purplepinapples", "CuberSaiklick",
             "xXxSteelVenomxXx"]

#pylint: disable=C0111
def parse_comment(comment):
    matcher = re.compile('^([^>].+?)\\:\\s*([^\\sA-Za-z!@#\$\%^&*()_+\-=,;\\\[\]\?<>`~\|]+).*')
    dnf_matcher = re.compile('^([^>: ]+) *:.*')
    times_matcher = re.compile('((\d*:?\d+\.?\d*)|(\d*\.?\d+)|(DNF))')
    comment_matcher = re.compile('[A-Za-z]+')

    results = {}

    for line in comment.splitlines():
        # Replace any * with nothing
        content = re.sub('\\*','', line)
        result = matcher.match(content)
        dnf_result = dnf_matcher.match(content)

        if result:
            name = events_util.get_friendly_event_name(result.group(1)) # Group 1 is name
            average = convert_min_sec(result.group(2))   # Group 2 is average

            try:
                results[name] = { "average": average }
            except:
                results[name] = { "average": "Error" }
                continue

            # Detect a list of numbers to get times
            content = content.replace(result.group(1), "", 1).replace(result.group(2), "", 1)

            for match in re.finditer(comment_matcher, content):
                if match.group(0) != "DNF": # Edge case for if the last time is a DNF
                    content = content[:match.start()]

            times = re.findall(times_matcher, content)
            final_times = []

            for t in times:
                if t[0] == "DNF":
                    final_times.append(t[0])
                else:
                    try:
                        final_times.append(convert_min_sec(t[0]))
                    except ValueError:
                        continue
            
            results[name]["times"] = final_times
        elif dnf_result != None:
            print("DNF RESULT ", dnf_result)
            # We have a puzzle name, but no average.
            name = events_util.get_friendly_event_name(dnf_result.group(1))
            results[name] = { "average": "DNF", "times": [] }

    return results
    
#pylint: disable=C0111
def is_blacklisted(reddit_user_id):
    return reddit_user_id in BLACKLIST
    
#pylint: disable=C0111
def get_root_comments(submission_id):
    praw = get_new_reddit()
    submission = praw.submission(submission_id)
    submission.comments.replace_more(limit=None)

    return submission.comments

#pylint: disable=C0111
def parse_post(submission_id):
    comments = get_root_comments(submission_id)
    entries = {}

    for comment in comments:
        if comment.author is not None:
            if ("NOT DONE" not in comment.body) and ("WIP" not in comment.body) and ("#FORMATTINGADVICE" not in comment.body) and not is_blacklisted(comment.author.name):
                results = parse_comment(comment.body)
                
                if results:
                    entries[comment.author.name] = results
    
    return entries

#pylint: disable=C0111
def score_entries(entries):
    events = {}

    for user,entry in entries.items():
        for e,o in entry.items():
            if e in events:
                events[e][user] = o["average"]
            else:
                events[e] = {}
    
    for event,entries in events.items():
        # Separate times from DNFs because sorted() can't work on strings
        to_sort = { user: avg for user,avg in entries.items() if avg != "DNF" }
        dnfs = [ (user, avg) for user,avg in entries.items() if avg == "DNF" ]

        to_sort = sorted(to_sort, key=to_sort.get) # Returns a list of keys in order
        events[event] = [ (user, entries[user]) for user in to_sort ] # Create a list of tuples according to the order of to_sorted
        events[event].extend(dnfs) # Appends the dnfs to the end (Last place)

    return events
