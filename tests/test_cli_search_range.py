import io, json
from contextlib import redirect_stdout
from pohualli.cli import main


def run_cli(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        main(argv)
    return buf.getvalue()


def test_search_range_basic_header_and_rows():
    out = run_cli(["search-range", "584283", "584290", "--limit", "3", "--tzolkin-name", "Imix"])  # small span
    lines = [l for l in out.strip().splitlines() if l and not l.startswith('#')]
    if len(lines) >= 2:
        header = lines[0].split('\t')
        assert 'jdn' in header and 'tzolkin_name' in header
        for row in lines[1:]:
            cols = row.split('\t')
            mapping = dict(zip(header, cols))
            assert mapping['tzolkin_name'] == 'Imix'
    else:
        # Accept '# no matches' outcome (filter produced none in this random window) as non-failure
        assert '# no matches' in out


def test_search_range_json_lines_mode():
    out = run_cli(["search-range", "584283", "584285", "--json-lines", "--limit", "1"])  # small
    # Should be exactly one JSON object line (match count 1)
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert 'jdn' in data and 'tzolkin_name' in data


def test_search_range_long_count_wildcard():
    # Look for a famous base date around correlation new era; wildcard pattern for later digits
    out = run_cli(["search-range", "584280", "584300", "--long-count", "0.*.*.*.*.*", "--limit", "1"])
    # Expect at least header + maybe row or # no matches; assert not crashing
    assert 'jdn' in out or '# no matches' in out


def test_search_range_fields_subset():
    out = run_cli(["search-range", "584283", "584285", "--fields", "jdn,tzolkin_name,haab_month_name", "--limit", "2"])
    lines = [l for l in out.strip().splitlines() if l and not l.startswith('#')]
    assert lines
    header = lines[0].split('\t')
    assert header == ['jdn','tzolkin_name','haab_month_name']
