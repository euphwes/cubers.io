import praw
import pickle
import score
import post_gen
#import oauth_data
import datetime

today = datetime.datetime.now()
# user_agent = 'CubeComps by /u/rhandyrhoads'
# r = praw.Reddit(user_agent=user_agent)
# scopes = ['identity', 'read', 'submit', 'edit', 'modconfig', 'modposts']
#This calls PrawOauth2Mini. The call is in a separate file which I didn't include because it includes the secret key.)
# oauth_helper = oauth_data.get_oauth(r, scopes)
# oauth_helper.refresh()
#r = oauth_data.get_oauth()

weeklyRotation = ["5x5", "7x7", "Megaminx"]
bonusEvents = ["3x3 Mirror Blocks/Bump", "F2L", "6x6", "Kilominx", "4x4 OH", "3x3x4", "3x3x5", "Void Cube",
                   "2-3-4 Relay", "FMC", "3x3 With Feet", "3x3x2", "3x3 Relay of 3", "PLL Time Attack"]
rerun = False
with open("scores.dat", "rb") as f:
    #cycleEvents index Arrays: [weeklyRotation event, bonusEvent1, bonusEvent2, currentCompetition number, algNumber,
    # current Post ID, current Results ID, previous post ID
    cycleEvents = pickle.load(f)

import json
from pprint import pprint
pprint(json.dumps(cycleEvents))

import sys
sys.exit(0)

if rerun:
    cycleEvents[0] = weeklyRotation[(weeklyRotation.index(cycleEvents[0]) + len(weeklyRotation) -1) % len(weeklyRotation)]
    cycleEvents[1] = bonusEvents[(bonusEvents.index(cycleEvents[1]) +len(bonusEvents) -1) % len(bonusEvents)]
    cycleEvents[2] = bonusEvents[(bonusEvents.index(cycleEvents[1]) +len(bonusEvents) - 1) % len(bonusEvents)]
    cycleEvents[3] -= 1
    cycleEvents[4] -= 1
    score.score_post(r, r.submission(id=cycleEvents[7]), cycleEvents, rerun)
if not rerun:
    oldResults = cycleEvents[6]
    score.score_post(r, r.submission(id=cycleEvents[5]), cycleEvents, rerun)

    cycleEvents[0] = weeklyRotation[(weeklyRotation.index(cycleEvents[0]) + 1) % len(weeklyRotation)]
    cycleEvents[1] = bonusEvents[(bonusEvents.index(cycleEvents[1]) +2) % len(bonusEvents)]
    cycleEvents[2] = bonusEvents[(bonusEvents.index(cycleEvents[1]) + 1) % len(bonusEvents)]
    cycleEvents[3] += 1
    cycleEvents[4] += 1


    post_gen.generate_post(r, cycleEvents, today)

    sub = r.subreddit('cubers')
    mod = sub.mod
    settings = mod.settings()
    sidebar = settings['description']
    newSidebar = sidebar.replace(('[Competition ' + str((cycleEvents[3] - 1)) + ']'), ('[Competition ' + str(cycleEvents[3]) + ']'))
    newSidebar = newSidebar.replace(cycleEvents[7], cycleEvents[5])
    newSidebar = newSidebar.replace('Competition ' + str((cycleEvents[3] -2)) + ' Results]', 'Competition ' + str((cycleEvents[3]) -1) + ' Results]')
    newSidebar = newSidebar.replace(oldResults, cycleEvents[6])

    mod.update(description=newSidebar)
    newComp = r.submission(id=cycleEvents[5])
    oldComp = r.submission(id=cycleEvents[7])
    if(oldComp.stickied):
        oldComp.mod.sticky(state=False)
        newComp.mod.sticky(state=True)


    with open("scores.dat", 'wb') as f:
        pickle.dump(cycleEvents, f)
