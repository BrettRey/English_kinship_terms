#!/usr/bin/env python3
"""Fix three issues in main-anon.docx for JoEL submission:
1. Set double-spaced, 12pt Times New Roman
2. Add figure/table caption numbering
3. Convert footnotes to endnotes (LAST -- XML surgery that python-docx would overwrite)
"""
import zipfile
import os
import xml.etree.ElementTree as ET
from copy import deepcopy

WML = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

SRC = "main-anon.docx"
DST = "main-anon.docx"

# === PHASE 1: python-docx operations (formatting + captions) ===

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_LINE_SPACING

# First, regenerate from pandoc to have a clean starting point
os.system(
    "pandoc main-anon.tex --from latex --to docx --citeproc "
    "--bibliography=references.bib --csl=unified-linguistics.csl "
    "-o main-anon.docx 2>&1"
)
print("Regenerated clean docx from tex")

doc = Document(DST)

# --- Fix 1: Double-spacing, 12pt Times New Roman ---
for p in doc.paragraphs:
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    for run in p.runs:
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)

for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
                for run in p.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(12)

style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(12)
style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE

print("Fix 1 done: double-spaced, 12pt Times New Roman")

# --- Fix 2: Caption numbering ---
fig_num = 0
tab_num = 0

for p in doc.paragraphs:
    text = p.text.strip()

    # Table captions: pandoc uses "Table Caption" style
    if p.style.name == "Table Caption" and not text.startswith("Table "):
        tab_num += 1
        if p.runs:
            p.runs[0].text = f"Table {tab_num}: " + p.runs[0].text
        print(f"  Table {tab_num}: {text[:60]}")

    # Figure captions: pandoc uses "Image Caption" style
    if p.style.name == "Image Caption" and not text.startswith("Figure "):
        fig_num += 1
        if p.runs:
            p.runs[0].text = f"Figure {fig_num}: " + p.runs[0].text
        print(f"  Figure {fig_num}: {text[:60]}")

print(f"Fix 2 done: numbered {tab_num} tables and {fig_num} figures")

# Save after python-docx operations
doc.save(DST)
print("Saved after python-docx fixes")

# === PHASE 2: XML surgery for footnotes → endnotes ===
# Must happen AFTER python-docx save, since python-docx would overwrite our XML

# Register namespaces
for prefix, uri in {
    "w": WML, "r": REL,
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "o": "urn:schemas-microsoft-com:office:office",
    "v": "urn:schemas-microsoft-com:vml",
}.items():
    ET.register_namespace(prefix, uri)

# Read all zip contents
with zipfile.ZipFile(DST, "r") as zin:
    names = zin.namelist()
    files = {name: zin.read(name) for name in names}

# Parse document.xml and footnotes.xml
doc_xml = ET.fromstring(files["word/document.xml"])
fn_xml = ET.fromstring(files["word/footnotes.xml"])

# Create endnotes.xml with separator entries
en_xml = ET.Element(f"{{{WML}}}endnotes")
for eid, etype in [("-1", "continuationSeparator"), ("0", "separator")]:
    en = ET.SubElement(en_xml, f"{{{WML}}}endnote")
    en.set(f"{{{WML}}}id", eid)
    en.set(f"{{{WML}}}type", etype)
    p = ET.SubElement(en, f"{{{WML}}}p")
    r = ET.SubElement(p, f"{{{WML}}}r")
    if etype == "separator":
        ET.SubElement(r, f"{{{WML}}}separator")
    else:
        ET.SubElement(r, f"{{{WML}}}continuationSeparator")

# Move real footnotes (id not 0 or -1) to endnotes
moved = 0
for fn_elem in list(fn_xml):
    fn_id = fn_elem.get(f"{{{WML}}}id")
    if fn_id and fn_id not in ("0", "-1"):
        en_elem = deepcopy(fn_elem)
        en_elem.tag = f"{{{WML}}}endnote"
        # Fix internal refs and styles
        for ref in en_elem.iter(f"{{{WML}}}footnoteRef"):
            ref.tag = f"{{{WML}}}endnoteRef"
        for sty in en_elem.iter(f"{{{WML}}}rStyle"):
            v = sty.get(f"{{{WML}}}val", "")
            if "Footnote" in v:
                sty.set(f"{{{WML}}}val", v.replace("Footnote", "Endnote"))
        for sty in en_elem.iter(f"{{{WML}}}pStyle"):
            v = sty.get(f"{{{WML}}}val", "")
            if "Footnote" in v:
                sty.set(f"{{{WML}}}val", v.replace("Footnote", "Endnote"))
        en_xml.append(en_elem)
        fn_xml.remove(fn_elem)
        moved += 1

# In document.xml: footnoteReference → endnoteReference
for fnref in doc_xml.iter(f"{{{WML}}}footnoteReference"):
    fnref.tag = f"{{{WML}}}endnoteReference"
for sty in doc_xml.iter(f"{{{WML}}}rStyle"):
    v = sty.get(f"{{{WML}}}val", "")
    if "Footnote" in v:
        sty.set(f"{{{WML}}}val", v.replace("Footnote", "Endnote"))

print(f"Fix 3: moved {moved} footnotes → endnotes")

# Update file contents
files["word/document.xml"] = ET.tostring(doc_xml, xml_declaration=True, encoding="UTF-8")
files["word/footnotes.xml"] = ET.tostring(fn_xml, xml_declaration=True, encoding="UTF-8")
files["word/endnotes.xml"] = ET.tostring(en_xml, xml_declaration=True, encoding="UTF-8")

# Ensure endnotes.xml in [Content_Types].xml
ct_xml = ET.fromstring(files["[Content_Types].xml"])
if not any(e.get("PartName") == "/word/endnotes.xml" for e in ct_xml):
    ov = ET.SubElement(ct_xml, "Override")
    ov.set("PartName", "/word/endnotes.xml")
    ov.set("ContentType",
           "application/vnd.openxmlformats-officedocument.wordprocessingml.endnotes+xml")
files["[Content_Types].xml"] = ET.tostring(ct_xml, xml_declaration=True, encoding="UTF-8")

# Ensure endnotes relationship in document.xml.rels
rels_key = "word/_rels/document.xml.rels"
if rels_key in files:
    rels_xml = ET.fromstring(files[rels_key])
    if not any(r.get("Target") == "endnotes.xml" for r in rels_xml):
        existing = {r.get("Id") for r in rels_xml}
        n = 1
        while f"rId{n}" in existing:
            n += 1
        new_rel = ET.SubElement(rels_xml, "Relationship")
        new_rel.set("Id", f"rId{n}")
        new_rel.set("Type",
                     "http://schemas.openxmlformats.org/officeDocument/2006/relationships/endnotes")
        new_rel.set("Target", "endnotes.xml")
    files[rels_key] = ET.tostring(rels_xml, xml_declaration=True, encoding="UTF-8")

# Write final zip
all_names = set(names) | {"word/endnotes.xml"}
with zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for name in all_names:
        if name in files:
            zout.writestr(name, files[name])

print(f"Fix 3 done: endnotes in {DST}")
print("\nAll fixes applied.")
