#!/usr/bin/env python3
"""
Compute vocative vs argument counts for kinship terms in CHILDES Eng-NA.

This version uses %mor tiers to detect proper nouns, allowing exclusion of
title+name constructions like 'Auntie Sarah' where the name is the head.
"""
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

KINSHIP_SET = set(KINSHIP)

# Terms that commonly appear in title+name constructions (e.g., Auntie Sarah,
# Grandma Peggy, Uncle John, Papa Joe).  Parent terms like mom/dad virtually
# never take a following proper noun in English, so they are excluded.
TITLE_KINSHIP = {
    'aunt', 'auntie', 'aunty', 'uncle', 'brother', 'sister',
    'grandma', 'grandpa', 'granny', 'gramma', 'nana', 'grandmom', 'grandmommy',
    'grandmother', 'grandfather', 'granddad', 'granddaddy', 'gramps', 'grampa',
    'grandpapa', 'grandmama',
    'mama', 'papa',
}

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

DETERMINERS = {
    'a','an','the',
    'this','that','these','those',
    'my','your','his','her','our','their','its','whose',
    'some','any','no','each','every','either','neither','both','all',
    'much','many','few','several','another','other','such','one'
}

CONJ = {'and', 'or'}

NOISE_RE = re.compile(r'^[xyw]{3,}$')
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
TOKEN_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*|[.,!?]")
MOR_TOKEN_RE = re.compile(r'\S+')


def norm_surface(tok: str) -> str:
    t = tok.lower()
    if t.endswith("'s") or t.endswith("'s"):
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


def has_genitive(tok: str) -> bool:
    t = tok.lower()
    return t.endswith("'s") or t.endswith("'s") or t.endswith("s'")


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


def has_determiner(word_norm, word_raw, idx):
    if has_genitive(word_raw[idx]):
        return True
    j = idx - 1
    if j >= 0:
        if word_norm[j] in DETERMINERS or has_genitive(word_raw[j]):
            return True
    if j >= 0 and word_norm[j] in CONJ and j - 2 >= 0:
        if word_norm[j - 1] in KINSHIP_SET and (
            word_norm[j - 2] in DETERMINERS or has_genitive(word_raw[j - 2])
        ):
            return True
    return False


def parse_mor_tokens(mor_line: str) -> list:
    """Parse %mor tier into list of (pos, lemma) tuples."""
    tokens = MOR_TOKEN_RE.findall(mor_line)
    result = []
    for tok in tokens:
        # Skip punctuation
        if tok in '.,!?;:':
            continue
        # Handle clitics (e.g., n:prop|Mommy~aux|be&3S)
        parts = tok.split('~')
        for part in parts:
            if '|' in part:
                pos, lemma = part.split('|', 1)
                # Remove inflection markers after &
                if '&' in lemma:
                    lemma = lemma.split('&')[0]
                result.append((pos, lemma.lower()))
            else:
                result.append(('unk', part.lower()))
    return result


def is_followed_by_proper_noun(mor_tokens: list, idx: int) -> bool:
    """Check if position idx in mor_tokens is followed by n:prop."""
    if idx + 1 < len(mor_tokens):
        next_pos, _ = mor_tokens[idx + 1]
        return next_pos == 'n:prop'
    return False


