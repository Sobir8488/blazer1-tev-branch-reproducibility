from __future__ import annotations

from pathlib import Path
import csv
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'figures'
DATA = ROOT / 'figure_source_data'
FIG.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)

# MNRAS-friendly typography and true-type embedding.
mpl.rcParams.update({
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'font.family': 'serif',
    'font.serif': ['DejaVu Serif'],
    'mathtext.fontset': 'dejavuserif',
    'font.size': 8.5,
    'axes.labelsize': 8.5,
    'axes.titlesize': 8.5,
    'xtick.labelsize': 7.5,
    'ytick.labelsize': 7.5,
    'legend.fontsize': 7.2,
    'axes.linewidth': 0.7,
    'xtick.major.width': 0.7,
    'ytick.major.width': 0.7,
    'xtick.major.size': 3,
    'ytick.major.size': 3,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.02,
})

# Color-blind-safe palette (Okabe-Ito family).
BLUE = '#0072B2'
ORANGE = '#D55E00'
GREEN = '#009E73'
PURPLE = '#CC79A7'
SKY = '#56B4E9'
YELLOW = '#E69F00'
GREY = '#6E6E6E'
LIGHT_GREY = '#D9D9D9'
BLACK = '#222222'


def clean(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(direction='out')


def panel(ax, label):
    ax.text(-0.12, 1.05, label, transform=ax.transAxes, fontweight='bold', va='bottom')


FIGURE_NAMES = {
    'Fig_active_TeVCat_validation_v0_5_3': 'figure_01_tevcat_validation.pdf',
    'Fig_active_harmonized_auc_v0_5_3': 'figure_02_harmonized_auc.pdf',
    'Fig_active_coverage_conditioning_v0_5_3': 'figure_03_coverage_conditioning.pdf',
    'Fig_active_ordered_branch_v0_5_3': 'figure_04_ordered_branch.pdf',
    'Fig_active_component_contributions_v0_5_3': 'figure_05_component_contributions.pdf',
    'Fig_active_hsp_circularity_v0_5_3': 'figure_06_hsp_sensitivity.pdf',
    'Fig_active_followup_lists_v0_5_3': 'figure_07_followup_lists.pdf',
}

def save(fig, stem):
    fig.savefig(FIG / FIGURE_NAMES[stem])
    plt.close(fig)


def write_csv(name, fieldnames, rows):
    with (DATA / name).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)


def figure_1_validation():
    # Exact tier-boundary values from v0.4.4 production outputs.
    rows = [
        {'tier': 'Start', 'catalogue_fraction': 0.0, 'recovery': 0.0, 'ci_low': 0.0, 'ci_high': 0.0, 'enrichment': np.nan},
        {'tier': 'Gold', 'catalogue_fraction': 294/5865, 'recovery': 21/34, 'ci_low': 0.450410, 'ci_high': 0.760998, 'enrichment': 12.321429},
        {'tier': 'Gold+Silver', 'catalogue_fraction': 880/5865, 'recovery': 30/34, 'ci_low': 0.733792, 'ci_high': 0.953286, 'enrichment': 5.880682},
        {'tier': 'Gold+Silver+Bronze', 'catalogue_fraction': 1760/5865, 'recovery': 1.0, 'ci_low': 0.898485, 'ci_high': 1.0, 'enrichment': 3.332386},
    ]
    write_csv('figure_1_tier_boundary_validation.csv', list(rows[0].keys()), rows)

    fig, axs = plt.subplots(1, 2, figsize=(6.95, 2.65), gridspec_kw={'wspace': 0.36})
    ax = axs[0]
    x = np.array([r['catalogue_fraction'] for r in rows])
    y = np.array([r['recovery'] for r in rows])
    # Extend the final tier to the full-catalogue endpoint without adding a separate annotation.
    x_step = np.r_[x, 1.0]; y_step = np.r_[y, 1.0]
    ax.step(x_step, y_step, where='post', color=BLUE, lw=1.6)
    ax.scatter(x[1:4], y[1:4], color=BLUE, s=25, zorder=3, edgecolor='white', linewidth=0.5)
    ax.plot([0, 1], [0, 1], ls='--', lw=1.0, color=GREY, label='Random ordering')
    for r, dy in zip(rows[1:4], [0.035, -0.08, -0.08]):
        ax.annotate(f"{int(round(100*r['catalogue_fraction']))}%: {int(round(34*r['recovery']))}/34",
                    (r['catalogue_fraction'], r['recovery']), xytext=(4, 10 if dy > 0 else -16),
                    textcoords='offset points', fontsize=7.2)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.03)
    ax.set_xlabel('Fraction of catalogue inspected')
    ax.set_ylabel('Fraction of TeVCat matches recovered')
    ax.legend(frameon=False, loc='lower right')
    clean(ax); panel(ax, '(a)')

    ax = axs[1]
    rr = rows[1:4]
    yy = np.arange(len(rr))
    rec = np.array([r['recovery'] for r in rr])
    lo = rec - np.array([r['ci_low'] for r in rr])
    hi = np.array([r['ci_high'] for r in rr]) - rec
    ax.errorbar(rec, yy, xerr=[lo, hi], fmt='o', color=ORANGE, ecolor=ORANGE,
                capsize=3, ms=5, lw=1.1)
    ax.set_yticks(yy, ['Gold', 'Gold+Silver', 'Top 30%'])
    ax.invert_yaxis(); ax.set_xlim(0.35, 1.04)
    ax.set_xlabel('Recovery fraction (Wilson 95% interval)')
    for i, r in enumerate(rr):
        ax.text(min(r['ci_high'] + 0.02, 1.01), i, f"E={r['enrichment']:.2f}", va='center', fontsize=7.2)
    clean(ax); panel(ax, '(b)')
    save(fig, 'Fig_active_TeVCat_validation_v0_5_3')


