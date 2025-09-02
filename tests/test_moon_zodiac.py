from pohualli import (
    julian_day_to_maya_moon, str_maya_moon, julian_day_to_abn_dist, str_abn_dist, ecliptic,
    julian_day_to_star_zodiac, julian_day_to_earth_zodiac, zodiac_to_name, zodiac_name_to_index
)

JDN_SAMPLE = 2451545  # J2000 epoch

def test_maya_moon_and_abn_dist():
    mm = julian_day_to_maya_moon(JDN_SAMPLE)
    ab = julian_day_to_abn_dist(JDN_SAMPLE)
    assert 0 <= mm <= 29.530588
    assert -173.31 <= ab <= 173.31
    smm = str_maya_moon(mm)
    sab = str_abn_dist(ab)
    assert 1 <= smm <= 30
    assert isinstance(sab, int)
    # ecliptic condition rarely true; just ensure function returns bool
    assert isinstance(ecliptic(mm, ab), bool)

def test_zodiac_basic():
    star = julian_day_to_star_zodiac(JDN_SAMPLE)
    earth = julian_day_to_earth_zodiac(JDN_SAMPLE)
    assert 0 <= star < 360
    assert 0 <= earth < 360
    name = zodiac_to_name(star)
    if name:
        idx = zodiac_name_to_index(name)
        assert 0 <= idx < 12
