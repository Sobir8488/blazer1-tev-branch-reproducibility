from __future__ import annotations

import numpy as np
import pandas as pd


def compute_score(df: pd.DataFrame, weights: dict) -> pd.DataFrame:
    out = df.copy()
    components = {
        "xray_brightness": ("S_X", +1),
        "gamma_hardness": ("S_gamma_hard", +1),
        "gamma_variability": ("S_gamma_var", +1),
        "wise_hsp_locus": ("S_IR", +1),
        "radio_compactness": ("S_R", +1),
        "synchrotron_peak_proxy": ("S_nu_peak", +1),
        "compton_dominance_penalty": ("S_CD_penalty", -1),
        "ebl_penalty": ("S_EBL_proxy", -1),
    }
    total = pd.Series(0.0, index=out.index)
    available_weight = pd.Series(0.0, index=out.index)
    for key, (col, sign) in components.items():
        w = float(weights.get(key, 0.0))
        if col not in out.columns or w == 0:
            continue
        x = pd.to_numeric(out[col], errors="coerce")
        valid = x.notna()
        total.loc[valid] += sign * w * x.loc[valid]
        available_weight.loc[valid] += abs(w)
    out["S_TeV_evo_raw"] = total
    out["S_TeV_evo"] = total / available_weight.replace(0, np.nan)
    return out


def assign_tiers(df: pd.DataFrame, gold=95, silver=85, bronze=70) -> pd.DataFrame:
    out = df.copy()
    s = pd.to_numeric(out["S_TeV_evo"], errors="coerce")
    q_gold = np.nanpercentile(s, gold)
    q_silver = np.nanpercentile(s, silver)
    q_bronze = np.nanpercentile(s, bronze)
    out["tev_priority_tier"] = "Low-priority"
    out.loc[s >= q_bronze, "tev_priority_tier"] = "Bronze"
    out.loc[s >= q_silver, "tev_priority_tier"] = "Silver"
    out.loc[s >= q_gold, "tev_priority_tier"] = "Gold"
    return out
