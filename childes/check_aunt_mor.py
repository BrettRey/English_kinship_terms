#!/usr/bin/env python3
"""
Diagnostic: check how many aunt/auntie tokens come from files lacking %mor
tiers, where title+name exclusion cannot operate.

For files WITHOUT %mor:
  - Count surface occurrences of aunt/auntie (case-insensitive)
  - Check how many are immediately followed by a capitalized word
    (surface heuristic for title+name: "Aunt Sarah", "Auntie Patty")

For files WITH %mor:
  - Count aunt/auntie tokens
  - Report how many had n:prop following in the %mor tier

This tells us whether the ~48% bare rate for aunt is inflated by
undetected title+name cases in non-%mor files.
"""
import pathlib
import re
from collections import defaultdict

CORPUS_ROOT = pathlib.Path("/Users/brettreynolds/Downloads/Eng-NA")

TARGETS = {"aunt", "auntie", "aunty"}

NOISE_RE = re.compile(r"^[xyw]{3,}$")
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
MOR_TOKEN_RE = re.compile(r"\S+")


def norm(tok: str) -> str:
    """Normalize to lowercase base form."""
    t = tok.lower()
    for suf in ("'s", "\u2019s", "s'"):
        if t.endswith(suf):
            t = t[: -len(suf)]
            break
    return t


def file_has_mor(lines: list) -> bool:
    """Return True if the file contains any %mor: lines."""
    return any(line.startswith("%mor:") for line in lines)


def parse_mor_subtokens(mor_line: str) -> list:
    """Parse %mor tier into [(pos, lemma), ...]."""
    content = mor_line.split(":", 1)[1] if ":" in mor_line else mor_line
    result = []
    for tok in MOR_TOKEN_RE.findall(content):
        if tok in ".,!?;:":
            continue
        for sub in tok.split("~"):
            if "|" in sub:
                pos, lemma = sub.split("|", 1)
                # strip inflection after &
                if "&" in lemma:
                    lemma = lemma.split("&")[0]
                result.append((pos, lemma.lower()))
    return result


def analyse_file_no_mor(lines: list, stats: dict):
    """Surface-only analysis for files without %mor tiers."""
    for line in lines:
        if not line.startswith("*"):
            continue
        try:
            utter = line.split(":", 1)[1]
        except IndexError:
            continue

        raw_tokens = WORD_RE.findall(utter)
        for i, tok in enumerate(raw_tokens):
            normed = norm(tok)
            if normed not in TARGETS:
                continue

            stats[normed]["total_no_mor"] += 1

            # Check if next token is a capitalized word (title+name heuristic)
            if i + 1 < len(raw_tokens):
                nxt = raw_tokens[i + 1]
                if nxt[0].isupper() and not NOISE_RE.fullmatch(nxt.lower()):
                    stats[normed]["title_name_surface_no_mor"] += 1
                    stats[normed]["title_name_examples_no_mor"].append(
                        f"{tok} {nxt}"
                    )
                else:
                    stats[normed]["no_cap_following_no_mor"] += 1
            else:
                # utterance-final
                stats[normed]["no_cap_following_no_mor"] += 1

            stats[normed]["files_no_mor"].add(str(line)[:80])


def analyse_file_with_mor(lines: list, stats: dict):
    """Analysis for files WITH %mor tiers."""
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.startswith("*"):
            i += 1
            continue

        try:
            utter = line.split(":", 1)[1]
        except IndexError:
            i += 1
            continue

        # Find %mor tier
        mor_line = None
        j = i + 1
        while j < len(lines) and lines[j].startswith("%"):
            if lines[j].startswith("%mor:"):
                mor_line = lines[j]
                break
            j += 1

        raw_tokens = WORD_RE.findall(utter)

        if mor_line:
            mor_tokens = parse_mor_subtokens(mor_line)
        else:
            mor_tokens = []

        # Walk surface tokens; keep a parallel index into mor_tokens.
        mor_idx = 0
        for si, tok in enumerate(raw_tokens):
            normed = norm(tok)
            if NOISE_RE.fullmatch(normed):
                mor_idx += 1
                continue

            if normed in TARGETS:
                stats[normed]["total_with_mor"] += 1

                # Check %mor for n:prop following
                found_prop = False
                if mor_tokens:
                    # Try to find matching position in mor_tokens
                    search_start = max(0, mor_idx - 2)
                    search_end = min(len(mor_tokens), mor_idx + 3)
                    for mi in range(search_start, search_end):
                        pos, lemma = mor_tokens[mi]
                        if lemma in TARGETS or normed.startswith(lemma):
                            # Found our kinship term; check next
                            if mi + 1 < len(mor_tokens):
                                next_pos, next_lemma = mor_tokens[mi + 1]
                                if next_pos == "n:prop":
                                    found_prop = True
                                    stats[normed]["title_name_mor"].append(
                                        f"{tok} -> n:prop|{next_lemma}"
                                    )
                            break

                if found_prop:
                    stats[normed]["n_prop_following_mor"] += 1
                else:
                    stats[normed]["no_prop_following_mor"] += 1

                # Also check surface capitalization for comparison
                if si + 1 < len(raw_tokens):
                    nxt = raw_tokens[si + 1]
                    if nxt[0].isupper() and not NOISE_RE.fullmatch(nxt.lower()):
                        stats[normed]["cap_following_with_mor"] += 1

            mor_idx += 1

        i += 1


