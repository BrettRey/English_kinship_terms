#!/usr/bin/env python3
import argparse
import pathlib
import re
import csv
from collections import Counter

# Broad North American kinship list
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

# Non-kin comparison list
NONKIN = ['teacher','doctor','boss','neighbor','friend','waiter','nurse','police','baby','kid']

# Stable benchmark words
BENCH = ['the','and','to','of','in','that']

LEXEME_LIST = KINSHIP + NONKIN + BENCH
LEXEME_SET = set(LEXEME_LIST)

# Multiword compounds that should be treated as single lexemes
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

# UK spelling normalization
VARIANT_MAP = {
    'neighbour': 'neighbor',
    'neighbours': 'neighbor',
}

# Derivational mapping for %mor lemmas with dv-AGT
AGENTIVE_MAP = {
    'teach': 'teacher',
    'wait': 'waiter',
}

NOISE_RE = re.compile(r'^[xyw]{3,}$')
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")

PUNCT_POS = {'cm','0v','0n','L2'}
LEMMA_WORD_RE = re.compile(r'[a-z]')


def norm_surface(tok: str) -> str:
    t = tok.lower()
    # possessive
    if t.endswith("'s") or t.endswith("’s"):
        base = t[:-2]
        if base in LEXEME_SET or base in MULTI_COMPONENTS:
            t = base
    elif t.endswith("s'"):
        base = t[:-1]
        if base in LEXEME_SET or base in MULTI_COMPONENTS:
            t = base
    # plural -ies
    if t.endswith('ies'):
        base = t[:-3] + 'y'
        if base in LEXEME_SET:
            t = base
            return VARIANT_MAP.get(t, t)
    # plural -es
    if t.endswith('es'):
        base = t[:-2]
        if base in LEXEME_SET and len(base) >= 3:
            t = base
            return VARIANT_MAP.get(t, t)
    # plural -s
    if t.endswith('s'):
        base = t[:-1]
        if base in LEXEME_SET and len(base) >= 3:
            t = base
            return VARIANT_MAP.get(t, t)
    return VARIANT_MAP.get(t, t)


def parse_mor_subtoken(sub: str):
    if '|' not in sub:
        return None
    pos, rest = sub.split('|', 1)
    return pos, rest


def norm_lemma(raw_lemma: str) -> str:
    base = raw_lemma.split('&', 1)[0]
    base = base.strip()
    if '-' in base:
        head, tail = base.rsplit('-', 1)
        if tail.isupper() or tail.isdigit():
            base = head
    base = base.lower()
    base = re.sub(r'^[^a-z]+|[^a-z]+$', '', base)
    if not base:
        return ''
    return VARIANT_MAP.get(base, base)


def compute(root: pathlib.Path):
    files = list(root.rglob('*.cha'))
    surface_counts = Counter()
    lemma_counts = Counter()
    surface_total = 0
    lemma_total = 0

    for f in files:
        try:
            for line in f.read_text(errors='ignore').splitlines():
                if line.startswith('*'):
                    try:
                        utter = line.split(':', 1)[1]
                    except Exception:
                        continue
                    tokens = WORD_RE.findall(utter)
                    for tok in tokens:
                        t = tok.lower()
                        if NOISE_RE.fullmatch(t):
                            continue
                        surface_total += 1
                    i = 0
                    n = len(tokens)
                    while i < n:
                        t1_raw = tokens[i].lower()
                        if NOISE_RE.fullmatch(t1_raw):
                            i += 1
                            continue
                        t1 = norm_surface(tokens[i])
                        if i + 1 < n:
                            t2_raw = tokens[i + 1].lower()
                            if not NOISE_RE.fullmatch(t2_raw):
                                t2 = norm_surface(tokens[i + 1])
                                key = (t1, t2)
                                if key in MULTIWORD:
                                    lex = MULTIWORD[key]
                                    if lex in LEXEME_SET:
                                        surface_counts[lex] += 1
                                        i += 2
                                        continue
                        if t1 in LEXEME_SET:
                            surface_counts[t1] += 1
                        i += 1
                elif line.startswith('%mor:'):
                    content = line.split('%mor:', 1)[1]
                    tokens = content.split()
                    lemmas = []
                    for tok in tokens:
                        for sub in tok.split('~'):
                            parsed = parse_mor_subtoken(sub)
                            if not parsed:
                                continue
                            pos, rest = parsed
                            if pos in PUNCT_POS:
                                continue
                            # agentive derivations
                            if '&dv-AGT' in rest:
                                base = rest.split('&', 1)[0].lower()
                                lemma = AGENTIVE_MAP.get(base, norm_lemma(rest))
                            else:
                                lemma = norm_lemma(rest)
                            if not lemma:
                                continue
                            if NOISE_RE.fullmatch(lemma):
                                continue
                            if not LEMMA_WORD_RE.search(lemma):
                                continue
                            lemmas.append(lemma)
                    lemma_total += len(lemmas)
                    i = 0
                    n = len(lemmas)
                    while i < n:
                        l1 = lemmas[i]
                        if i + 1 < n:
                            l2 = lemmas[i + 1]
                            key = (l1, l2)
                            if key in MULTIWORD:
                                lex = MULTIWORD[key]
                                if lex in LEXEME_SET:
                                    lemma_counts[lex] += 1
                                    i += 2
                                    continue
                        if l1 in LEXEME_SET:
                            lemma_counts[l1] += 1
                        i += 1
        except Exception:
            continue

    return surface_counts, lemma_counts, surface_total, lemma_total


def main():
    ap = argparse.ArgumentParser(description='Compute CHILDES Eng-NA kinship frequencies')
    ap.add_argument('--root', required=True, help='Path to Eng-NA corpus root')
    ap.add_argument('--out', required=True, help='Output TSV file path')
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    out_path = pathlib.Path(args.out)

    surface_counts, lemma_counts, surface_total, lemma_total = compute(root)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['term','category','surface_count','surface_per_million','lemma_count','lemma_per_million'])
        for term in LEXEME_LIST:
            sc = surface_counts.get(term, 0)
            lc = lemma_counts.get(term, 0)
            spm = (sc / surface_total * 1_000_000) if surface_total else 0
            lpm = (lc / lemma_total * 1_000_000) if lemma_total else 0
            cat = 'kinship' if term in KINSHIP else ('non-kin' if term in NONKIN else 'benchmark')
            w.writerow([term, cat, sc, f"{spm:.2f}", lc, f"{lpm:.2f}"])

    print('surface_total', surface_total)
    print('lemma_total', lemma_total)
    print('wrote', out_path)


if __name__ == '__main__':
    main()
