# House Style System

**Version:** 1.0.0

This directory contains the house style framework for LaTeX academic papers by Brett Reynolds.

## Contents

- `VERSION` - Current version (semantic versioning)
- `preamble.tex` - LaTeX preamble with packages and macros
- `style-rules.yaml` - Machine-readable style conventions
- `style-guide.md` - Human-readable style guide
- `templates/` - Project templates and tools

## Creating a New Paper

```bash
cd ~/Documents/LLM-CLI\ projects/
.house-style/templates/agents/create-paper.sh "Your Paper Title"
```

This creates a new paper directory with:
- Complete LaTeX structure
- House style snapshot (frozen at creation)
- Build automation (Makefile)
- Git repository with pre-commit hooks
- AI documentation for Claude/Kimi/Gemini

## Structure

```
.house-style/
├── VERSION                      # 1.0.0
├── preamble.tex                 # LaTeX setup
├── style-rules.yaml             # Machine-readable rules
├── style-guide.md               # Human-readable guide
├── README.md                    # This file
└── templates/
    ├── paper-template/          # Template for new papers
    │   ├── main.tex
    │   ├── references.bib
    │   ├── Makefile
    │   ├── .gitignore
    │   ├── CLAUDE.md
    │   ├── AGENTS.md
    │   ├── GEMINI.md
    │   └── .git/hooks/pre-commit
    └── agents/
        └── create-paper.sh      # Project creation script
```

## Updating Existing Papers

Papers get a **snapshot** of the house style at creation time. To update:

```bash
cd your-paper-directory/
cp ../.house-style/preamble.tex .house-style/
cp ../.house-style/style-rules.yaml .house-style/
# Update .house-style-version if desired
```

**Note:** Papers under review or published should generally NOT be updated.

## Modifying the House Style

1. Edit files in `.house-style/`
2. Increment `VERSION` following semantic versioning:
   - **Major** (X.0.0): Breaking changes to conventions
   - **Minor** (0.X.0): New conventions added
   - **Patch** (0.0.X): Corrections, clarifications
3. New papers will use the updated version
4. Existing papers can opt-in to updates manually

## Key Features

### Three-Agent System

1. **Creation Agent** (`create-paper.sh`) - Generates new papers
2. **AI Guidance** - Claude/Kimi/Gemini read rules during writing
3. **Enforcement** (future) - Pre-commit checks for violations

### Synchronized AI Documentation

All three AI doc files (CLAUDE.md, AGENTS.md, GEMINI.md) are kept in sync via pre-commit hook. Edit any one, and changes propagate to the others automatically.

### House Style Conventions

See `style-guide.md` for full documentation. Key points:

- **LaTeX**: `\term{}` for mention, `\enquote{}` for quotes
- **Notation**: `\crossmark` for cross-linguistic concepts
- **Writing**: Contractions preferred, ~60 word paragraphs
- **Structure**: Avoid `\paragraph{}`, use prose with markers
- **Citations**: `\citep{}` and `\textcite{}`

## Files Created by Template

When you create a new paper, you get:

```
New_Paper_Name/
├── .house-style-version         # Version tracking
├── .house-style/                # Local snapshot
│   ├── preamble.tex
│   └── style-rules.yaml
├── main.tex                     # Paper source
├── references.bib               # Bibliography
├── Makefile                     # Build commands
├── .gitignore                   # LaTeX artifacts
├── CLAUDE.md                    # AI documentation
├── AGENTS.md                    # (synced)
├── GEMINI.md                    # (synced)
└── .git/hooks/pre-commit        # Auto-sync hook
```

## Documentation

- **Human users**: Read `style-guide.md`
- **AI assistants**: Read `style-rules.yaml` (machine-readable)
- **Both**: See design doc at `../Functions_as_Comparanda__Categories_as_Kinds__A_Homeostatic_Approach_to_Typology/docs/plans/2025-11-07-house-style-system-design.md`

## Version History

### 1.0.0 (2025-11-07)
- Initial release
- LaTeX preamble with standard packages
- Style rules from house-style-and-preamble.tex
- Project creation agent
- Template with Makefile and AI docs
- Pre-commit hook for AI doc syncing
