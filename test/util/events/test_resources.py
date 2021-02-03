from unittest import TestCase

from app.util.events.resources import mbld_scrambler

# -------------------------------------------------------------------------------------------------

class InternalScramblersTest(TestCase):

    def test_mbld_scrambler(self):
        assert type(mbld_scrambler()) == str
