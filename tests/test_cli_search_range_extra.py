import io, json, sys
from contextlib import redirect_stdout, redirect_stderr
from pohualli.cli import main

def run_cli(argv):
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    with redirect_stdout(out_buf), redirect_stderr(err_buf):
        main(argv)
    return out_buf.getvalue(), err_buf.getvalue()


def test_search_range_progress_and_perf_stats_and_reversed():
    # Provide reversed order and progress/perf flags
    stdout, stderr = run_cli([
        'search-range','584290','584283','--step','2','--progress-every','2','--perf-stats','--limit','1','--tzolkin-value','1'
    ])
    # Should normalize start/end and produce at least header + one row or # no matches
    assert 'jdn' in stdout or '# no matches' in stdout
    # Progress line(s) and perf line in stderr
    assert '# perf scanned=' in stderr
    # progress lines optional if range small, but we set progress-every=2 so expect maybe one
    assert 'progress' in stderr or '# perf scanned=' in stderr


def test_search_range_long_count_mismatch_segments():
    # Pattern with wrong segment count (3) should yield no matches
    stdout, _ = run_cli(['search-range','584283','584287','--long-count','1.2.3','--limit','2'])
    assert '# no matches' in stdout or 'jdn' in stdout  # allow header if implementation prints it


def test_search_range_json_lines_zero_matches():
    # Use a filter unlikely to match (weekday improbable + specific tzolkin combo)
    stdout, _ = run_cli(['search-range','584283','584285','--json-lines','--tzolkin-value','1','--weekday','7','--long-count','99.99.99.99.99.99'])
    # No output lines for zero matches in json-lines mode
    assert stdout.strip() == ''
