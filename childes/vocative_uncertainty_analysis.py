#!/usr/bin/env python3
"""
Uncertainty propagation for vocative vs argument counts using manual-check confusion data.
"""
import argparse
import csv
import json
import math
import pathlib
import random
import re
from collections import Counter, defaultdict

# Broad North American kinship list (same as other scripts)
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

# Multiword compounds to treat as single kin lexemes
MULTIWORD = {
    ('grand','ma'): 'grandma',
    ('grand','mom'): 'grandmom',
    ('grand','mommy'): 'grandmommy',
    ('grand','mother'): 'grandmother',
    ('grand','pa'): 'grandpa',
    ('grand','dad'): 'granddad',
    ('grand','daddy'): 'granddaddy',
    ('grand','father'): 'grandfather',
    ('grand','papa'): 'grandpapa',
    ('grand','mama'): 'grandmama',
    ('step','mom'): 'stepmom',
    ('step','dad'): 'stepdad',
    ('step','mother'): 'stepmother',
    ('step','father'): 'stepfather',
    ('step','sister'): 'stepsister',
    ('step','brother'): 'stepbrother',
    ('step','son'): 'stepson',
    ('step','daughter'): 'stepdaughter',
    ('step','child'): 'stepchild',
}

MULTI_COMPONENTS = set()
for a, b in MULTIWORD:
    MULTI_COMPONENTS.add(a)
    MULTI_COMPONENTS.add(b)

DISCOURSE = {
    'hey','hi','hello','oh','okay','ok','yeah','yep','yes','no','please',
    'well','uh','um','huh','hm','hmm','mm'
}

NOISE_RE = re.compile(r'^[xyw]{3,}$')
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
TOKEN_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*|[.,!?]")


def categorize(term: str) -> str:
    if term in PARENT_SET:
        return 'parent'
    if term in GRANDPARENT_SET:
        return 'grandparent'
    return 'extended'


def load_observed_counts(path: pathlib.Path):
    counts = {}
    with path.open() as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            term = row['term'].strip().lower()
            if term not in KINSHIP_SET:
                continue
            voc = int(row['vocative_count'])
            arg = int(row['argument_count'])
            counts[term] = {'voc': voc, 'arg': arg}
    return counts


def aggregate_by_category(counts):
    agg = defaultdict(lambda: {'voc': 0, 'arg': 0})
    for term, vals in counts.items():
        cat = categorize(term)
        agg[cat]['voc'] += vals['voc']
        agg[cat]['arg'] += vals['arg']
    return agg


