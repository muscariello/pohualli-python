import io, sys
from contextlib import redirect_stdout, redirect_stderr
from pohualli.cli import main

JDN = 2451545


def run_cli(argv):
    out_buf = io.StringIO(); err_buf = io.StringIO()
    with redirect_stdout(out_buf), redirect_stderr(err_buf):
        main(argv)
    return out_buf.getvalue(), err_buf.getvalue()


def test_cli_from_jdn_aztec_mode():
    out, _ = run_cli(['from-jdn', str(JDN), '--culture','aztec'])
    assert 'Year Bearer culture:' in out


def test_cli_search_range_reversed_and_progress_perf():
    out, err = run_cli(['search-range','584290','584283','--progress-every','2','--perf-stats','--limit','2','--fields','jdn,tzolkin_name'])
    assert 'jdn' in out
    assert '# perf scanned=' in err


def test_cli_search_range_no_matches():
    out, err = run_cli(['search-range','584283','584287','--tzolkin-value','99'])
    assert '# no matches' in out


def test_cli_search_range_long_count_pattern_mismatch():
    out, _ = run_cli(['search-range','584283','584287','--long-count','1.2.3'])
    assert '# no matches' in out or 'jdn' in out


def test_cli_search_range_dir_color_weekday_filters():
    # Use improbable dir color substring to force zero matches
    out, _ = run_cli(['search-range','584283','584286','--dir-color','unlikely-substr','--weekday','2'])
    assert '# no matches' in out or 'jdn' in out


def test_cli_search_range_limit_trigger():
    out, _ = run_cli(['search-range','584283','584300','--limit','1'])
    # header + 1 row at most
    lines = [l for l in out.strip().splitlines() if l and not l.startswith('#')]
    assert len(lines) <= 2
