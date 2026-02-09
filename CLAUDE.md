# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Paper arguing that the English naming taboo (children addressing parents by kinship terms rather than first names) drives the proper-noun-like syntactic properties of English kinship terms.

**Working title:** English kinship terms: From taboo to syntax
**Author:** Brett Reynolds (Humber Polytechnic / University of Toronto)
**Status:** Complete draft in main.tex (~427 lines); active revision/polish phase

## File Structure

```
English_kinship_terms/
├── main.tex              # Complete draft (~427 lines)
├── references.bib        # Bibliography
├── local-preamble.tex    # Font overrides for house style
├── main.pdf              # Compiled output
├── notes/
│   ├── English kinship terms-taboo to syntax.md  # Gap analysis
│   ├── drafting-plan.md  # Section-by-section outline
│   └── advisory/         # Advisory board notes
├── drafts/
│   └── section1-opening.md  # Early draft of opening
├── literature/           # Reference PDFs and notes
│   ├── hill2022vocatives.pdf
│   ├── cgel-ch5.20.pdf
│   ├── bloch2006malagasy.pdf
│   └── [other sources]
└── .house-style/         # Symlinked house style
```

## Core Argument

The paper fills a genuine gap: no existing work connects the sociolinguistic prohibition (naming taboo) to the grammatical properties (bare singular behavior, strong proper name syntax).

**Proposed mechanism:** Social prohibition → address function → high frequency in name position → grammaticalization toward proper-noun-like syntax

**Key claim:** When "Mom" appears without a determiner referring to a unique individual, it functions as a **strong proper name**; with a determiner ("my mom"), it functions as a common noun with relational meaning.

## Critical Terminology (CGEL Framework)

This paper requires strict category–function distinctions:

| Concept | Definition |
|---------|------------|
| Determinative | Lexical category (word class): *the*, *some*, *my* |
| Determiner | Syntactic function in NP structure |
| Proper noun | Single word (lexical category): *John*, *Mom* |
| Proper name | NP functioning as name (may be multi-word): *the United Kingdom* |
| Strong proper name | Used without article: *Paris*, *Mom* |
| Weak proper name | Requires *the*: *the Thames* |
| Bare singular | Count noun without determiner (normally ungrammatical in English except kinship terms as names) |

## Two Disconnected Literatures

**Sociolinguistics (address forms):**
- Brown & Gilman 1960 (power/solidarity)
- Brown & Ford 1961 (American English address)
- Dickey 1997 (forms of address)
- Braun 1988 (*Terms of Address*)

**Syntax (proper nouns, bare nominals):**
- CGEL (Huddleston & Pullum 2002)
- Carlson 1977 (bare plurals as names of kinds)
- Hill 2022 (syntactization of kinship in vocatives)
- Chappell & McGregor 1996 (inalienable possession)

**Usage-based / Developmental:**
- Bybee 2006, 2010 (frequency and entrenchment)
- Duranti 2011 (caregiver self-reference)
- Benson & Anglin 1987 (kin-term acquisition order)

**The gap:** Neither literature cites the other. No causal mechanism proposed.

## Building the Document

```bash
# XeLaTeX required (not LuaLaTeX)
xelatex main.tex && biber main && xelatex main.tex && xelatex main.tex
```

Note: This project has `local-preamble.tex` to handle font substitutions. The house-style preamble expects specific fonts (EB Garamond, Charis SIL).

## House Style (Critical Conventions)

**Semantic Typography:**
- `\term{definiteness}` for concepts (small caps)
- `\mention{Mom}` for linguistic forms (italics)
- `\olang{der Hund}` for object language (italics)
- `\enquote{text}` for quotations

**Examples (langsci-gb4e):**
- `\ea ... \z` for numbered examples
- `\ungram{*She have left}` for ungrammatical
- `\marg{?text}` for marginal
- `\odd{#text}` for semantically odd

**Dashes:**
- Parenthetical: `~-- text~--` (en-dash with spaces)
- Ranges: `1960--1997` (en-dash, no spaces)

**Citations:**
- `\citep{key}` parenthetical
- `\textcite{key}` narrative

## Paper Structure (Current Draft)

1. **Introduction** (§1) - *Parent Trap* opening; two facts; proposed mechanism; CGEL framework (proper-name/proper-noun distinction front and centre); deitality (compressed); roadmap
2. **The naming taboo** (§2) - Cross-cultural taboos; power/solidarity; parent-child asymmetry; politeness and face; English taboo as frequency concentrator (not lexical replacement)
3. **Kinship terms with proper-noun status** (§3) - CGEL framework; bare singular pattern; deitality diagnostics; gradience across kin terms; vocatives
4. **From taboo to syntax** (§4) - Frequency argument; grammaticalization pathway; CHILDES corpus evidence (Table 1, manual QC, sensitivity analysis, vocative-bare correlation)
5. **Cross-linguistic predictions: Malagasy** (§5) - Determiner system; naming taboo; predictions; weaker taboos; within-family variation; honorifics; in-laws
6. **Objections and alternatives** (§6) - Vocative generalization; semantic uniqueness; sir/ma'am; lexical specification; causal directionality
7. **Conclusion** (§7) - Return to *Parent Trap*

## Remaining Tasks

**Drafting:** Complete
**Revision:** Active polish phase (intro restructured 2026-02-09)

**Acknowledged gaps (flagged in text as future work):**
- Diachronic trajectory of bare kin-term stabilization
- Variation across class/region/ethnicity

## Related Projects

| Project | Connection |
|---------|------------|
| `Personhood_and_proforms/` | Pro-forms and designatum-driven gender |
| `countability/` | HPC approach to grammatical properties |
| `Functions_as_Comparanda.../` | Typological framework |
| `HPC book/` | Part II (definiteness) may relate |

## Multi-Agent Dispatch (MANDATORY)

Before dispatching multiple agents, ALWAYS ask Brett:
1. **Which model(s)?** Claude, Codex, Gemini, Copilot
2. **Redundant outputs?** Multiple models on same task for different perspectives?

See portfolio-level `CLAUDE.md` for CLI command patterns and full workflow.

## Collaboration Logging

This project participates in portfolio-level collaboration logging for pedagogical purposes.

### When to Log

Log to `../Project-Management/collaboration-log/` when:
- **Architectural decisions** arise (paper structure, argument strategy, theoretical commitments)
- **Workflow innovations** emerge (new ways of researching, drafting, or coordinating)
- **Pushback moments** occur (human redirects or rejects LLM suggestions)
- **Failure modes** happen (when collaboration went wrong)

### What to Capture

Focus on the *process*, not the paper content:
- How did we decide on the argument structure?
- What alternatives were considered and rejected?
- Where did the LLM get something wrong that the human corrected?
- What worked well that could be replicated?

### Timing

- **Real-time**: Only for important things that could get lost in context compression
- **End-of-session**: Brief recap (usual practice)

See `../Project-Management/CLAUDE.md` for full logging protocol and session entry template.
