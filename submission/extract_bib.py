#!/usr/bin/env python3
"""Extract only the needed bib entries from the large bib file."""
import re

# Read all citation keys from main.tex
with open("main.tex") as f:
    tex = f.read()

keys = set()
for m in re.finditer(r"\\(?:citep|textcite|citealt|citet|cite)\{([^}]+)\}", tex):
    for k in m.group(1).split(","):
        keys.add(k.strip())

print(f"Found {len(keys)} citation keys in main.tex")

# Extract matching entries from references.bib
with open("references.bib") as f:
    bib = f.read()

entries = []
i = 0
while i < len(bib):
    m = re.search(r"@\w+\{", bib[i:])
    if not m:
        break
    start = i + m.start()
    # Find the matching closing brace
    depth = 0
    j = start
    for j in range(start + m.end() - 1, len(bib)):
        if bib[j] == "{":
            depth += 1
        elif bib[j] == "}":
            depth -= 1
            if depth == 0:
                break
    entry_text = bib[start : j + 1]
    # Extract key
    key_match = re.match(r"@\w+\{([^,\s]+)", entry_text)
    if key_match:
        key = key_match.group(1)
        if key in keys:
            entries.append(entry_text)
    i = j + 1

with open("submission/references.bib", "w") as f:
    f.write("\n\n".join(entries) + "\n")

found_keys = set()
for e in entries:
    km = re.match(r"@\w+\{([^,\s]+)", e)
    if km:
        found_keys.add(km.group(1))

print(f"Extracted {len(entries)} entries")
missing = keys - found_keys
if missing:
    print(f"Missing: {missing}")
else:
    print("All keys found.")
