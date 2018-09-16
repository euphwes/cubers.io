""" module doc """

import re
from time import sleep

from app.persistence.comp_manager import get_active_competition, get_competition
from app.util.reddit_util import get_submission_with_id, submit_competition_post,\
get_permalink_for_comp_thread

# -------------------------------------------------------------------------------------------------

def filter_empty_author_and_blacklist(entries):
    """ Returns a filtered list of competition entries (which here are PRAW Comments) which do
    not contain any author=None or authors from the blacklist. """

    # TODO: get blacklist
    blacklist = list()

    return [e for e in entries if (e.author is not None) and (e.author.name not in blacklist)]


def filter_entries_with_no_events(entries, event_names):
    """ Returns a filtered list of competition entries (which here are PRAW Comments) which do
    not mention any events from the competition. """

    return [e for e in entries if find_events(e, event_names)]


def filter_entries_that_are_wip(entries):
    """ Returns a filtered list of competition entries (which here are PRAW Comments) which have any
    of the work-in-progress magic phrases. """

    return [e for e in entries if ("WIP" not in e.body) and ("FORMATTINGADVICE" not in e.body)]

# -------------------------------------------------------------------------------------------------

def score_previous_competition(is_rerun=False, comp_id=None):
    """ Score the previous competition and post the results. """

    # Get the reddit thread ID and the competition model for the competition to be scored
    if comp_id:
        competition_being_scored = get_competition(comp_id)
    else:
        competition_being_scored = get_active_competition()

    submission_id = competition_being_scored.reddit_thread_id

    # Build a list of event names that were in this competition
    event_names = [comp_event.Event.name for comp_event in competition_being_scored.events]

    # Get the PRAW Submission object and make sure we have all the top-level comments
    submission = get_submission_with_id(submission_id)
    try_count = 0
    while try_count < 10:
        try_count += 1
        try:
            submission.comments.replace_more()
            break
        except:
            sleep(5)
    entries = submission.comments

    # Filter out all the entry comments we don't want
    entries = filter_empty_author_and_blacklist(entries)
    entries = filter_entries_with_no_events(entries, event_names)
    entries = filter_entries_that_are_wip(entries)

    # Create a competitor record for each entry
    competitors = [Competitor(entry) for entry in entries]

    # Creating a competitor record automatically removes any broken times/events
    # Filter out any competitors without any events left
    competitors = [c for c in competitors if c.events]

    # Remove duplicate users
    competitors = list(set(competitors))

    # Build up a dictionary of event name to participant list
    # Participant list contains tuple of (username, average)
    # Participant list is sorted by average
    comp_event_results = dict()
    for event_name in event_names:
        participating_users = list()
        for competitor in competitors:
            if event_name in competitor.events:
                time = competitor.event_time_map[event_name]
                participating_users.append((competitor.name, time, competitor))
        if not participating_users:
            continue
        participating_users.sort(key=lambda x: x[1])
        num_event_participants = len(participating_users)
        for i, record in enumerate(participating_users):
            record[2].points += (num_event_participants - (i+1) + 1)
        comp_event_results[event_name] = participating_users

    permalink  = get_permalink_for_comp_thread(submission_id)
    comp_title = competition_being_scored.title
    post_body = 'Results for [{}]({})!'.format(comp_title, permalink)

    for event_name in event_names:
        if not event_name in comp_event_results.keys():
            continue
        participants = comp_event_results[event_name]
        if not participants:
            continue
        post_body += '\n\n**{}**\n\n'.format(event_name)
        for participant in participants:
            post_body += '1. {}: {}\n\n'.format(participant[0], participant[1])

    post_body += '---\n\n**Total points this week**'
    post_body += '\n\nEach event gives `# of participants - place + 1` points\n\n'
    competitors.sort(key=lambda c: c.points, reverse=True)
    for competitor in competitors:
        post_body += '1. {}: {}\n\n'.format(competitor.name, competitor.points)

    title = 'Results for {}!'.format(competition_being_scored.title)
    new_post_id = submit_competition_post(title, post_body)


def find_events(comment, events):
    """ Returns a list of events that are present in this comment. """
    return [e for e in events if '{}:'.format(e) in comment.body]

# -------------------------------------------------------------------------------------------------

