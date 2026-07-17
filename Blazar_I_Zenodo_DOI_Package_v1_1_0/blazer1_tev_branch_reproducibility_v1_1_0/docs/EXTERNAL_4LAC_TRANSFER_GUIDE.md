# Non-overlapping 4LAC external-cohort transfer audit

## Cohort definition

The 4LAC-DR3 high- and low-latitude tables are combined into a 3511-source union. A source is considered represented in BlazEr1 when either:

1. normalized 4LAC `Source_Name` equals BlazEr1 `FGL_SRC_NAME`; or
2. the 4LAC counterpart coordinate is within 3 arcsec of the BlazEr1 catalogue coordinate.

The union of these keys removes 1165 sources and leaves 2346 4LAC-exclusive sources. The 3-arcsec rule produces no ambiguous multiple counterpart. Changing the positional radius from 0.5 to 5 arcsec changes the exclusive denominator by only four sources.

## Validation labels

Frozen TeVCat labels are attached only after the cohort is fixed. The primary radius is 180 arcsec, matching the core manuscript analysis. Entries with `source_type == UNID` are excluded from the firm extragalactic validation set. The final external cohort contains 57 firm positives.

## Frozen score projection

A uniform external X-ray/infrared layer is unavailable across the full Fermi-selected cohort. The published transfer coordinate therefore excludes:

- direct X-ray brightness;
- the X-ray-dependent Compton-dominance term;
- WISE/infrared colour.

It retains frozen gamma-ray hardness, gamma-ray variability, continuous synchrotron peak, and redshift/EBL terms with weights 1.00, 0.35, 1.00, and -0.80, respectively. Frozen BlazEr1 robust-standardisation constants and available-component normalization are used without re-estimation.

## Primary transfer outputs

- availability-weighted AUROC: 0.9011979490;
- 95% class-stratified bootstrap interval: 0.8626918979–0.9350059016;
- top 5%: 29/57 recovered, enrichment 10.1151;
- top 15%: 45/57 recovered, enrichment 5.2617;
- complete case: N=944, positives=51, AUROC 0.8879959599.

## Claim boundary

This is an external-cohort transportability audit. It is not described as fully independent validation because the 4LAC catalogue defines the cohort and supplies predictor fields. The close gamma-only AUROC is retained in the machine-readable products; no incremental superiority claim is made.
