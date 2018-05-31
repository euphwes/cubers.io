EVENT_NAMES = {
    "5x5": "5x5x5",
    "6x6": "6x6x6",
    "7x7": "7x7x7",
    "3x3 relay": "3x3 Relay of 3",
    "relay of 3": "3x3 Relay of 3",
    "4x4oh": "4x4 OH",
    "pyra": "Pyraminx",
    "blind": "3BLD",
    "f2l": "F2L",
    "bld": "3BLD",
    "pll time attack": "PLL Time Attack",
    "3x3 with feet": "3x3 With Feet",
    "3x3 oh": "3x3OH",
    "oll": "OH OLL",
    "mirror blocks": "3x3 Mirror Blocks/Bump",
    "3x3 mirror blocks/bump": "3x3 Mirror Blocks/Bump",
    "3x3 mirror blocks": "3x3 Mirror Blocks/Bump",
    "mirror blocks/bump": "3x3 Mirror Blocks/Bump"
}

def get_event_name(name):
    if name.lower() in EVENT_NAMES:
        return EVENT_NAMES[name]
    else:
        return name