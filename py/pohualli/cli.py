from __future__ import annotations
import argparse, json
from . import (
    julian_day_to_tzolkin_value, julian_day_to_tzolkin_name_index,
    julian_day_to_haab_packed, unpack_haab_month, unpack_haab_value,
    julian_day_to_long_count, tzolkin_number_to_name, haab_number_to_name,
    year_bearer_packed, DEFAULT_CONFIG, compute_composite, save_config, load_config
)
from .types import ABSOLUTE

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
    confs = sub.add_parser("save-config", help="Save current configuration to file")
    confs.add_argument("path", help="Path to JSON config file")
    confl = sub.add_parser("load-config", help="Load configuration from file")
    confl.add_argument("path", help="Path to JSON config file")
    args = p.parse_args(argv)

    if args.cmd == "from-jdn":
        jdn = args.jdn
        if args.new_era is not None:
            ABSOLUTE.new_era = args.new_era
        if args.year_bearer_ref:
            DEFAULT_CONFIG.year_bearer_str, DEFAULT_CONFIG.year_bearer_val = args.year_bearer_ref
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
    elif args.cmd == "save-config":
        save_config(args.path)
    elif args.cmd == "load-config":
        load_config(args.path)

if __name__ == "__main__":  # pragma: no cover
    main()
