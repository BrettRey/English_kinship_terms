#!/usr/bin/env python3
"""
Plot sensitivity analysis: vocative percent across heuristic variants.
Uses house style for typography consistency.
"""
import argparse
import csv
import pathlib
import sys

# Import house style
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / '.house-style'))
try:
    from plot_style import setup, COLORS, save_figure, add_grid
except ImportError:
    # Fallback if house style not available
    COLORS = {
        'tertiary': '#4DA375',   # Sage green (parent)
        'quaternary': '#9B6B9E', # Muted purple (grandparent)
        'secondary': '#E85D4C',  # Coral (extended)
    }
    def setup(): pass
    def save_figure(fig, path):
        fig.savefig(f'{path}.pdf')
        fig.savefig(f'{path}.png', dpi=200)
    def add_grid(ax, **kw): ax.grid(True, axis='y', linestyle=':', linewidth=0.5)

import matplotlib.pyplot as plt


def main():
    ap = argparse.ArgumentParser(description='Plot sensitivity analysis figure.')
    ap.add_argument('--input', required=True, help='sensitivity_comparison.tsv path')
    ap.add_argument('--out', required=True, help='Output path base (no extension)')
    args = ap.parse_args()

    setup()

    # Load data
    data = {}  # {category: {heuristic: vocative_percent}}
    with pathlib.Path(args.input).open() as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row['level'] != 'category':
                continue
            cat = row['label']
            if cat not in ('parent', 'grandparent', 'extended'):
                continue
            heur = row['heuristic']
            pct = float(row['vocative_percent'])
            data.setdefault(cat, {})[heur] = pct

    # Plotting
    heuristics = ['strict', 'default', 'loose']
    x = range(len(heuristics))

    colors = {
        'parent': COLORS.get('tertiary', '#4DA375'),
        'grandparent': COLORS.get('quaternary', '#9B6B9E'),
        'extended': COLORS.get('secondary', '#E85D4C'),
    }

    fig, ax = plt.subplots(figsize=(4.5, 3.0))

    for cat in ['parent', 'grandparent', 'extended']:
        y = [data.get(cat, {}).get(h, 0) for h in heuristics]
        ax.plot(x, y, 'o-', label=cat, color=colors[cat], markersize=6, linewidth=1.5)

    ax.set_xticks(x)
    ax.set_xticklabels(heuristics)
    ax.set_xlabel('Heuristic variant')
    ax.set_ylabel('Vocative percent')
    ax.set_ylim(0, None)

    # Legend inside plot, upper left
    ax.legend(frameon=False, loc='upper left')

    add_grid(ax, axis='y')
    fig.tight_layout()

    save_figure(fig, args.out)
    print(f'Saved: {args.out}.pdf and {args.out}.png')


if __name__ == '__main__':
    main()
