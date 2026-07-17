from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
from astropy.table import Table


def read_catalog(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing catalogue: {path}")
    suffix = path.suffix.lower()
    if suffix in {".fits", ".fit", ".fts"}:
        return Table.read(path).to_pandas()
    if suffix in {".csv", ".txt"}:
        return pd.read_csv(path)
    if suffix in {".vot", ".xml"}:
        return Table.read(path, format="votable").to_pandas()
    raise ValueError(f"Unsupported catalogue type: {path}")


def find_column(df: pd.DataFrame, candidates: Iterable[str]) -> Optional[str]:
    cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in df.columns:
            return cand
        if cand.lower() in cols:
            return cols[cand.lower()]
    return None


def standardize_position_columns(
    df: pd.DataFrame,
    ra_candidates=("ra", "RA", "RAJ2000", "ra_deg"),
    dec_candidates=("dec", "DEC", "DEJ2000", "dec_deg"),
) -> pd.DataFrame:
    out = df.copy()
    ra = find_column(out, ra_candidates)
    dec = find_column(out, dec_candidates)
    if ra is None or dec is None:
        raise KeyError(f"Could not identify RA/Dec columns. Columns: {list(out.columns)}")
    out["ra_deg"] = pd.to_numeric(out[ra], errors="coerce")
    out["dec_deg"] = pd.to_numeric(out[dec], errors="coerce")
    return out


def robust_zscore(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    med = x.median(skipna=True)
    mad = (x - med).abs().median(skipna=True)
    if not mad or pd.isna(mad):
        return (x - med) * 0.0
    return (x - med) / (1.4826 * mad)
