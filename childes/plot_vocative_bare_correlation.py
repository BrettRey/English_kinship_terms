#!/usr/bin/env python3
"""
Plot correlation between vocative % and bare-argument % for kinship terms.

Gelman-style: bootstrap CrI for Spearman rho (no p-values, no dual
statistics).  Reports robustness across min-arg thresholds, family
clusters, and child-only speakers.
"""
import argparse
import csv
import json
import math
import pathlib
import random
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

# Family clusters for robustness check: collapse morphological variants
FAMILY_CLUSTERS = {
    'MOM': ['mom', 'mommy', 'momma', 'mama', 'ma', 'mother'],
    'DAD': ['dad', 'daddy', 'dada', 'papa', 'pa', 'father'],
    'GRANDMA': ['grandma', 'granny', 'gramma', 'nana', 'grandmom', 'grandmommy',
                'grandmother', 'grandmama'],
    'GRANDPA': ['grandpa', 'granddad', 'granddaddy', 'gramps', 'grampa',
                'grandfather', 'grandpapa'],
    'AUNT': ['aunt', 'auntie', 'aunty'],
    'UNCLE': ['uncle'],
    'COUSIN': ['cousin'],
    'BROTHER': ['brother'],
    'SISTER': ['sister', 'sissy'],
    'SON': ['son'],
    'DAUGHTER': ['daughter'],
    'NIECE': ['niece'],
    'NEPHEW': ['nephew'],
}


def categorize(term: str) -> str:
    if term in PARENT_SET:
        return 'parent'
    if term in GRANDPARENT_SET:
        return 'grandparent'
    return 'extended'


def categorize_cluster(name: str) -> str:
    members = FAMILY_CLUSTERS[name]
    if members[0] in PARENT_SET:
        return 'parent'
    if members[0] in GRANDPARENT_SET:
        return 'grandparent'
    return 'extended'


def ranks(values):
    sorted_vals = sorted((v, i) for i, v in enumerate(values))
    ranks_out = [0.0] * len(values)
    i = 0
    while i < len(sorted_vals):
        j = i
        while j < len(sorted_vals) and sorted_vals[j][0] == sorted_vals[i][0]:
            j += 1
        avg_rank = (i + j - 1) / 2 + 1
        for k in range(i, j):
            ranks_out[sorted_vals[k][1]] = avg_rank
        i = j
    return ranks_out


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


def spearman(x, y):
    if not x:
        return None
    rx = ranks(x)
    ry = ranks(y)
    return pearson(rx, ry)


def bootstrap_spearman(x, y, n_boot=10000, seed=20260209):
    """Bootstrap CrI for Spearman rho."""
    rng = random.Random(seed)
    n = len(x)
    rhos = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        bx = [x[i] for i in idx]
        by = [y[i] for i in idx]
        r = spearman(bx, by)
        if r is not None:
            rhos.append(r)
    rhos.sort()
    lo = rhos[int(len(rhos) * 0.025)]
    hi = rhos[int(len(rhos) * 0.975)]
    return lo, hi


def load_rows(path, min_arg=50):
    """Load TSV and return list of row dicts passing the min-arg filter."""
    rows = []
    with pathlib.Path(path).open() as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            term = row['term'].strip().lower()
            if term not in KINSHIP_SET:
                continue
            voc = int(row['vocative_count'])
            arg = int(row['argument_count'])
            bare = int(row.get('arg_bare_count', 0))
            det = int(row.get('arg_det_count', 0))
            voc_chi = int(row.get('voc_chi_count', 0))
            if arg < min_arg:
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
                'voc': voc,
                'bare': bare,
                'det': det,
                'voc_chi': voc_chi,
            })
    return rows


def collapse_to_clusters(all_rows_raw, min_arg=50):
    """Collapse morphological variants into family clusters, then filter."""
    # Build a lookup from term -> raw row (before min-arg filter)
    raw = {}
    with pathlib.Path(all_rows_raw).open() as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            term = row['term'].strip().lower()
            if term in KINSHIP_SET:
                raw[term] = row

    cluster_rows = []
    for name, members in FAMILY_CLUSTERS.items():
        voc = sum(int(raw[m]['vocative_count']) for m in members if m in raw)
        arg = sum(int(raw[m]['argument_count']) for m in members if m in raw)
        bare = sum(int(raw[m].get('arg_bare_count', '0')) for m in members if m in raw)
        det = sum(int(raw[m].get('arg_det_count', '0')) for m in members if m in raw)
        if arg < min_arg or bare + det == 0:
            continue
        voc_pct = voc / (voc + arg) * 100.0 if (voc + arg) else 0.0
        bare_pct = bare / (bare + det) * 100.0 if (bare + det) else 0.0
        cluster_rows.append({
            'term': name,
            'category': categorize_cluster(name),
            'voc_pct': voc_pct,
            'bare_pct': bare_pct,
            'arg': arg,
        })
    return cluster_rows


def compute_rho_with_ci(rows):
    """Return (rho, lo, hi, n) for a set of rows."""
    x = [r['voc_pct'] for r in rows]
    y = [r['bare_pct'] for r in rows]
    rho = spearman(x, y)
    lo, hi = bootstrap_spearman(x, y)
    return rho, lo, hi, len(rows)


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

    rows = load_rows(args.input, args.min_arg)
    x = [r['voc_pct'] for r in rows]
    y = [r['bare_pct'] for r in rows]

    rho = spearman(x, y)
    ci_lo, ci_hi = bootstrap_spearman(x, y)

    # House style
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
    ax.legend(loc='lower right')
    fig.tight_layout()

    out_pdf = pathlib.Path(args.out_pdf)
    out_png = pathlib.Path(args.out_png)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=200)

    # Robustness checks
    # 1. Family clusters
    cluster_rows = collapse_to_clusters(args.input, args.min_arg)
    rho_cluster, ci_lo_cluster, ci_hi_cluster, n_cluster = compute_rho_with_ci(cluster_rows)

    # 2. Min-arg sensitivity
    min_arg_sensitivity = {}
    for threshold in [25, 50, 100]:
        trows = load_rows(args.input, threshold)
        tr, tlo, thi, tn = compute_rho_with_ci(trows)
        min_arg_sensitivity[str(threshold)] = {
            'rho': tr, 'ci_lo': tlo, 'ci_hi': thi, 'n': tn
        }

    if args.stats_out:
        stats = {
            'n_terms': len(rows),
            'min_arg': args.min_arg,
            'spearman_rho': rho,
            'ci_lo': ci_lo,
            'ci_hi': ci_hi,
            'bootstrap_draws': 10000,
            'robustness': {
                'family_clusters': {
                    'rho': rho_cluster,
                    'ci_lo': ci_lo_cluster,
                    'ci_hi': ci_hi_cluster,
                    'n': n_cluster,
                },
                'min_arg_sensitivity': min_arg_sensitivity,
            },
        }
        pathlib.Path(args.stats_out).write_text(json.dumps(stats, indent=2))

    print(f'Spearman rho = {rho:.2f} [{ci_lo:.2f}, {ci_hi:.2f}] (n={len(rows)})')
    print(f'Family clusters: rho = {rho_cluster:.2f} [{ci_lo_cluster:.2f}, {ci_hi_cluster:.2f}] (n={n_cluster})')
    for thresh, s in min_arg_sensitivity.items():
        print(f'min-arg {thresh}: rho = {s["rho"]:.2f} [{s["ci_lo"]:.2f}, {s["ci_hi"]:.2f}] (n={s["n"]})')
    print('wrote', out_pdf, out_png)


if __name__ == '__main__':
    main()
