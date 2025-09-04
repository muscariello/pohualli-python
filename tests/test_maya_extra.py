from pohualli import (
    tzolkin_number_to_name, tzolkin_name_to_number,
    haab_number_to_name, haab_name_to_number,
    julian_day_to_tzolkin_value, julian_day_to_tzolkin_name_index,
    julian_day_to_g_value, julian_day_to_haab_packed,
    unpack_haab_month, unpack_haab_value,
)
from pohualli.types import DEFAULT_CONFIG, CORRECTIONS


def test_negative_day_wrapping_and_offsets():
    # exercise negative branch logic in conversions
    day = -1000
    # tweak corrections to non-zero to hit arithmetic
    DEFAULT_CONFIG.tzolkin_haab_correction.tzolkin = 3
    CORRECTIONS.cTzolkinVal = 2
    v = julian_day_to_tzolkin_value(day)
    assert 1 <= v <= 13
    CORRECTIONS.cTzolkinStr = 5
    n = julian_day_to_tzolkin_name_index(day)
    assert 0 <= n < 20
    CORRECTIONS.cGValue = 1
    g = julian_day_to_g_value(day)
    assert 1 <= g <= 9
    CORRECTIONS.cHaabVal = 4
    packed = julian_day_to_haab_packed(day)
    assert 0 <= packed < 365
    assert 0 <= unpack_haab_month(packed) < 19
    assert 0 <= unpack_haab_value(packed) < 20


def test_aztec_mode_name_tables():
    # enable aztec naming and boundary checks
    DEFAULT_CONFIG.t_aztec = True
    try:
        for i in range(20):
            name = tzolkin_number_to_name(i)
            assert tzolkin_name_to_number(name) == i
        for i in range(19):
            name = haab_number_to_name(i)
            assert haab_name_to_number(name) == i
    finally:
        DEFAULT_CONFIG.t_aztec = False