def compute(root: pathlib.Path):
    files = list(root.rglob('*.cha'))
    voc_counts = Counter()
    arg_counts = Counter()
    arg_bare_counts = Counter()
    arg_det_counts = Counter()
    arg_title_name_excluded = Counter()  # Track excluded title+name cases
    voc_chi_counts = Counter()
    voc_adu_counts = Counter()
    surface_total = 0

    for f in files:
        try:
            lines = f.read_text(errors='ignore').splitlines()
            i = 0
            while i < len(lines):
                line = lines[i]
                if not line.startswith('*'):
                    i += 1
                    continue

                # Extract speaker
                try:
                    speaker = line[1:].split(':')[0].strip().upper()
                except Exception:
                    speaker = 'UNK'
                is_child = speaker == 'CHI'

                try:
                    utter = line.split(':', 1)[1]
                except Exception:
                    i += 1
                    continue

                # Look for %mor tier on next line(s)
                mor_line = None
                j = i + 1
                while j < len(lines) and lines[j].startswith('%'):
                    if lines[j].startswith('%mor:'):
                        mor_line = lines[j].split(':', 1)[1] if ':' in lines[j] else ''
                        break
                    j += 1
                
                mor_tokens = parse_mor_tokens(mor_line) if mor_line else []

                # Surface word count
                for tok in WORD_RE.findall(utter):
                    t = tok.lower()
                    if NOISE_RE.fullmatch(t):
                        continue
                    surface_total += 1

                # Tokenize for vocative detection
                tokens = TOKEN_RE.findall(utter)
                word_norm = []
                word_raw = []
                word_token_idx = []
                for idx, tok in enumerate(tokens):
                    if WORD_RE.fullmatch(tok):
                        t = tok.lower()
                        if NOISE_RE.fullmatch(t):
                            continue
                        word_norm.append(norm_surface(tok))
                        word_raw.append(tok)
                        word_token_idx.append(idx)

                if not word_norm:
                    i += 1
                    continue

                collapsed = collapse_multiword(word_norm)
                filtered = [w for w in collapsed if w not in DISCOURSE and not NOISE_RE.fullmatch(w)]
                utter_standalone = bool(filtered) and all(w in KINSHIP_SET for w in filtered)

                # Build index mapping from word_norm position to mor_tokens position
                # (simplified: assume 1:1 correspondence for words, ignoring clitics)
                mor_word_idx = 0

                idx = 0
                n = len(word_norm)
                while idx < n:
                    # Handle multiword compounds
                    if idx + 1 < n and (word_norm[idx], word_norm[idx + 1]) in MULTIWORD:
                        lex = MULTIWORD[(word_norm[idx], word_norm[idx + 1])]
                        if lex in KINSHIP_SET:
                            start_tok = word_token_idx[idx]
                            end_tok = word_token_idx[idx + 1]
                            is_voc = utter_standalone or is_comma_adjacent(tokens, start_tok, end_tok)
                            if is_voc:
                                voc_counts[lex] += 1
                                if is_child:
                                    voc_chi_counts[lex] += 1
                                else:
                                    voc_adu_counts[lex] += 1
                            else:
                                arg_counts[lex] += 1
                                if has_determiner(word_norm, word_raw, idx):
                                    arg_det_counts[lex] += 1
                                else:
                                    arg_bare_counts[lex] += 1
                        mor_word_idx += 2
                        idx += 2
                        continue

                    lex = word_norm[idx]
                    if lex in KINSHIP_SET:
                        start_tok = word_token_idx[idx]
                        end_tok = start_tok
                        is_voc = utter_standalone or is_comma_adjacent(tokens, start_tok, end_tok)
                        
                        if is_voc:
                            voc_counts[lex] += 1
                            if is_child:
                                voc_chi_counts[lex] += 1
                            else:
                                voc_adu_counts[lex] += 1
                        else:
                            arg_counts[lex] += 1
                            
                            # Check for title+name pattern using %mor
                            is_title_name = False
                            if lex in TITLE_KINSHIP and mor_tokens:
                                # Check if followed by proper noun in %mor tier
                                if mor_word_idx < len(mor_tokens):
                                    if is_followed_by_proper_noun(mor_tokens, mor_word_idx):
                                        is_title_name = True
                                        arg_title_name_excluded[lex] += 1
                            
                            if has_determiner(word_norm, word_raw, idx):
                                arg_det_counts[lex] += 1
                            elif is_title_name:
                                # Title+name: count as determined (not bare),
                                # since the name is the head, not the kinship term
                                arg_det_counts[lex] += 1
                            else:
                                arg_bare_counts[lex] += 1
                    
                    mor_word_idx += 1
                    idx += 1

                i += 1

        except Exception:
            continue

    return voc_counts, arg_counts, arg_bare_counts, arg_det_counts, voc_chi_counts, voc_adu_counts, surface_total, arg_title_name_excluded


def main():
    ap = argparse.ArgumentParser(description='Compute vocative vs argument counts for kinship terms in CHILDES Eng-NA')
    ap.add_argument('--root', required=True, help='Path to Eng-NA corpus root')
    ap.add_argument('--out', required=True, help='Output TSV file path')
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    out_path = pathlib.Path(args.out)

    result = compute(root)
    voc_counts, arg_counts, arg_bare_counts, arg_det_counts, voc_chi_counts, voc_adu_counts, surface_total, arg_title_name_excluded = result

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow([
            'term',
            'vocative_count','vocative_per_million',
            'voc_chi_count','voc_chi_per_million',
            'voc_adu_count','voc_adu_per_million',
            'argument_count','argument_per_million',
            'arg_bare_count','arg_bare_per_million',
            'arg_det_count','arg_det_per_million',
        ])
        for term in KINSHIP:
            vc = voc_counts.get(term, 0)
            vcc = voc_chi_counts.get(term, 0)
            vac = voc_adu_counts.get(term, 0)
            ac = arg_counts.get(term, 0)
            abc = arg_bare_counts.get(term, 0)
            adc = arg_det_counts.get(term, 0)
            vpm = (vc / surface_total * 1_000_000) if surface_total else 0
            vcpm = (vcc / surface_total * 1_000_000) if surface_total else 0
            vapm = (vac / surface_total * 1_000_000) if surface_total else 0
            apm = (ac / surface_total * 1_000_000) if surface_total else 0
            abpm = (abc / surface_total * 1_000_000) if surface_total else 0
            adpm = (adc / surface_total * 1_000_000) if surface_total else 0
            w.writerow([
                term,
                vc, f"{vpm:.2f}",
                vcc, f"{vcpm:.2f}",
                vac, f"{vapm:.2f}",
                ac, f"{apm:.2f}",
                abc, f"{abpm:.2f}",
                adc, f"{adpm:.2f}",
            ])

    print('surface_total', surface_total)
    print('wrote', out_path)
    
    # Report excluded title+name cases
    if arg_title_name_excluded:
        print('\nTitle+name cases excluded from bare-argument counts:')
        for term, count in sorted(arg_title_name_excluded.items(), key=lambda x: -x[1]):
            print(f'  {term}: {count}')


if __name__ == '__main__':
    main()
