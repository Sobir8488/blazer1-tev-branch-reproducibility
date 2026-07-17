from __future__ import annotations

import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
import astropy.units as u


def nearest_crossmatch(
    left: pd.DataFrame,
    right: pd.DataFrame,
    radius_arcsec: float,
    left_prefix: str = "left",
    right_prefix: str = "right",
) -> pd.DataFrame:
    """Nearest-neighbour sky match using columns ra_deg/dec_deg.

    Returns one row per left source with right columns appended only when a match
    is inside radius_arcsec. Right-side catalogue columns are explicitly masked
    for non-matches, preventing nearest-but-outside sources from leaking into
    feature construction.
    """
    out = left.copy()
    if "ra_deg" not in out.columns or "dec_deg" not in out.columns:
        raise KeyError("Left table must contain ra_deg and dec_deg")
    if "ra_deg" not in right.columns or "dec_deg" not in right.columns:
        raise KeyError("Right table must contain ra_deg and dec_deg")

    lmask = out["ra_deg"].notna() & out["dec_deg"].notna()
    rmask = right["ra_deg"].notna() & right["dec_deg"].notna()
    l = out.loc[lmask].copy().reset_index().rename(columns={"index": "_left_index"})
    r = right.loc[rmask].copy().reset_index().rename(columns={"index": "_right_index"})

    # Pre-create match status for all rows.
    out[f"{right_prefix}_matched"] = False
    out[f"{right_prefix}_sep_arcsec"] = np.nan

    if l.empty or r.empty:
        return out

    c1 = SkyCoord(l["ra_deg"].values * u.deg, l["dec_deg"].values * u.deg)
    c2 = SkyCoord(r["ra_deg"].values * u.deg, r["dec_deg"].values * u.deg)
    idx, sep2d, _ = c1.match_to_catalog_sky(c2)
    ok = sep2d.arcsec <= float(radius_arcsec)

    r_pref = r.add_prefix(f"{right_prefix}_")
    right_rows = r_pref.iloc[idx].reset_index(drop=True)
    right_rows.loc[~ok, :] = pd.NA
    right_rows[f"{right_prefix}_matched"] = ok
    right_rows[f"{right_prefix}_sep_arcsec"] = sep2d.arcsec

    # Drop left-side placeholder match columns before appending right-side columns.
    l_clean = l.drop(columns=[f"{right_prefix}_matched", f"{right_prefix}_sep_arcsec"], errors="ignore")
    matched = pd.concat([l_clean.reset_index(drop=True), right_rows.reset_index(drop=True)], axis=1)
    matched = matched.drop(columns=["_left_index"], errors="ignore")

    # Rows with missing left coordinates have no match and empty right-side columns.
    unmatched_left = out.loc[~lmask].copy()
    for col in right_rows.columns:
        if col not in unmatched_left.columns:
            unmatched_left[col] = pd.NA
    unmatched_left[f"{right_prefix}_matched"] = False
    unmatched_left[f"{right_prefix}_sep_arcsec"] = np.nan

    return pd.concat([matched, unmatched_left], ignore_index=True, sort=False)
