#!/usr/bin/env python3
"""
Stratified reservoir sample for manual QC of vocative vs argument labels.
"""
import argparse
import csv
import pathlib
import random
import re

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


def norm_surface(tok: str) -> str:
    t = tok.lower()
    # possessive
    if t.endswith("'s") or t.endswith("’s"):
        base = t[:-2]
        if base in KINSHIP_SET or base in MULTI_COMPONENTS:
            t = base
    elif t.endswith("s'"):
        base = t[:-1]
        if base in KINSHIP_SET or base in MULTI_COMPONENTS:
            t = base
    # plural -ies
    if t.endswith('ies'):
        base = t[:-3] + 'y'
        if base in KINSHIP_SET:
            return base
    # plural -es
    if t.endswith('es'):
        base = t[:-2]
        if base in KINSHIP_SET and len(base) >= 3:
            return base
    # plural -s
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


def collapse_multiword(word_norm):
    collapsed = []
    i = 0
    n = len(word_norm)
    while i < n:
        if i + 1 < n and (word_norm[i], word_norm[i + 1]) in MULTIWORD:
            collapsed.append(MULTIWORD[(word_norm[i], word_norm[i + 1])])
            i += 2
        else:
            collapsed.append(word_norm[i])
            i += 1
    return collapsed


def mark_tokens(tokens, start_idx, end_idx):
    marked = list(tokens)
    for i in range(start_idx, end_idx + 1):
        if 0 <= i < len(marked):
            marked[i] = f"[[{marked[i]}]]"
    return ' '.join(marked)


def reservoir_add(samples, counts, key, item, k):
    counts[key] += 1
    n = counts[key]
    if len(samples[key]) < k:
        samples[key].append(item)
    else:
        j = random.randrange(n)
        if j < k:
            samples[key][j] = item


def compute(root: pathlib.Path, n_per_stratum: int):
    files = list(root.rglob('*.cha'))

    samples = {
        'parent_voc': [],
        'parent_arg': [],
        'extended_voc': [],
        'extended_arg': [],
    }
    counts = {k: 0 for k in samples}

    for f in files:
        try:
            lines = f.read_text(errors='ignore').splitlines()
        except Exception:
            continue

        for line_no, line in enumerate(lines, start=1):
            if not line.startswith('*'):
                continue
            if ':' not in line:
                continue
            prefix, utter = line.split(':', 1)
            speaker = prefix.lstrip('*').strip()

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

            collapsed = collapse_multiword(word_norm)
            filtered = [w for w in collapsed if w not in DISCOURSE and not NOISE_RE.fullmatch(w)]
            utter_standalone = bool(filtered) and all(w in KINSHIP_SET for w in filtered)

            i = 0
            n = len(word_norm)
            while i < n:
                if i + 1 < n and (word_norm[i], word_norm[i + 1]) in MULTIWORD:
                    lex = MULTIWORD[(word_norm[i], word_norm[i + 1])]
                    if lex in KINSHIP_SET:
                        start_tok = word_token_idx[i]
                        end_tok = word_token_idx[i + 1]
                        is_voc = utter_standalone or is_comma_adjacent(tokens, start_tok, end_tok)
                        cat = 'parent' if lex in PARENT_SET else 'extended'
                        key = f"{cat}_{'voc' if is_voc else 'arg'}"
                        item = {
                            'term': lex,
                            'class': 'vocative' if is_voc else 'argument',
                            'category': cat,
                            'file': str(f.relative_to(root)),
                            'line_no': line_no,
                            'speaker': speaker,
                            'utterance': utter.strip(),
                            'tokens_marked': mark_tokens(tokens, start_tok, end_tok),
                        }
                        reservoir_add(samples, counts, key, item, n_per_stratum)
                    i += 2
                    continue

                lex = word_norm[i]
                if lex in KINSHIP_SET:
                    start_tok = word_token_idx[i]
                    end_tok = start_tok
                    is_voc = utter_standalone or is_comma_adjacent(tokens, start_tok, end_tok)
                    cat = 'parent' if lex in PARENT_SET else 'extended'
                    key = f"{cat}_{'voc' if is_voc else 'arg'}"
                    item = {
                        'term': lex,
                        'class': 'vocative' if is_voc else 'argument',
                        'category': cat,
                        'file': str(f.relative_to(root)),
                        'line_no': line_no,
                        'speaker': speaker,
                        'utterance': utter.strip(),
                        'tokens_marked': mark_tokens(tokens, start_tok, end_tok),
                    }
                    reservoir_add(samples, counts, key, item, n_per_stratum)
                i += 1

    return samples, counts


def main():
    ap = argparse.ArgumentParser(
        description='Sample vocative vs argument occurrences for manual QC in CHILDES Eng-NA'
    )
    ap.add_argument('--root', required=True, help='Path to Eng-NA corpus root')
    ap.add_argument('--out', required=True, help='Output TSV file path')
    ap.add_argument('--seed', type=int, default=20260131, help='Random seed for sampling')
    ap.add_argument('--n-per-stratum', type=int, default=50, help='Samples per stratum')
    args = ap.parse_args()

    random.seed(args.seed)

    root = pathlib.Path(args.root)
    out_path = pathlib.Path(args.out)

    samples, counts = compute(root, args.n_per_stratum)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', newline='') as fh:
        w = csv.writer(fh, delimiter='\t')
        w.writerow(['stratum','term','class','category','file','line_no','speaker','utterance','tokens_marked'])
        for key in ['parent_voc','parent_arg','extended_voc','extended_arg']:
            for item in samples[key]:
                w.writerow([
                    key,
                    item['term'],
                    item['class'],
                    item['category'],
                    item['file'],
                    item['line_no'],
                    item['speaker'],
                    item['utterance'],
                    item['tokens_marked'],
                ])

    print('wrote', out_path)
    print('total occurrences seen per stratum:')
    for k in sorted(counts):
        print(k, counts[k])


if __name__ == '__main__':
    main()
