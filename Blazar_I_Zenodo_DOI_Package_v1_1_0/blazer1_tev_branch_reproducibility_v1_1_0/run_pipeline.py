#!/usr/bin/env python
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

STEPS = [
    "scripts/01_standardize_catalogs.py",
    "scripts/02_crossmatch_catalogs.py",
    "scripts/03_build_features.py",
    "scripts/04_compute_tev_evolution_score.py",
    "scripts/05_export_input_package.py",
]


def main() -> None:
    for step in STEPS:
        print(f"\n=== {step} ===")
        subprocess.check_call([sys.executable, step, "--config", "configs/config.yaml"])


if __name__ == "__main__":
    main()
