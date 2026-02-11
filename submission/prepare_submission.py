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

def convert_examples(tex):
    """Convert langsci-gb4e blocks to pandoc-compatible LaTeX."""
    lines = tex.split("\n")
    out = []
    depth = 0
    sub_idx = 0

    for line in lines:
        stripped = line.strip()

        # Top-level \ea
        if depth == 0 and re.match(r"\\ea", stripped):
            depth = 1
            sub_idx = 0
            out.append("")
            out.append("\\begin{quote}")
            continue

        # Inner \ea (sub-examples start)
        if depth >= 1 and re.match(r"\\ea", stripped):
            depth += 1
            sub_idx += 1
            letter = chr(96 + sub_idx)
            # Extract: \ea[judgment]{{content}} or \ea[]{content} or \ea content
            rest = stripped
            rest = re.sub(r"^\\ea\[([^\]]*)\]\{*", lambda m: f"({m.group(1)}) " if m.group(1) else "", rest)
            rest = re.sub(r"^\\ea\s*", "", rest)
            rest = re.sub(r"\\hfill\s*", "  ", rest)
            # Strip outer grouping braces: {{content}} -> content
            while rest.startswith("{") and rest.endswith("}"):
                # Check if the outer braces are a matched pair
                depth = 0
                matched = True
                for ci, ch in enumerate(rest[1:], 1):
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        if depth == 0:
                            if ci == len(rest) - 1:
                                rest = rest[1:-1]
                            else:
                                matched = False
                            break
                        depth -= 1
                if not matched:
                    break
            # Remove any remaining unmatched trailing braces
            while rest.endswith("}"):
                opens = rest.count("{")
                closes = rest.count("}")
                if closes > opens:
                    rest = rest[:-1]
                else:
                    break
            out.append(f"\\noindent ({letter}) {rest}")
            continue

        # \ex (subsequent sub-examples)
        if depth >= 1 and re.match(r"\\ex", stripped):
            sub_idx += 1
            letter = chr(96 + sub_idx)
            rest = stripped
            rest = re.sub(r"^\\ex\[([^\]]*)\]\{*", lambda m: f"({m.group(1)}) " if m.group(1) else "", rest)
            rest = re.sub(r"^\\ex\s*", "", rest)
            rest = re.sub(r"\\hfill\s*", "  ", rest)
            # Strip outer grouping braces
            while rest.startswith("{") and rest.endswith("}"):
                depth = 0
                matched = True
                for ci, ch in enumerate(rest[1:], 1):
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        if depth == 0:
                            if ci == len(rest) - 1:
                                rest = rest[1:-1]
                            else:
                                matched = False
                            break
                        depth -= 1
                if not matched:
                    break
            while rest.endswith("}"):
                opens = rest.count("{")
                closes = rest.count("}")
                if closes > opens:
                    rest = rest[:-1]
                else:
                    break
            out.append(f"\\noindent ({letter}) {rest}")
            continue

        # \z closes a level
        if depth >= 1 and re.match(r"\\z", stripped):
            depth -= 1
            if depth <= 0:
                out.append("\\end{quote}")
                out.append("")
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

# === STEP 4: FINAL BRACE CLEANUP ===
# Fix unbalanced braces in example lines (\noindent (a) ...)
lines = tex.split("\n")
clean = []
for line in lines:
    if re.match(r"\\noindent \([a-z]\)", line):
        # Remove double }} -> } repeatedly until balanced
        while line.count("}") > line.count("{"):
            line = line.replace("}}", "}", 1)
    clean.append(line)
tex = "\n".join(clean)

# === Write output ===
with open("submission/main-anon.tex", "w") as f:
    f.write(tex)

print("Created submission/main-anon.tex")
