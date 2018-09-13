from pyTwistyScrambler import scrambler333, scrambler222, scrambler444, scrambler555, scrambler666, scrambler777, squareOneScrambler, megaminxScrambler, pyraminxScrambler, cuboidsScrambler, skewbScrambler, bigCubesScrambler, clockScrambler
import praw
import datetime
import re
import time
import pickle


def generate_post(r, data, today):

    comp_num = data[3]
    events = ["2x2", "3x3", "4x4", "3BLD", "Square-1", "Clock", "3x3OH", "Pyraminx", "Skewb", "2GEN", "LSE", "COLL"]
    weeklyRotation = ["5x5", "7x7", "Megaminx"]
    bonusEvents = ["3x3 Mirror Blocks/Bump", "F2L", "6x6", "Kilominx", "4x4 OH", "3x3x4", "3x3x5", "Void Cube",
                   "2-3-4 Relay", "FMC", "3x3 With Feet", "3x3x2", "3x3 Relay of 3", "PLL Time Attack"]
    OLLNum = data[4]
    compNum = data[3]

    cycleEvents = data[0:3]
    due_date = today + datetime.timedelta(days = 7)

    post = "Hello, and welcome to the /r/cubers weekly competitions! If you're new, please read the entire post before competing!  This is competition "+ str(comp_num)+ ", and will go until " + due_date.ctime() + "\n\n"
    post += "For help with formatting you can try out [this tool](https://gmct.github.io/) I made. Simply select events which you're looking to compete in and then enter your times. It'll compute your averages for you and return a properly formatted comment. It's likely to have many bugs since I just hacked it together in a night and haven't touched it too much since.\n\n"
    post += "There’s a rotation of 3 events to be held once a month: 5x5, 7x7, and Megaminx. You can also request an event to be done! If you want an event in an upcoming competition, either message me or comment on the results post. One event will be done per week. You must be able to do the event you're requesting.\n\n"

    post += "To compete:\n\n"
    post += "> 1. Scramble your cube, in the event that you are doing, with the scrambles provided. For OLL do the alg 5 times.\n\n"
    post += "> 1. Using a timer, such as [cstimer](http://cstimer.net/timer.php) or [qqtimer](http://www.qqtimer.net/), time your 5 solves and record the results. You are given up to 15 seconds to inspect the cube for each event.\n\n"
    post += "> 1. Post your results down below in a format such as this\n\n"
    post += "    **10x10: 0.41** = 0.37, 0.62, 0.23, (0.07), (1.13)\n\n"
    post += "> 1. Common mistakes with formatting include adding a space at the beginning of a line, not writing event names as they appear in the post, and bolding event name and average separately. Try to avoid these mistakes.\n\n"
    post += "> 1. Competition results are taken by 10 PM EDT on Sunday nights, so make sure to submit times by then!\n\n"

    post += "**Weekly Events:**\n\n"
    for item in events:
        post += "> * " + item + "\n\n"

    post += "**Weekly Rotation:** (one of these events will be used)\n\n"
    for item in weeklyRotation:
        if item in cycleEvents:
            post += "> * **!" + item + "!**\n\n"
        else:
            post += "> * " + item + "\n\n"

    post += "**This Week's Bonus Events:**\n\n"
    for i in range(1, 3):
        post += "> * " + cycleEvents[i] + "\n\n"

    post += "**In Queue:**\n\n"

    for i in range(bonusEvents.index(cycleEvents[2])+1, len(bonusEvents)):
        post += "> * " + bonusEvents[i] + "\n\n"
    for i in range(0, bonusEvents.index(cycleEvents[1])):
        post += "> * " + bonusEvents[i] + "\n\n"

    post += "Anyway, good luck to all those competing, especially those with upcoming WCA competitions!\n\n"
    post += "**2x2:**\n\n"
    for i in range(5):
        post += "> 1. " + scrambler222.get_WCA_scramble() + "\n\n"

    post += "**3x3:**\n\n"
    for i in range(5):
        post += "> 1. " + scrambler333.get_WCA_scramble() + "\n\n"

    post += "**4x4:**\n\n"
    for i in range(5):
        post += "> 1. " + scrambler444.get_WCA_scramble() + "\n\n"

    post += "**3x3OH:**\n\n"
    for i in range(5):
        post += "> 1. " + scrambler333.get_WCA_scramble() + "\n\n"

    post += "**Pyraminx:**\n\n"
    for i in range(5):
        post += "> 1. " + pyraminxScrambler.get_WCA_scramble() + "\n\n"

    post += "**Skewb:**\n\n"
    for i in range(5):
        post += "> 1. " + skewbScrambler.get_WCA_scramble() + "\n\n"

    post += "**3BLD:**\n\n"
    for i in range(3):
        post += "> 1. " + scrambler333.get_3BLD_scramble() + "\n\n"

    post += "**Square-1:**\n\n"
    for i in range(5):
        post += "> 1. " + squareOneScrambler.get_WCA_scramble() + "\n\n"

    post += "**Clock:**\n\n"
    for i in range(5):
        post += "> 1. " + clockScrambler.get_WCA_scramble() + "\n\n"

    for event in cycleEvents:
        post += "**" + event + ":**\n\n"
        if event == "5x5":
            for i in range(5):
                post += "> 1. " + scrambler555.get_WCA_scramble() + "\n\n"
        elif event == "3x3 Mirror Blocks/Bump":
            for i in range(5):
                post += "> 1. " + scrambler333.get_WCA_scramble() + "\n\n"
        elif event == "F2L":
            for i in range(5):
                post += "> 1. " + scrambler333.get_WCA_scramble() + "\n\n"
        elif event == "6x6":
            for i in range(3):
                post += "> 1. " + scrambler666.get_WCA_scramble() + "\n\n"
        elif event == "4x4 OH":
            for i in range(5):
                post += "> 1. " + scrambler444.get_WCA_scramble() + "\n\n"
        elif event == "7x7":
            for i in range(3):
                post += "> 1. " + scrambler777.get_WCA_scramble() + "\n\n"
        elif event == "3x3x4":
            for i in range(5):
                post += "> 1. " +cuboidsScrambler.get_3x3x4_scramble() + "\n\n"
        elif event == "3x3x5":
            for i in range(5):
                post += "> 1. " + cuboidsScrambler.get_3x3x5_scramble() + "\n\n"
        elif event == "Void Cube":
            for i in range(5):
                post += "> 1. " + scrambler333.get_WCA_scramble() + "\n\n"
        elif event == "2-3-4 Relay":
            post += "> 1. " + scrambler222.get_WCA_scramble() + "\n\n"
            post += "> 1. " + scrambler333.get_WCA_scramble() + "\n\n"
            post += "> 1. " + scrambler444.get_WCA_scramble() + "\n\n"
        elif event == "FMC":
            for i in range(3):
                post += "> 1. " + scrambler333.get_WCA_scramble() + "\n\n"
        elif event == "3x3 With Feet":
            for i in range(5):
                post += "> 1. " + scrambler333.get_WCA_scramble() + "\n\n"
        elif event == "3x3x2":
            for i in range(5):
                post += "> 1. " + cuboidsScrambler.get_3x3x2_scramble() + "\n\n"
        elif event == "Megaminx":
            for i in range(5):
                post += "> 1. " + megaminxScrambler.get_WCA_scramble() + "\n\n"
        elif event == "Kilominx":
            for i in range(5):
                post += "> 1. " + megaminxScrambler.get_WCA_scramble() + "\n\n"
        elif event == "3x3 Relay of 3":
            for i in range(3):
                post += "> 1. " + scrambler333.get_WCA_scramble() + "\n\n"
            continue

    post += "**2GEN:** (in this mode of solving, you can only do <R, U>, which has the moves R, R', R2, U, U', U2)\n\n"
    for i in range(5):
        post += "> 1. " + scrambler333.get_2genRU_scramble() + "\n\n"
    post += "**LSE:** (in this mode of solving, you can only do <M, U>, which has the moves M, M', M2, U, U', U2)\n\n"
    for i in range(5):
        post += "> 1. " + scrambler333.get_2genMU_scramble                         () + "\n\n"
    post += "**COLL:** this week we're doing [COLL E" + str(OLLNum) + "](http://algdb.net/puzzle/333/coll/e" + str(OLLNum) + ")"
    print(post)
    newComp = r.subreddit('cubers').submit(title="Cubing Competition " + str(data[3]) + "!", selftext=post, send_replies=False)
    data[7] = data[5]
    data[5] = newComp.id