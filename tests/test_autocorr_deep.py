from pohualli.autocorr import derive_auto_corrections
from pohualli import (
    julian_day_to_long_count, tzolkin_number_to_name,
    julian_day_to_haab_packed, unpack_haab_month, unpack_haab_value,
    year_bearer_packed, unpack_yb_val, unpack_yb_str,
    julian_day_to_819_station, julian_day_to_819_value, station_to_dir_col,
    dir_col_val_to_str
)

JDN = 2451545

def test_autocorr_long_count_and_year_bearer_and_819_success():
    # Compute actual long count for success branch
    lc = julian_day_to_long_count(JDN)
    lc_str = '.'.join(str(x) for x in lc)
    # Compute current year bearer spec (value + tzolkin name)
    packed = julian_day_to_haab_packed(JDN)
    hm = unpack_haab_month(packed)
    hv = unpack_haab_value(packed)
    yb_packed = year_bearer_packed(hm, hv, JDN)
    yb_val = unpack_yb_val(yb_packed)
    yb_name = tzolkin_number_to_name(unpack_yb_str(yb_packed))
    yb_spec = f"{yb_val} {yb_name}"
    # 819-cycle station/value and direction color
    st = julian_day_to_819_station(JDN, 0)
    val = julian_day_to_819_value(JDN, 0)
    dir_color = dir_col_val_to_str(station_to_dir_col(st, 0))
    res = derive_auto_corrections(
        JDN,
        long_count=lc_str,
        year_bearer=yb_spec,
        cycle819_station=st,
        cycle819_value=val,
        dir_color=dir_color,
    )
    # Verify fields set (offsets may be zero)
    assert res.lcd_offset is not None
    assert res.year_bearer_month is not None and res.year_bearer_day is not None
    assert res.cycle819_station_correction is not None
    assert res.cycle819_dir_color_correction is not None
