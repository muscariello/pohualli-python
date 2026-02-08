import json
import subprocess
import sys

from pohualli.rpc import handle_request_object


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
