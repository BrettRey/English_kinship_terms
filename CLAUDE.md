# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Paper arguing that the English naming taboo (children addressing parents by kinship terms rather than first names) drives the proper-noun-like syntactic properties of English kinship terms.

**Working title:** English kinship terms: From taboo to syntax
**Author:** Brett Reynolds (Humber Polytechnic / University of Toronto)
**Status:** Gap analysis complete; drafting not started

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

**The gap:** Neither literature cites the other. No causal mechanism proposed.

## Building the Document

When a main.tex is created:

```bash
# Using Makefile (preferred)
make              # Full build with bibliography
make quick        # Single pass (no bib update)
make clean        # Remove build artifacts

# Manual build (XeLaTeX required for house style)
xelatex main.tex && biber main && xelatex main.tex && xelatex main.tex
```

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

## Next Steps

1. Draft introduction connecting the two literatures
2. Systematically apply CGEL proper noun/name apparatus to kinship terms
3. Document the distributional evidence (corpus work on *Mom*, *Dad*)
4. Propose grammaticalization pathway
5. Address cross-linguistic evidence (English taboo is "weak" compared to Chinese, Vietnamese)

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
