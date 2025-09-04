from fastapi.testclient import TestClient
from pohualli.webapp import app
from pohualli.types import DEFAULT_CONFIG, CORRECTIONS

def test_home_param_overrides_and_preset_error(monkeypatch):
    client = TestClient(app)
    # invalid preset triggers error branch
    r = client.get('/', params={'preset':'does-not-exist','jdn':2451545,'new_era':'600000','ybm':'3','ybd':'4','tz_off':'5','tzn_off':'6','haab_off':'7','g_off':'8','lcd_off':'9','week_off':'10','c819s':'11','c819d':'12'})
    assert r.status_code == 200
    # verify that overrides applied (tzolkin name offset etc.)
    assert 'Unknown preset' in r.text
    assert DEFAULT_CONFIG.tzolkin_haab_correction.tzolkin == 5
    assert CORRECTIONS.cTzolkinStr == 6


def test_api_convert_year_bearer_override():
    client = TestClient(app)
    r = client.get('/api/convert', params={'jdn':2451545,'new_era':584285,'year_bearer_month':2,'year_bearer_day':3})
    assert r.status_code == 200
    assert r.json()['jdn'] == 2451545

