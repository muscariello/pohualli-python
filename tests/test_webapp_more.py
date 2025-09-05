from fastapi.testclient import TestClient
from pohualli.webapp import app, JOBS
import time

client = TestClient(app)


def test_range_job_not_found_and_cancel_not_found():
    r = client.get('/api/range-jobs/doesnotexist')
    assert r.status_code == 404
    c = client.post('/api/range-jobs/doesnotexist/cancel')
    assert c.status_code == 404


def test_cancel_after_completion_no_change():
    payload = {"start":2451545,"end":2451546,"step":1,"fields":"jdn"}
    j = client.post('/api/range-jobs', json=payload).json()
    jid = j['id']
    # wait completion
    for _ in range(40):
        d = client.get(f'/api/range-jobs/{jid}').json()
        if d['status'] == 'completed':
            break
        time.sleep(0.05)
    post = client.post(f'/api/range-jobs/{jid}/cancel').json()
    assert post['status'] in ('completed','canceled','canceling')


def test_derive_autocorr_direction_color_success():
    # Use minimal spec: just direction color 'Oeste' which should succeed deriving dir color correction within range
    # Need tzolkin spec as anchor to avoid ValueError on tz search
    base = client.get('/api/convert', params={'jdn':2451545}).json()
    tz_spec = f"{base['tzolkin_value']} {base['tzolkin_name']}"
    r = client.get('/api/derive-autocorr', params={'jdn':2451545,'tzolkin':tz_spec,'dir_color':'Oeste'})
    assert r.status_code == 200
    assert 'tzolkin_offset' in r.json()


def test_home_range_invalid_params_and_start_end_swap():
    # invalid numeric range triggers error message
    h = client.get('/', params={'r_start':'abc','r_end':'2451545'})
    assert h.status_code == 200
    assert 'Invalid range start/end' in h.text or 'Invalid range' in h.text
    # start > end swap
    h2 = client.get('/', params={'r_start':'2451550','r_end':'2451545','r_limit':'1'})
    assert h2.status_code == 200
    # Expect at least one of the field headers present from template
    assert 'Tzolkin' in h2.text or 'tzolkin' in h2.text


def test_home_culture_toggle_and_corrections():
    h = client.get('/', params={'culture':'aztec','tz_off':'2','tzn_off':'3','g_off':'4'})
    assert h.status_code == 200
    assert 'Aztec' in h.text

