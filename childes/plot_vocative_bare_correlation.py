#!/usr/bin/env python3
"""
Plot correlation between vocative % and bare-argument % for kinship terms.
"""
import argparse
import csv
import json
import math
import pathlib
import sys

try:
    import matplotlib.pyplot as plt
except Exception as exc:  # pragma: no cover
    plt = None
    MPL_IMPORT_ERROR = exc
else:
    MPL_IMPORT_ERROR = None


KINSHIP = [
    'mom','mommy','momma','mama','ma','mother',
    'dad','daddy','dada','papa','pa','father',
    'parent',
    'grandma','grandpa','granny','gramma','nana','grandmom','grandmommy',
    'grandmother','grandfather','granddad','granddaddy','gramps','grampa',
    'grandpapa','grandmama','grandparent',
    'aunt','auntie','aunty','uncle','cousin','niece','nephew',
    'brother','sister','sibling','sissy',
    'son','daughter','grandchild','grandson','granddaughter',
    'stepmom','stepdad','stepmother','stepfather','stepsister','stepbrother','stepson','stepdaughter','stepchild'
]

KINSHIP_SET = set(KINSHIP)

PARENT_SET = {
    'mom','mommy','momma','mama','ma','mother',
    'dad','daddy','dada','papa','pa','father'
}

GRANDPARENT_SET = {
    'grandma','grandpa','granny','gramma','nana','grandmom','grandmommy',
    'grandmother','grandfather','granddad','granddaddy','gramps','grampa',
    'grandpapa','grandmama','grandparent'
}


def categorize(term: str) -> str:
    if term in PARENT_SET:
        return 'parent'
    if term in GRANDPARENT_SET:
        return 'grandparent'
    return 'extended'


def pearson(x, y):
    n = len(x)
    if n == 0:
        return None
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    den_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
    den_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def ranks(values):
    # average ranks for ties
    sorted_vals = sorted((v, i) for i, v in enumerate(values))
    ranks_out = [0.0] * len(values)
    i = 0
    while i < len(sorted_vals):
        j = i
        while j < len(sorted_vals) and sorted_vals[j][0] == sorted_vals[i][0]:
            j += 1
        avg_rank = (i + j - 1) / 2 + 1  # 1-based
        for k in range(i, j):
            ranks_out[sorted_vals[k][1]] = avg_rank
        i = j
    return ranks_out


def spearman(x, y):
    if not x:
        return None
    rx = ranks(x)
    ry = ranks(y)
    return pearson(rx, ry)


def main():
    ap = argparse.ArgumentParser(description='Plot vocative % vs bare-argument % correlation.')
    ap.add_argument('--input', required=True, help='kinship_vocative_argument.tsv path')
    ap.add_argument('--out-pdf', required=True, help='Output PDF path')
    ap.add_argument('--out-png', required=True, help='Output PNG path')
    ap.add_argument('--stats-out', help='Optional JSON summary path')
    ap.add_argument('--min-arg', type=int, default=50, help='Minimum argument count per term')
    args = ap.parse_args()

    if plt is None:
        raise SystemExit(f'matplotlib not available: {MPL_IMPORT_ERROR}')

    rows = []
    with pathlib.Path(args.input).open() as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            term = row['term'].strip().lower()
            if term not in KINSHIP_SET:
                continue
            voc = int(row['vocative_count'])
            arg = int(row['argument_count'])
            bare = int(row.get('arg_bare_count', 0))
            det = int(row.get('arg_det_count', 0))
            if arg < args.min_arg:
                continue
            if bare + det == 0:
                continue
            voc_pct = voc / (voc + arg) * 100.0 if (voc + arg) else 0.0
            bare_pct = bare / (bare + det) * 100.0 if (bare + det) else 0.0
            rows.append({
                'term': term,
                'category': categorize(term),
                'voc_pct': voc_pct,
                'bare_pct': bare_pct,
                'arg': arg,
            })

    x = [r['voc_pct'] for r in rows]
    y = [r['bare_pct'] for r in rows]

    r_pearson = pearson(x, y)
    r_spearman = spearman(x, y)

    # House style setup
    # House style from shared module
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / '.house-style'))
    try:
        from plot_style import setup, COLORS, save_figure, add_grid
    except ImportError:
        print("Warning: plot_style not found, using defaults")
        COLORS = {'primary': 'black', 'secondary': '#E85D4C', 'tertiary': '#4DA375', 'quaternary': '#9B6B9E'}
        def setup(): pass
        def save_figure(fig, path): fig.savefig(path)
        def add_grid(ax, **kw): ax.grid(True, axis='y')

    setup()

    colors = {
        'parent': COLORS['tertiary'],
        'grandparent': COLORS['quaternary'],
        'extended': COLORS['secondary'],
    }

    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    for cat in ['parent', 'grandparent', 'extended']:
        xs = [r['voc_pct'] for r in rows if r['category'] == cat]
        ys = [r['bare_pct'] for r in rows if r['category'] == cat]
        if xs:
            ax.scatter(xs, ys, label=cat, alpha=0.9, s=32, color=colors[cat])

    ax.set_xlabel('Vocative percent')
    ax.set_ylabel('Bare-argument percent')
    ax.grid(True, axis='y', linestyle=':', linewidth=0.5, color='#E8E8E8')
    # Legend inside plot, lower right (no overlap with data)
    ax.legend(loc='lower right')
    # No title here - stats go in figure caption
    fig.tight_layout()

    out_pdf = pathlib.Path(args.out_pdf)
    out_png = pathlib.Path(args.out_png)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=200)

    if args.stats_out:
        stats = {
            'n_terms': len(rows),
            'min_arg': args.min_arg,
            'pearson_r': r_pearson,
            'spearman_rho': r_spearman,
        }
        pathlib.Path(args.stats_out).write_text(json.dumps(stats, indent=2))

    print('wrote', out_pdf, out_png)


if __name__ == '__main__':
    main()
