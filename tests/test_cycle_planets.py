from pohualli import (
    julian_day_to_819_station, julian_day_to_819_value, station_to_dir_col, dir_col_val_to_str,
    julian_day_to_planet_synodic_val, trunc_planet_synodic_val,
    P_VENUS, P_MERCURY
)


def test_819_cycle_basic():
    jdn = 600000
    station = julian_day_to_819_station(jdn, 0)
    val = julian_day_to_819_value(jdn, 0)
    assert station > 0
    assert 0 < val <= 819
    col = station_to_dir_col(station, 0)
    assert col in (1,2,3,4)
    assert dir_col_val_to_str(col) != ''


def test_planet_synodic_round_trip():
    jdn = 2451545  # J2000
    for planet in (P_MERCURY, P_VENUS):
        val = julian_day_to_planet_synodic_val(jdn, planet)
        iv = trunc_planet_synodic_val(val, planet)
        assert isinstance(iv, int)
