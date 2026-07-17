from __future__ import annotations

from pathlib import Path
import textwrap
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

mpl.rcParams.update({
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'font.family': 'DejaVu Serif',
    'font.size': 8,
    'axes.unicode_minus': False,
})

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)

# Taller canvas gives every text block enough physical height at MNRAS width.
fig, ax = plt.subplots(figsize=(7.25, 5.35))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

P = {
    'A_fill': '#EAF2F8', 'A_edge': '#3E6B8A', 'A_head': '#D7E7F2',
    'B_fill': '#FFF1DF', 'B_edge': '#A96822', 'B_head': '#F8E2C8',
    'C_fill': '#EAF5EA', 'C_edge': '#467447', 'C_head': '#DCEEDC',
    'side_fill': '#F3F3F3', 'side_edge': '#666666', 'text': '#111111',
    'flow': '#505050'
}

box_records = []
text_records = []


def wrap_bullets(lines, width=32):
    out = []
    for s in lines:
        parts = textwrap.wrap(
            s, width=width, break_long_words=False, break_on_hyphens=False
        ) or ['']
        out.append('• ' + parts[0])
        out.extend('  ' + q for q in parts[1:])
    return '\n'.join(out)


def header(x, y, w, text, fill, edge):
    patch = FancyBboxPatch(
        (x, y), w, 0.058,
        boxstyle='round,pad=0.0035,rounding_size=0.009',
        facecolor=fill, edgecolor=edge, linewidth=1.0, zorder=3
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2, y + 0.029, text,
        ha='center', va='center', fontsize=8.0, fontweight='bold',
        color=edge, zorder=4
    )


def box(x, y, w, h, title, lines, fill, edge, body=6.55, wrap=32):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle='round,pad=0.006,rounding_size=0.011',
        facecolor=fill, edgecolor=edge, linewidth=1.05, zorder=3
    )
    ax.add_patch(patch)
    title_obj = ax.text(
        x + 0.014, y + h - 0.026, title,
        ha='left', va='top', fontsize=7.65, fontweight='bold',
        color=P['text'], zorder=4
    )
    body_obj = ax.text(
        x + 0.014, y + h - 0.066, wrap_bullets(lines, wrap),
        ha='left', va='top', fontsize=body, linespacing=1.14,
        color=P['text'], zorder=4
    )
    box_records.append((patch, (x, y, w, h), title))
    text_records.extend([(title_obj, (x, y, w, h), title + ' [title]'),
                         (body_obj, (x, y, w, h), title + ' [body]')])


def arrow(x1, y1, x2, y2, color=None, ls='solid', lw=1.25, zorder=2):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=10.0,
        linewidth=lw, linestyle=ls, color=color or P['flow'],
        shrinkA=0, shrinkB=0, zorder=zorder
    ))


def elbow_arrow(points, color, ls='dashed', lw=1.1):
    """Draw an orthogonal route; only the final segment carries the arrowhead."""
    for (x1, y1), (x2, y2) in zip(points[:-2], points[1:-1]):
        ax.plot([x1, x2], [y1, y2], color=color, linestyle=ls,
                linewidth=lw, zorder=1.5, solid_capstyle='round')
    (x1, y1), (x2, y2) = points[-2], points[-1]
    arrow(x1, y1, x2, y2, color=color, ls=ls, lw=lw, zorder=2)


cols = [(0.022, 0.286), (0.357, 0.286), (0.692, 0.286)]
ys = [0.666, 0.411, 0.156]
h = 0.190
header_y = 0.920
header_h = 0.058

header(cols[0][0], header_y, cols[0][1], 'A  LABEL-FREE CONSTRUCTION', P['A_head'], P['A_edge'])
header(cols[1][0], header_y, cols[1][1], 'B  EXTERNAL EVALUATION', P['B_head'], P['B_edge'])
header(cols[2][0], header_y, cols[2][1], 'C  CLAIM-GATED OUTPUTS', P['C_head'], P['C_edge'])

# Phase-to-phase arrows stay entirely in the header gutters.
arrow(cols[0][0] + cols[0][1] + 0.006, header_y + header_h/2,
      cols[1][0] - 0.006, header_y + header_h/2, lw=1.15)
arrow(cols[1][0] + cols[1][1] + 0.006, header_y + header_h/2,
      cols[2][0] - 0.006, header_y + header_h/2, lw=1.15)

# A: label-free construction
box(cols[0][0], ys[0], cols[0][1], h, '1  Frozen catalogue', [
    'BlazEr1 parent (N = 5865) plus attached survey layers',
    'Freeze local derivatives, provenance, and manifest',
], P['A_fill'], P['A_edge'])
box(cols[0][0], ys[1], cols[0][1], h, '2  Resolve active features', [
    'Transform and robustly standardize the resolved inputs',
    'Use seven informative components; omit missing terms',
], P['A_fill'], P['A_edge'])
box(cols[0][0], ys[2], cols[0][1], h, '3  Freeze branch and tiers', [
    'Compute the active branch coordinate',
    'Fix 5 / 10 / 15 / 70 per cent tiers before TeVCat labels',
], P['A_fill'], P['A_edge'])

