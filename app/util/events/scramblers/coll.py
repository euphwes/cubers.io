""" Utilities for providing COLL "scrambles" which setup the desired COLL case. """

from random import choice


def get_coll_scramble(coll: str) -> str:
    """ Returns a random COLL "setup scramble" for the given COLL case. This includes links to speedsolving wiki to
     explain what COLL is, as well as a link to algdb.net for the specific COLL case. """

    url = "http://algdb.net/puzzle/333/coll/{}".format(coll.lower())
    href_tag = '<a href="{}" target="_blank">COLL {}</a>'.format(url, coll)
    coll_wiki_link = '<a href="https://www.speedsolving.com/wiki/index.php/COLL" target="_blank">'\
                     '<span class="far fa-question-circle"></span></a>'

    message_components = [
        "This week we're doing {} {}".format(href_tag, coll_wiki_link),
        "Perform the algorithm below to setup the case.",
        __build_scramble(coll)
    ]

    return '<br/>'.join(message_components)


def __build_scramble(coll):
    """ Returns a random COLL "setup scramble" for the given COLL case, with a random EPLL at the beginning or end,
    since that doesn't matter for the COLL itself and it will help to train recognition of the case. """

    setup = __inverse_scramble(choice(__COLL_EXEC_ALGS[coll])).strip()
    epll  = choice(__EPLLS).strip()
    return setup + " " + epll if choice([True, False]) else epll + " " + setup


def __inverse_scramble(s):
    """ Inverses a scramble. From this code-golf StackExchange post: https://codegolf.stackexchange.com/a/130196 """
    return ' '.join(i.strip("'") + "'" * (len(i) < 2) for i in s.split()[::-1])


