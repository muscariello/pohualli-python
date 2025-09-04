import subprocess, sys
import math
from pohualli.autocorr import _tzolkin_value_with_offset, _tzolkin_name_index_with_offset, _haab_packed_with_offset, _g_value_with_offset, _long_count_with_offset, derive_auto_corrections
from pohualli.types import CORRECTIONS, ABSOLUTE
from pohualli import julian_day_to_star_zodiac, julian_day_to_earth_zodiac
from pohualli.calendar_dates import gregorian_correction_pascal

NEG_JDN = -100000

def test_autocorr_internal_negative_offsets():
    # drive negative branches (day < 0) in helper functions using large negative JDN
    CORRECTIONS.cTzolkinVal = 0
    CORRECTIONS.cTzolkinStr = 0
    CORRECTIONS.cHaabVal = 0
    CORRECTIONS.cGValue = 0
    assert 1 <= _tzolkin_value_with_offset(NEG_JDN, 0) <= 13
    assert 0 <= _tzolkin_name_index_with_offset(NEG_JDN, 0) < 20
    hp = _haab_packed_with_offset(NEG_JDN, 0)
    assert 0 <= hp < 365
    assert 1 <= _g_value_with_offset(NEG_JDN, 0) <= 9


def test_long_count_counter_wrap():
    # Choose offset to force counter True (day < new_era - ERA_LENGTH)
    orig_new_era = ABSOLUTE.new_era
    try:
        ABSOLUTE.new_era = 584285
        # jdn so that jdn + off + 2 < new_era - 1872000 => pick off large negative
        lc = _long_count_with_offset(0, -3000000)
        assert isinstance(lc, tuple) and len(lc) == 6
    finally:
        ABSOLUTE.new_era = orig_new_era


def test_cli_from_jdn_textual_output():
    proc = subprocess.run([sys.executable,'-m','pohualli.cli','from-jdn','2451545'],capture_output=True,text=True)
    assert proc.returncode == 0 and 'Tzolkin:' in proc.stdout


def test_zodiac_wrap_behavior():
    # find jdn that produces star zodiac angle 0 after rounding
    jdn = 2449827  # base star Aries; angle should be 0
    assert julian_day_to_star_zodiac(jdn) == 0
    # force earth zodiac around wrap boundary by picking near base
    assert 0 <= julian_day_to_earth_zodiac(2449798) < 360


def test_gregorian_correction_negative_branch():
    # negative jdn triggers jd < 0 branch in correction
    val = gregorian_correction_pascal(-100000)
    assert isinstance(val, int)

