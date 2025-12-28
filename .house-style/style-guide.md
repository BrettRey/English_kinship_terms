# Brett Reynolds House Style Guide

**Version:** 2.0.0 (December 2025 typography redesign)
**For:** LaTeX academic papers in linguistic typology

This guide documents LaTeX conventions and writing style for academic papers. See `preamble.tex` for the corresponding LaTeX macros, `style-rules.yaml` for machine-readable rules, and `docs/plans/typography-design.md` for the full typography specification.

## Typography Overview

- **Font:** EB Garamond with old-style numerals; Charis SIL for IPA
- **Layout:** Letter paper with book-like asymmetric margins
- **Headings:** Small caps sections, italic subsections (Bringhurst-inspired)
- **Links:** Dark maroon (#800020)

## Table of Contents

1. [Terms, Mentions, and Quotations](#terms-mentions-and-quotations)
2. [Dashes, Ranges, Hyphens](#dashes-ranges-hyphens)
3. [Contractions and Plain Style](#contractions-and-plain-style)
4. [Numbered Examples](#numbered-examples)
5. [Category vs. Function](#category-vs-function)
6. [Citations](#citations)
7. [Journal Article Formatting](#journal-article-formatting)
8. [Dual-Audience Accessibility](#dual-audience-accessibility)
9. [BibTeX Conventions](#bibtex-conventions)

---

## Terms, Mentions, and Quotations

**Rule:** Distinguish between terms (concepts being defined), mentions (forms under discussion), and quotations.

### Three Semantic Macros

| Purpose | Macro | Rendering | Example |
|---------|-------|-----------|---------|
| Terms (concepts) | `\term{definiteness}` | small caps | The notion of \term{definiteness} is complex. |
| Mentions (forms) | `\mention{the}` | italics | The word \mention{the} is a determinative. |
| Object language | `\olang{der Hund}` | italics | German \olang{der Hund} 'the dog' |
| Quotations | `\enquote{text}` | curly quotes | As \enquote{going forward} spread... |

### Examples

- **Term:** `\term{definiteness}` involves identifiability and uniqueness.
- **Mention:** The determinative `\mention{the}` is not always definite.
- **Object language:** German `\olang{der Hund}` 'the dog'
- **Quotation:** `\enquote{Outer with an \enquote{inner} quote}`
- **Semantic meanings:** use single 'quote'

**Note:** `\term{}` is now small caps (was italics in v1). Use `\mention{}` for the old italics behavior.

---

## Dashes, Ranges, Hyphens

### Parenthetical Asides
Use an en dash (`--`) with surrounding spaces:

```latex
the category is stable~-- within limits~-- across registers
```

### Ranges and Relations
Use an en dash (no spaces):

```latex
2001--2025
pp.\ 113--127
the form--function distinction
```

### Compounds
Use hyphens only:

```latex
corpus-based study
task-specific rubric
```

---

## Contractions and Plain Style

**Contractions are preferred:**

> We don't gain anything by multiplying categories.

### Delete Throat-Clearers

❌ **Avoid:** "It is important to note that the results clearly show that..."
✅ **Prefer:** "The results show..."

❌ **Avoid:** Overly strong modals like "must" (e.g., "The features must cluster reliably")
✅ **Prefer:** Softer phrasing (e.g., "The features should cluster reliably")

### Simple Coordinators

Prefer simple coordinators (and, but) to hackneyed "academic" adverbs (moreover, furthermore, nevertheless, yet).

Sentence-initial coordinators are fine where they improve flow. Avoid overuse.

---

## Numbered Examples

Uses `langsci-gb4e` package. **Note:** No `exe` environment.

### Simple Example

```latex
\ea\label{ex:simple}
\textit{The committee have decided to adjourn.}
\z
```

### Judgement Markers and Subexamples

```latex
\ea\label{ex:sub}
    \ea \textit{She has already left.}
    \ex[*]{\ungram{\textit{She have already left.}}}
    \ex[\#]{\odd{\textit{The square triangle laughed.}}}
    \z
\z
```

Cross-reference: `see (\ref{ex:sub})`

### Interlinear Gloss

Abbreviations in small caps using `\abbr{}`:

```latex
\ea\label{ex:gloss}
\gll Ich sehe den Hund. \\
     I see the.\abbr{acc} dog \\
\glt `I see the dog.'
\z
```

---

## Category vs. Function

**Distinguish lexical categories from functions:**

- Categories: `\term{determinative}`, `\term{adjective}`
- Functions: `\term{head}`, `\term{modifier}`, `\term{subject}`

**Example:** In `\enquote{\term{those} books}`, `\term{those}` is a `\term{determinative}` (category) functioning as a `\term{determinative}` (function) of the NP.

### Cross-Linguistic Notation

Use the cross symbol to mark comparative concepts:

```latex
\textsc{subject}\crossmark
\textsc{topic}\crossmark
\textsc{noun}\crossmark
```

**Language-specific:**
```latex
\textsc{subject}\textsubscript{eng}
\textsc{topic}\textsubscript{jpn}
```

**Language-internal (generic):**
```latex
\textsc{subject}\textsubscript{$L$}
```

**Important:** Always use `\textsubscript{}` for these labels; do not use the underscore character (`\_`) directly in text mode.

---

## Citations

Using `biblatex` with `natbib=true`:

### Basic Citations

- **Parenthetical:** `\citep{HuddlestonPullum2002}`
- **Textual:** `\textcite{Pullum2018}`
- **Multiple:** `\citep{HuddlestonPullum2002,Pullum2018}`
- **With page:** `\citep[113--127]{HuddlestonPullum2002}`

---

## Journal Article Formatting

Scholarly journals use structural apparatus sparingly. Avoid textbook-style formatting.

### Document Structure and Headings

A typical journal article has a focused structure with 5-7 major sections (e.g., Introduction, Background, Analysis, Discussion, Conclusion). Avoid creating an excessive number of top-level sections.

✅ **Use:** `\section{}` and `\subsection{}` for the main divisions of the paper. These two levels are usually sufficient.

❌ **Avoid:** An overly granular structure. If you have more than 7-8 `\section`s, consider merging related topics.

❌ **Avoid:** Deeper nesting with `\subsubsection{}` or `\paragraph{}`. A topic that seems to require a third-level heading should be restructured, perhaps as a new `\subsection{}` or integrated into the main prose.

### Bold, Bullets, Enumeration

**Avoid bold labels in prose.** Taxonomies and argument sequences should flow as narrative, not as itemized lists.

- ❌ **Wrong:** **(i) Cross-linguistic property covariation.** The diagnostic features must cluster...
- ✅ **Right:** First, the diagnostic features must cluster...

**Enumerated lists are acceptable for:**
- Hypothesis or prediction lists
- Linguistic examples (`\ex` from langsci-gb4e)
- Illustrative codebook entries

**Avoid lists for:**
- Argumentative sequences (use prose with transitions: "first," "second," "finally")
- Objection-reply pairs (use discourse markers: "A first objection," "A related worry")
- Before/after pedagogical contrasts (use narrative)

### Transitions and Discourse Markers

Use ordinal markers and discourse connectives for flow:

**Sequence:** first, second, third; one [concern], another, a final [point]

**Objections:** A first objection concerns...; A second question asks...; A related worry...; Finally, does...

**Illustrations:** Consider first...; A second illustration...; The clearest case...

---

## Dual-Audience Accessibility

When writing for readers from multiple disciplines (e.g., linguists and philosophers), make cross-disciplinary terminology accessible without sacrificing rigor.

### Paragraph Length

Keep paragraphs under 100 words on average. Dense 200+ word paragraphs should be broken into 2--4 shorter units with clear topic sentences. **Aim for ~60 words per paragraph** in body text.

### Parenthetical Glosses

When introducing technical terms, add brief functional explanations:

- Latent variables (quantities representing unobserved category strength)
- Spearman's ρ (a rank correlation measure)
- Differential object marking (where only some objects trigger case or agreement)

### Concrete Before Abstract

Introduce technical apparatus with concrete examples or plain-language motivation:

❌ **Wrong:** Define a vector of observable diagnostics: **n**_L = ⟨ArgHead, ...⟩

✅ **Right:** Traditional typology trades in binary tallies: language X "has" adjectives or it doesn't. The comparanda × categories matrix provides something better: explicit measurement models. For nominality, define a vector...

### Comparanda Notation and Terminology

Maintain a strict distinction between comparative concepts and language-specific categories:

- Use **\textsc{Term}\textsubscript{cross}** for cross-linguistic comparanda (syntactic functions, semantic targets, discourse roles, comparative categories)
- Use **\textsc{Term}\textsubscript{eng}** (or other language tag) for language-specific realisations
- Use **\textsc{Term}\textsubscript{int}** for language-internal discussion without naming a language
- Reserve **function** (without modifier) for syntactic functions only
- Use **target** for semantic targets
- Use **role** for discourse/pragmatic roles
- Use **category** for lexical categories or their phrasal projections
- Remind readers that mappings between axes are rarely one-to-one: a single expression can realise multiple functions, targets, and roles simultaneously

---

## BibTeX Conventions

Protect capitals in proper nouns and first words after colons using braces:

```bibtex
title = {The {Cambridge} Grammar of the {English} Language}
title = {Radical Construction Grammar: {Syntactic} Theory...}
title = {Character identity mechanisms: {A} conceptual model...}
```

### What to Protect

- Proper nouns: `{Cambridge}`, `{English}`, `{American}`
- First word after colon: `{Syntactic}`, `{A}`, `{An}`
- Acronyms: `{HPC}`, `{DOM}`

### What NOT to Protect

- Common nouns, adjectives, verbs (unless part of proper noun)
- Title-initial words (BibTeX handles these automatically)

---

## Quick Reference

### LaTeX Macros (from preamble.tex)

```latex
% Semantic typography
\term{text}           % Terms/concepts (small caps)
\mention{text}        % Mentions/forms (italics)
\olang{text}          % Object language (italics)
\abbr{text}           % Small-caps abbreviations for glosses
\ipa{text}            % IPA in Charis SIL font

% Cross-linguistic
\crossmark            % Cross-linguistic subscript marker

% Judgements
\ungram{*sentence}    % Ungrammatical (*)
\marg{?sentence}      % Marginal (?)
\odd{#sentence}       % Odd (#)

% Abbreviations
\eg                   % e.g., with spacing
\ie                   % i.e., with spacing
\etc                  % etc. with spacing

% Numbers
\liningnums{2025}     % Lining figures (for tables, isolated years)
```

### Citation Commands

```latex
\citep{key}           % (Author Year)
\textcite{key}        % Author (Year)
\citep[page]{key}     % (Author Year:page)
```

### Example Commands

```latex
\ea ... \z            % Single example
\ea \ea ... \ex ... \z \z   % Subexamples
\gll ... \\ ... \\ \glt ... % Interlinear gloss
```

---

**For AI assistants:** This style guide should be followed when writing or editing LaTeX academic papers. Consult `style-rules.yaml` for machine-readable versions of these conventions.
