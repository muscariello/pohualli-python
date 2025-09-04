from pohualli import zodiac_name_to_index


def test_zodiac_heuristics_all_letters():
    # cover branches in heuristic mapping
    assert zodiac_name_to_index('Ar') == 0  # Aries
    assert zodiac_name_to_index('Aq') == 10  # Aquarius
    assert zodiac_name_to_index('Tau') == 1
    assert zodiac_name_to_index('Gem') == 2
    assert zodiac_name_to_index('Cnc') == 3
    assert zodiac_name_to_index('Cap') == 9
    assert zodiac_name_to_index('Leo') == 4
    assert zodiac_name_to_index('Lib') == 6
    assert zodiac_name_to_index('Vir') == 5
    assert zodiac_name_to_index('Sco') == 7
    assert zodiac_name_to_index('Sag') == 8
    assert zodiac_name_to_index('Psc') == 11
    assert zodiac_name_to_index('') == 255
    assert zodiac_name_to_index('Xyz') == 255
