# Smoke-test scope

The version 1.1.0 smoke test runs:

1. frozen core-score reconstruction;
2. reduced random-shift cross-match audit;
3. complete 4LAC-DR3 high+low cohort construction;
4. BlazEr1 overlap removal using the frozen name-or-position rule;
5. frozen TeVCat attachment after cohort construction;
6. reduced-bootstrap external-transfer scoring;
7. all package science and hygiene validation gates.

The smoke test uses reduced resampling only. Deterministic counts, score values, AUROCs, tier membership, and catalogue rows are unchanged. Final archived confidence intervals are generated with the production settings documented in `docs/REPRODUCIBILITY_GUIDE.md`.
