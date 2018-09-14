import re
import datetime



# 4db8z3, 4c819g, 4ba17z, 4fkgyz, 4hd2rg

events = ["2x2", "3x3", "4x4", "3BLD", "Square-1", "Clock", "3x3OH", "Pyraminx", "Skewb", "2GEN", "LSE", "COLL"]


#submission = r.get_submission(submission_id='58as92')

# def get_post(r, compNumber):
#     compGen = r.subreddit('cubers').search('Cubing Competition ' + str(compNumber) + "!", 'relevance')
#     return next(compGen)

def score_post(r, submission, data, rerun):
    events.extend(data[0:3])
    competitors = []

    competition_entries = submission.comments

    blacklist = ["CaptainCockmunch", "LorettAttran", "purplepinapples", "CuberSaiklick", "xXxSteelVenomxXx"]

    for entry in competition_entries:
        if not(entry.author is None):
            if ((len(find_events(entry))>0) & ("NOT DONE" not in entry.body) & ("WIP" not in entry.body) & ("#FORMATTINGADVICE" not in entry.body) & (not(entry.author is None)) &(entry.author.name not in blacklist)):
                if not rerun:
                    competitors.append(Competitor(entry))
                else:
                    commenttime = datetime.datetime.fromtimestamp(entry.created)
                    posttime = datetime.datetime.fromtimestamp(submission.created)
                    if (commenttime <= posttime + datetime.timedelta(days = 7)):
                        competitors.append(Competitor(entry))
    '''
    for competitor in competitors:
        competitor.fix_times()
        print(competitor)
        print()
    '''
    for competitor in competitors:
        competitor.fix_times()
        if len(competitor.get_events()) == 0:
            competitors.remove(competitor)
    checkedCompetitors = []
    for competitor in competitors:
        if competitor in checkedCompetitors:
            competitors.remove(competitor)
        checkedCompetitors.append(competitor)


    # Submission code comment out whichever one you want.
    if (rerun == False):
        newResults = r.subreddit('cubers').submit(title="Results for " + submission.title, selftext="Message me if you were not included in these results. \n\n" + sort(competitors, submission))
        data[6] = newResults.id
    else:
        results = r.submission(id=data[6])
        results.edit("EDIT: Performed rerun.\n\n" + sort(competitors, submission))


    #compSaveNames = []
    #for competitor in compSave:
        #compSaveNames.append(competitor.get_name())

    #for competitor in competitors:
        #if competitor.get_name() not in compSaveNames:
            #compSave.append(competitor)
            #compSaveNames.append(competitor.get_name)
        #else:
            #compSave[compSaveNames.index(competitor.get_name())].add_points(competitor.get_points())


    #print(score_selection_sort(compSave))


def find_events(comment):

    # , "3x3", "4x4", "3x3OH", "2GEN", "LSE", "OLL"
    myEvents = []

    for a in range(0, len(events)):
        if ((events[a] + ":" in comment.body)):
            myEvents.append(events[a])
    return myEvents

def swap(list, index1, index2):
    temp = list[index1]
    list[index1] = list[index2]
    list[index2] = temp

def selection_sort(list, index):
    minIndex = 0
    newMinFound = False

    for a in range(len(list) - 1):
        minIndex = a
        b = a + 1
        while (b < len(list)):
            minNumber = (float)(list[minIndex].get_times()[list[minIndex].get_events().index(index[minIndex])])
            #print((list[b].get_times()[list[b].get_events().index(index[b])]))
            print(list[b].get_name())
            if ((float)(list[b].get_times()[list[b].get_events().index(index[b])]) < (minNumber)):
                minIndex = b
                newMinFound = True
            b += 1

        if newMinFound:
            swap(list, a, minIndex)
            swap(index, a, minIndex)
            a = 0
        newMinFound = False

def score_selection_sort(list):
    maxIndex = 0
    scores = ""

    for i in range(len(list)):
        maxIndex = i

        for j in range(i+1, len(list)):
            if (list[j].get_points() > list[maxIndex].get_points()):
                maxIndex = j

        temp = list[i]
        list[i] = list[maxIndex]
        list[maxIndex] = temp

        scores += str(i + 1) + ". /u/" + list[i].get_name() + ": " + str(list[i].get_points()) + "\n\n"

    return scores


