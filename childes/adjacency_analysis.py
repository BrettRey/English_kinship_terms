#!/usr/bin/env python3
"""
Analyse vocative→argument adjacency in CHILDES Eng-NA.

For each kinship term, count cases where:
  (a) the term appears vocatively in utterance N, and
  (b) the *same* term appears as a bare argument in utterance N+1
      (within the same transcript).

This tests the bridging-context hypothesis: do speakers extend bare use
from vocative to argument within conversational turns?
"""
import argparse
import json
import pathlib
import re
from collections import Counter

# ---------- constants (shared with compute_childes_kinship_vocative.py) ----------

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
    'stepmom','stepdad','stepmother','stepfather','stepsister','stepbrother',
    'stepson','stepdaughter','stepchild',
]
KINSHIP_SET = set(KINSHIP)

MULTIWORD = {
    ('grand','ma'): 'grandma', ('grand','mom'): 'grandmom',
    ('grand','mommy'): 'grandmommy', ('grand','mother'): 'grandmother',
    ('grand','pa'): 'grandpa', ('grand','dad'): 'granddad',
    ('grand','daddy'): 'granddaddy', ('grand','father'): 'grandfather',
    ('grand','papa'): 'grandpapa', ('grand','mama'): 'grandmama',
    ('step','mom'): 'stepmom', ('step','dad'): 'stepdad',
    ('step','mother'): 'stepmother', ('step','father'): 'stepfather',
    ('step','sister'): 'stepsister', ('step','brother'): 'stepbrother',
    ('step','son'): 'stepson', ('step','daughter'): 'stepdaughter',
    ('step','child'): 'stepchild',
}

DISCOURSE = {
    'hey','hi','hello','oh','okay','ok','yeah','yep','yes','no','please',
    'well','uh','um','huh','hm','hmm','mm',
}

DETERMINERS = {
    'a','an','the',
    'this','that','these','those',
    'my','your','his','her','our','their','its','whose',
    'some','any','no','each','every','either','neither','both','all',
    'much','many','few','several','another','other','such','one',
}

NOISE_RE = re.compile(r'^[xyw]{3,}$')
WORD_RE  = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
TOKEN_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*|[.,!?]")


def norm_surface(tok: str) -> str:
    t = tok.lower()
    if t.endswith("'s") or t.endswith("\u2019s"):
        base = t[:-2]
        if base in KINSHIP_SET:
            t = base
    elif t.endswith("s'"):
        base = t[:-1]
        if base in KINSHIP_SET:
            t = base
    if t.endswith('ies'):
        base = t[:-3] + 'y'
        if base in KINSHIP_SET:
            return base
    if t.endswith('s') and not t.endswith("'s"):
        base = t[:-1]
        if base in KINSHIP_SET and len(base) >= 3:
            return base
    return t


def has_genitive(tok: str) -> bool:
    t = tok.lower()
    return t.endswith("'s") or t.endswith("\u2019s") or t.endswith("s'")


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


def classify_utterance(line: str):
    """Return sets of (vocative_terms, bare_arg_terms, det_arg_terms) in one utterance."""
    try:
        utter = line.split(':', 1)[1]
    except Exception:
        return set(), set(), set()

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
        return set(), set(), set()

    collapsed = collapse_multiword(word_norm)
    filtered = [w for w in collapsed if w not in DISCOURSE and not NOISE_RE.fullmatch(w)]
    utter_standalone = bool(filtered) and all(w in KINSHIP_SET for w in filtered)

    voc_terms = set()
    bare_terms = set()
    det_terms  = set()

    idx = 0
    n = len(word_norm)
    while idx < n:
        # multiword
        if idx + 1 < n and (word_norm[idx], word_norm[idx + 1]) in MULTIWORD:
            lex = MULTIWORD[(word_norm[idx], word_norm[idx + 1])]
            if lex in KINSHIP_SET:
                start_tok = word_token_idx[idx]
                end_tok   = word_token_idx[idx + 1]
                is_comma = (start_tok > 0 and tokens[start_tok - 1] == ',') or \
                           (end_tok + 1 < len(tokens) and tokens[end_tok + 1] == ',')
                if utter_standalone or is_comma:
                    voc_terms.add(lex)
                else:
                    if idx > 0 and (word_norm[idx - 1] in DETERMINERS or has_genitive(word_raw[idx - 1])):
                        det_terms.add(lex)
                    elif has_genitive(word_raw[idx]):
                        det_terms.add(lex)
                    else:
                        bare_terms.add(lex)
            idx += 2
            continue

        lex = word_norm[idx]
        if lex in KINSHIP_SET:
            start_tok = word_token_idx[idx]
            is_comma = (start_tok > 0 and tokens[start_tok - 1] == ',') or \
                       (start_tok + 1 < len(tokens) and tokens[start_tok + 1] == ',')
            if utter_standalone or is_comma:
                voc_terms.add(lex)
            else:
                if idx > 0 and (word_norm[idx - 1] in DETERMINERS or has_genitive(word_raw[idx - 1])):
                    det_terms.add(lex)
                elif has_genitive(word_raw[idx]):
                    det_terms.add(lex)
                else:
                    bare_terms.add(lex)
        idx += 1

    return voc_terms, bare_terms, det_terms


