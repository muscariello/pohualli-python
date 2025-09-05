# CLI Usage

## Core Commands

```bash
pohualli from-jdn 2451545                # Human readable
pohualli from-jdn 2451545 --json         # JSON composite
pohualli save-config config.json         # Persist current correlation & offsets
pohualli load-config config.json         # Restore saved configuration
pohualli list-correlations               # List preset correlations
pohualli apply-correlation gmt-584283    # Activate a preset
pohualli derive-autocorr 2451545 --tzolkin "4 Ahau"  # Solve offsets from constraints
```

Common flags:
- `--new-era <JDN>`: Override correlation for one invocation.
- `--year-bearer-ref <month> <day>`: Set reference Haab month/day for year bearer.
- `--culture {maya|aztec}`: Toggle year bearer culture logic.
- `--json`: Return JSON instead of textual output.

## Range Search (search-range)

Scan an inclusive Julian Day Number interval with multiple calendrical filters. Early, cheap filters are applied before computing full composites for performance.

```
pohualli search-range <start> <end> [filters...] [options...]
```

### Filters
All are optional; combine freely (logical AND):
- `--tzolkin-value N`          Tzolk'in number (1–13)
- `--tzolkin-name NAME`        Tzolk'in day name (case-insensitive)
- `--haab-day N`               Haab day number
- `--haab-month NAME`          Haab month name
- `--year-bearer-name NAME`    Year bearer Tzolk'in name
- `--dir-color SUBSTR`         Direction/Color substring (e.g. `Sur`, `norte`)
- `--weekday K`                ISO weekday (1=Mon .. 7=Sun)
- `--long-count PATTERN`       Pattern like `9.*.*.*.*.*` (`*` wildcard per component)

### Output Control
- `--fields a,b,c`     Comma list of columns (default full preset)
- `--limit N`          Stop after N matches (0 = no limit)
- `--json-lines`       Emit one JSON object per matching line (omit header)

### Performance / Diagnostics
- `--step S`             Increment JDN by S (default 1)
- `--progress-every N`   Write progress lines to stderr every N scanned days
- `--perf-stats`         Emit final stats: scanned, composite_calls, saved, matches

`composite_calls` counts how many full composites were built after early filters passed. `saved` shows how many composites were avoided due to early rejections (efficiency gain).

### Examples
```bash
# First 5 Imix dates in range
pohualli search-range 584283 584800 --tzolkin-name Imix --limit 5

# Tzolk'in value + Haab month intersection
pohualli search-range 500000 500400 --tzolkin-value 4 --haab-month Kumku --limit 3

# Long Count pattern (wildcards)
pohualli search-range 600000 610000 --long-count '9.*.*.*.*.*' --limit 2

# JSON lines (machine friendly)
pohualli search-range 584283 584350 --tzolkin-value 1 --json-lines --limit 2

# Custom columns
pohualli search-range 584283 584400 --fields jdn,tzolkin_name,haab_month_name --limit 3

# Aztec culture (affects year bearer derivation only)
pohualli search-range 584283 584500 --culture aztec --tzolkin-value 7 --limit 2

# Progress + perf stats
pohualli search-range 584283 584600 --tzolkin-value 5 --progress-every 100 --perf-stats --limit 10
```

### Exit Codes and Behavior
- Returns 0 on success (even with zero matches).
- Prints `# no matches` (table mode) when no rows match.
- In JSON lines mode zero matches produce no output lines.

### Performance Tips
- Put the most selective early filters first conceptually (e.g. Tzolk'in / Haab / Long Count). All early filters are cheap and reduce composite builds.
- Use `--step` for coarse sampling when exploring large eras.
- Combine `--progress-every` and `--perf-stats` for long multi-minute scans to track efficiency.

## Deriving Corrections (derive-autocorr)
Provide any subset of constraints (tzolkin, haab, g, long-count, year-bearer, cycle819 station/value, dir-color) plus a baseline JDN. The solver brute-forces minimal offset set producing those targets.

Example:
```bash
pohualli derive-autocorr 2451545 --tzolkin "4 Ahau" --haab "3 Pop" --g 5
```
Outputs JSON with fields like `tzolkin_offset`, `haab_offset`, `g_offset`, etc.

## Configuration Persistence
```bash
pohualli save-config mycfg.json
pohualli apply-correlation gmt-584283
pohualli load-config mycfg.json   # restores previous offsets & new era
```

## Text vs JSON Conversions
`from-jdn` without `--json` prints human-readable multi-line description; with `--json` returns a full composite including long count tuple, zodiac info, 819-cycle data, and applied correction offsets.

## Troubleshooting
- Zero matches? Relax filters or verify correlation (list/apply a preset).
- Unexpected Year Bearer? Check `--culture` and reference via `--year-bearer-ref`.
- Long Count pattern never matches: ensure the number of components matches internal representation (6 segments).