def sort(competitors, submission):
    full = "Results for " + submission.title
    compCount = 0

    for a in range(len(events)):
        temp = []
        index = []
        place = 1
        compCount = 0
        full += "\n\n" + "**" + events[a] + "**" + "\n\n"
        for competitor in competitors:

            if ((events[a] in competitor.get_events())):
                index.append(events[a])

                temp.append(competitor)
                compCount += 1

            elif (events[a].upper() in competitor.get_events()):
                index.append(events[a].upper())
                temp.append(competitor)

                compCount += 1

            elif (events[a].lower() in competitor.get_events()):
                index.append(events[a].lower())
                temp.append(competitor)

                compCount += 1

        selection_sort(temp, index)

        for b in range(len(temp)):
            if (events[a] != "FMC") & ((float)(temp[b].get_times()[temp[b].get_events().index(index[b])]) >= 60):
                time = temp[b].get_times()[temp[b].get_events().index(index[b])]
                dec = (int)(time[len(time) - 2:])
                secs = (int)(time[0: len(time) - 3])
                mins = secs // 60
                secs %= 60
                # I'm rather sleep-deprived and all I know is that this is going to be a way to shorten the lines of code and I have a bottle of Maru lube by me.
                maru = ""
                if(secs < 10):
                    if (dec < 10):
                        maru = str(mins) + ":0" + str(secs) + ".0" + str(dec)
                    else:
                        maru = str(mins) + ":0" + str(secs) + "." + str(dec)
                else:
                    if (dec < 10):
                        maru = str(mins) + ":" + str(secs) + ".0" + str(dec)
                    else:
                        maru = str(mins) + ":" + str(secs) + "." + str(dec)

                temp[b].get_times()[temp[b].get_events().index(index[b])] = maru

                full += str(place) + ". /u/" + temp[b].get_name() + ": " + (temp[b].get_times()[temp[b].get_events().index(index[b])]) + "\n\n"
            else:
                full += str(place) + ". /u/" + temp[b].get_name() + ": " + (temp[b].get_times()[temp[b].get_events().index(index[b])]) + "\n\n"

            temp[b].add_points(len(temp) - place + 1)
            place += 1
    full += "**Points from this week (participants - place + 1):**\n\n"
    full += score_selection_sort(competitors)

    return full


class Competitor:
    points = 0
    isXP = False

    def __init__(self, entry):
        self.entry = entry
        self.events = parse(entry.body)[1]
        self.numEvents = len(events)
        self.name = entry.author.name
        self.times = parse(entry.body)[0]
        self.score = 0
        self.fix_times()

    def find_averages (self, comment):
        times = []
        pos = 0
        for i in range(0, self.numEvents):
            pos = comment.body.index(self.events[i] + ":")
            times.append(self.find_next_time(comment.body, pos, self.events[i]))
        return times

    def find_next_time(self, s, pos, e):
        time = s[pos + len(e) + 1: s.index(".", pos) + 3].strip()
        time = re.sub('[* ()=/]', '', time)

        if ((":" in time[0: time.index(".") + 3])):
            try:
                mins = (int)(time[0: time.index(":")])
                secs = (int)(time[time.index(":") + 1: time.index(".")])
                dec = (int)(time[time.index(".") + 1: time.index(".") + 3])

                secs += mins * 60
                if (dec < 10):
                    return str(secs) + ".0" + str(dec)
                else:
                    return str(secs) + "." + str(dec)
            except ValueError:
                return "Error"
        else:
            return time[0: time.index(".") + 3]

    def fix_times(self):
        while("Error" in self.times):
            self.events.pop(self.times.index("Error"))
            self.times.pop(self.times.index("Error"))
            self.numEvents -= 1

    def add_points(self, a):
        self.points += a

    def set_points(self, a):
        self.points = a

    def get_points(self):
        return self.points

    def get_name(self):
        return self.name

    def get_events(self):
        return self.events

    def remove_error(self):
        self.events.remove(self.times.index("Error"))
        self.times.remove("Error")
        self.numEvents -= 1

    def get_times(self):
        return self.times

    def get_num_times(self):
        return self.numEvents

    def is_XP(self):
        isXP = True

    def get_is_XP(self):
        return self.isXP

    def __repr__(self):
        return "Username: " + self.name + "\nEvents: " + str(self.events) + "\nTimes: " + str(self.times) + "\nNumber of events: " + str(self.numEvents) + "\nPoints: " + str(self.get_points())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.get_name == other.get_name()
        else:
            return false

    def __ne__(self, other):
        return not self.__eq__(other)

