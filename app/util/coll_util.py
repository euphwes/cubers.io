""" Utilities for providing COLL scrambles to setup the COLL case. """

from random import choice

# -------------------------------------------------------------------------------------------------

def get_coll_scramble(coll):
    """ Returns a random COLL "setup scramble" for the given COLL case. """

    url = "http://algdb.net/puzzle/333/coll/{}".format(coll.lower())
    href_tag = '<a href="{}" target="_blank">COLL {}</a>'.format(url, coll)

    message_components = [
        "This week we're doing COLL {}.".format(href_tag),
        "Perform the algorithm below to setup the case.",
        __inverse_scramble(choice(__COLL_EXEC_ALGS[coll]))
    ]

    return '<br/>'.join(message_components)


def __scramble(coll):
    """ Returns a random COLL "setup scramble" for the given COLL case. """
    setup = __inverse_scramble(choice(__COLL_EXEC_ALGS[coll]))
    return setup

# -------------------------------------------------------------------------------------------------

# lol - got this Rubik's Cube alg inversing function from a code-golf stackexchange post:
# https://codegolf.stackexchange.com/a/130196
# pylint: disable=C0103
__inverse_scramble = lambda s:' '.join(i.strip("'")+"'"*(len(i)<2)for i in s.split()[::-1])

# These are all algs to execute the COLL case they are associated with, sourced from
# http://algdb.net/puzzle/333/coll
# As these algs are to solve the given COLL, they will need to be inversed to become "setup" algs
__COLL_EXEC_ALGS = {
    'B1': [
        "R' U' R U' R' U2 R",
        "y R U2 R' U' R U' R ",
        "y2 L' U' L U' L' U2 L",
        "y' L U2 L' U' L U' L'"
    ],
    'B2': [
        "y R' U' R U' R' U R' D' R U R' D R2",
        "y' L' U' L U' L' U L' D' L U L' D L2",
        "y2 R' U2 F' R U R' U' R' F R2 U R' U R",
        "y2 R2 D R' U R D' R' U R' U' R U' R'"
    ],
    'B3': [
        "L R' U' R U L' U2 R' U2 R",
        "y2 R L' U' L U R' U2 L' U2 L",
        "R U R' F' R U2 R' U2 R' F R2 U' R'",
        "y2 R2 D R' U2 R D' R2 U' R U' R'"
    ],
    'B4': [
        "R' U' R U R' F R U R' U' R' F' R2",
        "y2 R U2 R' U2 L' U R U' R' L",
        "y2 R' U' R U' R2 D' R U2 R' D R2",
        "y2 M R U2 R' U2 R' F R F' M'"
    ],
    'B5': [
        "R' U L U' R U L'",
        "y2 L' U R U' L U R'",
        "y2 r' F R F' r U R'"
    ],
    'B6': [
        "R U' R' U2 R U' R' U2 R' D' R U R' D R",
        "R U R' F' R U2 R' U' R U' R' F R U' R'",
        "R' U' R U' L U' R' U L' U2 R",
        "y2 L' U' L U' R U' L' U R' U2 L"
    ],

    'C1': [
        "R U R' U R U2 R'",
        "y2 L U L' U L U2 L'",
        "y' R' U2 R U R' U R",
        "y L' U2 L U L' U L"
    ],
    'C2': [
        "L' U2 L U2 R U' L' U L R'",
        "y2 R U R' U R2 D R' U2 R D' R2",
        "L' U2 L U2 l F' L' F M'",
        "y2 R' U2 R U2 L U' R' U L' R"
    ],
    'C3': [
        "L' R U R' U' L U2 R U2 R'",
        "F R' U' R2 U' R2 U2 R2 U' R' F'",
        "y2 R2 D' R U2 R' D R2 U R' U R",
        "y B' U' R U R' B U R U2 R'"
    ],
    'C4': [
        "y' R U R' U R U' R D R' U' R D' R2",
        "y R' U' R U' R2 F' R U R U' R' F U2 R",
        "y' F R' U2 R F' R' F U2 F' R",
        "y2 R2 D' R U' R' D R U' R U R' U R"
    ],
    'C5': [
        "R U' L' U R' U' L",
        "z D R' U' R D' R' U R z'",
        "y2 L U' R' U L' U' R",
        "y' M' U R U' r' F R' F' R"
    ],
    'C6': [
        "F' R U2 R' U2 R' F2 R U R U' R' F'",
        "F R U' R2 U2 R U R' U R2 U R' F'",
        "y2 R U R' F' R U R' U R U2 R' F R U' R'",
        "R' U2 L U' R U L' U R' U R"
    ],

    'D1': [
        "y' R U2 R' U' R U R' U' R U R' U' R U' R'",
        "y2 R' U' R U' R' U R U' R' U R U' R' U2 R",
        "y' R U R' U R U' R' U R U' R' U R U2 R'",
        "R' U' R U' R' U2 R U' R U R' U R U2 R'"
    ],
    'D2': [
        "R' U2 R' D' R U2 R' D R2",
        "y2 L' U2 L' D' L U2 L' D L2",
        "y' r D r' U r D' r' U y R U2 R'",
        "R U R' U2 L U' R U L' U R'"
    ],
    'D3': [
        "y R U2 R D R' U2 R D' R2",
        "R' F' R U R' U' R' F R2 U' R' U2 R",
        "y' L U2 L D L' U2 L D' L2",
        "y' x' R U R' D R U2 R' D' R U R' x"
    ],
    'D4': [
        "x' R U' R' D R U R' D' x",
        "y F R' F' r U R U' r'",
        "y' l' U' L' U R U' L U x'",
        "y F l' U' L U l F' L'"
    ],
    'D5': [
        "y2 F' r U R' U' r' F R",
        "y' F R U' R' U' R U2 R' U' F'",
        "y x R' U R D' R' U' R D x'",
        "y2 r U R U' r' F R' F'"
    ],
    'D6': [
        "y' R' U' R U R' F' R U R' U' R' F R2",
        "y r U2 R2 F R F' R U2 r'",
        "F R U R' U' R U' R' U2 R U2 R' U' F'",
        "R2 F' R U R U' R' F R U' R' U R"
    ],

    'E1': [
        "R' U' R U' R' U2 R2 U R' U R U2 R'",
        "y' R U R' U' R U' R' U2 R U' R' U2 R U R'",
        "y2 R U R' U R U2 R2 U' R U' R' U2 R",
        "y2 R U R' U R U2 R' U R U2 R' U' R U' R'"
    ],
    'E2': [],
    'E3': [],
    'E4': [],
    'E5': [],
    'E6': [],

    'F1': [],
    'F2': [],
    'F3': [],
    'F4': [],
    'F5': [],
    'F6': [],

    'G1': [],
    'G2': [],
    'G3': [],
    'G4': [],
    'G5': [],
    'G6': [],

    'H1': [],
    'H2': [],
    'H3': [],
    'H4': []
}
