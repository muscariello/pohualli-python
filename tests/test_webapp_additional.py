from fastapi.testclient import TestClient
import time, os
from pohualli.webapp import app, JOBS

client = TestClient(app)


def test_create_range_job_reverse_and_negative_step():
    # Provide end < start and negative step to exercise normalization
    payload = {"start":2451550,"end":2451545,"step":-5,"limit":1,"fields":"jdn"}
    r = client.post('/api/range-jobs', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data['start'] == 2451545 and data['end'] == 2451550
    assert data['step'] == 1  # negative coerced to 1


def test_range_job_cancel_mid_run_via_endpoint():
    # Large span to allow cancel window
    payload = {"start":2451545,"end":2452545,"step":1,"fields":"jdn","limit":0}
    r = client.post('/api/range-jobs', json=payload)
    jid = r.json()['id']
    # Issue cancel soon; loop should still be running and produce partial results
    time.sleep(0.01)
    c = client.post(f'/api/range-jobs/{jid}/cancel')
    assert c.status_code == 200
    cd = c.json()
    assert cd['status'] in ('canceled','canceling','completed')
    # Fetch final state after some time if still running
    for _ in range(60):
        d = client.get(f'/api/range-jobs/{jid}').json()
        if d['status'] in ('canceled','completed','error'):
            if d['status'] == 'canceled':
                assert d['partial'] is True or d['scanned'] < d['total']
            break
        time.sleep(0.02)


def test_derive_autocorr_invalid_spec_error():
    # Invalid tzolkin format should produce 400
    r = client.get('/api/derive-autocorr', params={'jdn':2451545,'tzolkin':'bad-spec'})
    assert r.status_code == 400
    assert 'error' in r.json()


def test_home_unknown_preset_and_single_conversion():
    # Unknown preset triggers error message but continues rendering
    h = client.get('/', params={'preset':'__no_such__','jdn':'2451545'})
    assert h.status_code == 200
    assert '__no_such__' in h.text
    # Should include composite data content somewhere (tzolkin or Long Count text)
    assert 'Tzolkin' in h.text or 'Long Count' in h.text


def test_home_range_with_filters_and_limit():
    # Provide simple range search within home with filters + limit
    h = client.get('/', params={'r_start':'2451545','r_end':'2451555','r_limit':'1','r_tzval':'1'})
    assert h.status_code == 200
    # Ensure a table-like header or match appears
    assert 'tzolkin' in h.text.lower() or 'jdn' in h.text.lower()
