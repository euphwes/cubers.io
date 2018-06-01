import unittest
from app.util import reddit_util

class TestParseMethods(unittest.TestCase):
        def test_get_comments(self):
            comments = reddit_util.get_root_comments("8n1cs0")
            print(comments)
            self.assertTrue(len(comments) > 0)
            self.assertFalse(len(comments) == 0)

#results = reddit_util.parse_comment(comment)

#for event, o in results.items():
    #print(event)
    #print("--- average: ", o["average"])
    #print("--- times: ", o["times"], "\n")
comment = '''**2x2: 6.20** = 7.11, 5.68, (5.09), (10.53), 5.82 ouch ouhawdu hiua wd
>ouch

**3x3: 15.36** = 16.56, (12.29), (17.93), 14.89, 14.65 oiajwodij oaij 16.56 aoijwd joaj

**3x3OH: 32.34** = (52.53), 31.67, 32.56, 32.79, (31.56)
>can you guess which solve I tried using ZZ on?

**Pyraminx: 9.67** = (11.43), (9.05), 10.45, 9.50, 9.07
>i hate this event

**Skewb: 9.15** = 9.40, 8.94, (10.15), 9.11, (7.30)

**3BLD: 3:09.141** = DNF, 3:12.351, 3:09.141, DNF oaijwodj oawjdo ij DNF 1209.0
>Wtf those two successes were both PB singles. My PB before this was 4:15'''

if __name__ == "__main__":
    unittest.main()