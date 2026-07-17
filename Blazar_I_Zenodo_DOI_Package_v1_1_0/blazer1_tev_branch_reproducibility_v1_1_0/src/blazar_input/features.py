from __future__ import annotations

import re
import numpy as np
import pandas as pd
from .io import robust_zscore


def add_wise_colours(df: pd.DataFrame) -> pd.DataFrame:
    """Add WISE/Legacy-Survey mid-IR colour diagnostics.

    Priority order:
    1) external AllWISE cross-match columns, if present;
    2) BlazEr1/Legacy Survey WISE columns already present in the parent table.

    The resulting S_IR is a conservative HSP-like IR-locus proxy, not a formal
    WISE blazar-locus classifier.
    """
    out = df.copy()
    w1 = _first_numeric(out, [
        "w1mpro", "W1mag", "wise_w1mpro", "wise_W1mag",
        "W1_MAG", "DERED_MAG_W1", "W1_MAG_AB", "wise_W1_MAG",
    ])
    w2 = _first_numeric(out, [
        "w2mpro", "W2mag", "wise_w2mpro", "wise_W2mag",
        "W2_MAG", "DERED_MAG_W2", "W2_MAG_AB", "wise_W2_MAG",
    ])
    w3 = _first_numeric(out, [
        "w3mpro", "W3mag", "wise_w3mpro", "wise_W3mag",
        "W3_MAG", "W3_MAG_AB", "wise_W3_MAG",
    ])

    # Some BlazEr1 rows already carry a direct W1-W2 column.
    direct_w12 = _first_numeric(out, ["W1_MINUS_W2", "wise_W1_MINUS_W2"])
    out["wise_w1_w2"] = (w1 - w2).where((w1 - w2).notna(), direct_w12)
    out["wise_w2_w3"] = w2 - w3

    # HSP-like sources tend to be less MIR-red than strongly quasar-like FSRQs.
    # Keep this broad and robust: extreme W1-W2 red colours are penalized, while
    # moderate W2-W3 values are favoured when available.
    s12 = -((out["wise_w1_w2"] - 0.55).abs())
    s23 = -0.25 * ((out["wise_w2_w3"] - 1.7).abs())
    out["S_IR"] = robust_zscore(s12.add(s23, fill_value=0.0))
    out.loc[out["wise_w1_w2"].isna() & out["wise_w2_w3"].isna(), "S_IR"] = np.nan
    out["wise_feature_available"] = out["wise_w1_w2"].notna() | out["wise_w2_w3"].notna()
    return out


def add_radio_compactness(df: pd.DataFrame) -> pd.DataFrame:
    """Add radio compactness from VLASS when available, otherwise from BlazEr1 proxies."""
    out = df.copy()
    speak = _first_numeric(out, ["Speak", "peak_flux", "peak_flux_mJy", "vlass_Speak", "vlass_peak_flux_mJy"])
    sint = _first_numeric(out, ["Sint", "total_flux", "int_flux_mJy", "vlass_Sint", "vlass_int_flux_mJy"])
    ratio = speak / sint.replace(0, np.nan)

    # RFC compactness proxy: unresolved / total when VLBI resolved+unresolved columns exist.
    rfc_scores = []
    for band in ["S", "C", "X", "U", "K"]:
        res = _first_numeric(out, [f"RFC_{band}BAND_RES"])
        unres = _first_numeric(out, [f"RFC_{band}BAND_UNRES"])
        rfc_scores.append(unres / (res + unres).replace(0, np.nan))
    rfc_compact = pd.concat(rfc_scores, axis=1).median(axis=1, skipna=True) if rfc_scores else pd.Series(np.nan, index=out.index)

    morph_cols = ["XIE_MORPH_BZCAT", "XIE_MORPH_KDEBLLACS", "XIE_MORPH_WIBRALS", "MOJAVE_CLASS", "TANAMI_CLASS"]
    morph_text = _combined_text(out, morph_cols)
    morph_score = pd.Series(np.nan, index=out.index, dtype=float)
    compact_mask = morph_text.str.contains("COMPACT|CORE|UNRES|BL Lac|BLL|Q", case=False, na=False)
    extended_mask = morph_text.str.contains("EXTENDED|SEPARATED|DOUBLE|LOBE|FRI|FRII|RADIO GALAXY", case=False, na=False)
    morph_score.loc[compact_mask] = 1.0
    morph_score.loc[extended_mask] = 0.35

    out["radio_compactness_flux_ratio"] = ratio
    out["radio_compactness_rfc"] = rfc_compact
    out["radio_compactness_morph"] = morph_score
    out["radio_compactness"] = _coalesce_numeric([ratio, rfc_compact, morph_score])
    out["S_R"] = robust_zscore(out["radio_compactness"].clip(lower=0, upper=2))
    out["radio_feature_available"] = out["radio_compactness"].notna()
    return out