def main():
    files = sorted(CORPUS_ROOT.rglob("*.cha"))
    print(f"Found {len(files)} .cha files\n")

    stats = defaultdict(lambda: defaultdict(lambda: 0))
    # Override certain keys to be lists/sets
    for t in TARGETS:
        stats[t]["files_no_mor"] = set()
        stats[t]["title_name_examples_no_mor"] = []
        stats[t]["title_name_mor"] = []

    n_files_no_mor = 0
    n_files_with_mor = 0
    files_no_mor_with_hits = []

    for f in files:
        try:
            lines = f.read_text(errors="ignore").splitlines()
        except Exception:
            continue

        has_mor = file_has_mor(lines)

        if has_mor:
            n_files_with_mor += 1
            analyse_file_with_mor(lines, stats)
        else:
            n_files_no_mor += 1
            # Check if this file has any aunt/auntie
            text_lower = "\n".join(lines).lower()
            if any(t in text_lower for t in TARGETS):
                files_no_mor_with_hits.append(str(f))
            analyse_file_no_mor(lines, stats)

    # -- Report --

    print(f"Files with %mor tiers:    {n_files_with_mor:,}")
    print(f"Files without %mor tiers: {n_files_no_mor:,}")
    print()

    for term in sorted(TARGETS):
        s = stats[term]
        total_no = s["total_no_mor"]
        tn_no = s["title_name_surface_no_mor"]
        bare_no = s["no_cap_following_no_mor"]
        total_with = s["total_with_mor"]
        prop_with = s["n_prop_following_mor"]
        no_prop_with = s["no_prop_following_mor"]
        cap_with = s["cap_following_with_mor"]

        print(f"=== {term.upper()} ===")
        print(f"  FILES WITHOUT %mor:")
        print(f"    Total tokens:                        {total_no:>5}")
        print(f"    Followed by capitalized word (title+name?): {tn_no:>5}")
        print(f"    NOT followed by capitalized word:    {bare_no:>5}")
        if total_no > 0:
            pct_tn = 100 * tn_no / total_no
            print(f"    % likely title+name:                 {pct_tn:>5.1f}%")
        print()
        print(f"  FILES WITH %mor:")
        print(f"    Total tokens:                        {total_with:>5}")
        print(f"    Followed by n:prop in %mor:          {prop_with:>5}")
        print(f"    NOT followed by n:prop:              {no_prop_with:>5}")
        print(f"    (Surface cap following, for comparison): {cap_with:>5}")
        if total_with > 0:
            pct_prop = 100 * prop_with / total_with
            print(f"    % title+name (by n:prop):            {pct_prop:>5.1f}%")
        print()

        # Show some examples of title+name from non-%mor files
        examples = s["title_name_examples_no_mor"]
        if examples:
            unique = sorted(set(examples))
            print(f"  Surface title+name examples (no-%mor files):")
            for ex in unique[:20]:
                print(f"    {ex}")
            if len(unique) > 20:
                print(f"    ... and {len(unique) - 20} more unique patterns")
            print()

        # Show %mor title+name examples
        mor_examples = s["title_name_mor"]
        if mor_examples:
            unique_mor = sorted(set(mor_examples))
            print(f"  %mor-confirmed title+name examples:")
            for ex in unique_mor[:20]:
                print(f"    {ex}")
            if len(unique_mor) > 20:
                print(f"    ... and {len(unique_mor) - 20} more unique patterns")
            print()

    # Summary impact assessment
    print("=== IMPACT ON BARE RATES ===")
    print()
    print("From existing kinship_vocative_argument.tsv:")
    print("  aunt:   305 bare / 629 argument = 48.5% bare")
    print("  auntie: 148 bare / 313 argument = 47.3% bare")
    print("  aunty:   15 bare /  24 argument = 62.5% bare")
    print()

    for term in sorted(TARGETS):
        s = stats[term]
        total_no = s["total_no_mor"]
        tn_no = s["title_name_surface_no_mor"]
        if total_no > 0:
            print(
                f"  {term}: {total_no} tokens from non-%mor files, "
                f"of which {tn_no} ({100*tn_no/total_no:.1f}%) look like title+name"
            )
            print(
                f"    -> Worst case: up to {tn_no} undetected title+name cases "
                f"inflating the bare count"
            )
        else:
            print(f"  {term}: 0 tokens from non-%mor files (all covered by %mor)")
        print()

    if files_no_mor_with_hits:
        print(f"\nNon-%mor files containing aunt/auntie/aunty ({len(files_no_mor_with_hits)}):")
        for fp in sorted(files_no_mor_with_hits):
            print(f"  {pathlib.Path(fp).relative_to(CORPUS_ROOT)}")


if __name__ == "__main__":
    main()