def figure_2_harmonized_auc():
    rows = [
        {'score': 'X-ray only', 'auc': 0.969637, 'ci_low': 0.940526, 'ci_high': 0.989010},
        {'score': 'Active branch', 'auc': 0.939635, 'ci_low': 0.915964, 'ci_high': 0.961182},
        {'score': 'No X-ray', 'auc': 0.876014, 'ci_low': 0.841548, 'ci_high': 0.907858},
    ]
    write_csv('figure_2_harmonized_auc.csv', list(rows[0].keys()), rows)
    fig, ax = plt.subplots(figsize=(3.35, 2.55), constrained_layout=True)
    x = np.arange(3)
    y = np.array([r['auc'] for r in rows])
    lo = y - np.array([r['ci_low'] for r in rows])
    hi = np.array([r['ci_high'] for r in rows]) - y
    cols = [ORANGE, BLUE, GREY]
    for i in range(3):
        ax.errorbar(i, y[i], yerr=[[lo[i]], [hi[i]]], fmt='o', color=cols[i],
                    ecolor=cols[i], capsize=3.5, ms=5.5, lw=1.2)
        ax.text(i, r['ci_high'] + 0.009 if (r := rows[i]) else y[i], f"{y[i]:.3f}", ha='center', fontsize=7.2)
    ax.set_xticks(x, [r['score'] for r in rows])
    ax.set_ylabel('AUROC (95% bootstrap interval)')
    ax.set_ylim(0.82, 1.005)
    ax.grid(axis='y', color=LIGHT_GREY, lw=0.5, alpha=0.8)
    ax.text(0.5, 0.833, r'$\Delta\mathrm{AUROC}_{X-\mathrm{active}}=0.030$, $p=1.45\times10^{-3}$',
            ha='center', fontsize=6.9)
    clean(ax)
    save(fig, 'Fig_active_harmonized_auc_v0_5_3')


def figure_3_coverage():
    rows = [
        {'score': 'X-ray only', 'unrestricted': 0.970472, 'conditioned': 0.916605},
        {'score': 'Active branch', 'unrestricted': 0.940980, 'conditioned': 0.880460},
        {'score': 'No X-ray', 'unrestricted': 0.876014, 'conditioned': 0.825484},
    ]
    write_csv('figure_3_coverage_conditioning.csv', list(rows[0].keys()), rows)
    fig, ax = plt.subplots(figsize=(3.35, 2.55))
    xx = [0, 1]
    for r, c, marker in zip(rows, [ORANGE, BLUE, GREY], ['o', 's', '^']):
        yy = [r['unrestricted'], r['conditioned']]
        ax.plot(xx, yy, color=c, marker=marker, lw=1.35, ms=4.8, label=r['score'])
        ax.text(-0.045, yy[0], f"{yy[0]:.3f}", ha='right', va='center', color=c, fontsize=6.8)
        ax.text(1.045, yy[1], f"{yy[1]:.3f}", ha='left', va='center', color=c, fontsize=6.8)
    ax.set_xticks(xx, ['Unrestricted', 'Exact-pattern\nconditioned'])
    ax.set_xlim(-0.28, 1.28); ax.set_ylim(0.79, 1.0)
    ax.set_ylabel('AUROC')
    ax.grid(axis='y', color=LIGHT_GREY, lw=0.5)
    ax.legend(frameon=False, loc='lower left')
    clean(ax)
    save(fig, 'Fig_active_coverage_conditioning_v0_5_3')


