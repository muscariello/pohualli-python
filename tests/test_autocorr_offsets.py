from pohualli.autocorr import derive_auto_corrections
from pohualli import (
    julian_day_to_tzolkin_value, julian_day_to_tzolkin_name_index,
    tzolkin_number_to_name,
    julian_day_to_haab_packed, unpack_haab_month, unpack_haab_value, haab_number_to_name,
    julian_day_to_g_value
)
from pohualli.types import DEFAULT_CONFIG

JDN = 2451545


def test_tzolkin_non_zero_offset_derivation():
    original = DEFAULT_CONFIG.tzolkin_haab_correction.tzolkin
    try:
        target_offset = 7
        DEFAULT_CONFIG.tzolkin_haab_correction.tzolkin = target_offset
        val = julian_day_to_tzolkin_value(JDN)
        name_idx = julian_day_to_tzolkin_name_index(JDN)
        name = tzolkin_number_to_name(name_idx)
        spec = f"{val} {name}"
        res = derive_auto_corrections(JDN, tzolkin=spec)
        assert res.tzolkin_offset == target_offset
    finally:
        DEFAULT_CONFIG.tzolkin_haab_correction.tzolkin = original


def test_haab_non_zero_offset_derivation():
    original = DEFAULT_CONFIG.tzolkin_haab_correction.haab
    try:
        target_offset = 11
        DEFAULT_CONFIG.tzolkin_haab_correction.haab = target_offset
        packed = julian_day_to_haab_packed(JDN)
        month = unpack_haab_month(packed)
        day = unpack_haab_value(packed)
        month_name = haab_number_to_name(month)
        spec = f"{day} {month_name}"
        res = derive_auto_corrections(JDN, haab=spec)
        assert res.haab_offset == target_offset
    finally:
        DEFAULT_CONFIG.tzolkin_haab_correction.haab = original


def test_g_non_zero_offset_derivation():
    original = DEFAULT_CONFIG.tzolkin_haab_correction.g
    try:
        target_offset = 3
        DEFAULT_CONFIG.tzolkin_haab_correction.g = target_offset
        g_val = julian_day_to_g_value(JDN)
        res = derive_auto_corrections(JDN, g_value=g_val)
        assert res.g_offset == target_offset
    finally:
        DEFAULT_CONFIG.tzolkin_haab_correction.g = original
