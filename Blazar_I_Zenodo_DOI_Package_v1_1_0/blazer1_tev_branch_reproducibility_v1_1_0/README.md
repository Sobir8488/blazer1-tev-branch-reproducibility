DOI: 10.5281/zenodo.21416005
# BlazEr1 X-ray-anchored TeV-favourable population branch: reproducibility and external-cohort transfer package

**Version:** 1.1.0  
**Release date:** 2026-07-17  
**Associated manuscript:** *An X-ray-anchored TeV-favourable population branch in eROSITA blazars*

## Scope

This archival release preserves the complete reproducibility layer for the BlazEr1 TeV-favourability analysis and its non-overlapping 4LAC-DR3 transfer audit. It contains frozen catalogue snapshots, deterministic analysis inputs, source code, machine-readable statistical products, final follow-up catalogues, figure source data, vector figures, provenance records, and automated science checks.

TeVCat labels are attached only after the relevant ranking and cohort definitions are frozen. All scores are empirical population coordinates; none is a calibrated TeV detection probability.

## Core BlazEr1 results preserved in the release

- Parent catalogue: **5865** BlazEr1 sources.
- Retrospective firm TeVCat matches: **34**.
- Active Gold tier: **294** sources, recovering **21/34** matches.
- Gold+Silver: **880** sources, recovering **30/34** matches.
- Harmonized AUROC ordering: X-ray-only **0.970** > active branch **0.940** > no-X-ray **0.876**.
- Follow-up List A: **243** X-ray-prioritized sources.
- Follow-up List B: **163** HSP-branch-frontier sources.

## External 4LAC transfer products added in version 1.1.0

- 4LAC-DR3 union: **3511** sources.
- BlazEr1 overlap removed by frozen name-or-position rule: **1165** sources.
- Non-overlapping 4LAC-exclusive cohort: **2346** sources.
- Firm extragalactic TeVCat associations in the exclusive cohort: **57**.
- Frozen X-ray/IR-independent transfer AUROC: **0.901** (95% stratified-bootstrap interval **0.863–0.935**).
- Complete-case transfer AUROC: **0.888** (**0.840–0.930**; 944 sources and 51 positives).
- The transfer result establishes cross-catalogue ranking transportability. It does **not** establish universal X-ray dominance or incremental superiority over the simpler gamma-only baseline.

## Start here

1. Read `docs/REPRODUCIBILITY_GUIDE.md`.
2. Create the environment: `conda env create -f environment.yml`.
3. Activate it: `conda activate blazer1_tev_branch_v1_1_0`.
4. Run the short verification: `python run_release.py --fast`.
5. Run the production replay: `python run_release.py`.
6. Inspect `validation/package_validation.json` and `validation/PACKAGE_AUDIT_REPORT.md`.

## Directory map

- `data/frozen_analysis_input/`: deterministic starting point for the core analysis replay.
- `data/frozen_third_party_inputs/`: exact public catalogue snapshots used by the project.
- `data/final/`: active-score catalogues and final follow-up lists.
- `data/external_transfer/`: 4LAC-exclusive cohort and frozen transfer-score catalogues.
- `scripts/`, `src/`: analysis code.
- `tables/`: machine-readable statistical products.
- `figures/`: final vector figures only.
- `figure_source_data/`, `figure_generation/`: figure reproducibility.
- `provenance/`: catalogue lineage, frozen-input checksums, random seeds, and analysis decisions.
- `metadata/`: Zenodo-ready metadata.
- `validation/`: automated science and package checks.

## Versioned filenames

The core v0.4.4/v1.0.0 result files retain their original filenames so that the published checksums and replay paths remain stable. New external-transfer products use the `v1_1_0` suffix. The authoritative package version is recorded in `VERSION`, `configs/config.yaml`, and the Zenodo metadata.

## Deliberate exclusions

- Manuscript TeX and PDF files are not included.
- Exploratory one-positive X-ray/WISE ordering estimates from the public half-sky feasibility check are not included because they do not support formal inference.
- Live catalogue queries are not required for the frozen replay.
- Non-PDF figure formats are excluded from the archival release.

## Citation

Use the version-specific Zenodo DOI generated for this release and cite the associated manuscript when available. See `CITATION.cff` and `docs/CITATION_GUIDE.md`.
