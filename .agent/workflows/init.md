---
description: Initialize session with project context for English kinship terms paper
---

# /init Workflow: English Kinship Terms

Use this workflow at the start of a new session to load project context.

## 1. Review Core Documents

Read the following files to understand the project state:

1. `CLAUDE.md` - Project overview, terminology, and conventions
2. `English kinship terms-taboo to syntax.md` - Gap analysis and literature review
3. `drafting-plan.md` - Section-by-section drafting plan

## 2. Check Current Status

Review the project status in `CLAUDE.md`:
- **Gap analysis:** Complete
- **Drafting:** Not started
- **Next steps:** Listed in CLAUDE.md and drafting-plan.md

## 3. Key Terminology (CGEL Framework)

Maintain strict category–function distinctions:

| Concept | Definition |
|---------|------------|
| Proper noun | Lexical category: *John*, *Mom* |
| Proper name | NP functioning as name: *the United Kingdom* |
| Strong proper name | Without article: *Paris*, *Mom* |
| Weak proper name | With *the*: *the Thames* |
| Bare singular | Count noun without determiner |

## 4. Core Argument

**Proposed mechanism:** Social prohibition → address function → high frequency in name position → grammaticalization toward proper-noun-like syntax

## 5. Advisory Board Voices

Consult `advisory-board.md` and `advisory-gemini.md` for guidance from imagined consultants:
- **Bybee:** Frequency and entrenchment
- **Traugott:** Grammaticalization trajectories
- **Brown:** Power dynamics as engine
- **Zimmer/Gerwig:** Concrete scenes, real dialogue

## 6. House Style

LaTeX conventions in `.house-style/`:
- `\term{}` for concepts (small caps)
- `\mention{}` for linguistic forms (italics)
- `\ea ... \z` for numbered examples
- En-dashes for parentheticals: `~-- text~--`

## 7. Multi-Agent Dispatch

Before dispatching multiple agents, ALWAYS ask Brett:
1. Which model(s)?
2. Redundant outputs for different perspectives?

## 8. Report Ready

After completing this workflow, summarize:
- Current project status
- Recommended next action
- Any gaps or questions
