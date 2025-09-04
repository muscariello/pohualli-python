import pytest
from pohualli.autocorr import derive_auto_corrections

JDN = 2451545

def test_autocorr_invalid_tzolkin_spec():
    with pytest.raises(ValueError):
        derive_auto_corrections(JDN, tzolkin='badformat')


def test_autocorr_invalid_haab_spec():
    with pytest.raises(ValueError):
        derive_auto_corrections(JDN, haab='badformat')


def test_autocorr_long_count_5_component_auto_insert():
    # Provide 5 components - will insert leading 1 internally
    # We expect it to likely fail the search window producing ValueError, which covers that branch.
    with pytest.raises(ValueError):
        derive_auto_corrections(JDN, long_count='0.0.0.0.0')


def test_autocorr_year_bearer_failure():
    # improbable year bearer spec
    with pytest.raises(ValueError):
        derive_auto_corrections(JDN, year_bearer='13 DOESNOTEXIST')


def test_autocorr_dir_color_invalid():
    with pytest.raises(ValueError):
        derive_auto_corrections(JDN, dir_color='notacolor')