def add_gamma_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    gamma_index = _first_numeric(out, [
        "PL_Index", "Spectral_Index", "Photon_Index", "fermi_PL_Index",
        "fermi_Spectral_Index", "FGL_PL_INDEX", "FGL_LP_INDEX",
    ])
    variability = _first_numeric(out, ["Variability_Index", "fermi_Variability_Index"])
    curvature = _first_numeric(out, ["fermi_LP_SigCurv", "FGL_LP_SIGCURV"])
    # Harder spectra have smaller photon index, hence negative z-score.
    out["gamma_photon_index_adopted"] = gamma_index
    out["S_gamma_hard"] = -robust_zscore(gamma_index)
    out["S_gamma_var"] = robust_zscore(np.log10(variability.where(variability > 0)))
    out["S_gamma_curv_penalty"] = robust_zscore(curvature)
    out["gamma_feature_available"] = gamma_index.notna() | variability.notna()
    return out


def add_xray_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    fx = _first_numeric(out, [
        "Fx", "flux", "flux_x", "erass1_flux", "xray_flux",
        "ML_FLUX_1", "PWL20_FLUX_ABS_0", "PWL17_FLUX_ABS_0",
        "PWL15_FLUX_ABS_0", "FIXED_FLUX_ABS_0", "FREE_FLUX_ABS_0",
        "SOFTFLUX_S", "XRT_ABS_FLUX_V", "XRT_UNABS_FLUX_V",
    ])
    out["xray_flux_adopted"] = fx
    out["log_fx"] = np.log10(fx.where(fx > 0))
    out["S_X"] = robust_zscore(out["log_fx"])
    out["xray_feature_available"] = fx.notna() & (fx > 0)
    return out