def parse(post):
        # The next source line after this big comment block is creating a regular expression parser.
        # Regular expressions use special letters with certain meanings to create a pattern recognition object.
        # I'm going to break it down like this (just incase you've never seen this)
        # ( )  creates a group, a substring we're looking for. We want 2 groups: the puzzle "name" and the average.

        # Broken down in squence:
        # ^ = "start of a line". So we're saying "From the start of the line  ... "
        # ( = start a group at the first character
        # [^ = match any characters that are not
        # \\: = a colon (slash escaped to prevent python from interpreting it)
        # ] = end of character list
        # + = 1 or more times. Basically take everything before the first colon, but there must be SOMETHING before the colon.
        # ) end the first group. Anything after this is not part of the name anymore.
        # \\s = followed by space ...
        # * = 0 or more times. (allow 0 or more spaces before the colon)
        # \\: = followed by a colon.If the line does not contain a colon this will NOT match that line. It's compulsory for a match.
        # \\s* = followed by 0 or more spaces (allow any amount of spaces before the average)
        # ( = begin the next group (which will be our average)
        # [^ = match any characters that are not
        # \\s = a space
        # ] = end of character list.
        # + = 1 or more times.
        # ) = end of group.
        # . = match any character whatsoever
        # * = as many times as possible. (These last two ensure we "match" a line no matter what comes after the average.)

        # As as long as a line of text "fits" this pattern, we will get a successful match. Otherwise we get 'None'.
        matcher = re.compile('^(.+?)\\:\\s*([^\\s]+).*')
        #matcher = re.compile('^([^\\:\\s]+)\\s*\\:\\s*([^\\s]+).*')
        # Create a second matcher to find "empty" results. ONLY apply it if the first rule didn't match. (see below)
        dnfMatcher = re.compile('^([^\\:\\s]+)\\s*\\:.*')

        times = []
        events = []

        #Split our post into individual lines, and process them
        for line in post.splitlines():
                # Now replace any * characters with nothing.
                content = re.sub ('\\*','',line)

                # Use our matchers to see if the current line matches our pattern(s).
                result = matcher.match (content)
                dnfResult = dnfMatcher.match (content)

                name = ''
                average = ''
                if result != None:
                        # We have gotten a puzzle name and an average.
                        name = result.group (1)      #The first group was name.
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
                        average = result.group (2)   #The second group was average.
                        if (":" in average):
                            try:
                                mins = (int)(average[0: average.index(":")])
                                secs = (int)(average[average.index(":") + 1: average.index(".")])
                                dec = (int)(average[average.index(".") + 1: average.index(".") + 3])

                                secs += mins * 60
                                if (dec < 10):
                                    average = str(secs) + ".0" + str(dec)
                                else:
                                    average =  str(secs) + "." + str(dec)
                            except ValueError:
                                average = "Error"

                        try:
                            float(re.sub('[* ()=/]', '', average).strip())
                            times.append(re.sub('[* ()=/]', '', average).strip())
                        except:
                            times.append("Error")

                elif dnfResult != None:
                        # We have a puzzle name, but no average.
                        name = dnfResult.group (1)
                        average = 'DNF'
                        events.append(dnfResult.group(1))
                        times.append("Error")

                else:
                        #If a line didn't match any of the two rules, skip it.
                        continue
        return [times, events]
#End of method Parse