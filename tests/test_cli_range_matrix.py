import io, sys
from contextlib import redirect_stdout, redirect_stderr
from pohualli.cli import main


def run_cli(args):
    out = io.StringIO(); err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        main(args)
    return out.getvalue(), err.getvalue()


def test_cli_range_all_filters_combo_minimal():
    # Use small range and mix filters likely to still produce at least 0 or 1 result
    out, err = run_cli(['search-range','584283','584290','--tzolkin-value','5','--haab-day','9','--limit','1','--progress-every','2','--perf-stats'])
    assert '# perf scanned=' in err
    assert 'jdn' in out or '# no matches' in out


def test_cli_range_weekday_and_dircolor():
    out, _ = run_cli(['search-range','584283','584288','--weekday','1','--dir-color','Sur','--limit','1'])
    assert 'jdn' in out or '# no matches' in out


def test_cli_range_year_bearer_name():
    out, _ = run_cli(['search-range','584283','584300','--year-bearer-name','Eb','--limit','1'])
    assert 'jdn' in out or '# no matches' in out