def add_evolution_proxies(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    fx = _first_numeric(out, [
        "xray_flux_adopted", "Fx", "flux", "flux_x", "erass1_flux", "xray_flux",
        "ML_FLUX_1", "PWL20_FLUX_ABS_0", "FIXED_FLUX_ABS_0", "FREE_FLUX_ABS_0",
        "SOFTFLUX_S", "XRT_ABS_FLUX_V", "XRT_UNABS_FLUX_V",
    ])
    fg = _first_numeric(out, [
        "Energy_Flux100", "Energy_Flux", "flux_gamma", "fermi_Energy_Flux100",
        "FGL_FLUX_A", "FGL_FLUX_B",
    ])
    out["gamma_energy_flux_adopted"] = fg
    out["cd_proxy"] = np.log10(fg.where(fg > 0) / fx.where(fx > 0))
    out["S_CD_penalty"] = robust_zscore(out["cd_proxy"])

    z, zsrc = _adopt_redshift(out)
    out["redshift_adopted"] = z
    out["redshift_adopted_source"] = zsrc
    out["S_EBL_proxy"] = robust_zscore(np.log10(1 + z.where(z > 0)))
    out.loc[z.isna(), "S_EBL_proxy"] = np.nan

    lognu, method = _adopt_synch_peak_proxy(out)
    out["log_nu_peak_proxy"] = lognu
    out["log_nu_peak_proxy_method"] = method
    out["S_nu_peak"] = robust_zscore(out["log_nu_peak_proxy"])

    feature_cols = ["S_X", "S_gamma_hard", "S_gamma_var", "S_IR", "S_R", "S_nu_peak", "S_CD_penalty", "S_EBL_proxy"]
    out["n_score_components_available"] = out[feature_cols].notna().sum(axis=1)
    out["has_known_tev_match"] = out.get("tevcat_matched", pd.Series(False, index=out.index)).astype("boolean")
    return out


def _adopt_redshift(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    candidates = [
        ("Z_SPEC", "Z_SPEC"),
        ("Z_MASTER", "Z_MASTER"),
        ("Z_4LAC", "Z_4LAC"),
        ("Z_BZCAT", "Z_BZCAT"),
        ("Z_SIMBAD", "Z_SIMBAD"),
        ("Z_3HSP", "Z_3HSP"),
        ("Z_MILLIQUAS", "Z_MILLIQUAS"),
        ("z", "external_z"),
        ("redshift", "external_redshift"),
        ("Redshift", "external_Redshift"),
        ("Z_PHOTO", "Z_PHOTO"),
    ]
    z = pd.Series(np.nan, index=df.index, dtype=float)
    src = pd.Series(pd.NA, index=df.index, dtype="object")
    for col, label in candidates:
        if col not in df.columns:
            continue
        val = pd.to_numeric(df[col], errors="coerce")
        # Remove placeholders and clearly non-physical values.
        val = val.where((val > 0) & (val < 8))
        use = z.isna() & val.notna()
        z.loc[use] = val.loc[use]
        src.loc[use] = label
    return z, src


def _adopt_synch_peak_proxy(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    lognu = pd.Series(np.nan, index=df.index, dtype=float)
    method = pd.Series(pd.NA, index=df.index, dtype="object")

    # 4LAC low-energy peak frequency may already be in Hz.
    le_freq = _first_numeric(df, ["LAC_LE_FREQ", "lac_le_freq", "LE_FREQ"])
    use = lognu.isna() & (le_freq > 1e9) & (le_freq < 1e20)
    lognu.loc[use] = np.log10(le_freq.loc[use])
    method.loc[use] = "LAC_LE_FREQ"

    sed = _combined_text(df, ["LAC_SED_CLASS", "SED_CLASS", "fermi_SED_CLASS"])
    sed_map = {
        "HSP": 16.5,
        "ISP": 15.0,
        "LSP": 13.5,
    }
    for key, val in sed_map.items():
        use = lognu.isna() & sed.str.contains(key, case=False, na=False)
        lognu.loc[use] = val
        method.loc[use] = f"SED_CLASS_{key}"

    alpha_rx = _first_numeric(df, ["ALPHA_RX", "alpha_rx", "Alpha_rx", "arx"])
    use = lognu.isna() & alpha_rx.notna()
    # Broad empirical proxy: smaller alpha_rx generally implies X-ray-brighter/HSP-like SEDs.
    lognu.loc[use] = (17.0 - 5.5 * alpha_rx.loc[use]).clip(lower=12.0, upper=18.5)
    method.loc[use] = "ALPHA_RX_PROXY"

    # HSP catalogue membership is a last-resort categorical signal.
    hsp_text = _combined_text(df, ["HSP_SRC_NAME"])
    use = lognu.isna() & hsp_text.notna() & ~hsp_text.str.contains("^b?'-'$|nan|None", case=False, na=False)
    lognu.loc[use] = 16.5
    method.loc[use] = "HSP_CATALOGUE_FLAG"
    return lognu, method


def _first_numeric(df: pd.DataFrame, names: list[str]) -> pd.Series:
    cols_lower = {c.lower(): c for c in df.columns}
    for n in names:
        col = n if n in df.columns else cols_lower.get(n.lower())
        if col is not None:
            return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(np.nan, index=df.index, dtype=float)


def _coalesce_numeric(series_list: list[pd.Series]) -> pd.Series:
    out = pd.Series(np.nan, index=series_list[0].index if series_list else None, dtype=float)
    for s in series_list:
        use = out.isna() & s.notna()
        out.loc[use] = s.loc[use]
    return out


def _combined_text(df: pd.DataFrame, names: list[str]) -> pd.Series:
    parts = []
    cols_lower = {c.lower(): c for c in df.columns}
    for n in names:
        col = n if n in df.columns else cols_lower.get(n.lower())
        if col is not None:
            parts.append(df[col].map(_clean_str))
    if not parts:
        return pd.Series(pd.NA, index=df.index, dtype="object")
    out = parts[0]
    for p in parts[1:]:
        out = out.fillna("") + " " + p.fillna("")
    out = out.str.strip()
    out = out.replace("", pd.NA)
    return out


def _clean_str(x) -> str | None:
    if pd.isna(x):
        return None
    s = str(x).strip()
    # Convert strings like b'ABC' coming from FITS byte columns serialized to CSV.
    m = re.match(r"^b[\'\"](.*)[\'\"]$", s)
    if m:
        s = m.group(1)
    if s.lower() in {"nan", "none", "null", "--", "-", ""}:
        return None
    return s
