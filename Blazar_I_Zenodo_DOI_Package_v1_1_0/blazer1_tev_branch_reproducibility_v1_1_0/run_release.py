#!/usr/bin/env python
from __future__ import annotations
import argparse, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PHASES = [
    ["scripts/35_statistical_hardening_v0_3_0.py", "scripts/36_hsp_circularity_sensitivity_v0_3_0.py"],
    ["scripts/40_harmonized_statistics_v0_3_1.py", "scripts/41_candidate_list_hardening_v0_3_1.py", "scripts/42_time_split_iact_validation_v0_3_2.py", "scripts/43_iact_observed_control_v0_3_3.py"],
    ["scripts/44_exact_score_definition_v0_4_2.py", "scripts/45_random_shift_crossmatch_audit_v0_4_2.py", "scripts/46_component_coverage_audit_v0_4_2.py", "scripts/47_xray_matched_control_balance_v0_4_2.py", "scripts/49_make_scientific_hardening_report_v0_4_2.py"],
    ["scripts/50_score_architecture_variants_v0_4_3.py", "scripts/51_availability_pattern_conditioning_v0_4_3.py", "scripts/52_candidate_stability_v0_4_3.py", "scripts/54_make_score_architecture_report_v0_4_3.py"],
    ["scripts/55_active_score_primary_validation_v0_4_4.py", "scripts/56_active_branch_robustness_v0_4_4.py", "scripts/57_active_interpretability_v0_4_4.py", "scripts/58_active_candidates_and_iact_v0_4_4.py"],
]

def run(path, env, *args):
    command=[sys.executable, path, *map(str,args)]
    print(f"\n=== {' '.join(command[1:])} ===", flush=True)
    subprocess.check_call(command, cwd=ROOT, env=env)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--fast', action='store_true', help='Smoke test with reduced resampling.')
    p.add_argument('--skip-figures', action='store_true')
    a=p.parse_args()
    expected=ROOT/'data/processed/tev_evolution_score_catalog_v0_1_8_xray_control_augmented.csv'
    if not expected.exists():
        expected.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/'data/frozen_analysis_input/tev_evolution_score_catalog_v0_1_8_xray_control_augmented.csv', expected)
    interim=ROOT/'data/interim'; interim.mkdir(parents=True, exist_ok=True)
    for n in ['blazer1_standardized.csv','tevcat_standardized.csv']:
        shutil.copy2(ROOT/'data/frozen_analysis_input'/n, interim/n)
    ext=ROOT/'data/external'; ext.mkdir(parents=True, exist_ok=True)
    for n in ['iact_discovery_history_v0_3_2.csv','iact_observed_outcomes_v0_3_3.csv']:
        shutil.copy2(ROOT/'data/frozen_analysis_input'/n, ext/n)
    env=os.environ.copy()
    if a.fast:
        env.update(BLAZER_V030_N_BOOT='50', BLAZER_V031_N_BOOT='50', BLAZER_V042_N_SHIFT='10', BLAZER_V043_N_BOOT='50', BLAZER_V043_N_PERM='50', BLAZER_V044_N_BOOT='50', BLAZER_V044_N_WEIGHT='30', BLAZER_V043_SEED='8488', BLAZER_V044_SEED='8488', BLAZER_V042_SMOKE_MODE='1')
    else:
        env.update(BLAZER_V030_N_BOOT='5000', BLAZER_V031_N_BOOT='5000', BLAZER_V042_N_SHIFT='1000', BLAZER_V043_N_BOOT='5000', BLAZER_V043_N_PERM='5000', BLAZER_V044_N_BOOT='5000', BLAZER_V044_N_WEIGHT='1000', BLAZER_V043_SEED='8488', BLAZER_V044_SEED='8488')
    phases = [[
        'scripts/44_exact_score_definition_v0_4_2.py',
        'scripts/45_random_shift_crossmatch_audit_v0_4_2.py',
    ]] if a.fast else PHASES
    for phase in phases:
        for step in phase: run(step, env)
    if a.fast:
        run('scripts/62_external_4lac_transfer_v1_1_0.py', env, '--n-bootstrap', '200', '--n-random-shifts', '20')
    else:
        run('scripts/62_external_4lac_transfer_v1_1_0.py', env, '--n-bootstrap', '20000', '--n-random-shifts', '250')
    if not a.skip_figures:
        run('figure_generation/make_manuscript_figures.py', env)
        run('figure_generation/make_workflow_figure.py', env)
    run('validate_package.py', env)
    print('\nRelease reproduction completed successfully.')
if __name__=='__main__': main()
