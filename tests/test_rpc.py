import json
import io
import subprocess
import sys

import pytest

from pohualli import compute_composite
from pohualli.rpc import RpcError, handle_request_object
from pohualli import rpc as rpcmod


def _call(method: str, params: dict, req_id: int = 1):
    response, _ = handle_request_object(
        {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
    )
    return response["result"]


def test_convert_restores_global_state_between_calls():
    first = _call("convert", {"jdn": 2451545, "new_era": 584283}, req_id=10)
    second = _call("convert", {"jdn": 2451545}, req_id=11)

    assert first["context"]["new_era"] == 584283
    assert second["context"]["new_era"] == 584285
    assert first["composite"]["long_count"] != second["composite"]["long_count"]


def test_search_range_returns_rows():
    result = _call(
        "search_range",
        {"start": 2451545, "end": 2451555, "tzolkin_value": 4, "limit": 2},
        req_id=12,
    )
    assert result["count"] <= 2
    assert "fields" in result
    if result["rows"]:
        assert "jdn" in result["rows"][0]


def test_stdio_protocol_parse_error_and_quit():
    payload = "\n".join(
        [
            '{"jsonrpc":"2.0","id":1,"method":"health","params":{}}',
            "{not-json}",
            '{"jsonrpc":"2.0","id":2,"method":"quit","params":{}}',
            "",
        ]
    )
    proc = subprocess.run(
        [sys.executable, "-m", "pohualli.rpc"],
        input=payload,
        text=True,
        capture_output=True,
        check=True,
    )
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    assert len(lines) == 3

    first = json.loads(lines[0])
    second = json.loads(lines[1])
    third = json.loads(lines[2])

    assert first["result"]["status"] == "ok"
    assert second["error"]["code"] == -32700
    assert third["result"]["status"] == "bye"


def test_invalid_request_object_type():
    with pytest.raises(RpcError) as exc:
        handle_request_object(["not", "an", "object"])
    assert exc.value.code == -32600


def test_invalid_request_missing_method():
    with pytest.raises(RpcError) as exc:
        handle_request_object({"jsonrpc": "2.0", "id": 99, "params": {}})
    assert exc.value.code == -32600
    assert exc.value.data == {"id": 99}


def test_unknown_method():
    with pytest.raises(RpcError) as exc:
        handle_request_object(
            {"jsonrpc": "2.0", "id": 2, "method": "does_not_exist", "params": {}}
        )
    assert exc.value.code == -32601


def test_params_must_be_object():
    with pytest.raises(RpcError) as exc:
        handle_request_object(
            {"jsonrpc": "2.0", "id": 3, "method": "health", "params": ["bad"]}
        )
    assert exc.value.code == -32602


def test_convert_validation_errors():
    with pytest.raises(RpcError) as exc:
        _call("convert", {"culture": "maya"}, req_id=20)
    assert exc.value.code == -32602

    with pytest.raises(RpcError) as exc:
        _call("convert", {"jdn": 2451545, "culture": "invalid"}, req_id=21)
    assert exc.value.code == -32602

    with pytest.raises(RpcError) as exc:
        _call("convert", {"jdn": 2451545, "preset": "nope"}, req_id=22)
    assert exc.value.code == -32602

    with pytest.raises(RpcError) as exc:
        _call("convert", {"jdn": 2451545, "year_bearer_month": 0}, req_id=23)
    assert exc.value.code == -32602


def test_list_correlations_non_empty():
    result = _call("list_correlations", {}, req_id=24)
    assert "presets" in result
    assert isinstance(result["presets"], list)
    assert len(result["presets"]) > 0
    assert "name" in result["presets"][0]


def test_derive_autocorr_success():
    conv = _call("convert", {"jdn": 2451545}, req_id=25)
    comp = conv["composite"]
    tz_spec = f"{comp['tzolkin_value']} {comp['tzolkin_name']}"
    result = _call("derive_autocorr", {"jdn": 2451545, "tzolkin": tz_spec}, req_id=26)
    assert "autocorr" in result
    assert "tzolkin_offset" in result["autocorr"]


def test_search_range_fields_variants_and_invalid_type():
    by_string = _call(
        "search_range",
        {"start": 2451545, "end": 2451548, "fields": "jdn,tzolkin_name", "limit": 1},
        req_id=27,
    )
    assert by_string["fields"] == ["jdn", "tzolkin_name"]

    by_list = _call(
        "search_range",
        {"start": 2451545, "end": 2451548, "fields": ["jdn", "haab_month_name"], "limit": 1},
        req_id=28,
    )
    assert by_list["fields"] == ["jdn", "haab_month_name"]

    with pytest.raises(RpcError) as exc:
        _call("search_range", {"start": 2451545, "end": 2451548, "fields": 123}, req_id=29)
    assert exc.value.code == -32602


def test_search_range_normalizes_negative_step_and_limit():
    result = _call(
        "search_range",
        {"start": 2451545, "end": 2451550, "step": -5, "limit": -1},
        req_id=30,
    )
    assert result["count"] >= 0
    assert result["scanned"] >= 1


def test_convert_corrections_validation_and_state_restore():
    with pytest.raises(RpcError) as exc:
        _call(
            "convert",
            {"jdn": 2451545, "corrections": {"tzolkin": "bad-int"}},
            req_id=31,
        )
    assert exc.value.code == -32602

    baseline = _call("convert", {"jdn": 2451545}, req_id=32)
    first = _call(
        "convert",
        {"jdn": 2451545, "corrections": {"tzolkin": 11, "week": 3, "c819_station": 2}},
        req_id=33,
    )
    second = _call("convert", {"jdn": 2451545}, req_id=34)
    # Correction-modified call should differ from baseline.
    assert first["composite"]["tzolkin_value"] != baseline["composite"]["tzolkin_value"]
    # Ensure temporary corrections do not leak across calls.
    assert second["composite"]["tzolkin_value"] == baseline["composite"]["tzolkin_value"]


def test_search_range_with_composite_and_early_filters():
    conv = _call("convert", {"jdn": 2451545}, req_id=35)
    comp = conv["composite"]
    long_count = ".".join(str(x) for x in comp["long_count"])
    params = {
        "start": 2451545,
        "end": 2451545,
        "haab_day": comp["haab_day"],
        "haab_month": comp["haab_month_name"],
        "year_bearer_name": comp["year_bearer_name"],
        "long_count": long_count,
        "dir_color": comp["dir_color_str"],
        "weekday": comp["iso_weekday"],
        "fields": ["jdn", "year_bearer_name", "dir_color_str"],
    }
    result = _call("search_range", params, req_id=36)
    assert result["count"] == 1
    assert result["rows"][0]["jdn"] == 2451545

    # Exercise wildcard pattern branch (non-match).
    miss = _call(
        "search_range",
        {"start": 2451545, "end": 2451545, "long_count": "99.*.*.*.*.*"},
        req_id=37,
    )
    assert miss["count"] == 0


def test_handle_request_quit_and_error_id_passthrough():
    response, should_quit = handle_request_object(
        {"jsonrpc": "2.0", "id": 40, "method": "quit", "params": {}}
    )
    assert should_quit is True
    assert response["result"]["status"] == "bye"

    with pytest.raises(RpcError) as exc:
        handle_request_object({"jsonrpc": "2.0", "id": "abc", "method": "", "params": {}})
    assert exc.value.code == -32600
    assert exc.value.data == {"id": "abc"}


def test_stdio_protocol_invalid_request_and_unknown_method_errors():
    payload = "\n".join(
        [
            '{"jsonrpc":"2.0","id":"x","method":"","params":{}}',
            '{"jsonrpc":"2.0","id":7,"method":"nope","params":{}}',
            '{"jsonrpc":"2.0","id":8,"method":"quit","params":{}}',
            "",
        ]
    )
    proc = subprocess.run(
        [sys.executable, "-m", "pohualli.rpc"],
        input=payload,
        text=True,
        capture_output=True,
        check=True,
    )
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    assert len(lines) == 3
    r0 = json.loads(lines[0])
    r1 = json.loads(lines[1])
    r2 = json.loads(lines[2])
    assert r0["id"] == "x"
    assert r0["error"]["code"] == -32600
    assert r1["id"] == 7
    assert r1["error"]["code"] == -32601
    assert r2["result"]["status"] == "bye"


def test_internal_int_and_str_validators():
    with pytest.raises(RpcError) as exc:
        rpcmod._as_int({"x": None}, "x", required=True)
    assert exc.value.code == -32602

    with pytest.raises(RpcError) as exc:
        rpcmod._as_int({"x": "abc"}, "x")
    assert exc.value.code == -32602

    with pytest.raises(RpcError) as exc:
        rpcmod._as_str({}, "x", required=True)
    assert exc.value.code == -32602

    with pytest.raises(RpcError) as exc:
        rpcmod._as_str({"x": None}, "x", required=True)
    assert exc.value.code == -32602

    with pytest.raises(RpcError) as exc:
        rpcmod._as_str({"x": 5}, "x")
    assert exc.value.code == -32602


def test_apply_context_overrides_year_bearer_and_corrections_validation():
    snap = rpcmod._snapshot_state()
    try:
        rpcmod._apply_context_overrides({"year_bearer_month": 1, "year_bearer_day": 2})
        assert rpcmod.DEFAULT_CONFIG.year_bearer_str == 1
        assert rpcmod.DEFAULT_CONFIG.year_bearer_val == 2
    finally:
        rpcmod._restore_state(snap)

    with pytest.raises(RpcError) as exc:
        rpcmod._apply_context_overrides({"corrections": "bad"})
    assert exc.value.code == -32602

    # Unknown corrections keys are ignored by design.
    rpcmod._apply_context_overrides({"corrections": {"unknown_field": 1}})


def test_match_long_count_length_mismatch():
    assert rpcmod._match_long_count(["1", "2"], (1, 2, 3)) is False


def test_search_range_filter_mismatch_paths():
    jdn = 2451545
    comp = compute_composite(jdn).to_dict()

    # Tzolkin name mismatch
    res = _call(
        "search_range",
        {"start": jdn, "end": jdn, "tzolkin_name": "definitely-not-a-name"},
        req_id=41,
    )
    assert res["count"] == 0

    # Haab day mismatch
    res = _call(
        "search_range",
        {"start": jdn, "end": jdn, "haab_day": comp["haab_day"] + 1},
        req_id=42,
    )
    assert res["count"] == 0

    # Haab month mismatch
    res = _call(
        "search_range",
        {"start": jdn, "end": jdn, "haab_month": "notamonth"},
        req_id=43,
    )
    assert res["count"] == 0

    # Year bearer mismatch
    res = _call(
        "search_range",
        {"start": jdn, "end": jdn, "year_bearer_name": "notaname"},
        req_id=44,
    )
    assert res["count"] == 0

    # Composite-only filters mismatch paths
    res = _call(
        "search_range",
        {"start": jdn, "end": jdn, "dir_color": "nonexistent-color"},
        req_id=45,
    )
    assert res["count"] == 0

    res = _call(
        "search_range",
        {"start": jdn, "end": jdn, "weekday": 7 if comp["iso_weekday"] != 7 else 6},
        req_id=46,
    )
    assert res["count"] == 0


def test_health_and_params_none():
    response, should_quit = handle_request_object(
        {"jsonrpc": "2.0", "id": 50, "method": "health", "params": None}
    )
    assert should_quit is False
    assert response["result"]["status"] == "ok"


def test_main_writes_rpc_error_response(monkeypatch):
    fake_in = io.StringIO('{"jsonrpc":"2.0","id":55,"method":"","params":{}}\n')
    fake_out = io.StringIO()
    monkeypatch.setattr(sys, "stdin", fake_in)
    monkeypatch.setattr(sys, "stdout", fake_out)

    rpcmod.main()
    lines = [line for line in fake_out.getvalue().splitlines() if line.strip()]
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["id"] == 55
    assert payload["error"]["code"] == -32600


def test_main_writes_internal_error_response(monkeypatch):
    fake_in = io.StringIO('{"jsonrpc":"2.0","id":77,"method":"health","params":{}}\n')
    fake_out = io.StringIO()
    monkeypatch.setattr(sys, "stdin", fake_in)
    monkeypatch.setattr(sys, "stdout", fake_out)

    def boom(_: object):
        raise RuntimeError("boom")

    monkeypatch.setattr(rpcmod, "handle_request_object", boom)
    rpcmod.main()
    payload = json.loads(fake_out.getvalue().strip())
    assert payload["id"] == 77
    assert payload["error"]["code"] == -32603
    assert "detail" in payload["error"]["data"]


def test_search_range_swaps_start_and_end():
    result = _call("search_range", {"start": 2451550, "end": 2451545}, req_id=60)
    assert result["scanned"] >= 1