# These all algs to execute the COLL case they are associated with, sourced from http://algdb.net/puzzle/333/coll.
# As these algs are to solve the given COLL, they will need to be inversed to become "setup" algs.
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
    'E2': [
        "R' F R U' R' U' R U R' F' R U R' U' R' F R F' R",
        "R2 F' R U R2 U' R' F R U' R2 U R2 U R'",
        "y' R' U' R F R2 D' R U R' D R2 U' F'",
        "y' L' U L U' F R' F R F2 L F' L' F"
    ],
    'E3': [
        "y2 R2 D R' U2 R D' R' U2 R'",
        "x' R U' R' D R U2 R' D' R U' R' x",
        "R' U L' U R U' L U2 R' U R",
        "R' U' R U' R' U2 R2 U' L' U R' U' L"
    ],
    'E4': [
        "F R U' R' U R U R' U R U' R' F'",
        "y2 R' F2 R U2 R U2 R' F2 R U2 R'",
        "x' R2 D2 R' U2 R D2 R' U2 R'",
        "y R U R2 U' R' F R U R2 U' R' F'"
    ],
    'E5': [
        "R2 D' R U2 R' D R U2 R",
        "y2 L2 D' L U2 L' D L U2 L",
        "L U' R U' L' U R' U2 L U' L'",
        "y2 x R' U R D' R' U2 R D R' U R x'"
    ],
    'E6': [
        "R' U2 R F U' R' U' R U F'",
        "R2 D' R U R' D R U R U' R' U' R",
        "R' U2 R U2 R' F' R U R' U' R' F R2",
        "R U' R' U' R U R D R' U R D' R2"
    ],

    'F1': [
        "R U2 R' U' R U' R2 U2 R U R' U R",
        "y' R U R' U R U2 R' U' R U2 R' U' R U' R'",
        "R U2 R' U' R U' R' U R U R' U R U2 R'",
        "y L' U' L U' L' U2 L R U R' U R U2 R'"
    ],
    'F2': [
        "R' U R U2 R' L' U R U' L",
        "y2 R' F R U R' U' R' F' R2 U' R' U2 R",
        "y2 R U' R' U2 L R U' R' U L'",
        "R' U2 R U R2 F R U R U' R' F' R"
    ],
    'F3': [
        "y l' U' L U R U' r' F",
        "y2 x' R U R' D R U' R' D' x",
        "y' F R F' r U R' U' r'",
        "y R' F' r U R U' r' F"
    ],
    'F4': [
        "y2 F R U R' U' R U' R' U' R U R' F'",
        "y' x' R U2 R D2 R' U2 R D2 R2 x",
        "y R U2 R' F2 R U2 R' U2 R' F2 R",
        "F U' L' U R2 U' L U R2 F'"
    ],
    'F5': [
        "y' r U R' U' r' F R F'",
        "R U R D R' U' R D' R2",
        "R' F' R U R' U' R' F R U R",
        "y' R U R' U' L' U R U' R' L"
    ],
    'F6': [
        "R' U R2 D r' U2 r D' R2 U' R",
        "y2 R U' R2 D' r U2 r' D R2 U R'",
        "y2 R' U' R U' R' U R U R' F' R U R' U' R' F R2",
        "R' U' R U R2 D' R U2 R' D R2 U' R' U R"
    ],

    'G1': [
        "R U2 R2 U' R2 U' R2 U2 R",
        "f R U R' U' f' F R U R' U' F'",
        "R' U2 R2 U R2 U R2 U2 R'",
        "y2 L' U2 L2 U L2 U L2 U2 L'"
    ],
    'G2': [
        "R' F2 R U2 R U2 R' F2 U' R U' R'",
        "y F U R U' R' U R U' R2 F' R U R U' R'",
        "R' U2 R U R' U' R U2 L U' R' U R L'",
        "y2 L' U' L U L F' L2 U' L U L' U' L U F"
    ],
    'G3': [
        "R' U' F' R U R' U' R' F R2 U2 R' U2 R",
        "y F U R U' R' U R U2 R' U' R U R' F'",
        "R U2 R' U L' U2 R U R' U' R U' R' L",
        "y' B' R2 U R2 U' R2 U' S R2 F z'"
    ],
    'G4': [
        "R U R' U' R' F R2 U R' U' R U R' U' F'",
        "y' R' U2 R U R' U R2 U' L' U R' U' L",
        "R U R' U R U2 R' U' R U' L' U R' U' L",
        "R U2 R' U' R U R' U2 r' F R F' M'"
    ],
    'G5': [
        "R U' L' U R' U L U L' U L",
        "y' R U R' U F' R U2 R' U2 R' F R",
        "r U' r' U' r U r' U' x' R2 U' R' U R' x",
        "y2 L' U R U' L U' R' U' R U' R'"
    ],
    'G6': [
        "R U D' R U R' D R2 U' R' U' R2 U2 R",
        "F R2 U' R U' R U' R' U2 R' U R2 F'",
        "R2 D' R U R' D R U R U' R' U R U R' U R",
        "y R U2 R' U' F' R U2 R' U' R U' R' F R U' R'"
    ],

    'H1': [
        "R U R' U R U' R' U R U2 R'",
        "y' R U2 R' U' R U R' U' R U' R'",
        "R' U' R U' R' U R U' R' U2 R",
        "L U L' U L U' L' U L U2 L'"
    ],
    'H2': [
        "F R U' R' U R U2 R' U' R U R' U' F'",
        "L' U R U' L U' R' U2 r' F R F' M'",
        "f R2 S' U' R2 U' R2 U R2 F'",
        "R L' U' L U' L' U L U2 R' U L' U2 L"
    ],
    'H3': [
        "R U R' U R U L' U R' U' L",
        "R' F' R U2 R U2 R' F U' R U' R'",
        "R U R' U R U r' F R' F' r",
        "R' U' R U' R' U' L U' R U L'"
    ],
    'H4': [
        "y F R U R' U' R U R' U' R U R' U' F'",
        "y F U R U' R' U R U' R' U R U' R' F'",
        "y R U R' U y' R' U R U' R2 F R F' R",
        "y R' U' R' F R F' R' F R F' R' F R F' U R"
    ]
}

__EPLLS = [
    # Nothing
    "",

    # H perms
    "M2 U M2 U2 M2 U M2",
    "M2 U' M2 U2 M2 U' M2",
    "R2 U2 R U2 R2 U2 R2 U2 R U2 R2",
    "M2 U' M2 U2 M2 U' M2",

    # Ua perms
    "y2 R U' R U R U R U' R' U' R2",
    "R2 U' R' U' R U R U R U' R",
    "y2 M2 U M U2 M' U M2",
    "M2 U M' U2 M U M2",

    # Ub perms
    "y2 R2 U R U R' U' R' U' R' U R'",
    "R' U R' U' R' U' R' U R U R2",
    "y2 M2 U' M U2 M' U' M2",
    "M2 U' M' U2 M U' M2",

    # Z perms
    "M2 U M2 U M' U2 M2 U2 M'",
    "y M2 U' M2 U' M' U2 M2 U2 M'",
    "M' U' M2 U' M2 U' M' U2 M2",
    "R' U' R2 U R U R' U' R U R U' R U' R'"
]
