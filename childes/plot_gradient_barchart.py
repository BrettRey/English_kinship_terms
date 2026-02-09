#!/usr/bin/env python3
"""
Plot gradient bar chart showing bare-argument rate by kinship term,
ordered by the grammaticalization hierarchy.
"""
import argparse
import csv
import pathlib

try:
    import matplotlib.pyplot as plt
except Exception as exc:
    plt = None
    MPL_IMPORT_ERROR = exc
else:
    MPL_IMPORT_ERROR = None


KINSHIP_SET = {
    'mom','mommy','momma','mama','ma','mother',
    'dad','daddy','dada','papa','pa','father',
    'parent',
    'grandma','grandpa','granny','gramma','nana','grandmom','grandmommy',
    'grandmother','grandfather','granddad','granddaddy','gramps','grampa',
    'grandpapa','grandmama','grandparent',
    'aunt','auntie','aunty','uncle','cousin','niece','nephew',
    'brother','sister','sibling','sissy',
    'son','daughter','grandchild','grandson','granddaughter',
}

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


def main():
    ap = argparse.ArgumentParser(description='Plot bare-argument rate gradient by kinship term.')
    ap.add_argument('--input', required=True, help='kinship_vocative_argument.tsv path')
    ap.add_argument('--out-pdf', required=True, help='Output PDF path')
    ap.add_argument('--out-png', required=True, help='Output PNG path')
    ap.add_argument('--min-arg', type=int, default=50, help='Minimum argument count per term')
    args = ap.parse_args()

    if plt is None:
        raise SystemExit(f'matplotlib not available: {MPL_IMPORT_ERROR}')

    # Read data
    rows = []
    with pathlib.Path(args.input).open() as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            term = row['term'].strip().lower()
            if term not in KINSHIP_SET:
                continue
            arg = int(row['argument_count'])
            bare = int(row.get('arg_bare_count', 0))
            det = int(row.get('arg_det_count', 0))
            voc = int(row['vocative_count'])
            if arg < args.min_arg:
                continue
            if bare + det == 0:
                continue
            bare_pct = bare / (bare + det) * 100.0
            voc_pct = voc / (voc + arg) * 100.0 if (voc + arg) else 0.0
            rows.append({
                'term': term,
                'category': categorize(term),
                'bare_pct': bare_pct,
                'voc_pct': voc_pct,
                'arg': arg,
            })

    # Sort by bare_pct descending
    rows.sort(key=lambda r: r['bare_pct'], reverse=True)

    # House style
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['EB Garamond', 'Garamond', 'Georgia', 'Times New Roman'],
        'axes.spines.top': False,
        'axes.spines.right': False,
        'legend.frameon': False,
    })

    colors = {
        'parent': '#4DA375',      # Sage green (house tertiary)
        'grandparent': '#9B6B9E', # Muted purple (house quaternary)
        'extended': '#E85D4C',    # Coral (house secondary)
    }

    # Create horizontal bar chart
    fig, ax = plt.subplots(figsize=(5.2, 4.5))

    terms = [r['term'] for r in rows]
    bare_pcts = [r['bare_pct'] for r in rows]
    bar_colors = [colors[r['category']] for r in rows]

    y_pos = range(len(terms))
    bars = ax.barh(y_pos, bare_pcts, color=bar_colors, height=0.7, alpha=0.9)

    ax.set_yticks(y_pos)
    # Add n to labels
    labels = [f"{r['term']} (n={r['arg']})" for r in rows]
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()  # Highest at top
    ax.set_xlabel('Bare-argument percent')
    ax.set_xlim(0, 100)
    ax.grid(True, axis='x', linestyle=':', linewidth=0.5, color='#E8E8E8')

    # Add category legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=colors['parent'], label='parent'),
        Patch(facecolor=colors['grandparent'], label='grandparent'),
        Patch(facecolor=colors['extended'], label='extended'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=8)

    fig.tight_layout()

    # Save
    out_pdf = pathlib.Path(args.out_pdf)
    out_png = pathlib.Path(args.out_png)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=200)

    print(f'wrote {out_pdf} and {out_png}')
    print(f'Terms included: {len(rows)}')
    for r in rows:
        print(f"  {r['term']:12} {r['bare_pct']:5.1f}% bare  ({r['category']})")


if __name__ == '__main__':
    main()
