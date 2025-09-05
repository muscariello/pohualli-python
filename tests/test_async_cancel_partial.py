import os, time
os.environ.setdefault('POHUALLI_RANGE_THROTTLE','300')  # ensure job not instantaneous
from fastapi.testclient import TestClient
from pohualli.webapp import app

client = TestClient(app)

def test_async_cancel_partial_results():
    payload = {
        "start": 2451545,
        "end": 2452545,  # large span to allow cancellation
        "step": 1,
        "limit": 0,
        "fields": "jdn,tzolkin_name"
    }
    r = client.post('/api/range-jobs', json=payload)
    assert r.status_code == 200
    jid = r.json()['id']
    # Immediately cancel
    c = client.post(f'/api/range-jobs/{jid}/cancel')
    assert c.status_code == 200
    data = c.json()
    # Accept immediate transitional or final state
    assert data['status'] in ('canceling','canceled')
    if data['status'] == 'canceled':
        # Full payload expected
        assert data['scanned'] <= data['total']
        assert 'partial' in data and data['partial'] is True
    else:
        # Poll briefly for final state
        for _ in range(40):  # up to ~2s
            s = client.get(f'/api/range-jobs/{jid}')
            jd = s.json()
            if jd.get('status') in ('canceled','completed','error'):
                # We asked to cancel; allow completed if it finished just before cancellation
                assert jd['status'] in ('canceled','completed')
                break
            time.sleep(0.05)
