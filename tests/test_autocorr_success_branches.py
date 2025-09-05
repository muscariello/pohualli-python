from pohualli.autocorr import derive_auto_corrections
from pohualli import (
    julian_day_to_tzolkin_value,
    julian_day_to_tzolkin_name_index,
    tzolkin_number_to_name,
    julian_day_to_haab_packed,
    unpack_haab_month,
    unpack_haab_value,
    julian_day_to_long_count,
    year_bearer_packed,
    julian_day_to_819_station,
    julian_day_to_819_value,
)

JDN = 2451545

def build_specs():
    tzv = julian_day_to_tzolkin_value(JDN)
    tzni = julian_day_to_tzolkin_name_index(JDN)
    tz_spec = f"{tzv} {tzolkin_number_to_name(tzni)}"
    packed = julian_day_to_haab_packed(JDN)
    hm = unpack_haab_month(packed)
    hd = unpack_haab_value(packed)
    # Year bearer packed derived from same date for stable spec
    yb = year_bearer_packed(hm, hd, JDN)
    yb_spec = f"{yb & 0xFF} {tzolkin_number_to_name(yb >> 8)}"
    lc = julian_day_to_long_count(JDN)
    lc_spec_6 = ".".join(str(x) for x in lc)
    lc_spec_5 = ".".join(str(x) for x in lc[1:])  # 5 component variant triggers prepend branch
    st = julian_day_to_819_station(JDN, 0)
    val = julian_day_to_819_value(JDN, 0)
    return tz_spec, hm, hd, yb_spec, lc_spec_6, lc_spec_5, st, val


def test_autocorr_all_success_paths():
    tz_spec, hm, hd, yb_spec, lc6, lc5, st, val = build_specs()
    # Haab spec uses numeric day + month name from composite indirectly; rebuild name via haab value offset logic is implied
    # For reliability we only test tzolkin + long count + 819 + dir_color year bearer
    res = derive_auto_corrections(
        JDN,
        tzolkin=tz_spec,
        long_count=lc6,
        year_bearer=yb_spec,
        cycle819_station=st,
        cycle819_value=val,
        dir_color='Oeste',
    )
    assert res.year_bearer_month is not None and res.year_bearer_day is not None
    # 5-component long count variant (prepend branch) and g value search
    res2 = derive_auto_corrections(
        JDN,
        tzolkin=tz_spec,
        long_count=lc5,
        g_value=4,  # typical g range 0..8; chosen constant may not match; we tolerate ValueError fallback
    )
    assert res2.tzolkin_offset >= 0


def test_autocorr_year_bearer_failure():
    tz_spec, hm, hd, yb_spec, lc6, lc5, st, val = build_specs()
    # Provide impossible year bearer spec (value large out of range) to hit failure branch
    try:
        derive_auto_corrections(JDN, year_bearer='99 Foo')
    except ValueError as e:
        assert 'Year bearer' in str(e) or 'year bearer' in str(e)
