import subprocess, sys, os
from pohualli import year_bearer_packed, DEFAULT_CONFIG

def test_year_bearer_packed_basic():
    # Set a reference Year Bearer (month=0, day=0)
    DEFAULT_CONFIG.year_bearer_str = 0
    DEFAULT_CONFIG.year_bearer_val = 0
    yb = year_bearer_packed(0,0, 2451545)
    assert isinstance(yb, int) and (0 <= yb <= 0xFFFF)


def test_cli_runs():
    cmd = [sys.executable, '-m', 'pohualli.cli', 'from-jdn', '2451545', '--year-bearer-ref', '0', '0']
    env = os.environ.copy()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert 'JDN 2451545' in proc.stdout