def parse_confusion(s: str):
    parts = [p.strip() for p in s.split(',')]
    if len(parts) != 4:
        raise ValueError('confusion must be tp,fp,fn,tn')
    tp, fp, fn, tn = (int(p) for p in parts)
    return {'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn}


def normalize_label(val: str):
    v = (val or '').strip().lower()
    if v.startswith('v'):
        return 'vocative'
    if v.startswith('a'):
        return 'argument'
    if v in {'ambig', 'ambiguous', 'uncertain'}:
        return 'ambiguous'
    return None


def confusion_from_labels(path: pathlib.Path, pred_col: str, true_col: str,
                          cat_col: str, ambiguous: str):
    conf = {
        'parent': {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0},
        'extended': {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0},
    }
    with path.open() as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cat_raw = (row.get(cat_col, '') or '').strip().lower()
            if cat_raw not in conf:
                continue
            pred = normalize_label(row.get(pred_col, ''))
            true = normalize_label(row.get(true_col, ''))
            if true == 'ambiguous':
                if ambiguous == 'drop':
                    continue
                true = 'vocative' if ambiguous == 'voc' else 'argument'
            if pred not in {'vocative', 'argument'} or true not in {'vocative', 'argument'}:
                continue
            if pred == 'vocative' and true == 'vocative':
                conf[cat_raw]['tp'] += 1
            elif pred == 'vocative' and true == 'argument':
                conf[cat_raw]['fp'] += 1
            elif pred == 'argument' and true == 'vocative':
                conf[cat_raw]['fn'] += 1
            elif pred == 'argument' and true == 'argument':
                conf[cat_raw]['tn'] += 1
    return conf


def beta_summary(samples):
    samples = list(samples)
    if not samples:
        return {'mean': None, 'median': None, 'q025': None, 'q975': None}
    samples.sort()
    n = len(samples)
    mean = sum(samples) / n
    median = samples[n // 2]
    q025 = samples[int(0.025 * (n - 1))]
    q975 = samples[int(0.975 * (n - 1))]
    return {'mean': mean, 'median': median, 'q025': q025, 'q975': q975}


def simulate_corrections(conf, observed, draws, prior_a, prior_b, seed):
    rng = random.Random(seed)
    out = {}
    for cat in ('parent', 'extended'):
        if cat not in conf:
            continue
        tp = conf[cat]['tp']
        fp = conf[cat]['fp']
        fn = conf[cat]['fn']
        tn = conf[cat]['tn']
        ppv_a = prior_a + tp
        ppv_b = prior_b + fp
        fov_a = prior_a + fn
        fov_b = prior_b + tn
        pred_voc = observed[cat]['voc']
        pred_arg = observed[cat]['arg']
        total = pred_voc + pred_arg
        ppv_draws = []
        fov_draws = []
        rate_draws = []
        for _ in range(draws):
            ppv = rng.betavariate(ppv_a, ppv_b)
            fov = rng.betavariate(fov_a, fov_b)
            true_voc = pred_voc * ppv + pred_arg * fov
            rate = true_voc / total if total else 0.0
            ppv_draws.append(ppv)
            fov_draws.append(fov)
            rate_draws.append(rate)
        out[cat] = {
            'ppv_summary': beta_summary(ppv_draws),
            'fov_summary': beta_summary(fov_draws),
            'true_voc_rate_summary': beta_summary(rate_draws),
            'draws': {
                'ppv': ppv_draws,
                'fov': fov_draws,
                'true_voc_rate': rate_draws,
            },
        }
    if 'parent' in out and 'extended' in out:
        diff = [p - e for p, e in zip(out['parent']['draws']['true_voc_rate'],
                                      out['extended']['draws']['true_voc_rate'])]
        ratio = [p / e if e > 0 else math.inf
                 for p, e in zip(out['parent']['draws']['true_voc_rate'],
                                 out['extended']['draws']['true_voc_rate'])]
        out['contrast'] = {
            'diff_summary': beta_summary(diff),
            'ratio_summary': beta_summary(ratio),
        }
    return out


def norm_surface(tok: str) -> str:
    t = tok.lower()
    if t.endswith("'s") or t.endswith("’s"):
        base = t[:-2]
        if base in KINSHIP_SET or base in MULTI_COMPONENTS:
            t = base
    elif t.endswith("s'"):
        base = t[:-1]
        if base in KINSHIP_SET or base in MULTI_COMPONENTS:
            t = base
    if t.endswith('ies'):
        base = t[:-3] + 'y'
        if base in KINSHIP_SET:
            return base
    if t.endswith('es'):
        base = t[:-2]
        if base in KINSHIP_SET and len(base) >= 3:
            return base
    if t.endswith('s'):
        base = t[:-1]
        if base in KINSHIP_SET and len(base) >= 3:
            return base
    return t


def is_comma_adjacent(tokens, start_idx, end_idx):
    if start_idx > 0 and tokens[start_idx - 1] == ',':
        return True
    if end_idx + 1 < len(tokens) and tokens[end_idx + 1] == ',':
        return True
    return False


def collapse_with_spans(word_norm):
    items = []
    i = 0
    n = len(word_norm)
    while i < n:
        if i + 1 < n and (word_norm[i], word_norm[i + 1]) in MULTIWORD:
            items.append((MULTIWORD[(word_norm[i], word_norm[i + 1])], i, i + 1))
            i += 2
        else:
            items.append((word_norm[i], i, i))
            i += 1
    return items


def compute_counts(root: pathlib.Path, heuristic: str):
    voc_counts = Counter()
    arg_counts = Counter()
    files = list(root.rglob('*.cha'))
    for f in files:
        try:
            lines = f.read_text(errors='ignore').splitlines()
        except Exception:
            continue
        for line in lines:
            if not line.startswith('*'):
                continue
            if ':' not in line:
                continue
            utter = line.split(':', 1)[1]
            tokens = TOKEN_RE.findall(utter)
            word_norm = []
            word_token_idx = []
            for idx, tok in enumerate(tokens):
                if WORD_RE.fullmatch(tok):
                    t = tok.lower()
                    if NOISE_RE.fullmatch(t):
                        continue
                    word_norm.append(norm_surface(tok))
                    word_token_idx.append(idx)
            if not word_norm:
                continue
            items = collapse_with_spans(word_norm)
            filtered = [(lex, s, e) for (lex, s, e) in items
                        if lex not in DISCOURSE and not NOISE_RE.fullmatch(lex)]
            utter_standalone = bool(filtered) and all(lex in KINSHIP_SET for lex, _, _ in filtered)
            initial_lex = filtered[0] if filtered else None
            for lex, start_i, end_i in items:
                if lex not in KINSHIP_SET:
                    continue
                start_tok = word_token_idx[start_i]
                end_tok = word_token_idx[end_i]
                comma = is_comma_adjacent(tokens, start_tok, end_tok)
                if heuristic == 'strict':
                    is_voc = comma
                elif heuristic == 'loose':
                    is_initial = initial_lex is not None and start_i == initial_lex[1]
                    is_voc = comma or utter_standalone or is_initial
                else:
                    is_voc = comma or utter_standalone
                if is_voc:
                    voc_counts[lex] += 1
                else:
                    arg_counts[lex] += 1
    return voc_counts, arg_counts


def write_sensitivity(out_path: pathlib.Path, root: pathlib.Path):
    heuristics = ['default', 'strict', 'loose']
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow([
            'heuristic', 'level', 'label',
            'vocative_count', 'argument_count', 'vocative_percent'
        ])
        for h in heuristics:
            voc_counts, arg_counts = compute_counts(root, h)
            # per-term rows
            for term in KINSHIP:
                voc = voc_counts.get(term, 0)
                arg = arg_counts.get(term, 0)
                total = voc + arg
                pct = (voc / total * 100.0) if total else 0.0
                w.writerow([h, 'term', term, voc, arg, f"{pct:.2f}"])
            # category rows
            cat_voc = defaultdict(int)
            cat_arg = defaultdict(int)
            for term in KINSHIP:
                cat = categorize(term)
                cat_voc[cat] += voc_counts.get(term, 0)
                cat_arg[cat] += arg_counts.get(term, 0)
            for cat in ('parent', 'grandparent', 'extended'):
                voc = cat_voc.get(cat, 0)
                arg = cat_arg.get(cat, 0)
                total = voc + arg
                pct = (voc / total * 100.0) if total else 0.0
                w.writerow([h, 'category', cat, voc, arg, f"{pct:.2f}"])
            all_voc = sum(voc_counts.values())
            all_arg = sum(arg_counts.values())
            total = all_voc + all_arg
            pct = (all_voc / total * 100.0) if total else 0.0
            w.writerow([h, 'category', 'all', all_voc, all_arg, f"{pct:.2f}"])


def main():
    ap = argparse.ArgumentParser(
        description='Propagate uncertainty from manual QC into vocative-rate estimates.'
    )
    ap.add_argument('--observed', required=True,
                    help='TSV with observed vocative/argument counts (e.g., kinship_vocative_argument.tsv)')
    ap.add_argument('--out', required=True, help='Output JSON path')
    ap.add_argument('--draws', type=int, default=20000, help='Posterior draws')
    ap.add_argument('--seed', type=int, default=20260131, help='Random seed')
    ap.add_argument('--prior', default='1,1', help='Beta prior a,b for PPV/FOV')
    ap.add_argument('--confusion-parent', help='tp,fp,fn,tn for parent')
    ap.add_argument('--confusion-extended', help='tp,fp,fn,tn for extended')
    ap.add_argument('--labels', help='Manual-labels TSV to derive confusion')
    ap.add_argument('--pred-col', default='class', help='Predicted label column in labels file')
    ap.add_argument('--true-col', default='manual_label', help='Manual label column in labels file')
    ap.add_argument('--cat-col', default='category', help='Category column in labels file')
    ap.add_argument('--ambiguous', choices=['drop', 'voc', 'arg'], default='drop',
                    help='How to handle ambiguous manual labels')
    ap.add_argument('--samples-out', help='Optional TSV with posterior draws')
    ap.add_argument('--root', help='Eng-NA corpus root for sensitivity analysis')
    ap.add_argument('--sensitivity-out', help='Write sensitivity comparison TSV')
    args = ap.parse_args()

    observed_path = pathlib.Path(args.observed)
    observed_counts = load_observed_counts(observed_path)
    observed_by_cat = aggregate_by_category(observed_counts)
    for cat in ('parent', 'extended', 'grandparent'):
        observed_by_cat.setdefault(cat, {'voc': 0, 'arg': 0})

    prior_a, prior_b = (float(x.strip()) for x in args.prior.split(','))

    conf = {}
    if args.labels:
        conf = confusion_from_labels(
            pathlib.Path(args.labels),
            pred_col=args.pred_col,
            true_col=args.true_col,
            cat_col=args.cat_col,
            ambiguous=args.ambiguous,
        )
    else:
        if not args.confusion_parent or not args.confusion_extended:
            raise SystemExit('Provide --labels or both --confusion-parent and --confusion-extended')
        conf['parent'] = parse_confusion(args.confusion_parent)
        conf['extended'] = parse_confusion(args.confusion_extended)

    posterior = simulate_corrections(
        conf=conf,
        observed=observed_by_cat,
        draws=args.draws,
        prior_a=prior_a,
        prior_b=prior_b,
        seed=args.seed,
    )

    out = {
        'settings': {
            'draws': args.draws,
            'seed': args.seed,
            'prior': {'a': prior_a, 'b': prior_b},
        },
        'observed_counts': observed_by_cat,
        'confusion_counts': conf,
        'posterior_summary': {
            k: {kk: vv for kk, vv in v.items() if kk.endswith('summary')}
            for k, v in posterior.items()
        },
    }

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True))

    if args.samples_out:
        samples_path = pathlib.Path(args.samples_out)
        samples_path.parent.mkdir(parents=True, exist_ok=True)
        with samples_path.open('w', newline='') as f:
            w = csv.writer(f, delimiter='\t')
            w.writerow(['draw', 'parent_rate', 'extended_rate', 'diff', 'ratio'])
            parent_rates = posterior.get('parent', {}).get('draws', {}).get('true_voc_rate', [])
            extended_rates = posterior.get('extended', {}).get('draws', {}).get('true_voc_rate', [])
            for i, (p, e) in enumerate(zip(parent_rates, extended_rates), start=1):
                diff = p - e
                ratio = p / e if e > 0 else math.inf
                w.writerow([i, f"{p:.6f}", f"{e:.6f}", f"{diff:.6f}", f"{ratio:.6f}"])

    if args.sensitivity_out:
        if not args.root:
            raise SystemExit('Provide --root when using --sensitivity-out')
        write_sensitivity(pathlib.Path(args.sensitivity_out), pathlib.Path(args.root))

    print('wrote', out_path)


if __name__ == '__main__':
    main()
