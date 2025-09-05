import io
from contextlib import redirect_stdout
from pohualli.cli import main

JDN = 2451545

def run_cli(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        main(argv)
    return buf.getvalue()


def test_cli_from_jdn_textual_with_options():
    out = run_cli(['from-jdn',str(JDN),'--new-era','584283','--year-bearer-ref','2','3'])
    assert 'JDN 2451545' in out
    assert 'Tzolkin:' in out
    assert 'Haab:' in out
    assert 'Long Count:' in out
    assert 'Year Bearer packed:' in out


def test_cli_apply_correlation_variant():
    out = run_cli(['apply-correlation','gmt-584283'])
    assert 'gmt-584283' in out