def analyse(root: pathlib.Path):
    files = sorted(root.rglob('*.cha'))

    # Counters
    voc_then_bare  = Counter()   # voc in utt N → bare arg same term in N+1
    voc_then_det   = Counter()   # voc in utt N → det arg same term in N+1
    voc_then_voc   = Counter()   # voc in utt N → voc same term in N+1
    voc_then_none  = Counter()   # voc in utt N → term absent in N+1
    voc_total      = Counter()   # total vocative tokens (utterances containing voc)
    bare_total     = Counter()   # total bare-arg utterances

    # Also track: does bare arg in N follow voc in N-1?
    bare_preceded_by_voc = Counter()
    bare_not_preceded    = Counter()

    for f in files:
        try:
            lines = f.read_text(errors='ignore').splitlines()
        except Exception:
            continue

        # Extract speaker utterance lines only
        utts = []
        for line in lines:
            if line.startswith('*'):
                utts.append(line)

        for i, line in enumerate(utts):
            voc, bare, det = classify_utterance(line)

            for t in voc:
                voc_total[t] += 1
            for t in bare:
                bare_total[t] += 1

            # Look at previous utterance for bare terms
            if i > 0 and bare:
                prev_voc, _, _ = classify_utterance(utts[i - 1])
                for t in bare:
                    if t in prev_voc:
                        bare_preceded_by_voc[t] += 1
                    else:
                        bare_not_preceded[t] += 1

            # Look at next utterance for vocative terms
            if voc and i + 1 < len(utts):
                next_voc, next_bare, next_det = classify_utterance(utts[i + 1])
                for t in voc:
                    if t in next_bare:
                        voc_then_bare[t] += 1
                    elif t in next_det:
                        voc_then_det[t] += 1
                    elif t in next_voc:
                        voc_then_voc[t] += 1
                    else:
                        voc_then_none[t] += 1

    return {
        'voc_then_bare': voc_then_bare,
        'voc_then_det': voc_then_det,
        'voc_then_voc': voc_then_voc,
        'voc_then_none': voc_then_none,
        'voc_total': voc_total,
        'bare_total': bare_total,
        'bare_preceded_by_voc': bare_preceded_by_voc,
        'bare_not_preceded': bare_not_preceded,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    results = analyse(root)

    # Aggregate parent vs extended
    PARENT = {'mom','mommy','momma','mama','ma','mother',
              'dad','daddy','dada','papa','pa','father'}
    GRAND  = {'grandma','grandpa','granny','gramma','nana','grandmom',
              'grandmommy','grandmother','grandfather','granddad',
              'granddaddy','gramps','grampa','grandpapa','grandmama'}

    summary = {}
    for term in KINSHIP:
        vt = results['voc_total'].get(term, 0)
        if vt < 20:
            continue
        vtb = results['voc_then_bare'].get(term, 0)
        vtd = results['voc_then_det'].get(term, 0)
        vtv = results['voc_then_voc'].get(term, 0)
        vtn = results['voc_then_none'].get(term, 0)
        bt  = results['bare_total'].get(term, 0)
        bpv = results['bare_preceded_by_voc'].get(term, 0)
        bnp = results['bare_not_preceded'].get(term, 0)

        summary[term] = {
            'vocative_utterances': vt,
            'voc_followed_by_bare_arg': vtb,
            'voc_followed_by_det_arg': vtd,
            'voc_followed_by_voc': vtv,
            'voc_followed_by_absent': vtn,
            'pct_voc_then_bare': round(100 * vtb / vt, 1) if vt else 0,
            'bare_arg_utterances': bt,
            'bare_preceded_by_voc': bpv,
            'pct_bare_after_voc': round(100 * bpv / bt, 1) if bt else 0,
        }

    # Category aggregates
    for cat_name, cat_set in [('PARENT', PARENT), ('GRANDPARENT', GRAND)]:
        vt = sum(results['voc_total'].get(t, 0) for t in cat_set)
        vtb = sum(results['voc_then_bare'].get(t, 0) for t in cat_set)
        vtd = sum(results['voc_then_det'].get(t, 0) for t in cat_set)
        vtv = sum(results['voc_then_voc'].get(t, 0) for t in cat_set)
        vtn = sum(results['voc_then_none'].get(t, 0) for t in cat_set)
        bt = sum(results['bare_total'].get(t, 0) for t in cat_set)
        bpv = sum(results['bare_preceded_by_voc'].get(t, 0) for t in cat_set)

        summary[cat_name] = {
            'vocative_utterances': vt,
            'voc_followed_by_bare_arg': vtb,
            'voc_followed_by_det_arg': vtd,
            'voc_followed_by_voc': vtv,
            'voc_followed_by_absent': vtn,
            'pct_voc_then_bare': round(100 * vtb / vt, 1) if vt else 0,
            'bare_arg_utterances': bt,
            'bare_preceded_by_voc': bpv,
            'pct_bare_after_voc': round(100 * bpv / bt, 1) if bt else 0,
        }

    out = pathlib.Path(args.out)
    out.write_text(json.dumps(summary, indent=2))
    print(f'Wrote {out}')

    # Print summary
    print(f"\n{'Term':<14} {'Voc utt':>8} {'→bare':>6} {'→det':>6} {'→voc':>6} {'→absent':>8} {'%→bare':>7}   {'Bare utt':>9} {'after voc':>10} {'%after':>7}")
    print('-' * 110)
    for term, d in sorted(summary.items(), key=lambda x: -x[1]['vocative_utterances']):
        print(f"{term:<14} {d['vocative_utterances']:>8} {d['voc_followed_by_bare_arg']:>6} "
              f"{d['voc_followed_by_det_arg']:>6} {d['voc_followed_by_voc']:>6} "
              f"{d['voc_followed_by_absent']:>8} {d['pct_voc_then_bare']:>6.1f}%   "
              f"{d['bare_arg_utterances']:>9} {d['bare_preceded_by_voc']:>10} {d['pct_bare_after_voc']:>6.1f}%")


if __name__ == '__main__':
    main()
