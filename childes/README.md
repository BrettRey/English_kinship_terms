# CHILDES Eng-NA kinship term frequencies

This folder contains the results and a reproducible script for computing frequency per million words for a broad set of North American English kinship terms, a comparable non-kin list, and benchmark words in the CHILDES Eng-NA corpus.

## Inputs
- Corpus root used: `/Users/brettreynolds/Downloads/Eng-NA`
- File type: `*.cha` (7,825 files)
- All speakers included (no filtering by participant code).

## Output
- `kinship_frequencies.tsv`
- Columns: `term`, `category`, `surface_count`, `surface_per_million`, `lemma_count`, `lemma_per_million`

Totals used for normalization:
- Surface tokens (`*` tiers): 11,465,138
- Lemma tokens (`%mor` tiers): 9,780,311

Note: `%mor` counts exclude files without `%mor` tiers (1,495 files in this corpus).

## How to reproduce
Run the script (from anywhere):

```bash
python /Users/brettreynolds/Documents/LLM-CLI-projects/English_kinship_terms/childes/compute_childes_kinship.py \
  --root /Users/brettreynolds/Downloads/Eng-NA \
  --out /Users/brettreynolds/Documents/LLM-CLI-projects/English_kinship_terms/childes/kinship_frequencies.tsv
```

## Lists used

### Kinship (broad North American list)
```
mom, mommy, momma, mama, ma, mother,
dad, daddy, dada, papa, pa, father,
parent,
grandma, grandpa, granny, gramma, nana, grandmom, grandmommy,
grandmother, grandfather, granddad, granddaddy, gramps, grampa,
grandpapa, grandmama, grandparent,
aunt, auntie, aunty, uncle, cousin, niece, nephew,
brother, sister, sibling, sissy,
son, daughter, grandchild, grandson, granddaughter,
stepmom, stepdad, stepmother, stepfather, stepsister, stepbrother, stepson, stepdaughter, stepchild
```

### Non-kin comparison list
```
teacher, doctor, boss, neighbor, friend, waiter, nurse, police, baby, kid
```

### Benchmarks (stable high-frequency words)
```
the, and, to, of, in, that
```

## Tokenization/normalization details
- **Surface**: counts come from `*` tiers using word-like tokens (`[A-Za-z]+(?:[-'][A-Za-z]+)*`), case-insensitive.
- **Lemmas**: counts come from `%mor` tiers, splitting clitics on `~` and reading the lemma after `|`.
- Punctuation tiers removed: `cm`, `0v`, `0n`, `L2`.
- Possessives and plurals are stripped only when they map to a target lexeme (e.g., `mom's` → `mom`, `moms` → `mom`).
- UK spelling `neighbour(s)` is normalized to `neighbor`.
- Multiword compounds are counted as single lexemes and not double-counted (e.g., `grand mom` → `grandmom`, `step dad` → `stepdad`).
- `%mor` agentive derivations mapped: `teach&dv-AGT` → `teacher`, `wait&dv-AGT` → `waiter`.

## Notes
- All speakers are included (CHI + adult talkers). If you want child-only or adult-only counts, modify the script to filter by speaker codes on `*` lines (e.g., `*CHI:`).
- `kinship_frequencies.tsv` is currently sorted by the input list order; you can resort for presentation.


## Vocative vs argument counts

Output:
- `kinship_vocative_argument.tsv`
- Columns: `term`, `vocative_count`, `vocative_per_million`, `argument_count`, `argument_per_million`

Normalization:
- Per-million rates use the same surface denominator as above (11,465,138 word tokens from `*` tiers).

How to reproduce:

```bash
python /Users/brettreynolds/Documents/LLM-CLI-projects/English_kinship_terms/childes/compute_childes_kinship_vocative.py   --root /Users/brettreynolds/Downloads/Eng-NA   --out /Users/brettreynolds/Documents/LLM-CLI-projects/English_kinship_terms/childes/kinship_vocative_argument.tsv
```

Vocative heuristic (surface-only, reproducible):
- **Vocative** if the kin term is **comma-adjacent** (immediately before or after `,`) **or** the utterance is a **stand-alone address**.
- **Stand-alone address** = after collapsing multiword kin forms (e.g., `grand mom` → `grandmom`) and removing discourse markers (`hey`, `oh`, `okay`, `uh`, etc.), the utterance contains **only** kin terms.
- **Argument** otherwise.

Notes:
- Uses only `*` tiers (no `%mor`/`%gra`).
- Tokenization uses word-like strings from the raw `*` line and punctuation tokens for comma detection.
- This is a **conservative** vocative measure (high precision, lower recall for vocatives without commas).

## Manual check (sampling and QC)

Outputs:
- `manual_check_samples.tsv`
- `manual_check_summary.md`

How to reproduce the sample:

```bash
python /Users/brettreynolds/Documents/LLM-CLI-projects/English_kinship_terms/childes/sample_childes_vocative_manual_check.py \
  --root /Users/brettreynolds/Downloads/Eng-NA \
  --out /Users/brettreynolds/Documents/LLM-CLI-projects/English_kinship_terms/childes/manual_check_samples.tsv \
  --seed 20260131 \
  --n-per-stratum 50
```

Note: `manual_check_samples.tsv` includes utterance excerpts from CHILDES. Verify redistribution
policy before publishing raw excerpts; if needed, share only the script and summary.

## Uncertainty analysis (manual QC → corrected rates)

Script:
- `vocative_uncertainty_analysis.py`

Example (using summary confusion counts):

```bash
python /Users/brettreynolds/Documents/LLM-CLI-projects/English_kinship_terms/childes/vocative_uncertainty_analysis.py \
  --observed /Users/brettreynolds/Documents/LLM-CLI-projects/English_kinship_terms/childes/kinship_vocative_argument.tsv \
  --confusion-parent "49,1,13,37" \
  --confusion-extended "33,17,0,50" \
  --out /Users/brettreynolds/Documents/LLM-CLI-projects/English_kinship_terms/childes/uncertainty_results.json
```

Sensitivity analysis (recompute counts with stricter/looser heuristics):

```bash
python /Users/brettreynolds/Documents/LLM-CLI-projects/English_kinship_terms/childes/vocative_uncertainty_analysis.py \
  --observed /Users/brettreynolds/Documents/LLM-CLI-projects/English_kinship_terms/childes/kinship_vocative_argument.tsv \
  --confusion-parent "49,1,13,37" \
  --confusion-extended "33,17,0,50" \
  --out /Users/brettreynolds/Documents/LLM-CLI-projects/English_kinship_terms/childes/uncertainty_results.json \
  --root /Users/brettreynolds/Downloads/Eng-NA \
  --sensitivity-out /Users/brettreynolds/Documents/LLM-CLI-projects/English_kinship_terms/childes/sensitivity_comparison.tsv
```
