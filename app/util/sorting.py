""" Utilities for sorting collections of various types of objects. """

# -------------------------------------------------------------------------------------------------

def cmp_to_key(mycmp):
    """ Converts a cmp= function into a key= function. This facilitates writing comparator functions
    for custom sorting of objects based on their attributes. """

    class Comparator:
        """ A wrapper around the custom comparator function which turns it into a Comparator object,
        which is suitable as the `key` argument for Python's `sort` from the stdlib. """

        def __init__(self, obj):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0

    return Comparator


def cmp_to_key_wrapped(func):
    """ A decorator for cleanly wrapping a comparator function in `cmp_to_key`. """

    return cmp_to_key(func)

# -------------------------------------------------------------------------------------------------

@cmp_to_key_wrapped
def sort_user_event_results(val1, val2):
    """ Compares two UserEventResults based on their `result` field. Lack of a result
    to be sorted to the end, DNFs right before that, then compare time values directly. """

    result1 = val1.result
    result2 = val2.result
    if not result1:
        result1 = 100000000
    if not result2:
        result2 = 100000000
    if result1 == 'DNF':
        result1 = 99999999
    if result2 == 'DNF':
        result2 = 99999999
    return int(result1) - int(result2)


@cmp_to_key_wrapped
def sort_personal_best_records(pb1, pb2):
    """ Compares two PersonalBestRecords based on their `personal_best` field. Lack of a result
    to be sorted to the end, DNFs right before that, then compare time values directly. """

    val1 = pb1.personal_best
    val2 = pb2.personal_best
    if not val1:
        val1 = 100000000
    if not val2:
        val2 = 100000000
    if val1 == 'DNF':
        val1 = 99999999
    if val2 == 'DNF':
        val2 = 99999999
    return int(val1) - int(val2)
