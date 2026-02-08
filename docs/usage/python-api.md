# Python API

Primary entry point:

`compute_composite(jdn: int) -> CompositeResult`

Example:

```python
from pohualli import compute_composite

res = compute_composite(2451545)
print(res.tzolkin_value, res.tzolkin_name, res.long_count)
```

`CompositeResult` includes (selected):

- `tzolkin_value`, `tzolkin_name`
- `haab_day`, `haab_month_name`
- `long_count`
- `year_bearer_value`, `year_bearer_name`
- `cycle819_station`, `dir_color_str`
- planetary indices (`mercury_index`, `venus_index`, etc.)
- `maya_moon_age`, `eclipse_possible`
- `star_zodiac_deg`, `star_zodiac_name`

Configuration objects are in `pohualli.types` (for example `DEFAULT_CONFIG`).

## JSON-RPC Backend API

The Flutter desktop app communicates with the backend via newline-delimited JSON-RPC over stdin/stdout.

Start backend:

```bash
pohualli-rpc
```

Supported methods:

- `health`
- `list_correlations`
- `convert`
- `derive_autocorr`
- `search_range`
- `quit`

Example request lines:

```json
{"jsonrpc":"2.0","id":1,"method":"health","params":{}}
{"jsonrpc":"2.0","id":2,"method":"convert","params":{"jdn":2451545,"culture":"maya"}}
```