class Competitor:
    def __init__(self, entry):
        parse_results = parse(entry.body)
        self.events = parse_results[1]
        self.times = parse_results[0]
        self.name = '/u/{}'.format(entry.author.name)
        self.points = 0
        self.fix_times()
        self.event_time_map = dict(zip(self.events, self.times))

    def fix_times(self):
        while("Error" in self.times):
            self.events.pop(self.times.index("Error"))
            self.times.pop(self.times.index("Error"))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        else:
            return False

    def __hash__(self):
        return hash(self.name)

    def __ne__(self, other):
        return not self.__eq__(other)

# -------------------------------------------------------------------------------------------------
#   This is pretty awful below, but it's functional so let's mess with it as little as possible!
#   Just minor tweaks to improve readibility
# -------------------------------------------------------------------------------------------------

def parse(post):
    """ ... """

    # As as long as a line of text "fits" this pattern, we will get a successful match. Otherwise we get 'None'.
    matcher = re.compile('^(.+?)\\:\\s*([^\\s]+).*')

    # Create a second matcher to find "empty" results. ONLY apply it if the first rule didn't match. (see below)
    dnf_matcher = re.compile('^([^\\:\\s]+)\\s*\\:.*')

    times = list()
    events = list()
    raw_times = list()

    # Split our post into individual lines, and process them
    for line in post.splitlines():
        # Now replace any * characters with nothing.
        content = re.sub ('\\*','',line)

        # Use our matchers to see if the current line matches our pattern(s).
        result = matcher.match(content)
        dnf_result = dnf_matcher.match(content)

        name = ''
        average = ''
        if result != None:
            # We have gotten a puzzle name and an average.
            name = result.group(1)      #The first group was name.
            if (result.group(1).lower() == "mirror blocks"):
                events.append("3x3 Mirror Blocks/Bump")
            elif (result.group(1).lower() == "3x3 mirror blocks/bump"):
                events.append("3x3 Mirror Blocks/Bump")
            elif (result.group(1).lower() == "3x3 relay"):
                events.append("3x3 Relay of 3")
            elif (result.group(1).lower() == "relay of 3"):
                events.append("3x3 Relay of 3")
            elif (result.group(1).lower() == "5x5x5"):
                events.append("5x5")
            elif (result.group(1).lower() == "6x6x6"):
                events.append("6x6")
            elif (result.group(1).lower() == "7x7x7"):
                events.append("7x7")
            elif (result.group(1).lower() == "4x4oh"):
                events.append("4x4 OH")
            elif (result.group(1).lower() == "pyra"):
                events.append("Pyraminx")
            elif (result.group(1).lower() == "blind"):
                events.append("3BLD")
            elif (result.group(1).lower() == "4x4oh"):
                events.append("4x4 OH")
            elif (result.group(1).lower() == "f2l"):
                events.append("F2L")
            elif (result.group(1).lower() == "bld"):
                events.append("3BLD")
            elif (result.group(1).lower() == "pll time attack"):
                events.append("PLL Time Attack")
            elif (result.group(1).lower() == "3x3 mirror blocks/bump"):
                events.append("3x3 Mirror Blocks/Bump")
            elif (result.group(1).lower() == "3x3 mirror blocks"):
                events.append("3x3 Mirror Blocks/Bump")
            elif (result.group(1).lower() == "mirror blocks/bump"):
                events.append("3x3 Mirror Blocks/Bump")
            elif (result.group(1).lower() == "3x3 with feet"):
                events.append("3x3 With Feet")
            elif (result.group(1).lower() == "3x3 oh"):
                events.append("3x3OH")
            elif (result.group(1).lower() == "oll"):
                events.append("OH OLL")
            else:
                events.append(result.group(1))
                
            average = result.group(2)   #The second group was average.
            if (":" in average):
                try:
                    mins = (int)(average[0: average.index(":")])
                    secs = (int)(average[average.index(":") + 1: average.index(".")])
                    dec = (int)(average[average.index(".") + 1: average.index(".") + 3])

                    secs += mins * 60
                    if (dec < 10):
                        average = str(secs) + ".0" + str(dec)
                    else:
                        average = str(secs) + "." + str(dec)
                except ValueError:
                    average = "Error"

            try:
                float(re.sub('[* ()=/]', '', average).strip())
                times.append(re.sub('[* ()=/]', '', average).strip())
            except:
                times.append("Error")

        elif dnf_result != None:
            # We have a puzzle name, but no average.
            name = dnf_result.group(1)
            events.append(dnf_result.group(1))
            times.append("Error")

        else:
            #If a line didn't match any of the two rules, skip it.
            continue
    return [times, events, raw_times]