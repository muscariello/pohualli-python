from __future__ import annotations
from .maya import julian_day_to_tzolkin_name_index, julian_day_to_tzolkin_value, julian_day_to_tzolkin_name_index as julian_day_to_tzolkin
from .types import DEFAULT_CONFIG
from .types import SheetWindowConfig

# Mirrors Pascal logic from YearBear.pas

def year_bearer_packed(haab_str: int, haab_val: int, jdn: int, *,
                                             config: SheetWindowConfig | None = None,
                                             t_aztec_flag: bool | None = None) -> int:
        """Compute packed year bearer as in Pascal YearBearerPacked.

        Arguments:
            haab_str: Haab month index of the target date
            haab_val: Haab day number of the target date
            jdn: Julian Day Number of the target date
            config: optional config supplying reference year bearer (defaults to global DEFAULT_CONFIG)
            t_aztec_flag: override aztec mode (otherwise from config)

        Returns: 16-bit packed (tzolkinNameIndex << 8) | tzolkinValue
        """
        cfg = config or DEFAULT_CONFIG
        t_aztec = cfg.t_aztec if t_aztec_flag is None else t_aztec_flag
        yb_pack = (cfg.year_bearer_str * 20) + cfg.year_bearer_val
        haab_pack = (haab_str * 20) + haab_val
        interval = haab_pack - yb_pack
        if interval < 0:
                interval += 365
        if t_aztec:
                interval -= 364
        base_jdn = jdn - interval
        tzolkin_name_idx = julian_day_to_tzolkin(base_jdn)
        tzolkin_value = julian_day_to_tzolkin_value(base_jdn)
        return (tzolkin_name_idx << 8) | tzolkin_value


def unpack_yb_str(yb: int) -> int:
    return (yb >> 8) & 0xFF


def unpack_yb_val(yb: int) -> int:
    return yb & 0xFF
