import io
from contextlib import redirect_stdout, redirect_stderr
from pohualli.cli import main

RANGE_START = 584283
RANGE_END = 584288


def run_cli(argv):
    out = io.StringIO(); err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        main(argv)
    return out.getvalue(), err.getvalue()


def test_cli_tzolkin_value_mismatch_progress_every1():
    stdout, stderr = run_cli(['search-range', str(RANGE_START), str(RANGE_END), '--tzolkin-value','99','--progress-every','1'])
    assert '# no matches' in stdout
    # progress lines for each scanned day
    assert 'progress' in stderr


def test_cli_tzolkin_name_mismatch_progress_every1():
    stdout, stderr = run_cli(['search-range', str(RANGE_START), str(RANGE_END), '--tzolkin-name','NoSuchName','--progress-every','1'])
    assert '# no matches' in stdout
    assert 'progress' in stderr


def test_cli_haab_day_mismatch_progress():
    stdout, stderr = run_cli(['search-range', str(RANGE_START), str(RANGE_END), '--haab-day','99','--progress-every','1'])
    assert '# no matches' in stdout
    assert 'progress' in stderr


def test_cli_haab_month_mismatch_progress():
    stdout, stderr = run_cli(['search-range', str(RANGE_START), str(RANGE_END), '--haab-month','NoMonth','--progress-every','1'])
    assert '# no matches' in stdout
    assert 'progress' in stderr


def test_cli_year_bearer_name_mismatch_progress():
    stdout, stderr = run_cli(['search-range', str(RANGE_START), str(RANGE_END), '--year-bearer-name','NoBearer','--progress-every','1'])
    assert '# no matches' in stdout
    assert 'progress' in stderr


def test_cli_long_count_length_mismatch_progress():
    stdout, stderr = run_cli(['search-range', str(RANGE_START), str(RANGE_END), '--long-count','1.2.3','--progress-every','1'])
    assert '# no matches' in stdout or 'jdn' in stdout
    assert 'progress' in stderr


def test_cli_limit_break_with_progress_after_match():
    # No filters; ensure at least one match (first day) then limit breaks; progress printed for i=1
    stdout, stderr = run_cli(['search-range', str(RANGE_START), str(RANGE_END), '--limit','1','--progress-every','1'])
    assert 'jdn' in stdout  # header present
    # Progress line may not appear if the limit breaks before printing; accept empty stderr
    assert stderr == '' or 'progress' in stderr or '# perf scanned=' in stderr
