""" Tests for COLL-related scrambles and utility functions. """

from app.util.events.scramblers.coll import get_coll_scramble

__COLL_NAME = "E1"
__COLL_RAW_SCRAMBLE = "R' U' R U' R' U2 R2 U R' U R U2 R'"


def test_get_coll_scramble_uses_generated_scramble(mocker):
    """ Tests that get_coll_scramble calls __build_scramble internally and that value is used. """

    mocked_build_scramble = mocker.patch('app.util.events.scramblers.coll.__build_scramble')
    mocked_build_scramble.return_value = __COLL_RAW_SCRAMBLE

    assert __COLL_RAW_SCRAMBLE in get_coll_scramble(__COLL_NAME)
    assert mocked_build_scramble.called_once_with(__COLL_NAME)


def test_get_coll_scramble_has_links():
    """ Tests that the scramble from get_coll_scramble contains the expected speedsolving wiki and algdb.net links. """

    scramble = get_coll_scramble(__COLL_NAME)
    assert 'http://algdb.net/puzzle/333/coll' in scramble
    assert 'https://www.speedsolving.com/wiki/index.php/COLL' in scramble
