# Reproducibility guide

## Deterministic analysis boundary

The core BlazEr1 replay begins from `data/frozen_analysis_input/tev_evolution_score_catalog_v0_1_8_xray_control_augmented.csv`. This boundary fixes catalogue assembly and the X-ray/no-X-ray control layer while retaining the exact public input snapshots for provenance and independent rebuilding.

The 4LAC transfer replay begins from the frozen files:

- `data/frozen_third_party_inputs/4lac_dr3_high.fits`;
- `data/frozen_third_party_inputs/4lac_dr3_low.fits`;
- `data/frozen_third_party_inputs/blazer1_catalog.fits`;
- `data/frozen_analysis_input/tevcat_standardized.csv`.

The transfer script rebuilds the 4LAC union, removes BlazEr1 overlap, attaches TeVCat labels after cohort construction, computes the frozen X-ray/IR-independent projection, and regenerates all transfer tables and catalogues.

## Environment

```bash
conda env create -f environment.yml
conda activate blazer1_tev_branch_v1_1_0
```

A pip-only environment can be created with `requirements.txt`.

## Short verification

```bash
python run_release.py --fast
```

The fast run uses reduced resampling but performs the full catalogue construction and deterministic score calculations. It then runs the package validation gates.

## Production replay

```bash
python run_release.py
```

Production settings:

- 5000 paired bootstrap draws for the core harmonized analysis;
- 5000 within-pattern permutations;
- 1000 random coordinate shifts for the core cross-match audit;
- 1000 score-weight perturbation draws;
- 20000 class-stratified bootstrap draws for the 4LAC transfer AUROCs;
- 250 random coordinate shifts for each 4LAC transfer null diagnostic;
- core random seed 8488; transfer bootstrap seed 260717.

## Transfer-only replay

```bash
python scripts/62_external_4lac_transfer_v1_1_0.py
```

For a quick transfer-only check:

```bash
python scripts/62_external_4lac_transfer_v1_1_0.py \
  --n-bootstrap 200 \
  --n-random-shifts 20
```

## Expected science checks

### Core BlazEr1 analysis

- parent N = 5865;
- firm TeVCat N = 34;
- Gold N = 294 with 21 matches;
- Gold+Silver N = 880 with 30 matches;
- AUROC ordering: X-ray-only > active branch > no-X-ray;
- List A N = 243;
- List B N = 163.

### 4LAC external-cohort transfer

- 4LAC union N = 3511;
- BlazEr1 overlap N = 1165;
- 4LAC-exclusive N = 2346;
- firm extragalactic TeVCat positives N = 57;
- no ambiguous BlazEr1 match within 3 arcsec;
- overlap TeVCat identity cross-check = 34/34;
- frozen no-X/no-IR AUROC = 0.9011979490;
- complete-case N = 944, positives = 51, AUROC = 0.8879959599;
- Gold transfer recovery = 29/57;
- Gold+Silver transfer recovery = 45/57.

## Interpretation boundary

The transfer analysis tests whether frozen population geometry remains informative after changing the parent selection and source set. It does not calibrate detection probability, establish causal feature importance, demonstrate universal X-ray dominance, or establish an incremental advantage over the gamma-only baseline.