# B: external evaluation
box(cols[1][0], ys[0], cols[1][1], h, '4  Retrospective validation', [
    'Attach 34 TeVCat matches only after the ranking is frozen',
    'Measure enrichment and harmonized AUROC with paired inference',
], P['B_fill'], P['B_edge'])
box(cols[1][0], ys[1], cols[1][1], h, '5  Control selection history', [
    'Compare X-ray-only, no-X-ray, and exact availability patterns',
    'Run random-shift and X-ray-matched controls',
], P['B_fill'], P['B_edge'])
box(cols[1][0], ys[2], cols[1][1], h, '6  Test robustness and identity', [
    'Weight, leave-one-out, HSP, and PCA audits',
    'Separate aggregate recovery from candidate stability',
], P['B_fill'], P['B_edge'])

# C: claim-gated outputs
box(cols[2][0], ys[0], cols[2][1], h, '7  Population interpretation', [
    'Quantify the X-ray gateway and coverage-history contribution',
    'Map the low-z, high-peak branch and component asymmetry',
], P['C_fill'], P['C_edge'])
box(cols[2][0], ys[1], cols[2][1], h, '8  Follow-up products', [
    'List A: 243 stable X-ray-prioritized sources',
    'List B: 163 proxy-sensitive HSP-frontier sources',
    'Gate by redshift, attenuation, and score stability',
], P['C_fill'], P['C_edge'], body=6.25, wrap=30)
box(cols[2][0], ys[2], cols[2][1], h, '9  External consistency checks', [
    'Report-date chronology and observed-control pilot',
    'Treat as targetability checks, not detection probabilities',
], P['C_fill'], P['C_edge'])

# Within-column flow arrows live only in white gaps between boxes.
for x, w in cols:
    xc = x + w / 2
    arrow(xc, ys[0] - 0.007, xc, ys[1] + h + 0.007)
    arrow(xc, ys[1] - 0.007, xc, ys[2] + h + 0.007)

# External sidecars in a dedicated lower band.
side_y, side_h = 0.030, 0.060
side1 = (0.420, side_y, 0.170, side_h)
side2 = (0.748, side_y, 0.185, side_h)
for x, y, w, hh in [side1, side2]:
    ax.add_patch(FancyBboxPatch(
        (x, y), w, hh,
        boxstyle='round,pad=0.0035,rounding_size=0.007',
        facecolor=P['side_fill'], edgecolor=P['side_edge'],
        linewidth=0.9, zorder=3
    ))
ax.text(side1[0] + side1[2]/2, side_y + side_h/2,
        'TeVCat labels\nenter after ranking',
        ha='center', va='center', fontsize=6.45, color='#333333', zorder=4)
ax.text(side2[0] + side2[2]/2, side_y + side_h/2,
        'IACT reports and\nobserved outcomes',
        ha='center', va='center', fontsize=6.45, color='#333333', zorder=4)

# Dashed routes use the inter-column gutters and never cross a box.
gutter_ab = 0.333
elbow_arrow([
    (side1[0] + side1[2]/2, side_y + side_h),
    (gutter_ab, side_y + side_h),
    (gutter_ab, ys[0] + h/2),
    (cols[1][0] - 0.008, ys[0] + h/2),
], P['B_edge'])

gutter_bc = 0.668
elbow_arrow([
    (side2[0] + side2[2]/2, side_y + side_h),
    (gutter_bc, side_y + side_h),
    (gutter_bc, ys[2] + h/2),
    (cols[2][0] - 0.008, ys[2] + h/2),
], P['C_edge'])

fig.subplots_adjust(left=0.008, right=0.992, top=0.995, bottom=0.005)

# Render once and validate that every text block stays inside its assigned box.
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
inv = ax.transData.inverted()
violations = []
for text_obj, (x, y, w, hh), label in text_records:
    bb = text_obj.get_window_extent(renderer=renderer)
    (x0, y0), (x1, y1) = inv.transform([[bb.x0, bb.y0], [bb.x1, bb.y1]])
    margin = 0.006
    if x0 < x - margin or x1 > x + w + margin or y0 < y - margin or y1 > y + hh + margin:
        violations.append((label, (x0, y0, x1, y1), (x, y, x+w, y+hh)))
if violations:
    raise RuntimeError(f'Text overflow detected: {violations}')

path = OUT / 'figure_08_analysis_workflow.pdf'
fig.savefig(path, bbox_inches='tight', pad_inches=0.025)
plt.close(fig)
print('Wrote workflow PDF v1.0.0; text-overflow validation passed.')
