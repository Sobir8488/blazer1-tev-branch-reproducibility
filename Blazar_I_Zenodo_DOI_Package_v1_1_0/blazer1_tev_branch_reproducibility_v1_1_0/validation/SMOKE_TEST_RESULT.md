# Smoke-test result

- Release: 1.1.0
- Status: **PASS**
- Command: `python run_release.py --fast --skip-figures`
- Test environment: Python 3.11-compatible package environment
- Core BlazEr1 validation: PASS
- 4LAC-exclusive cohort reconstruction: PASS
- External-transfer score reconstruction: PASS
- Package hygiene gates: PASS

The smoke run reproduced the fixed counts 5865/34 for the core analysis and 3511/1165/2346/57 for the 4LAC union, overlap, exclusive cohort, and firm external positives.
