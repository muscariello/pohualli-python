from pohualli import (
    tzolkin_number_to_name, tzolkin_name_to_number,
    haab_number_to_name, haab_name_to_number,
    julian_day_to_tzolkin_value, julian_day_to_tzolkin_name_index,
    julian_day_to_haab_packed, unpack_haab_value, unpack_haab_month,
    julian_day_to_long_count, long_count_to_julian_day
)
from pohualli.types import ABSOLUTE


def test_round_trip_tzolkin_names():
    for i in range(20):
        name = tzolkin_number_to_name(i)
        assert tzolkin_name_to_number(name) == i


def test_haab_name_lookup():
    for i in range(19):
        name = haab_number_to_name(i)
        assert haab_name_to_number(name) == i


def test_long_count_round_trip_sample():
    # Known date: 0.0.0.0.0 -> baseline offset arithmetic
    lc = (0,0,0,0,0,0)
    j = long_count_to_julian_day(lc)
    lc2 = julian_day_to_long_count(j)
    assert lc2 == lc


def test_haab_pack_unpack():
    # take arbitrary day
    day = 1000
    packed = julian_day_to_haab_packed(day)
    assert 0 <= packed < 365
    # derived components should be within range
    assert 0 <= unpack_haab_month(packed) < 19
    assert 0 <= unpack_haab_value(packed) < 20


def test_long_count_new_era_override():
    # Save original
    orig = ABSOLUTE.new_era
    try:
        ABSOLUTE.new_era = 584285
        lc = julian_day_to_long_count(ABSOLUTE.new_era)
        # baseline should produce a small or zeroed structure after inverse transform
        j = long_count_to_julian_day(lc)
        assert isinstance(lc, tuple) and len(lc) == 6
        # Invariance check: converting back yields original JDN
        assert j == ABSOLUTE.new_era
    finally:
        ABSOLUTE.new_era = orig
