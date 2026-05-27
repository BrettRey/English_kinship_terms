# STATUS.md - English Kinship Terms

**Last updated:** 2026-05-27

## Current Phase

**SUBMITTED** - Journal of English Linguistics (JEngL-26-0039), February 12, 2026. Preprint: LingBuzz [lingbuzz/009751](https://ling.auf.net/lingbuzz/009751)

## 2026-05-27 PM Provenance Audit

- Dirty state classified as submission/admin residue, not manuscript-source drift.
- Tracked manuscript source and submission-generation files (`main.tex`, `references.bib`, `submission/main-anon.tex`, `submission/references.bib`, `submission/prepare_submission.py`, `submission/fix_docx.py`) are clean relative to `HEAD`.
- `Reynolds_English_kinship_terms_taboo_to_syntax.pdf` is byte-identical to tracked `main.pdf`; `reynolds2025kinship.pdf` is an older pre-submission/preprint artifact.
- Untracked `submission/main-anon.docx` is the intermediate DOCX produced by the submission script; tracked `submission/English_kinship_terms_taboo_to_syntax_anon.docx` remains the named anonymized JoEL manuscript artifact.
- Untracked cover-letter/title-page DOCX/Markdown files and May 9 literature notes should be committed or parked in a routine hygiene pass, but they do not indicate a post-submission manuscript edit.

## Timeline

- **2025-12-28**: Gap analysis to full draft (~8 hours)
- **2025-12-28**: Multi-agent advisory review completed
- **2025-12-29**: Revision: CHILDES data integrated, Malagasy predictions refined, bibliography verified, text cohesion improved

## Draft Status

| Section | Status |
|---------|--------|
| 1. Introduction | Complete |
| 2. The naming taboo | Complete (cross-cultural parade added) |
| 3. Proper-noun syntax | Complete |
| 4. From taboo to syntax | Complete (CHILDES table added) |
| 5. Cross-linguistic predictions: Malagasy | Complete (ry vocative, Paul 2018) |
| 6. Broader predictions | Complete |
| 7. Objections and alternatives | Complete |
| 8. Conclusion | Complete |

## Key Changes (2025-12-29)

1. **CHILDES corpus evidence** - Frequency table showing parent terms 16-43% vocative, extended kin 4-7%
2. **Malagasy prediction refined** - *ry*/bare in vocative vs. *i/ra* in argument position (Paul 2018, Potsdam 2010)
3. **Literature strengthened** - Sloat 1969, Longobardi 1994, Hill 2022, Kripke 1980
4. **Cross-cultural naming taboos** - Hawaiian kapu, Zulu hlonipha, Apache ghost-names
5. **Repository public** - [github.com/BrettRey/English_kinship_terms](https://github.com/BrettRey/English_kinship_terms)

### 2026-02-11 Session Notes
- Fixed 6 fabricated/incorrect bib entries: Hill2022 DOI, IrvineGunner2018 (completely fabricated), Potsdam2010 (wrong paper), Bloch2006 (wrong publication), Traugott1993 (fabricated), Traugott2003 (chimera of two books)
- Removed unverifiable Dziwirek2019; replaced citation with BrownFord1961
- Added Figure 3 cross-reference in CHILDES results discussion
- Submission pipeline: rewrote example conversion (tabular instead of inline) to fix pandoc eating example numbers
- Updated submission/references.bib to match corrected main bib
- PDF renamed and uploaded to LingBuzz

### 2026-02-10 Session Notes (session 2)
- Cut Longobardi/DP paragraph from §6.4 entirely (paper doesn't need to engage with DP framework)
- Cut two redundant recap paragraphs opening the conclusion; now opens with "Three contributions stand out"
- Tightened Parent Trap return to avoid near-verbatim echoes of intro; "restoration of a word" → "restoration of a license"
- Fixed Oxford spelling: realisation → realization (2 instances)
- Updated acknowledgements: Claude Opus 4.5 → 4.6
- Researched Chomsky DP-rejection: best candidate is Chomsky (2021) *Gengo Kenkyu* 160: 1–41; Pullum & Miller (2022) "NPs versus DPs: why Chomsky was right" on lingbuzz — source unverified, not cited
- Renamed PDF for lingbuzz upload

### 2026-02-10 Session Notes (session 1)
- Contracted 18 uncontracted forms (house style: contractions preferred)
- Cut redundancy: 4.7% adjacency paragraph, sediment analogy cluster, engine/counterfactual paragraph, hlonipha preview, weaker-taboo restatement
- Rewrote §6.2 (semantics objection): "precondition" → candidacy framing (Partee-inspired); dropped "consistency" argument
- Cut Korean/Japanese from §5.4 (no proper-noun diagnostic in article-less languages)
- Fixed plural-author references in single-author paper (our → present purposes, I, the frequency mechanism)
- Added relational persistence to Teacher/Waiter contrast
- Distanced from Longobardi/DP; rewrote diachronic prediction as honestly untestable
- Used \mentionhead for sir/ma'am heading; tempered frequency claim

### 2026-02-09 Session Notes
- Intro restructured: proper-name/proper-noun distinction moved earlier into CGEL subsection
- Deitality subsection compressed from 3 paragraphs to 1
- Caregiver self-reference added as secondary frequency factor with Duranti 2011 citation
- Bybee paraphrase rewritten for clarity
- Abstract refined ("correlates with" replacing "predicts")
- Vocative footnote streamlined with forward reference to §3
- *Parent Trap* footnoted as "Disney, 1998"
- Insertion points: Dziwirek2019, Downing1996, BensonAnglin1987 all integrated; Surono2018 superseded by cross-cultural opening

### 2026-02-06 Session Notes
- Sharpened proper-name / proper-noun distinction throughout: bare *Mom* IS a proper name (naming function, binary); the gradient across kinship terms is in proper-noun entrenchment (lexical category)
- New paragraph in CGEL framework subsection making the distinction explicit
- New sentence before gradient examples locating the gradient in proper-noun entrenchment
- ~25 terminology fixes: "proper-name syntax/status/properties" → "proper-noun" (except Malagasy "proper-name determiners")
- Section 3 heading now "Kinship terms with proper-noun status"
- HPC perspective motivated the edits but HPC vocabulary stays out of the paper

## Remaining Limitations

- Diachronic evidence thin (when did bare *Mom* become licensed?)
- Scandinavian weak-taboo prediction anecdotal
- Malagasy prediction awaits fieldwork

## Files

- `main.tex` - Full draft (~427 lines, 18 pages)
- `main.pdf` - Compiled PDF
- `references.bib` - Bibliography
- `childes/` - Frequency extraction scripts and data
- `literature/` - Source PDFs
- `board-*.md` - Advisory reviews
