from pohualli.autocorr import derive_auto_corrections

JDN = 2451545

# Craft a long count pattern that is valid format but unlikely within ±5000 offset
# We'll take the real long count and add a huge number to the baktun so that only
# the widened ±200000 window is attempted then still fails.
# First derive actual long count.
from pohualli import julian_day_to_long_count
_actual = julian_day_to_long_count(JDN)
_impossible = (_actual[0] + 50,) + _actual[1:]
_pattern = '.'.join(str(x) for x in _impossible)


def test_long_count_widening_failure():
    try:
        derive_auto_corrections(JDN, long_count=_pattern)
    except ValueError as e:
        assert 'Unable to match long count' in str(e)
    else:
        raise AssertionError('Expected failure for unreachable long count pattern')


def test_dir_color_unknown_spec():
    try:
        derive_auto_corrections(JDN, dir_color='NoSuchDirColor')
    except ValueError as e:
        assert 'direction/color' in str(e)
    else:
        raise AssertionError('Expected failure for invalid dir color')
