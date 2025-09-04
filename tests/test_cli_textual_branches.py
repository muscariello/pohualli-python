import subprocess, sys, json

JDN = 2451545

def test_cli_from_jdn_textual_with_options():
    cmd = [sys.executable,'-m','pohualli.cli','from-jdn',str(JDN),'--new-era','584283','--year-bearer-ref','2','3']
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    # verify printed markers indicating lines executed
    assert 'JDN 2451545' in proc.stdout
    assert 'Tzolkin:' in proc.stdout
    assert 'Haab:' in proc.stdout
    assert 'Long Count:' in proc.stdout
    assert 'Year Bearer packed:' in proc.stdout


def test_cli_apply_correlation_variant():
    cmd = [sys.executable,'-m','pohualli.cli','apply-correlation','gmt-584283']
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert 'gmt-584283' in proc.stdout
