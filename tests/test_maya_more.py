from pohualli import (
    tzolkin_number_to_name, tzolkin_name_to_number,
    haab_number_to_name, haab_name_to_number,
    julian_day_to_tzolkin_value, julian_day_to_tzolkin_name_index,
    julian_day_to_g_value, julian_day_to_haab_packed,
    unpack_haab_month, unpack_haab_value,
    long_count_to_julian_day, julian_day_to_long_count
)
from pohualli.types import ABSOLUTE


def test_invalid_indices_and_name_roundtrip():
    # invalid indices return '' or 255
    assert tzolkin_number_to_name(-1) == ''
    assert tzolkin_name_to_number('NOPE') == 255
    assert haab_number_to_name(40) == ''
    assert haab_name_to_number('NOPE') == 255


def test_long_count_inverse_far_offset():
    orig = ABSOLUTE.new_era
    try:
        ABSOLUTE.new_era = 600000  # shift era
        lc = julian_day_to_long_count(ABSOLUTE.new_era)
        j = long_count_to_julian_day(lc)
        assert j == ABSOLUTE.new_era
    finally:
        ABSOLUTE.new_era = orig
