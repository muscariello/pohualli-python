import json
from fastapi.testclient import TestClient
from pohualli.webapp import app

client = TestClient(app)

def test_api_convert():
    r = client.get('/api/convert', params={'jdn':2451545})
    assert r.status_code == 200
    data = r.json()
    assert data['jdn'] == 2451545
    assert 'tzolkin_name' in data

def test_home_page():
    r = client.get('/')
    assert r.status_code == 200
    r2 = client.get('/', params={'jdn':2451545})
    assert r2.status_code == 200
    assert 'Tzolkin' in r2.text

def test_api_derive_autocorr():
    # Use a simple tzolkin spec derived from composite for stability
    jdn = 2451545
    comp = client.get('/api/convert', params={'jdn': jdn}).json()
    tz_spec = f"{comp['tzolkin_value']} {comp['tzolkin_name']}"
    r = client.get('/api/derive-autocorr', params={'jdn': jdn, 'tzolkin': tz_spec})
    assert r.status_code == 200
    data = r.json()
    assert 'tzolkin_offset' in data
    assert 0 <= data['tzolkin_offset'] < 260
