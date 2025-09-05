# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations
import argparse, json
from .correlations import list_presets, apply_preset
from . import (
    julian_day_to_tzolkin_value, julian_day_to_tzolkin_name_index,
    julian_day_to_haab_packed, unpack_haab_month, unpack_haab_value,
    julian_day_to_long_count, tzolkin_number_to_name, haab_number_to_name,
    year_bearer_packed, DEFAULT_CONFIG, compute_composite, save_config, load_config
)
from .types import ABSOLUTE
from .autocorr import derive_auto_corrections

def format_long_count(lc):
    return ".".join(str(x) for x in lc)

def main(argv=None):
    p = argparse.ArgumentParser(prog="pohualli", description="Mesoamerican calendar conversions")
    sub = p.add_subparsers(dest="cmd", required=True)
    conv = sub.add_parser("from-jdn", help="Convert a Julian Day Number")
    conv.add_argument("jdn", type=int)
    conv.add_argument("--year-bearer-ref", nargs=2, type=int, metavar=("MONTH","DAY"), help="Reference Year Bearer Haab month/day (default from config)")
    conv.add_argument("--new-era", type=int, help="Override New Era (base JDN for Long Count)")
    conv.add_argument("--json", action='store_true', help="Output JSON composite result")
    conv.add_argument("--culture", choices=['maya','aztec'], help="Year bearer culture; Aztec mode subtracts 364 days before deriving bearer (default Maya)")
    confs = sub.add_parser("save-config", help="Save current configuration to file")
    confs.add_argument("path", help="Path to JSON config file")
    confl = sub.add_parser("load-config", help="Load configuration from file")
    confl.add_argument("path", help="Path to JSON config file")
    corr_list = sub.add_parser('list-correlations', help='List available correlation presets')
    corr_apply = sub.add_parser('apply-correlation', help='Apply a correlation preset')
    corr_apply.add_argument('name', help='Preset name (see list-correlations)')
    ac = sub.add_parser('derive-autocorr', help='Brute-force derive correction offsets from a target date and specs')
    ac.add_argument('jdn', type=int)
    ac.add_argument('--tzolkin')
    ac.add_argument('--haab')
    ac.add_argument('--g', type=int)
    ac.add_argument('--long-count')
    ac.add_argument('--year-bearer')
    ac.add_argument('--cycle819-station', type=int)
    ac.add_argument('--cycle819-value', type=int)
    ac.add_argument('--dir-color')
    # --- range search ---
    sr = sub.add_parser('search-range', help='Scan an inclusive JDN range and filter matching calendrical criteria')
    sr.add_argument('start', type=int, help='Start JDN (inclusive)')
    sr.add_argument('end', type=int, help='End JDN (inclusive)')
    sr.add_argument('--tzolkin-value', type=int, help='Filter: Tzolkin value (1..13)')
    sr.add_argument('--tzolkin-name', help='Filter: Tzolkin day name (case-insensitive)')
    sr.add_argument('--haab-day', type=int, help='Filter: Haab day number (0..19 Maya / 1..20 Aztec)')
    sr.add_argument('--haab-month', help='Filter: Haab month name (case-insensitive)')
    sr.add_argument('--year-bearer-name', help='Filter: Year bearer Tzolkin name (case-insensitive)')
    sr.add_argument('--dir-color', help='Filter: Direction/Color string (substring match)')
    sr.add_argument('--weekday', type=int, choices=list(range(1,8)), help='Filter: ISO weekday (1=Mon .. 7=Sun)')
    sr.add_argument('--long-count', help="Filter: Long Count pattern e.g. '13.*.*.*.*.*' (use * as wildcard segment)")
    sr.add_argument('--limit', type=int, help='Stop after this many matches')
    sr.add_argument('--json-lines', action='store_true', help='Output JSON per line instead of table')
    sr.add_argument('--fields', help='Comma list of fields for table output (default preset)')
    sr.add_argument('--progress-every', type=int, default=0, help='Emit a progress line every N days scanned (stderr)')
    sr.add_argument('--step', type=int, default=1, help='Increment JDN by this step (default 1)')
    sr.add_argument('--perf-stats', action='store_true', help='Emit performance stats (stderr) at end: scanned vs composite calls')
    sr.add_argument('--culture', choices=['maya','aztec'], help='Year bearer culture toggle (affects year bearer derivation)')
    args = p.parse_args(argv)

    if args.cmd == "from-jdn":
        jdn = args.jdn
        if args.new_era is not None:
            ABSOLUTE.new_era = args.new_era
        if args.year_bearer_ref:
            DEFAULT_CONFIG.year_bearer_str, DEFAULT_CONFIG.year_bearer_val = args.year_bearer_ref
        if getattr(args, 'culture', None):
            DEFAULT_CONFIG.t_aztec = (args.culture == 'aztec')
        if args.json:
            comp = compute_composite(jdn)
            print(json.dumps(comp.to_dict(), indent=2, sort_keys=True))
        else:
            # Retain legacy textual output
            tzv = julian_day_to_tzolkin_value(jdn)
            tzn_idx = julian_day_to_tzolkin_name_index(jdn)
            haab_packed = julian_day_to_haab_packed(jdn)
            haab_month = unpack_haab_month(haab_packed)
            haab_day = unpack_haab_value(haab_packed)
            lc = julian_day_to_long_count(jdn)
            yb = year_bearer_packed(haab_month, haab_day, jdn)
            print(f"JDN {jdn}")
            print(f"Tzolkin: {tzv} {tzolkin_number_to_name(tzn_idx)} (val={tzv}, nameIndex={tzn_idx})")
            print(f"Haab: {haab_day} {haab_number_to_name(haab_month)} (monthIndex={haab_month})")
            print(f"Long Count: {'.'.join(str(x) for x in lc)} (NewEra={ABSOLUTE.new_era})")
            print(f"Year Bearer packed: 0x{yb:04X} (nameIndex={yb>>8}, value={yb & 0xFF})")
            print(f"Year Bearer culture: {'Aztec' if DEFAULT_CONFIG.t_aztec else 'Maya'}" + (" (Aztec mode uses interval-364 adjustment)" if DEFAULT_CONFIG.t_aztec else ""))
    elif args.cmd == "save-config":
        save_config(args.path)
    elif args.cmd == "load-config":
        load_config(args.path)
    elif args.cmd == 'list-correlations':
        for pset in list_presets():
            print(f"{pset.name}\t{pset.new_era}\t{pset.description}")
    elif args.cmd == 'apply-correlation':
        preset = apply_preset(args.name)
        print(f"Applied correlation '{preset.name}' (New Era={preset.new_era})")
    elif args.cmd == 'derive-autocorr':
        res = derive_auto_corrections(
            args.jdn,
            tzolkin=args.tzolkin,
            haab=args.haab,
            g_value=args.g,
            long_count=args.long_count,
            year_bearer=args.year_bearer,
            cycle819_station=args.cycle819_station,
            cycle819_value=args.cycle819_value,
            dir_color=args.dir_color,
        )
        print(json.dumps(res.__dict__, indent=2, sort_keys=True))
    elif args.cmd == 'search-range':
        start, end = args.start, args.end
        if start > end:
            start, end = end, start
        step = args.step if args.step and args.step > 0 else 1
        if getattr(args, 'culture', None):
            DEFAULT_CONFIG.t_aztec = (args.culture == 'aztec')
        # Prepare filters (lowercased for case-insensitive)
        tz_name = args.tzolkin_name.lower() if args.tzolkin_name else None
        haab_month = args.haab_month.lower() if args.haab_month else None
        yb_name = args.year_bearer_name.lower() if args.year_bearer_name else None
        dir_color_f = args.dir_color.lower() if args.dir_color else None
        lc_pattern = args.long_count.split('.') if args.long_count else None
        def match_lc(lc_tuple):
            if not lc_pattern:
                return True
            if len(lc_pattern) != len(lc_tuple):
                return False
            for pat, val in zip(lc_pattern, lc_tuple):
                if pat != '*' and pat != str(val):
                    return False
            return True
        # Choose output fields
        default_fields = ['jdn','gregorian_date','tzolkin_value','tzolkin_name','haab_day','haab_month_name','long_count','year_bearer_name','dir_color_str']
        fields = [f.strip() for f in (args.fields.split(',') if args.fields else default_fields)]
        count = 0
        total = ((end - start) // step) + 1
        composite_calls = 0
        # Iterate range with early (cheap) filters before constructing full composite
        for i, jdn in enumerate(range(start, end+1, step), start=1):
            # Early filtering using individual conversion functions to avoid full composite cost
            # Only compute the pieces actually required by specified filters.
            # Tzolkin filters
            if args.tzolkin_value or tz_name:
                tzv_early = julian_day_to_tzolkin_value(jdn)
                if args.tzolkin_value and tzv_early != args.tzolkin_value:
                    if args.progress_every and (i % args.progress_every == 0):
                        import sys
                        print(f"# progress {i}/{total} ({(i/total)*100:.1f}%) matches={count}", file=sys.stderr)
                    continue
                if tz_name:
                    tzn_idx_early = julian_day_to_tzolkin_name_index(jdn)
                    if tzolkin_number_to_name(tzn_idx_early).lower() != tz_name:
                        if args.progress_every and (i % args.progress_every == 0):
                            import sys
                            print(f"# progress {i}/{total} ({(i/total)*100:.1f}%) matches={count}", file=sys.stderr)
                        continue
            # Haab filters
            need_haab = (args.haab_day is not None) or haab_month or yb_name
            if need_haab:
                haab_packed = julian_day_to_haab_packed(jdn)
                h_month_idx = unpack_haab_month(haab_packed)
                h_day_val = unpack_haab_value(haab_packed)
                if args.haab_day is not None and h_day_val != args.haab_day:
                    if args.progress_every and (i % args.progress_every == 0):
                        import sys
                        print(f"# progress {i}/{total} ({(i/total)*100:.1f}%) matches={count}", file=sys.stderr)
                    continue
                if haab_month and haab_number_to_name(h_month_idx).lower() != haab_month:
                    if args.progress_every and (i % args.progress_every == 0):
                        import sys
                        print(f"# progress {i}/{total} ({(i/total)*100:.1f}%) matches={count}", file=sys.stderr)
                    continue
                if yb_name:
                    # Year bearer name is derived from haab month/day and JDN
                    yb = year_bearer_packed(h_month_idx, h_day_val, jdn)
                    yb_name_early = tzolkin_number_to_name(yb >> 8).lower()
                    if yb_name_early != yb_name:
                        if args.progress_every and (i % args.progress_every == 0):
                            import sys
                            print(f"# progress {i}/{total} ({(i/total)*100:.1f}%) matches={count}", file=sys.stderr)
                        continue
            # Long Count filter (pattern) early
            if lc_pattern:
                lc_early = julian_day_to_long_count(jdn)
                if not match_lc(lc_early):
                    if args.progress_every and (i % args.progress_every == 0):
                        import sys
                        print(f"# progress {i}/{total} ({(i/total)*100:.1f}%) matches={count}", file=sys.stderr)
                    continue
            # At this point all early filters passed; build composite (expensive) only once
            comp = compute_composite(jdn)
            composite_calls += 1
            # Remaining filters that currently require composite fields
            if dir_color_f and dir_color_f not in comp.dir_color_str.lower():
                continue
            if args.weekday and comp.iso_weekday != args.weekday:
                continue
            # (Long count was already evaluated if pattern provided)
            count += 1
            if args.json_lines:
                print(json.dumps(comp.to_dict(), sort_keys=True))
            else:
                row_vals = []
                for f in fields:
                    v = getattr(comp, f, '')
                    if isinstance(v, (list, tuple)):
                        v = '.'.join(str(x) for x in v)
                    row_vals.append(str(v))
                if count == 1 and not args.json_lines:
                    print('\t'.join(fields))
                print('\t'.join(row_vals))
            if args.limit and count >= args.limit:
                break
            if args.progress_every and (i % args.progress_every == 0):
                import sys
                print(f"# progress {i}/{total} ({(i/total)*100:.1f}%) matches={count}", file=sys.stderr)
        # If no matches and not JSON mode, optionally print header
        if count == 0 and not args.json_lines:
            print("# no matches")
        if args.perf_stats:
            import sys
            scanned = ((end - start) // step) + 1
            saved = scanned - composite_calls
            print(f"# perf scanned={scanned} composite_calls={composite_calls} saved={saved} matches={count}", file=sys.stderr)

if __name__ == "__main__":  # pragma: no cover
    main()
