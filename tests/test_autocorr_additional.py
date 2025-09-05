from pohualli.autocorr import derive_auto_corrections
from pohualli import (
    julian_day_to_tzolkin_value,
    julian_day_to_tzolkin_name_index,
    tzolkin_number_to_name,
    julian_day_to_haab_packed,
    unpack_haab_month,
    unpack_haab_value,
)

JDN = 2451545

def tz_spec():
    v = julian_day_to_tzolkin_value(JDN)
    i = julian_day_to_tzolkin_name_index(JDN)
    return f"{v} {tzolkin_number_to_name(i)}"


def test_autocorr_g_value_success():
    # Try all g offsets until one matches; ensure branch success path
    for g in range(9):
        try:
            res = derive_auto_corrections(JDN, tzolkin=tz_spec(), g_value=g)
            assert 0 <= res.g_offset < 9
            return
        except ValueError:
            continue
    raise AssertionError('No g value matched (unexpected)')


def test_autocorr_haab_success():
    packed = julian_day_to_haab_packed(JDN)
    hm = unpack_haab_month(packed)
    hd = unpack_haab_value(packed)
    from pohualli import haab_number_to_name
    spec = f"{hd} {haab_number_to_name(hm)}"
    res = derive_auto_corrections(JDN, haab=spec)
    assert 0 <= res.haab_offset < 365


def test_autocorr_819_failure():
    try:
        derive_auto_corrections(JDN, cycle819_station=9999)
    except ValueError as e:
        assert '819-cycle' in str(e)

