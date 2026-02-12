#!/usr/bin/env python3
"""
Prepare anonymized, pandoc-ready version of main.tex for JoEL submission.

Strategy: Keep the LaTeX intact as much as possible. Define macros in the
preamble so pandoc can expand them. Only transform things pandoc truly
can't handle (langsci-gb4e examples).
"""
import re

with open("main.tex") as f:
    tex = f.read()

# === STEP 1: CONVERT EXAMPLES (before anything else) ===
# langsci-gb4e \ea...\z must become something pandoc understands.
# Convert to indented paragraphs with manual labels.

def strip_outer_braces(s):
    """Remove matched outer braces: {{content}} -> content."""
    while s.startswith("{") and s.endswith("}"):
        d = 0
        matched = True
        for ci, ch in enumerate(s[1:], 1):
            if ch == "{":
                d += 1
            elif ch == "}":
                if d == 0:
                    if ci == len(s) - 1:
                        s = s[1:-1]
                    else:
                        matched = False
                    break
                d -= 1
        if not matched:
            break
    # Fix unbalanced trailing braces
    while s.count("}") > s.count("{") and s.endswith("}"):
        s = s[:-1]
    return s


def balance_braces(s):
    """Remove unmatched closing braces from the string."""
    opens = 0
    result = []
    for ch in s:
        if ch == "{":
            opens += 1
            result.append(ch)
        elif ch == "}":
            if opens > 0:
                opens -= 1
                result.append(ch)
            # else: skip stray }
        else:
            result.append(ch)
    return "".join(result)


def extract_content(stripped, cmd):
    """Extract content from \\ea[judgment]{{text}} or \\ea text."""
    rest = stripped
    rest = re.sub(
        rf"^\\{cmd}\[([^\]]*)\]\{{*",
        lambda m: f"({m.group(1)}) " if m.group(1) else "",
        rest,
    )
    rest = re.sub(rf"^\\{cmd}\s*", "", rest)
    rest = re.sub(r"\\hfill\s*", "  ", rest)
    rest = strip_outer_braces(rest)
    return balance_braces(rest)


def convert_examples(tex):
    """Convert langsci-gb4e blocks to pandoc-compatible LaTeX.

    Produces a borderless tabular for each example:
      Column 1: example number (first row only)
      Column 2: sub-label + content
    Pandoc converts tabular to Word tables; fix_docx.py strips borders.
    """
    lines = tex.split("\n")
    out = []
    depth = 0
    sub_idx = 0
    ex_num = 0  # global example counter
    items = []  # collect (letter, content) for current example

    for line in lines:
        stripped = line.strip()

        # Top-level \ea — start a new example
        if depth == 0 and re.match(r"\\ea", stripped):
            depth = 1
            sub_idx = 0
            ex_num += 1
            items = []
            continue

        # Inner \ea (first sub-example)
        if depth >= 1 and re.match(r"\\ea", stripped):
            depth += 1
            sub_idx += 1
            letter = chr(96 + sub_idx)
            rest = extract_content(stripped, "ea")
            items.append((letter, rest))
            continue

        # \ex (subsequent sub-examples)
        if depth >= 1 and re.match(r"\\ex", stripped):
            sub_idx += 1
            letter = chr(96 + sub_idx)
            rest = extract_content(stripped, "ex")
            items.append((letter, rest))
            continue

        # \z closes a level
        if depth >= 1 and re.match(r"\\z", stripped):
            depth -= 1
            if depth <= 0:
                # Emit the example as a tabular
                out.append("")
                out.append("\\begin{tabular}{ll}")
                for i, (letter, content) in enumerate(items):
                    num_col = f"({ex_num})" if i == 0 else ""
                    out.append(f"{num_col} & {letter}. \\quad {content} \\\\")
                out.append("\\end{tabular}")
                out.append("")
                items = []
                depth = 0
            continue

        # Pass through everything else
        out.append(line)

    return "\n".join(out)

tex = convert_examples(tex)

# === STEP 2: ANONYMIZATION ===

tex = re.sub(
    r"\\author\{.*?\}",
    r"\\author{[Anonymous for review]}",
    tex,
    flags=re.DOTALL,
)
tex = re.sub(r"\\orcidlink\{[^}]+\}", "", tex)
tex = tex.replace(r"\textcite{reynolds2025definiteness}", r"\textcite{anon2025}")
tex = re.sub(
    r"\\url\{https://github\.com/BrettRey/English_kinship_terms\}",
    "[URL removed for anonymous review]",
    tex,
)
tex = re.sub(
    r"I used Claude.*?interpretations\.",
    "[Acknowledgments removed for anonymous review.]",
    tex,
)

# === STEP 3: REPLACE PREAMBLE ===
# Remove house-style input and provide macro definitions directly

preamble_defs = r"""
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{textcomp}
\usepackage[style=american]{csquotes}

% House-style macro definitions for pandoc
\newcommand{\mention}[1]{\textit{#1}}
\newcommand{\mentionhead}[1]{\textit{#1}}
\newcommand{\term}[1]{\textsc{#1}}
\newcommand{\olang}[1]{\textit{#1}}
\newcommand{\ungram}[1]{*#1}
\newcommand{\marg}[1]{?#1}
\newcommand{\odd}[1]{\##1}
\newcommand{\crossmark}{}
"""

tex = tex.replace(r"\input{.house-style/preamble.tex}", preamble_defs)
tex = tex.replace(r"\input{local-preamble.tex}", "")

# Fix ~-- dashes for pandoc
tex = tex.replace("~-- ", " -- ")
tex = tex.replace("~--", " --")

# Remove \S (section sign)
tex = re.sub(r"\\S(?=\\ref|~)", "Section~", tex)
tex = re.sub(r"\\S(\d)", r"Section \1", tex)

# === Write output ===
with open("submission/main-anon.tex", "w") as f:
    f.write(tex)

print("Created submission/main-anon.tex")
