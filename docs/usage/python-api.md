# Python API

Primary entry point: `compute_composite(jdn: int) -> CompositeResult`.

`CompositeResult` includes (selected):
- `tzolkin_value`, `tzolkin_name`
- `haab_day`, `haab_month_name`
- `long_count`
- `year_bearer_value`, `year_bearer_name`
- `cycle819_station`, `dir_color_str`
- `mercury_index`, `venus_index`, etc.
- `maya_moon_age`, `eclipse_possible`
- `star_zodiac_deg`, `star_zodiac_name`

Configuration objects live in `pohualli.types` (e.g. `DEFAULT_CONFIG`).
