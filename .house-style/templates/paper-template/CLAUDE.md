# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an academic research paper titled "{{PAPER_TITLE}}" by Brett Reynolds.

## Build System

This LaTeX project requires **XeLaTeX or LuaLaTeX** (not pdfLaTeX) due to the Charis SIL font requirement.

### Compilation Commands

```bash
# Full build sequence
lualatex main.tex
biber main
lualatex main.tex
lualatex main.tex

# Or use automated build
make              # Full build
make quick        # Single pass
make clean        # Clean artifacts
```

The multiple runs are necessary to resolve all cross-references and citations.

## File Structure

```
{{PAPER_DIR}}/
├── main.tex                  # Main document
├── references.bib            # Bibliography
├── .house-style/             # House style snapshot
│   ├── preamble.tex         # LaTeX preamble
│   └── style-rules.yaml     # Style conventions
├── Makefile                  # Build automation
├── CLAUDE.md                 # This file
├── AGENTS.md                 # Synced with this file
└── GEMINI.md                 # Synced with this file
```

## House Style

This project uses Brett Reynolds house style (see `.house-style/style-rules.yaml`).

### Key LaTeX Conventions

**Terms, Mentions, Quotations:**
- Use `\term{}` for terms/concepts (small caps): `\term{definiteness}`
- Use `\mention{}` for mentions/forms (italics): `\mention{the}`
- Use `\olang{}` for object language (italics): `\olang{der Hund}`
- Use `\enquote{}` for quotations: `\enquote{actual quote}`
- Never use raw quotes for mention

**Cross-linguistic Notation:**
- Cross-linguistic: `\textsc{subject}\crossmark`
- Language-specific: `\textsc{subject}\textsubscript{eng}`

**Dashes:**
- Parenthetical: `foo~-- bar~-- baz` (en dash with spaces)
- Ranges: `2001--2025` (en dash, no spaces)
- Compounds: `corpus-based` (hyphen)

**Citations:**
- Parenthetical: `\citep{key}`
- Textual: `\textcite{key}`

### Writing Style

**Preferred:**
- Use contractions (don't, won't)
- Keep paragraphs ~60 words, max 100
- Direct verbs and short clauses
- Concrete before abstract

**Avoid:**
- Throat-clearers: "It is important to note that..."
- `\paragraph{}` headings (use topic sentences)
- Bold labels in prose
- Hackneyed adverbs: moreover, furthermore

**Document Structure:**
- Use `\section{}` and `\subsection{}` only
- Avoid bullet points for arguments (use prose)
- Use ordinal markers: "first," "second," "third"

**Examples (gb4e):**
```latex
\ea\label{ex:example}
\textit{Example sentence.}
\z
```

## Common Tasks

**Adding References:**
1. Add entry to `references.bib`
2. Protect capitals: `title = {The {Cambridge} Grammar...}`
3. Use `\textcite{key}` or `\citep{key}`

**Building:**
```bash
make              # Full build
make quick        # Fast build
make clean        # Clean up
```

**Git Workflow:**
- Pre-commit hook keeps CLAUDE.md, AGENTS.md, GEMINI.md synced
- Commit often with meaningful messages
- Build before committing to ensure no LaTeX errors

## Multi-Agent Dispatch (MANDATORY)

**Before dispatching multiple agents, ALWAYS ask Brett:**

1. **Which model(s)?** Options: Claude, Codex, Gemini, Copilot
   - Codex is often best for Brett's work
   - Claude has the smallest context window
   - Different models have different strengths

2. **Redundant outputs?** Should multiple models tackle the same task?
   - Useful for judgment calls (e.g., "Should I add this figure?")
   - Not needed for factual tasks

### CLI Command Patterns

| CLI | Command | Notes |
|-----|---------|-------|
| **Codex** | `codex -p 'prompt' > output.txt &` | Include "Read [PATH] first" in prompt |
| **Gemini** | `cat file.tex \| gemini --yolo -o text 'prompt'` | Must pipe content (file reading broken in YOLO) |
| **Copilot** | `copilot -p 'prompt' > output.txt &` | Fast; add `--allow-all-tools` for file ops |

**Token limits:** Gemini > Codex > Claude (most constrained)

See portfolio `CLAUDE.md` or `HPC book/.agent/workflows/multi-agent-review.md` for full patterns.