def figure_4_branch():
    rows = [
        {'stage': 'FSRQ/QSO', 'score': -0.350, 'z': 1.216, 'lognu': 12.346},
        {'stage': 'BCU/uncertain', 'score': -0.202, 'z': 0.875, 'lognu': 12.363},
        {'stage': 'BL Lac', 'score': 0.370, 'z': 0.462, 'lognu': 13.212},
        {'stage': 'HSP', 'score': 1.875, 'z': 0.378, 'lognu': 16.500},
    ]
    write_csv('figure_4_ordered_branch.csv', list(rows[0].keys()), rows)
    fig, axs = plt.subplots(1, 3, figsize=(6.95, 2.48), gridspec_kw={'wspace': 0.43})
    x = np.arange(4); labels = [r['stage'] for r in rows]
    values = [
        ([r['score'] for r in rows], r'Median $S_{\rm TeV,branch}$', (-0.55, 2.10), 3),
        ([r['z'] for r in rows], 'Median redshift', (0, 1.34), 3),
        ([r['lognu'] for r in rows], r'Median $\log\nu_{\rm peak}$ proxy', (11.5, 17.2), 3),
    ]
    stage_colors = ['#B8D4E8', '#82B8D8', '#4D9BC6', BLUE]
    for j, (vals, ylabel, ylim, decimals) in enumerate(values):
        ax = axs[j]
        bars = ax.bar(x, vals, color=stage_colors, edgecolor='white', linewidth=0.5)
        ax.set_xticks(x, labels, rotation=27, ha='right')
        ax.set_ylabel(ylabel); ax.set_ylim(*ylim)
        ax.axhline(0, color=GREY, lw=0.6) if j == 0 else None
        for b, v in zip(bars, vals):
            dy = 0.035*(ylim[1]-ylim[0])
            ax.text(b.get_x()+b.get_width()/2, v + (dy if v >= 0 else -dy), f'{v:.{decimals}f}',
                    ha='center', va='bottom' if v >= 0 else 'top', fontsize=6.8)
        clean(ax); panel(ax, f'({chr(97+j)})')
    save(fig, 'Fig_active_ordered_branch_v0_5_3')


def figure_5_contributions():
    components = [
        ('X-ray brightness', BLUE),
        ('Gamma hardness', YELLOW),
        ('Gamma variability', GREEN),
        ('WISE/HSP locus', ORANGE),
        ('Synchrotron peak proxy', PURPLE),
        ('Compton-dominance penalty', '#8C564B'),
        ('Redshift/EBL penalty', '#E78AC3'),
    ]
    known = [37.646738, 6.168862, 9.222498, 4.300260, 28.956320, 6.221798, 7.483523]
    gold = [26.060757, 2.833159, 0.784852, 7.454924, 52.936272, 2.957155, 6.972881]
    rows = []
    for sample, vals in [('Known TeV', known), ('Gold non-TeV', gold)]:
        for (label, _), v in zip(components, vals): rows.append({'sample': sample, 'component': label, 'percent': v})
    write_csv('figure_5_component_contributions.csv', ['sample', 'component', 'percent'], rows)

    fig, ax = plt.subplots(figsize=(6.95, 2.42))
    y = np.array([1, 0])
    left = np.zeros(2)
    for idx, (label, color) in enumerate(components):
        vals = np.array([known[idx], gold[idx]])
        ax.barh(y, vals, left=left, color=color, label=label, height=0.52,
                edgecolor='white', linewidth=0.45)
        left += vals
    ax.set_yticks(y, ['Known TeV', 'Gold non-TeV'])
    ax.set_xlim(0, 100); ax.set_xlabel('Fraction of total absolute contribution (%)')
    ax.text(37.646738/2, 1, 'X-ray\n37.6%', ha='center', va='center', color='white', fontsize=7, fontweight='bold')
    ax.text(26.060757/2, 0, 'X-ray\n26.1%', ha='center', va='center', color='white', fontsize=7, fontweight='bold')
    peak_left_known = sum(known[:4]); peak_left_gold = sum(gold[:4])
    ax.text(peak_left_known + known[4]/2, 1, 'Peak\n29.0%', ha='center', va='center', fontsize=7, fontweight='bold')
    ax.text(peak_left_gold + gold[4]/2, 0, 'Peak\n52.9%', ha='center', va='center', fontsize=7, fontweight='bold')
    ax.legend(ncol=4, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.26),
              columnspacing=1.0, handlelength=1.2)
    clean(ax)
    save(fig, 'Fig_active_component_contributions_v0_5_3')


