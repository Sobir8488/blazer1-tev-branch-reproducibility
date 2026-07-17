#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent


def check(condition: bool, name: str, value: object) -> dict[str, object]:
    return {"check": name, "value": value, "pass": bool(condition)}


def source_column(frame: pd.DataFrame) -> str:
    exact = [c for c in frame.columns if c.lower() in {"source_name", "source_name_v044", "src_name", "ianame"}]
    if exact:
        return exact[0]
    fuzzy = [c for c in frame.columns if "source" in c.lower() and "name" in c.lower()]
    if fuzzy:
        return fuzzy[0]
    raise KeyError("No source-name column found")


def main() -> None:
    validation = pd.read_csv(ROOT / "tables" / "table_active_primary_validation_v0_4_4.csv")
    gold = validation[(validation.score_variant == "active_primary") & (validation.tier_set == "Gold")].iloc[0]
    gold_silver = validation[(validation.score_variant == "active_primary") & (validation.tier_set == "Gold+Silver")].iloc[0]

    auc = pd.read_csv(ROOT / "tables" / "table_active_harmonized_auc_v0_4_4.csv").set_index("quantity")
    auc_x = float(auc.loc["AUROC xray_only", "estimate"])
    auc_active = float(auc.loc["AUROC active_full", "estimate"])
    auc_no_x = float(auc.loc["AUROC no_xray", "estimate"])

    list_a = pd.read_csv(ROOT / "data" / "final" / "candidate_list_A_xray_prioritized_all_v1_0_0.csv")
    list_b = pd.read_csv(ROOT / "data" / "final" / "candidate_list_B_hsp_branch_frontier_all_v1_0_0.csv")
    overlap = len(set(list_a[source_column(list_a)].astype(str)) & set(list_b[source_column(list_b)].astype(str)))

    transfer_flow = pd.read_csv(ROOT / "tables" / "table_4lac_transfer_sample_flow_v1_1_0.csv").set_index("stage")
    transfer_metrics = pd.read_csv(ROOT / "tables" / "table_4lac_transfer_metrics_v1_1_0.csv").set_index("score_variant")
    transfer_tiers = pd.read_csv(ROOT / "tables" / "table_4lac_transfer_tier_enrichment_v1_1_0.csv")
    transfer_crosscheck = pd.read_csv(ROOT / "tables" / "table_4lac_transfer_frozen_34_crosscheck_v1_1_0.csv").iloc[0]
    transfer_radius = pd.read_csv(ROOT / "tables" / "table_4lac_overlap_radius_sensitivity_v1_1_0.csv").set_index("radius_arcsec")
    transfer_scores = pd.read_csv(ROOT / "data" / "external_transfer" / "4lac_exclusive_transfer_scores_v1_1_0.csv")

    primary_transfer = transfer_metrics.loc["Fully no-X/no-IR, availability weighted"]
    complete_transfer = transfer_metrics.loc["Fully no-X/no-IR, complete case"]
    gamma_only = transfer_metrics.loc["Gamma only"]
    gold_transfer = transfer_tiers[(transfer_tiers.score_variant == "Fully no-X/no-IR, availability weighted") & (transfer_tiers.tier == "Gold")].iloc[0]
    gold_silver_transfer = transfer_tiers[(transfer_tiers.score_variant == "Fully no-X/no-IR, availability weighted") & (transfer_tiers.tier == "Gold+Silver")].iloc[0]

    config = yaml.safe_load((ROOT / "configs" / "config.yaml").read_text(encoding="utf-8"))
    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))

    image_extensions = {".png", ".svg", ".jpg", ".jpeg", ".eps", ".webp"}
    non_pdf_images = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in image_extensions]
    manuscript_tex = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.tex") if "manuscript" in p.name.lower() or p.name.lower().startswith("blazar_i") or p.name.lower().startswith("appendix_")]
    excluded_feasibility = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file() and ("unverified" in p.name.lower() or p.name in {"BlazEr1u.fit", "BlazEr1u.fit.gz", "BlazEr1c.fit.gz"})]

    checks = [
        check((ROOT / "VERSION").read_text().strip() == "1.1.0", "release_version_file", (ROOT / "VERSION").read_text().strip()),
        check(config["project"]["version"] == "1.1.0", "config_version", config["project"]["version"]),
        check(float(config["score"]["weights"]["radio_compactness"]) == 0.0, "radio_component_inactive", config["score"]["weights"]["radio_compactness"]),
        check(zenodo["version"] == "1.1.0", "zenodo_metadata_version", zenodo["version"]),
        check(int(gold.analysis_N) == 5865, "parent_N", int(gold.analysis_N)),
        check(int(gold.known_TeV_N) == 34, "known_TeV_N", int(gold.known_TeV_N)),
        check(int(gold.tier_N) == 294 and int(gold.recovered_N) == 21, "Gold_tier", [int(gold.tier_N), int(gold.recovered_N)]),
        check(int(gold_silver.tier_N) == 880 and int(gold_silver.recovered_N) == 30, "Gold_Silver_tier", [int(gold_silver.tier_N), int(gold_silver.recovered_N)]),
        check(auc_x > auc_active > auc_no_x, "core_AUROC_order", [auc_x, auc_active, auc_no_x]),
        check(len(list_a) == 243, "List_A_N", len(list_a)),
        check(len(list_b) == 163, "List_B_N", len(list_b)),
        check(overlap == 0, "candidate_lists_disjoint", overlap),
        check(int(transfer_flow.loc["4LAC union", "N"]) == 3511, "4LAC_union_N", int(transfer_flow.loc["4LAC union", "N"])),
        check(int(transfer_flow.loc["Primary overlap: name OR position", "N"]) == 1165, "4LAC_BlazEr1_overlap_N", int(transfer_flow.loc["Primary overlap: name OR position", "N"])),
        check(int(transfer_flow.loc["Primary 4LAC-exclusive cohort", "N"]) == 2346, "4LAC_exclusive_N", int(transfer_flow.loc["Primary 4LAC-exclusive cohort", "N"])),
        check(int(transfer_flow.loc["Firm extragalactic TeVCat positives: exclusive", "N"]) == 57, "4LAC_exclusive_TeV_N", int(transfer_flow.loc["Firm extragalactic TeVCat positives: exclusive", "N"])),
        check(int(transfer_flow.loc["Ambiguous overlap within 3 arcsec", "N"]) == 0, "4LAC_overlap_ambiguity", int(transfer_flow.loc["Ambiguous overlap within 3 arcsec", "N"])),
        check(bool(transfer_crosscheck["PASS"]) and int(transfer_crosscheck["N_identity_intersection"]) == 34, "frozen_34_identity_crosscheck", transfer_crosscheck.to_dict()),
        check(abs(float(primary_transfer.AUROC) - 0.9011979490009427) < 1e-12, "4LAC_transfer_AUROC", float(primary_transfer.AUROC)),
        check(int(primary_transfer.N) == 2346 and int(primary_transfer.N_positive) == 57, "4LAC_transfer_denominator", [int(primary_transfer.N), int(primary_transfer.N_positive)]),
        check(abs(float(complete_transfer.AUROC) - 0.8879959598621083) < 1e-12, "4LAC_complete_case_AUROC", float(complete_transfer.AUROC)),
        check(int(complete_transfer.N) == 944 and int(complete_transfer.N_positive) == 51, "4LAC_complete_case_denominator", [int(complete_transfer.N), int(complete_transfer.N_positive)]),
        check(int(gold_transfer.positive_in_tier) == 29 and int(gold_transfer.total_positive) == 57, "4LAC_Gold_recovery", [int(gold_transfer.positive_in_tier), int(gold_transfer.total_positive)]),
        check(int(gold_silver_transfer.positive_in_tier) == 45 and int(gold_silver_transfer.total_positive) == 57, "4LAC_Gold_Silver_recovery", [int(gold_silver_transfer.positive_in_tier), int(gold_silver_transfer.total_positive)]),
        check(abs(float(primary_transfer.AUROC) - float(gamma_only.AUROC)) < 0.01, "gamma_only_increment_not_overstated", [float(gamma_only.AUROC), float(primary_transfer.AUROC)]),
        check(int(transfer_radius.loc[3.0, "n_exclusive_union_name_or_position"]) == 2346, "primary_overlap_radius", int(transfer_radius.loc[3.0, "n_exclusive_union_name_or_position"])),
        check(len(transfer_scores) == 2346, "transfer_score_catalogue_rows", len(transfer_scores)),
        check(len(list((ROOT / "figures").glob("*.pdf"))) == 8, "figure_pdf_count", len(list((ROOT / "figures").glob("*.pdf")))),
        check(not non_pdf_images, "pdf_only_figures", non_pdf_images),
        check(not manuscript_tex, "manuscript_tex_absent", manuscript_tex),
        check(not excluded_feasibility, "non_inferential_feasibility_products_absent", excluded_feasibility),
        check((ROOT / "data" / "frozen_third_party_inputs" / "4lac_dr3_high.fits").exists() and (ROOT / "data" / "frozen_third_party_inputs" / "4lac_dr3_low.fits").exists(), "frozen_4LAC_inputs_exist", True),
        check((ROOT / "scripts" / "62_external_4lac_transfer_v1_1_0.py").exists(), "external_transfer_replay_script_exists", True),
    ]

    status = "PASS" if all(item["pass"] for item in checks) else "FAIL"
    output = {"release": "1.1.0", "status": status, "checks": checks}
    validation_dir = ROOT / "validation"
    validation_dir.mkdir(exist_ok=True)
    (validation_dir / "package_validation.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
