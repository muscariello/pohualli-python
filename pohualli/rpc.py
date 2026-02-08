"""JSON-RPC bridge over stdin/stdout for native desktop frontends.

This module is designed for Flutter desktop integration (Option B):
the UI starts a long-lived Python process and exchanges newline-delimited
JSON-RPC request/response objects over stdio.
"""

from __future__ import annotations

import copy
import json
import sys
from dataclasses import asdict
from typing import Any

from . import (
    apply_preset,
    compute_composite,
    derive_auto_corrections,
    haab_number_to_name,
    julian_day_to_haab_packed,
    julian_day_to_long_count,
    julian_day_to_tzolkin_name_index,
    julian_day_to_tzolkin_value,
    list_presets,
    tzolkin_number_to_name,
    unpack_haab_month,
    unpack_haab_value,
    year_bearer_packed,
)
from . import correlations
from .types import ABSOLUTE, CORRECTIONS, DEFAULT_CONFIG


class RpcError(Exception):
    def __init__(self, code: int, message: str, data: Any | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


_ERR_PARSE = -32700
_ERR_INVALID_REQUEST = -32600
_ERR_METHOD_NOT_FOUND = -32601
_ERR_INVALID_PARAMS = -32602
_ERR_INTERNAL = -32603


def _require_params_dict(params: Any) -> dict[str, Any]:
    if params is None:
        return {}
    if not isinstance(params, dict):
        raise RpcError(_ERR_INVALID_PARAMS, "params must be an object")
    return params


def _as_int(params: dict[str, Any], key: str, *, required: bool = False, default: int | None = None) -> int | None:
    if key not in params:
        if required:
            raise RpcError(_ERR_INVALID_PARAMS, f"missing required param '{key}'")
        return default
    value = params[key]
    if value is None:
        if required:
            raise RpcError(_ERR_INVALID_PARAMS, f"param '{key}' cannot be null")
        return default
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise RpcError(_ERR_INVALID_PARAMS, f"param '{key}' must be an integer") from exc


def _as_str(params: dict[str, Any], key: str, *, required: bool = False) -> str | None:
    if key not in params:
        if required:
            raise RpcError(_ERR_INVALID_PARAMS, f"missing required param '{key}'")
        return None
    value = params[key]
    if value is None:
        if required:
            raise RpcError(_ERR_INVALID_PARAMS, f"param '{key}' cannot be null")
        return None
    if not isinstance(value, str):
        raise RpcError(_ERR_INVALID_PARAMS, f"param '{key}' must be a string")
    return value


def _snapshot_state() -> dict[str, Any]:
    return {
        "absolute": copy.deepcopy(vars(ABSOLUTE)),
        "config": copy.deepcopy(vars(DEFAULT_CONFIG)),
        "config_correction": copy.deepcopy(vars(DEFAULT_CONFIG.tzolkin_haab_correction)),
        "corrections": copy.deepcopy(vars(CORRECTIONS)),
        "active_preset": correlations.active_preset_name(),
    }


def _restore_state(snapshot: dict[str, Any]) -> None:
    for key, value in snapshot["absolute"].items():
        setattr(ABSOLUTE, key, value)
    for key, value in snapshot["config"].items():
        if key == "tzolkin_haab_correction":
            continue
        setattr(DEFAULT_CONFIG, key, value)
    for key, value in snapshot["config_correction"].items():
        setattr(DEFAULT_CONFIG.tzolkin_haab_correction, key, value)
    for key, value in snapshot["corrections"].items():
        setattr(CORRECTIONS, key, value)
    setattr(correlations, "_ACTIVE_PRESET", snapshot["active_preset"])


def _apply_context_overrides(params: dict[str, Any]) -> None:
    preset = _as_str(params, "preset")
    if preset:
        try:
            apply_preset(preset)
        except KeyError as exc:
            raise RpcError(_ERR_INVALID_PARAMS, f"unknown preset '{preset}'") from exc

    new_era = _as_int(params, "new_era")
    if new_era is not None:
        ABSOLUTE.new_era = new_era

    yb_month = _as_int(params, "year_bearer_month")
    yb_day = _as_int(params, "year_bearer_day")
    if (yb_month is None) ^ (yb_day is None):
        raise RpcError(
            _ERR_INVALID_PARAMS,
            "year_bearer_month and year_bearer_day must both be provided",
        )
    if yb_month is not None and yb_day is not None:
        DEFAULT_CONFIG.year_bearer_str = yb_month
        DEFAULT_CONFIG.year_bearer_val = yb_day

    culture = _as_str(params, "culture")
    if culture is not None:
        culture_l = culture.lower()
        if culture_l not in {"maya", "aztec"}:
            raise RpcError(_ERR_INVALID_PARAMS, "culture must be 'maya' or 'aztec'")
        DEFAULT_CONFIG.t_aztec = culture_l == "aztec"

    corrections = params.get("corrections")
    if corrections is not None:
        if not isinstance(corrections, dict):
            raise RpcError(_ERR_INVALID_PARAMS, "corrections must be an object")
        mapping = {
            "tzolkin": ("cfg", "tzolkin"),
            "haab": ("cfg", "haab"),
            "g": ("cfg", "g"),
            "lcd": ("cfg", "lcd"),
            "tzolkin_name": ("corr", "cTzolkinStr"),
            "week": ("corr", "cWeekCorrection"),
            "c819_station": ("cfg_direct", "cycle819_station_correction"),
            "c819_dir": ("cfg_direct", "cycle819_dir_color_correction"),
        }
        for key, value in corrections.items():
            if key not in mapping:
                continue
            try:
                int_value = int(value)
            except (TypeError, ValueError) as exc:
                raise RpcError(_ERR_INVALID_PARAMS, f"corrections.{key} must be an integer") from exc
            target, field = mapping[key]
            if target == "cfg":
                setattr(DEFAULT_CONFIG.tzolkin_haab_correction, field, int_value)
            elif target == "corr":
                setattr(CORRECTIONS, field, int_value)
            else:
                setattr(DEFAULT_CONFIG, field, int_value)


def _handle_health(_: dict[str, Any]) -> dict[str, Any]:
    return {"status": "ok"}


def _handle_list_correlations(_: dict[str, Any]) -> dict[str, Any]:
    return {"presets": [asdict(preset) for preset in list_presets()]}


def _handle_convert(params: dict[str, Any]) -> dict[str, Any]:
    snapshot = _snapshot_state()
    try:
        _apply_context_overrides(params)
        jdn = _as_int(params, "jdn", required=True)
        assert jdn is not None  # appease type checker
        comp = compute_composite(jdn).to_dict()
        return {
            "composite": comp,
            "context": {
                "new_era": ABSOLUTE.new_era,
                "culture": "aztec" if DEFAULT_CONFIG.t_aztec else "maya",
                "active_preset": correlations.active_preset_name(),
            },
        }
    finally:
        _restore_state(snapshot)


def _handle_derive_autocorr(params: dict[str, Any]) -> dict[str, Any]:
    snapshot = _snapshot_state()
    try:
        _apply_context_overrides(params)
        jdn = _as_int(params, "jdn", required=True)
        assert jdn is not None
        result = derive_auto_corrections(
            jdn,
            tzolkin=_as_str(params, "tzolkin"),
            haab=_as_str(params, "haab"),
            g_value=_as_int(params, "g"),
            long_count=_as_str(params, "long_count"),
            year_bearer=_as_str(params, "year_bearer"),
            cycle819_station=_as_int(params, "cycle819_station"),
            cycle819_value=_as_int(params, "cycle819_value"),
            dir_color=_as_str(params, "dir_color"),
        )
        return {"autocorr": result.__dict__}
    finally:
        _restore_state(snapshot)


def _match_long_count(pattern: list[str] | None, value: tuple[int, ...]) -> bool:
    if not pattern:
        return True
    if len(pattern) != len(value):
        return False
    for pat, segment in zip(pattern, value):
        if pat != "*" and pat != str(segment):
            return False
    return True


def _resolve_fields(raw_fields: Any) -> list[str]:
    default_fields = [
        "jdn",
        "gregorian_date",
        "tzolkin_value",
        "tzolkin_name",
        "haab_day",
        "haab_month_name",
        "long_count",
        "year_bearer_name",
        "dir_color_str",
    ]
    if raw_fields is None:
        return default_fields
    if isinstance(raw_fields, str):
        out = [field.strip() for field in raw_fields.split(",") if field.strip()]
        return out or default_fields
    if isinstance(raw_fields, list):
        out = [str(field).strip() for field in raw_fields if str(field).strip()]
        return out or default_fields
    raise RpcError(_ERR_INVALID_PARAMS, "fields must be a comma-separated string or array")


def _handle_search_range(params: dict[str, Any]) -> dict[str, Any]:
    snapshot = _snapshot_state()
    try:
        _apply_context_overrides(params)
        start = _as_int(params, "start", required=True)
        end = _as_int(params, "end", required=True)
        assert start is not None and end is not None
        if end < start:
            start, end = end, start
        step = _as_int(params, "step", default=1) or 1
        if step <= 0:
            step = 1
        limit = _as_int(params, "limit", default=0) or 0
        if limit < 0:
            limit = 0

        tzolkin_value = _as_int(params, "tzolkin_value")
        tzolkin_name = _as_str(params, "tzolkin_name")
        haab_day = _as_int(params, "haab_day")
        haab_month = _as_str(params, "haab_month")
        yb_name = _as_str(params, "year_bearer_name")
        dir_color = _as_str(params, "dir_color")
        weekday = _as_int(params, "weekday")
        long_count = _as_str(params, "long_count")
        lc_pattern = long_count.split(".") if long_count else None
        fields = _resolve_fields(params.get("fields"))

        tzolkin_name_l = tzolkin_name.lower() if tzolkin_name else None
        haab_month_l = haab_month.lower() if haab_month else None
        yb_name_l = yb_name.lower() if yb_name else None
        dir_color_l = dir_color.lower() if dir_color else None

        rows: list[dict[str, Any]] = []
        scanned = 0
        for jdn in range(start, end + 1, step):
            scanned += 1
            if tzolkin_value is not None or tzolkin_name_l:
                tz_val = julian_day_to_tzolkin_value(jdn)
                if tzolkin_value is not None and tz_val != tzolkin_value:
                    continue
                if tzolkin_name_l:
                    tz_idx = julian_day_to_tzolkin_name_index(jdn)
                    if tzolkin_number_to_name(tz_idx).lower() != tzolkin_name_l:
                        continue
            if haab_day is not None or haab_month_l or yb_name_l:
                packed = julian_day_to_haab_packed(jdn)
                month = unpack_haab_month(packed)
                day = unpack_haab_value(packed)
                if haab_day is not None and day != haab_day:
                    continue
                if haab_month_l and haab_number_to_name(month).lower() != haab_month_l:
                    continue
                if yb_name_l:
                    yb = year_bearer_packed(month, day, jdn)
                    if tzolkin_number_to_name(yb >> 8).lower() != yb_name_l:
                        continue
            if lc_pattern:
                lc = julian_day_to_long_count(jdn)
                if not _match_long_count(lc_pattern, lc):
                    continue

            comp = compute_composite(jdn)
            if dir_color_l and dir_color_l not in comp.dir_color_str.lower():
                continue
            if weekday is not None and comp.iso_weekday != weekday:
                continue

            row: dict[str, Any] = {}
            for field in fields:
                value = getattr(comp, field, "")
                if isinstance(value, (tuple, list)):
                    value = ".".join(str(v) for v in value)
                row[field] = value
            rows.append(row)
            if limit and len(rows) >= limit:
                break

        return {"rows": rows, "count": len(rows), "scanned": scanned, "fields": fields}
    finally:
        _restore_state(snapshot)


def _dispatch(method: str, params: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if method == "health":
        return _handle_health(params), False
    if method == "list_correlations":
        return _handle_list_correlations(params), False
    if method == "convert":
        return _handle_convert(params), False
    if method == "derive_autocorr":
        return _handle_derive_autocorr(params), False
    if method == "search_range":
        return _handle_search_range(params), False
    if method == "quit":
        return {"status": "bye"}, True
    raise RpcError(_ERR_METHOD_NOT_FOUND, f"method '{method}' not found")


def handle_request_object(request: Any) -> tuple[dict[str, Any], bool]:
    if not isinstance(request, dict):
        raise RpcError(_ERR_INVALID_REQUEST, "request must be an object")
    request_id = request.get("id")
    method = request.get("method")
    if not isinstance(method, str) or not method:
        raise RpcError(_ERR_INVALID_REQUEST, "request must include string method", data={"id": request_id})
    params = _require_params_dict(request.get("params"))
    result, should_quit = _dispatch(method, params)
    return {"jsonrpc": "2.0", "id": request_id, "result": result}, should_quit


def _error_response(error: RpcError, request_id: Any = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": error.code, "message": error.message},
    }
    if error.data is not None:
        payload["error"]["data"] = error.data
    return payload


def main() -> None:
    should_quit = False
    while not should_quit:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        req_id = None
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                req_id = obj.get("id")
            response, should_quit = handle_request_object(obj)
        except json.JSONDecodeError:
            response = _error_response(RpcError(_ERR_PARSE, "invalid JSON"), None)
        except RpcError as rpc_error:
            req_id = rpc_error.data.get("id") if isinstance(rpc_error.data, dict) and "id" in rpc_error.data else req_id
            response = _error_response(rpc_error, req_id)
        except Exception as exc:  # pragma: no cover - unexpected
            response = _error_response(
                RpcError(_ERR_INTERNAL, "internal error", {"detail": str(exc)}),
                req_id,
            )
        sys.stdout.write(json.dumps(response, sort_keys=True) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":  # pragma: no cover
    main()