def figure_6_hsp():
    rows = [
        {'variant': 'Active', 'auc': 0.940980, 'gold': 21/34, 'gs': 30/34, 'jaccard': 1.0, 'top30': 1.0},
        {'variant': 'No HSP', 'auc': 0.958190, 'gold': 24/34, 'gs': 32/34, 'jaccard': 0.348624, 'top30': 13/30},
        {'variant': 'Continuous', 'auc': 0.958230, 'gold': 24/34, 'gs': 32/34, 'jaccard': 0.348624, 'top30': 13/30},
        {'variant': 'No peak', 'auc': 0.959996, 'gold': 25/34, 'gs': 32/34, 'jaccard': 0.367442, 'top30': 11/30},
    ]
    write_csv('figure_6_hsp_sensitivity.csv', list(rows[0].keys()), rows)
    fig, axs = plt.subplots(1, 2, figsize=(6.95, 2.7), gridspec_kw={'wspace': 0.33})
    x = np.arange(4)
    labels = [r['variant'] for r in rows]
    for key, label, c, marker in [('auc','AUROC',BLUE,'o'), ('gold','Gold recovery',ORANGE,'s'), ('gs','Gold+Silver recovery',GREEN,'^')]:
        yy = np.array([r[key] for r in rows])
        axs[0].plot(x, yy, marker=marker, color=c, label=label, lw=1.2, ms=4.5)
    axs[0].set_xticks(x, labels, rotation=22, ha='right'); axs[0].set_ylim(0.55, 1.01)
    axs[0].set_ylabel('Validation metric'); axs[0].grid(axis='y', color=LIGHT_GREY, lw=0.5)
    axs[0].legend(frameon=False, loc='lower right')
    clean(axs[0]); panel(axs[0], '(a)')
    for key, label, c, marker in [('jaccard','Gold Jaccard',PURPLE,'o'), ('top30','Top-30 overlap fraction',GREY,'s')]:
        yy = np.array([r[key] for r in rows])
        axs[1].plot(x, yy, marker=marker, color=c, label=label, lw=1.2, ms=4.5)
    axs[1].set_xticks(x, labels, rotation=22, ha='right'); axs[1].set_ylim(0, 1.04)
    axs[1].set_ylabel('Candidate-identity stability'); axs[1].grid(axis='y', color=LIGHT_GREY, lw=0.5)
    axs[1].legend(frameon=False, loc='upper right')
    clean(axs[1]); panel(axs[1], '(b)')
    save(fig, 'Fig_active_hsp_circularity_v0_5_3')


def figure_7_followup():
    rows = [
        {'list': 'List A core', 'n': 183, 'active_percentile': 94.87, 'xray_percentile': 97.61},
        {'list': 'List B core', 'n': 78, 'active_percentile': 97.99, 'xray_percentile': 88.34},
    ]
    write_csv('figure_7_followup_lists.csv', list(rows[0].keys()), rows)
    fig, ax = plt.subplots(figsize=(3.35, 2.35))
    yy = np.array([1, 0])
    for i, r in enumerate(rows):
        y = yy[i]
        ax.plot([r['active_percentile'], r['xray_percentile']], [y, y], color=LIGHT_GREY, lw=2)
        ax.scatter(r['active_percentile'], y, color=BLUE, s=35, label='Active percentile' if i == 0 else None, zorder=3)
        ax.scatter(r['xray_percentile'], y, color=ORANGE, s=35, marker='s', label='X-ray percentile' if i == 0 else None, zorder=3)
        ax.text(r['active_percentile'], y+0.13, f"{r['active_percentile']:.1f}", ha='center', fontsize=6.9, color=BLUE)
        ax.text(r['xray_percentile'], y-0.16, f"{r['xray_percentile']:.1f}", ha='center', fontsize=6.9, color=ORANGE)
    ax.set_yticks(yy, [f"List A: X-ray-prioritized\ncore (N={rows[0]['n']})", f"List B: HSP frontier\ncore (N={rows[1]['n']})"])
    ax.set_xlim(60, 101); ax.set_ylim(-0.5, 1.5)
    ax.set_xlabel('Median parent-sample percentile')
    ax.grid(axis='x', color=LIGHT_GREY, lw=0.5)
    ax.legend(frameon=False, loc='lower center', bbox_to_anchor=(0.5, -0.33), ncol=2)
    clean(ax)
    save(fig, 'Fig_active_followup_lists_v0_5_3')


def main():
    figure_1_validation()
    figure_2_harmonized_auc()
    figure_3_coverage()
    figure_4_branch()
    figure_5_contributions()
    figure_6_hsp()
    figure_7_followup()
    print('Created seven polished PDF figures and source-data CSV files.')


if __name__ == '__main__':
    main()
