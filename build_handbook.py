"""Fill the SRMIST Project Hand Book in place — preserve the original
hierarchy exactly, only fill values, remove the two extra blank student rows,
tidy fonts/spacing, and add page borders + page numbers."""

import os
import shutil
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

ROOT = "/Users/yashchauhan/Desktop/minor project"
SRC = os.path.join(ROOT, "Project Hand Book.docx")
OUT = os.path.join(ROOT, "output", "doc", "Project_Hand_Book_Filled.docx")

shutil.copyfile(SRC, OUT)
d = Document(OUT)


# ── Helpers ─────────────────────────────────────────────────────────────────
def set_cell_bg(cell, color_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    for el in tc_pr.findall(qn("w:shd")):
        tc_pr.remove(el)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color_hex)
    tc_pr.append(shd)


def set_row_min_height(row, twips):
    trPr = row._tr.get_or_add_trPr()
    for el in trPr.findall(qn("w:trHeight")):
        trPr.remove(el)
    h = OxmlElement("w:trHeight")
    h.set(qn("w:val"), str(twips))
    h.set(qn("w:hRule"), "atLeast")
    trPr.append(h)


def set_table_borders(table):
    tbl = table._tbl
    tblPr = tbl.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)
    for el in tblPr.findall(qn("w:tblBorders")):
        tblPr.remove(el)
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "6")
        b.set(qn("w:space"), "0")
        b.set(qn("w:color"), "000000")
        borders.append(b)
    tblPr.append(borders)


def remove_page_borders(section):
    sectPr = section._sectPr
    for el in sectPr.findall(qn("w:pgBorders")):
        sectPr.remove(el)


def insert_page_break_before(p):
    """Force the given paragraph to start on a new page."""
    pPr = p._p.find(qn("w:pPr"))
    if pPr is None:
        pPr = OxmlElement("w:pPr")
        p._p.insert(0, pPr)
    pbb = OxmlElement("w:pageBreakBefore")
    pPr.append(pbb)


def add_signature_line_before(p):
    """Insert a clean ruled line (bottom border) paragraph before `p` so the
    user can sign above the 'Signature of the Supervisor' label."""
    line_p_el = OxmlElement("w:p")
    pPr = OxmlElement("w:pPr")
    # right-align the line so it sits above the label
    jc = OxmlElement("w:jc")
    jc.set(qn("w:val"), "right")
    pPr.append(jc)
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "8")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "000000")
    pBdr.append(bottom)
    pPr.append(pBdr)
    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:before"), "360")
    spacing.set(qn("w:after"), "0")
    pPr.append(spacing)
    line_p_el.append(pPr)
    # add a fixed-width tab/space so the underline has length
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), "Times New Roman")
    rFonts.set(qn("w:hAnsi"), "Times New Roman")
    rPr.append(rFonts)
    r.append(rPr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = "                                                  "
    r.append(t)
    line_p_el.append(r)
    p._p.addprevious(line_p_el)


def center_section_horizontally(section):
    """Make table-row alignment centered so tables sit in the page middle."""
    pass


def add_page_number_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.text = ""
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    label = p.add_run("Page ")
    label.font.name = "Times New Roman"
    label.font.size = Pt(10)
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE   \\* MERGEFORMAT "
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    txt = OxmlElement("w:t")
    txt.text = "1"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    nr = p.add_run()
    nr.font.name = "Times New Roman"
    nr.font.size = Pt(10)
    rPr = nr._r
    rPr.append(fld_begin)
    rPr.append(instr)
    rPr.append(fld_sep)
    rPr.append(txt)
    rPr.append(fld_end)


def write_in_cell(cell, text, bold=False, size=11,
                  align=None, valign=WD_ALIGN_VERTICAL.CENTER):
    for p in list(cell.paragraphs):
        p._p.getparent().remove(p._p)
    p = cell.add_paragraph()
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(size)
    r.font.name = "Times New Roman"
    cell.vertical_alignment = valign


def append_in_cell(cell, text, bold=False, size=11,
                   align=None, bullet_marker=False):
    p = cell.add_paragraph()
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(("• " if bullet_marker else "") + text)
    r.bold = bold
    r.font.size = Pt(size)
    r.font.name = "Times New Roman"


def style_existing_paragraph(p, text, bold=False, size=11, italic=False,
                             align=None, space_before=4, space_after=4,
                             indent=None):
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    if indent is not None:
        p.paragraph_format.left_indent = Inches(indent)
    if text:
        r = p.add_run(text)
        r.bold = bold
        r.italic = italic
        r.font.size = Pt(size)
        r.font.name = "Times New Roman"


def take_paragraph_block(start_idx, n):
    """Return up to n contiguous paragraphs starting at start_idx, inserting
    new <w:p/> elements where necessary so we always have n paragraphs to
    write into. Returns a list of Paragraph objects."""
    paras = d.paragraphs
    out = [paras[start_idx]]
    cur = paras[start_idx]._p
    body = cur.getparent()
    # find existing following paragraphs (capped at next non-empty)
    available = 1
    for j in range(start_idx + 1, len(paras)):
        if paras[j].text.strip():
            break
        out.append(paras[j])
        available += 1
        if available >= n:
            break
    # if more needed, append fresh <w:p/> after the last collected paragraph
    last = out[-1]._p
    while len(out) < n:
        new_p = OxmlElement("w:p")
        last.addnext(new_p)
        out.append(Paragraph(new_p, paras[start_idx]._parent))
        last = new_p
    return out


def write_block(start_idx, lines):
    """Write `lines` (list of dicts: {text, bold, size, indent, align}) into
    contiguous paragraphs starting at start_idx. Removes any leftover empty
    paragraphs from the original block beyond what we needed."""
    paras = d.paragraphs
    # find next non-empty paragraph (boundary of the block)
    end = len(paras)
    for j in range(start_idx + 1, len(paras)):
        if paras[j].text.strip():
            end = j
            break
    # available = end - start_idx
    targets = take_paragraph_block(start_idx, len(lines))
    for tp, line in zip(targets, lines):
        style_existing_paragraph(
            tp,
            text=line.get("text", ""),
            bold=line.get("bold", False),
            italic=line.get("italic", False),
            size=line.get("size", 11),
            align=line.get("align"),
            space_before=line.get("space_before", 4),
            space_after=line.get("space_after", 4),
            indent=line.get("indent"),
        )
    # delete any *unused* empty paragraphs between the last written and the
    # next anchor; keep at most one trailing blank for breathing room.
    last_p_el = targets[-1]._p
    paras = d.paragraphs
    last_idx = next(i for i, p in enumerate(paras) if p._p is last_p_el)
    blanks_kept = 0
    j = last_idx + 1
    while j < len(d.paragraphs):
        cur = d.paragraphs[j]
        if cur.text.strip():
            break
        if blanks_kept < 1:
            blanks_kept += 1
            j += 1
            continue
        cur._p.getparent().remove(cur._p)


# ============================================================================
# 1) TABLE 0 — Project information / Supervision team
# ============================================================================
t0 = d.tables[0]
# row 0: Title — value goes in merged cells 2..4 (we write to cells[2])
write_in_cell(
    t0.rows[0].cells[2],
    "Digital Inclusion and Circular Economy Behavior in Indian States: "
    "A Digital Circularity Index and Explainable XGBoost Analysis",
    bold=True,
    align=WD_ALIGN_PARAGRAPH.LEFT,
)

# row 1: Project Site / Location
write_in_cell(
    t0.rows[1].cells[2],
    "SRM Institute of Science and Technology, Kattankulathur Campus, "
    "Tamil Nadu, India",
    align=WD_ALIGN_PARAGRAPH.LEFT,
)

# row 2: Name and address — already populated (Kattankulathur), normalise font
write_in_cell(
    t0.rows[2].cells[2],
    "SRM IST, Kattankulathur, Chengalpattu District – 603203 "
    "(in-house academic project)",
    align=WD_ALIGN_PARAGRAPH.LEFT,
)

# row 4: header row (Supervisor / Co-Supervisor / External Supervisor) — leave
# the original header text intact, only restyle font.
for ci in (1, 3, 4):
    cell = t0.rows[4].cells[ci]
    for p in cell.paragraphs:
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)
            r.bold = True

# Supervisor block (col 1)
write_in_cell(t0.rows[5].cells[1], "Dr. Suresh Kumar", bold=True,
              align=WD_ALIGN_PARAGRAPH.LEFT)
write_in_cell(t0.rows[6].cells[1], "Associate Professor",
              align=WD_ALIGN_PARAGRAPH.LEFT)
write_in_cell(t0.rows[7].cells[1], "Computational Intelligence",
              align=WD_ALIGN_PARAGRAPH.LEFT)
# row 8 col 1 — Campus already says 'Kattankulathur'; reformat
write_in_cell(t0.rows[8].cells[1], "Kattankulathur",
              align=WD_ALIGN_PARAGRAPH.LEFT)
write_in_cell(t0.rows[9].cells[1], "—",
              align=WD_ALIGN_PARAGRAPH.LEFT)
write_in_cell(t0.rows[10].cells[1], "sureshk5@srmist.edu.in",
              align=WD_ALIGN_PARAGRAPH.LEFT)

# Co-Supervisor (col 3) and External Supervisor (col 4) — '—'
for r_idx in (5, 6, 7, 8, 9, 10):
    write_in_cell(t0.rows[r_idx].cells[3], "—",
                  align=WD_ALIGN_PARAGRAPH.CENTER)
    write_in_cell(t0.rows[r_idx].cells[4], "—",
                  align=WD_ALIGN_PARAGRAPH.CENTER)

# Re-style the label cells so they match (left col)
label_cells_t0 = [
    (0, 0), (1, 0), (2, 0), (3, 0),
    (4, 0),  # blank field-name col next to header
    (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0),
]
for ri, ci in label_cells_t0:
    cell = t0.rows[ri].cells[ci]
    txt = cell.text.strip()
    if txt:
        write_in_cell(cell, txt, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT)
        set_cell_bg(cell, "F2F2F2")

# header cells styled grey
write_in_cell(t0.rows[3].cells[0], "Supervision Team", bold=True,
              align=WD_ALIGN_PARAGRAPH.CENTER, size=12)
set_cell_bg(t0.rows[3].cells[0], "E7E6E6")

# Light grey for supervisor/co-sup/external header row
for ci in (1, 3, 4):
    set_cell_bg(t0.rows[4].cells[ci], "E7E6E6")

# row min-heights
for row in t0.rows:
    set_row_min_height(row, 380)
set_table_borders(t0)


# ============================================================================
# 2) TABLE 1 — Student team (remove the two extra empty rows)
# ============================================================================
t1 = d.tables[1]

# Header row (row 0) — restyle, light grey
hdr_labels = ("Name of student", "Register Number", "Department",
              "Mobile Number", "Email ID")
for ci, lbl in enumerate(hdr_labels):
    write_in_cell(t1.rows[0].cells[ci], lbl, bold=True,
                  align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_bg(t1.rows[0].cells[ci], "E7E6E6")
set_row_min_height(t1.rows[0], 420)

students = [
    ("Yash Chauhan",      "RA2311026010170", "CINTEL", "—",
     "yash.vks.chauhan@gmail.com"),
    ("Shreya Srivastava", "RA2311026010186", "CINTEL", "—",
     "shreya@srmist.edu.in"),
]
for ri, row_vals in enumerate(students, start=1):
    for ci, val in enumerate(row_vals):
        align = (WD_ALIGN_PARAGRAPH.LEFT if ci in (0, 4)
                 else WD_ALIGN_PARAGRAPH.CENTER)
        write_in_cell(t1.rows[ri].cells[ci], val, align=align)
    set_row_min_height(t1.rows[ri], 460)

# Remove the two trailing empty student rows (originally rows 3 and 4)
tbl_el = t1._tbl
trs = tbl_el.findall(qn("w:tr"))
# Keep only first 3 rows: header + 2 students
for tr in trs[3:]:
    tbl_el.remove(tr)
set_table_borders(t1)


# ============================================================================
# 3) TABLE 2 — Degree/Program / Mission / Problem / Assumptions / Stakeholders
# ============================================================================
t2 = d.tables[2]

# Rows 0-2 — Degree/Programme metadata (just restyle)
prog_meta = [
    (0, "Degree / Programme", "B.Tech", "Specialisation",
     "Computer Science & Engineering"),
    (1, "Academic Year", "2025-2026 (Even)", "Semester", "6"),
    (2, "Course Code", "21CSP302L", "Course Title", "Minor Project"),
]
for ri, l1, v1, l2, v2 in prog_meta:
    write_in_cell(t2.rows[ri].cells[0], l1, bold=True,
                  align=WD_ALIGN_PARAGRAPH.LEFT)
    set_cell_bg(t2.rows[ri].cells[0], "F2F2F2")
    write_in_cell(t2.rows[ri].cells[1], v1, align=WD_ALIGN_PARAGRAPH.LEFT)
    write_in_cell(t2.rows[ri].cells[2], l2, bold=True,
                  align=WD_ALIGN_PARAGRAPH.LEFT)
    set_cell_bg(t2.rows[ri].cells[2], "F2F2F2")
    write_in_cell(t2.rows[ri].cells[3], v2, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_row_min_height(t2.rows[ri], 380)

# Row 3 — Mission Statement (header row, merged across)
write_in_cell(t2.rows[3].cells[0], "Mission Statement", bold=True, size=12,
              align=WD_ALIGN_PARAGRAPH.CENTER)
set_cell_bg(t2.rows[3].cells[0], "E7E6E6")
set_row_min_height(t2.rows[3], 380)

# Row 4 — Mission body
mission = (
    "To deliver a reproducible, evidence-driven study that quantifies the "
    "relationship between digital inclusion and circular-economy behavior "
    "across 16 Indian states by constructing a Digital Circularity Index "
    "(DCI) and validating it through classical statistics, leak-free machine "
    "learning, and SHAP-based explainability — so that policy decisions on "
    "Digital India and Swachh Bharat can be informed by a single, integrated "
    "analytical lens."
)
write_in_cell(t2.rows[4].cells[0], mission,
              align=WD_ALIGN_PARAGRAPH.JUSTIFY)
set_row_min_height(t2.rows[4], 1100)

# Row 5 — Problem / Product Description (header)
write_in_cell(t2.rows[5].cells[0], "Problem / Product Description",
              bold=True, size=12,
              align=WD_ALIGN_PARAGRAPH.CENTER)
set_cell_bg(t2.rows[5].cells[0], "E7E6E6")
set_row_min_height(t2.rows[5], 380)

# Rows 6..12 — Problem body. Original keeps 7 body rows. Use them:
# row 6 = paragraph 1, row 7 = paragraph 2, ...
problem_paragraphs = [
    "India is simultaneously expanding digital infrastructure (tele-density "
    "above 85%, UPI exceeding 14 billion monthly transactions) and pursuing "
    "circular-economy goals across 11 priority sectors under NITI Aayog's "
    "strategy. Yet research on these two agendas has stayed largely separate: "
    "Digital India studies focus on growth and financial inclusion, while CE "
    "studies focus on waste-management technology and Extended Producer "
    "Responsibility.",

    "There is no state-level composite that links digital access with "
    "circular-economy outcomes, and no defensible small-n analytical pipeline "
    "that pairs OLS with leak-free machine-learning validation. As a result, "
    "policy makers cannot say whether connectivity investment also functions "
    "as a sustainability investment — a question with direct implications for "
    "cross-ministry budget allocation.",

    "This project addresses that gap by integrating seven verified government "
    "data sources (TRAI, RBI, NITI Aayog, NPCI, CPCB, Census of India, and "
    "Dataful) into a 16-state dataset, constructing three composite indices "
    "(Digital Access Score, CE Behavior Score, Digital Circularity Index), "
    "and testing three hypotheses (H1 association, H2 UPI mediation, H3 "
    "tele-density threshold) using OLS, bootstrap, HC3, permutation, "
    "mediation, piecewise regression, seven-model LOO-CV, leak-free nested-CV "
    "XGBoost, SHAP explainability and K-Means clustering.",

    "Deliverables: a unified state-level dataset with full provenance, 22 "
    "publication-ready figures, an IEEE-format conference paper, a "
    "reproducible Python code base, and a defense-ready minor project report.",
]
# put each paragraph in successive body rows. Rows 6..(6+len-1) are body.
for offset, ptext in enumerate(problem_paragraphs):
    row_idx = 6 + offset
    write_in_cell(t2.rows[row_idx].cells[0], ptext,
                  align=WD_ALIGN_PARAGRAPH.JUSTIFY,
                  valign=WD_ALIGN_VERTICAL.TOP)
    set_row_min_height(t2.rows[row_idx], 700)

# Any leftover body rows (rows 6+len .. 12) — collapse into one filler row
# (keep them but mark as blank with single non-breaking space to avoid empty
# look). Easier: set their min height small and blank text.
for offset in range(len(problem_paragraphs), 7):
    row_idx = 6 + offset
    write_in_cell(t2.rows[row_idx].cells[0], "",
                  align=WD_ALIGN_PARAGRAPH.LEFT)
    set_row_min_height(t2.rows[row_idx], 80)

# Row 13 — Assumptions header
write_in_cell(t2.rows[13].cells[0], "Assumptions and Constraints",
              bold=True, size=12,
              align=WD_ALIGN_PARAGRAPH.CENTER)
set_cell_bg(t2.rows[13].cells[0], "E7E6E6")
set_row_min_height(t2.rows[13], 380)

# Row 14 — Assumptions body
assumptions = [
    ("A1", "Inner-join across the seven sources yields exactly 16 states "
            "with complete observations; no imputation is performed."),
    ("A2", "Min–max normalisation to [0, 100] and the documented weight "
            "schemes (DAS 40/30/30, CEBS 35/40/25) are appropriate for a "
            "transparent composite-index construction."),
    ("A3", "Cross-sectional state-level data supports correlational "
            "inference (H1) but not causal claims; mediation (H2) and "
            "threshold (H3) results are interpreted with that limit in mind."),
    ("C1", "n = 16 is small — every model is validated under LOO-CV or "
            "nested LOO-CV, and reviewer-defense statistics (HC3, bootstrap "
            "10k, permutation 10k) are mandatory."),
    ("C2", "Census 2011 is the most recent available source for literacy "
            "and urbanisation; downstream interpretation accounts for this lag."),
    ("C3", "Reproducibility requires fixed random seeds (seed = 42) and "
            "saved intermediate CSVs at every pipeline boundary."),
]
cell = t2.rows[14].cells[0]
for p in list(cell.paragraphs):
    p._p.getparent().remove(p._p)
for idx, (rid, stmt) in enumerate(assumptions):
    p = cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(4)
    bold_run = p.add_run(rid + ".  ")
    bold_run.bold = True
    bold_run.font.size = Pt(11)
    bold_run.font.name = "Times New Roman"
    body_run = p.add_run(stmt)
    body_run.font.size = Pt(11)
    body_run.font.name = "Times New Roman"
cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
set_row_min_height(t2.rows[14], 1800)

# Row 15 — Stakeholders header
write_in_cell(t2.rows[15].cells[0], "Stakeholders", bold=True, size=12,
              align=WD_ALIGN_PARAGRAPH.CENTER)
set_cell_bg(t2.rows[15].cells[0], "E7E6E6")
set_row_min_height(t2.rows[15], 380)

# Row 16 — Stakeholders body
stakeholders = [
    ("Primary",
     "Project supervisor (Dr. Suresh Kumar) and the Department of "
     "Computational Intelligence, SRMIST."),
    ("Academic",
     "Project Review Committee, IEEE conference reviewers, and peer "
     "researchers in ICT4D and circular-economy analytics."),
    ("Policy",
     "NITI Aayog (SDG India Index team), Ministry of Electronics & IT "
     "(Digital India), Ministry of Environment (Swachh Bharat / EPR), and "
     "state planning departments."),
    ("Data Providers",
     "TRAI, RBI, NPCI, CPCB, Census of India, NITI Aayog and Dataful — "
     "whose published datasets feed the unified state-level table."),
    ("End Users",
     "Policy analysts and researchers using the DCI as a diagnostic tool "
     "for cross-ministry planning."),
]
cell = t2.rows[16].cells[0]
for p in list(cell.paragraphs):
    p._p.getparent().remove(p._p)
for grp, desc in stakeholders:
    p = cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(4)
    g = p.add_run(grp + " — ")
    g.bold = True
    g.font.size = Pt(11)
    g.font.name = "Times New Roman"
    b = p.add_run(desc)
    b.font.size = Pt(11)
    b.font.name = "Times New Roman"
cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
set_row_min_height(t2.rows[16], 1500)

set_table_borders(t2)


# ============================================================================
# 4) BODY PARAGRAPHS — SPRINTS / WORKSHEET / RESEARCH ARTICLE
#    Preserve the original section headers exactly. Just write content into
#    the empty paragraphs that follow each header, and tidy fonts/spacing.
# ============================================================================

def find_paragraph_index(needle):
    """Return the first paragraph index whose text contains `needle`."""
    for i, p in enumerate(d.paragraphs):
        if needle in p.text:
            return i
    raise ValueError(f"Header not found: {needle}")


def fill_section(header_idx, lines):
    """Re-style the existing header paragraph at `header_idx`, then fill the
    empty paragraphs that follow it with `lines` (list of dicts).

    Each dict: text, bold, italic, size, indent, align, space_before, space_after.
    Empty paragraphs trailing the block are removed; one trailing blank is
    kept for breathing room before the next header (or 'Signature of the
    Supervisor')."""
    # 1) restyle the existing header — make it bold, centered, slightly larger
    header_p = d.paragraphs[header_idx]
    header_text = header_p.text.strip()
    style_existing_paragraph(
        header_p, text=header_text, bold=True, size=14,
        align=WD_ALIGN_PARAGRAPH.LEFT,
        space_before=12, space_after=8,
    )
    # 2) fill the body
    paras = d.paragraphs
    end = len(paras)
    for j in range(header_idx + 1, len(paras)):
        if paras[j].text.strip():
            end = j
            break
    targets = take_paragraph_block(header_idx + 1, len(lines))
    for tp, line in zip(targets, lines):
        style_existing_paragraph(
            tp,
            text=line.get("text", ""),
            bold=line.get("bold", False),
            italic=line.get("italic", False),
            size=line.get("size", 11),
            align=line.get("align", WD_ALIGN_PARAGRAPH.JUSTIFY),
            space_before=line.get("space_before", 2),
            space_after=line.get("space_after", 4),
            indent=line.get("indent"),
        )
    # 3) collapse trailing blanks beyond the last written paragraph, except
    #    keep up to TWO blanks for spacing before the next non-empty paragraph.
    last_p_el = targets[-1]._p
    paras = d.paragraphs
    last_idx = next(i for i, p in enumerate(paras) if p._p is last_p_el)
    j = last_idx + 1
    blanks_kept = 0
    while j < len(d.paragraphs):
        cur = d.paragraphs[j]
        if cur.text.strip():
            break
        if blanks_kept < 2:
            blanks_kept += 1
            j += 1
            continue
        cur._p.getparent().remove(cur._p)


def sprint_lines(num, title, duration, goal,
                 yash_tasks, shreya_tasks, scrum):
    """Build a cohesive list of paragraph specs for one sprint section."""
    lines = []
    lines.append({"text": f"Sprint {num} — {title}", "bold": True,
                  "size": 13, "align": WD_ALIGN_PARAGRAPH.LEFT,
                  "space_before": 4, "space_after": 6})
    lines.append({"text": f"Duration: {duration}", "bold": True,
                  "align": WD_ALIGN_PARAGRAPH.LEFT,
                  "space_after": 2})
    lines.append({"text": f"Sprint Goal: {goal}",
                  "align": WD_ALIGN_PARAGRAPH.JUSTIFY,
                  "space_after": 8})

    lines.append({"text": "Yash Chauhan (RA2311026010170) — Contributions",
                  "bold": True, "size": 12,
                  "align": WD_ALIGN_PARAGRAPH.LEFT,
                  "space_before": 4, "space_after": 4})
    for t in yash_tasks:
        lines.append({"text": "•  " + t,
                      "indent": 0.25,
                      "align": WD_ALIGN_PARAGRAPH.JUSTIFY,
                      "space_after": 2})

    lines.append({"text": "Shreya Srivastava (RA2311026010186) — Contributions",
                  "bold": True, "size": 12,
                  "align": WD_ALIGN_PARAGRAPH.LEFT,
                  "space_before": 8, "space_after": 4})
    for t in shreya_tasks:
        lines.append({"text": "•  " + t,
                      "indent": 0.25,
                      "align": WD_ALIGN_PARAGRAPH.JUSTIFY,
                      "space_after": 2})

    lines.append({"text": f"Daily Scrum Highlights — Sprint {num}",
                  "bold": True, "size": 12,
                  "align": WD_ALIGN_PARAGRAPH.LEFT,
                  "space_before": 8, "space_after": 4})
    for date_, msg in scrum:
        lines.append({"text": f"•  {date_} — {msg}",
                      "indent": 0.25,
                      "align": WD_ALIGN_PARAGRAPH.JUSTIFY,
                      "space_after": 2})
    return lines


# Sprint 1 ---------------------------------------------------------------
s1_idx = find_paragraph_index("Division of work and contributors of SPRINT 1")
fill_section(
    s1_idx,
    sprint_lines(
        num=1,
        title="Data Engineering, EDA & Statistical Validation",
        duration="01 February 2026 – 21 February 2026 (3 weeks)",
        goal="Build a verified 16-state dataset, compute the DAS / CEBS / DCI "
             "composite indices, generate publication-grade EDA, and produce "
             "a defense-ready statistical test of H1, H2 and H3.",
        yash_tasks=[
            "Source ingestion from TRAI, RBI, NITI Aayog and NPCI "
            "(01_data_engineering.py).",
            "Inner-join merge on the State key; min–max normalisation; "
            "construction of DAS, CEBS and DCI columns.",
            "OLS regression of CEBS on DAS with full diagnostics — "
            "Breusch-Pagan, Durbin-Watson, Cook's distance.",
            "Robustness battery: HC3 robust standard errors, bootstrap CIs "
            "(10,000 resamples) and permutation test (10,000 resamples).",
        ],
        shreya_tasks=[
            "Source ingestion from CPCB, Census of India and Dataful; "
            "data-quality QA and provenance logging.",
            "EDA figures fig1–fig8: correlation heatmap, DAS-vs-CEBS scatter, "
            "DCI ranking, distributions, boxplots, UPI trends, regression "
            "panels and UPI-vs-SDG.",
            "Mediation analysis (Baron & Kenny, Sobel) and piecewise "
            "threshold regression for H2 / H3.",
            "Weight-sensitivity analysis across seven alternative DAS "
            "schemes; extended-sample (n = 21) validation.",
        ],
        scrum=[
            ("03 Feb",
             "Inner-join produces 16 clean states with 0 missing values; "
             "DAS, CEBS and DCI columns committed."),
            ("09 Feb",
             "Primary OLS confirmed — r = 0.781, R² = 0.610, p < 0.001."),
            ("14 Feb",
             "HC3 p = 1.1×10⁻⁵ and bootstrap 95% CI [0.648, 0.979] both "
             "exclude 0."),
            ("18 Feb",
             "Mediation Sobel z = −0.241 (no UPI mediation); piecewise "
             "breakpoint located at 118.77% tele-density."),
            ("21 Feb",
             "Sprint 1 retrospective committed; data and statistical "
             "artifacts handed off to Sprint 2."),
        ],
    ),
)


# Sprint 2 ---------------------------------------------------------------
s2_idx = find_paragraph_index("Division of work and contributors of SPRINT 2")
fill_section(
    s2_idx,
    sprint_lines(
        num=2,
        title="Machine Learning, Explainability & Clustering",
        duration="22 February 2026 – 08 March 2026 (~2.5 weeks)",
        goal="Confirm the OLS signal using out-of-sample machine learning, "
             "quantify feature importance through SHAP, and uncover state "
             "typologies with K-Means clustering.",
        yash_tasks=[
            "Seven-model LOO-CV harness — Linear, Ridge, Lasso, ElasticNet, "
            "SVR, Random Forest and Gradient Boosting — on digital-only and "
            "full feature sets.",
            "Leak-free nested LOO-CV wrapper for XGBoost — outer LOO with "
            "inner 4-fold GridSearchCV.",
            "Repeated K-Fold cross-validation stability check across "
            "100 × 4 = 400 splits.",
        ],
        shreya_tasks=[
            "SHAP global and per-state explanations — beeswarm, bar and "
            "waterfall plots for all 16 states (focus on Haryana and Bihar).",
            "K-Means clustering with silhouette-selected k = 2; PCA(2) biplot "
            "for geometric interpretation.",
            "Cluster profile table separating Digital Leaders from Emerging "
            "States.",
        ],
        scrum=[
            ("24 Feb",
             "Lasso full-model LOO-CV R² = 0.568; ElasticNet digital-only "
             "R² = 0.364."),
            ("28 Feb",
             "Nested-CV XGBoost reaches R² = 0.511, p = 0.002 (leak-free)."),
            ("02 Mar",
             "SHAP global ranks tele-density (5.01) and Per-Capita NSDP "
             "(4.88) as the top two drivers."),
            ("05 Mar",
             "K-Means k = 2 yields a 2.5× DCI gap — Digital Leaders 46.7 "
             "vs. Emerging States 18.3."),
            ("08 Mar",
             "Sprint 2 retrospective; ML and clustering outputs handed to "
             "the writing track."),
        ],
    ),
)


# Sprint 3 ---------------------------------------------------------------
s3_idx = find_paragraph_index("Division of work and contributors of SPRINT 3")
fill_section(
    s3_idx,
    sprint_lines(
        num=3,
        title="Documentation, Paper Submission & Review Defense",
        duration="09 March 2026 – 25 April 2026 (~6 weeks)",
        goal="Compile the IEEE-format conference paper, finalise the minor "
             "project report, and prepare reviewer-defense materials.",
        yash_tasks=[
            "IEEE conference paper draft — Abstract, Introduction, Methods, "
            "Results, Discussion, Conclusion — with a full IEEE-style "
            "reference list.",
            "Final minor project report with seven chapters, table of "
            "contents, list of figures, list of tables and abbreviations index.",
            "Reproducibility audit — fixed seeds, saved CSV outputs at every "
            "pipeline boundary, README with run instructions.",
        ],
        shreya_tasks=[
            "22 publication-ready figures at 300 DPI; figure captions "
            "cross-checked against the corresponding results files.",
            "Reviewer-defense Q&A — small-n justification, multicollinearity "
            "(VIF), HC3 vs. OLS, nested-CV vs. flat CV.",
            "Policy-implications section drawing on SHAP and clustering — "
            "Digital Leaders vs. Emerging States playbooks.",
        ],
        scrum=[
            ("14 Mar", "Paper Sections 1–3 drafted; figures 1–12 finalised."),
            ("22 Mar", "Paper Sections 4–6 drafted; nested-CV table and SHAP "
                       "plots embedded."),
            ("02 Apr", "Internal review pass on the paper; minor report TOC, "
                       "List of Figures and List of Tables generated."),
            ("17 Apr", "Final report ready — page borders, page numbers, "
                       "black-and-white tables and the architecture diagram added."),
            ("25 Apr", "Handbook compiled, sprint retrospectives archived, "
                       "submission packet ready."),
        ],
    ),
)


# Restyle the three "Signature of the Supervisor" lines + ensure spacing
for i, p in enumerate(d.paragraphs):
    if p.text.strip() == "Signature of the Supervisor":
        style_existing_paragraph(
            p, text="Signature of the Supervisor", bold=True, size=11,
            align=WD_ALIGN_PARAGRAPH.RIGHT,
            space_before=24, space_after=24,
        )


# ── Worksheet / Data Collection / Observations ─────────────────────────────
ws_idx = find_paragraph_index("Worksheet / Data collection")
ws_lines = [
    {"text": "A. Verified Primary Data Sources",
     "bold": True, "size": 12, "space_before": 4, "space_after": 4,
     "align": WD_ALIGN_PARAGRAPH.LEFT},
    {"text": "•  TRAI (2024) — Tele-density (%) per state, Quarterly Indicator Report.",
     "indent": 0.25},
    {"text": "•  RBI (2024–25) — Per-Capita NSDP (INR), Handbook of Statistics, Table 9.",
     "indent": 0.25},
    {"text": "•  NITI Aayog (2023–24) — SDG India Index Score per state.",
     "indent": 0.25},
    {"text": "•  NPCI / Dataful (2024–25) — UPI per-capita transactions, monthly product statistics.",
     "indent": 0.25},
    {"text": "•  CPCB (2021–22) — E-waste processed (tonnes), Annual e-waste report.",
     "indent": 0.25},
    {"text": "•  Census of India (2011) — Literacy rate (%) and Urban population (%), Primary Census Abstract.",
     "indent": 0.25},

    {"text": "B. Primary Outputs of Data Collection",
     "bold": True, "size": 12, "space_before": 8, "space_after": 4,
     "align": WD_ALIGN_PARAGRAPH.LEFT},
    {"text": "•  /data/trai_state_data_final_v2.csv — unified 16-state × 15-variable table with explicit provenance columns.",
     "indent": 0.25},
    {"text": "•  /results/ — OLS, robustness, mediation, piecewise, LOO-CV, nested-CV, SHAP and clustering result files.",
     "indent": 0.25},
    {"text": "•  /figures/ fig1–fig22 — 22 publication-ready figures rendered at 300 DPI.",
     "indent": 0.25},

    {"text": "C. Descriptive Statistics (n = 16)",
     "bold": True, "size": 12, "space_before": 8, "space_after": 4,
     "align": WD_ALIGN_PARAGRAPH.LEFT},
    {"text": "•  DAS — Mean 64.95, Std. Dev. 19.69, Range 30.27 to 94.40, Median 67.02.",
     "indent": 0.25},
    {"text": "•  CEBS — Mean 46.98, Std. Dev. 13.90, Range 27.23 to 87.30, Median 47.78.",
     "indent": 0.25},
    {"text": "•  DCI — Mean 32.52, Std. Dev. 17.40, Range 8.24 (Bihar) to 72.97 (Haryana).",
     "indent": 0.25},

    {"text": "D. Headline Observations",
     "bold": True, "size": 12, "space_before": 8, "space_after": 4,
     "align": WD_ALIGN_PARAGRAPH.LEFT},
    {"text": "•  Pearson r(DAS, CEBS) = 0.781, p < 0.001 — strong positive association.",
     "indent": 0.25},
    {"text": "•  OLS R² = 0.610; HC3 robust p = 1.1×10⁻⁵; bootstrap 95% CI for r = [0.648, 0.979].",
     "indent": 0.25},
    {"text": "•  Tele-density tops SHAP global importance (mean |φ| = 5.01); UPI ranks last (0.91), "
              "consistent with the non-significant Sobel mediation (z = −0.241).",
     "indent": 0.25},
    {"text": "•  K-Means k = 2 separates Digital Leaders (DCI 46.7) from Emerging States (DCI 18.3) — a 2.5× gap.",
     "indent": 0.25},
]
fill_section(ws_idx, ws_lines)


# ── Research Article / Publication Details ─────────────────────────────────
ra_idx = find_paragraph_index("Research Article")
# also restyle the "(include certificates and proofs)" paragraph that sits
# right after the header in the original.
ra_lines = [
    {"text": "(includes certificates and proofs)", "italic": True,
     "align": WD_ALIGN_PARAGRAPH.LEFT,
     "space_before": 2, "space_after": 8},
    {"text": "Title: ", "bold": True,
     "align": WD_ALIGN_PARAGRAPH.LEFT, "space_after": 0},
    {"text": "Digital Inclusion and Circular Economy Behavior in Indian States: "
              "A Digital Circularity Index and Explainable XGBoost Analysis.",
     "align": WD_ALIGN_PARAGRAPH.JUSTIFY, "indent": 0.25, "space_after": 6},

    {"text": "Authors: ", "bold": True,
     "align": WD_ALIGN_PARAGRAPH.LEFT, "space_after": 0},
    {"text": "Yash Chauhan (RA2311026010170), Shreya Srivastava "
              "(RA2311026010186); Supervisor — Dr. Suresh Kumar.",
     "align": WD_ALIGN_PARAGRAPH.JUSTIFY, "indent": 0.25, "space_after": 6},

    {"text": "Affiliation: ", "bold": True,
     "align": WD_ALIGN_PARAGRAPH.LEFT, "space_after": 0},
    {"text": "Department of Computational Intelligence, SRM Institute of "
              "Science and Technology, Kattankulathur, Tamil Nadu, India.",
     "align": WD_ALIGN_PARAGRAPH.JUSTIFY, "indent": 0.25, "space_after": 6},

    {"text": "Target Venue: ", "bold": True,
     "align": WD_ALIGN_PARAGRAPH.LEFT, "space_after": 0},
    {"text": "IEEE conference (paper formatted to the IEEE conference template).",
     "align": WD_ALIGN_PARAGRAPH.JUSTIFY, "indent": 0.25, "space_after": 6},

    {"text": "Status: ", "bold": True,
     "align": WD_ALIGN_PARAGRAPH.LEFT, "space_after": 0},
    {"text": "Manuscript drafted; figures 1–22 embedded; reference list "
              "complete; submission package prepared (paper24.pdf, paper24.tex).",
     "align": WD_ALIGN_PARAGRAPH.JUSTIFY, "indent": 0.25, "space_after": 6},

    {"text": "Patent Disclosure: ", "bold": True,
     "align": WD_ALIGN_PARAGRAPH.LEFT, "space_after": 0},
    {"text": "Not applicable.",
     "align": WD_ALIGN_PARAGRAPH.JUSTIFY, "indent": 0.25, "space_after": 6},

    {"text": "Supporting Artifacts: ", "bold": True,
     "align": WD_ALIGN_PARAGRAPH.LEFT, "space_after": 0},
    {"text": "Defense-ready minor project report, reproducible Python code "
              "base, and certificates / proofs attached separately.",
     "align": WD_ALIGN_PARAGRAPH.JUSTIFY, "indent": 0.25, "space_after": 6},
]
fill_section(ra_idx, ra_lines)


# Restyle the standalone "(include certificates and proofs)" paragraph if it
# still exists as a separate entry — fold it into the header section by
# removing duplication.
for p in list(d.paragraphs):
    if p.text.strip() == "(include certificates and proofs)":
        p._p.getparent().remove(p._p)
        break


# ── Apply consistent base font to all body paragraphs (Times New Roman 11) ──
for p in d.paragraphs:
    for r in p.runs:
        if not r.font.name:
            r.font.name = "Times New Roman"
        if not r.font.size:
            r.font.size = Pt(11)


# ── Centre table contents on every page ────────────────────────────────────
def centre_all_table_text(table):
    """Shift cell text alignment to centred so the tables read symmetric on
    the page, except for body cells of the Mission / Problem / Assumptions /
    Stakeholders block which keep justified prose."""
    for row in table.rows:
        seen = set()
        for cell in row.cells:
            if id(cell._tc) in seen:
                continue
            seen.add(id(cell._tc))
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for p in cell.paragraphs:
                # leave paragraphs containing long prose (>140 chars) justified
                if len(p.text) > 140:
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


for tbl in d.tables:
    centre_all_table_text(tbl)
    tbl.alignment = 1  # WD_TABLE_ALIGNMENT.CENTER


# ── Drop the gap between Title-block and Student/Mission tables ────────────
# Reduce paragraph spacing on every empty paragraph that sits *between* the
# three top tables.
body = d.element.body
seen_first_table = False
for el in body.iterchildren():
    tag = el.tag.split("}")[-1]
    if tag == "tbl":
        seen_first_table = True
        continue
    if tag == "p" and seen_first_table:
        text = "".join((t.text or "") for t in el.iter(qn("w:t"))).strip()
        if text:
            break  # reached non-empty body paragraph after the tables
        # collapse the empty paragraph to a tiny strip so the tables hug
        pPr = el.find(qn("w:pPr"))
        if pPr is None:
            pPr = OxmlElement("w:pPr")
            el.insert(0, pPr)
        # remove any prior spacing
        for sp in pPr.findall(qn("w:spacing")):
            pPr.remove(sp)
        spacing = OxmlElement("w:spacing")
        spacing.set(qn("w:before"), "0")
        spacing.set(qn("w:after"), "60")
        spacing.set(qn("w:line"), "240")
        spacing.set(qn("w:lineRule"), "auto")
        pPr.append(spacing)


# ── Add a signature line ABOVE each "Signature of the Supervisor" ──────────
for p in list(d.paragraphs):
    if p.text.strip() == "Signature of the Supervisor":
        # right-align the label
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for r in p.runs:
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)
        # insert a ruled line just before it
        add_signature_line_before(p)


# ── Force each Sprint section to begin on its own page ─────────────────────
for needle in (
    "Division of work and contributors of SPRINT 1",
    "Division of work and contributors of SPRINT 2",
    "Division of work and contributors of SPRINT 3",
    "Worksheet / Data collection / Observation",
    "Research Article with Journal Publication Details",
):
    for p in d.paragraphs:
        if needle in p.text:
            insert_page_break_before(p)
            break


# ── Insert SRMIST logo at the top-right of the first page ──────────────────
SRM_LOGO = os.path.join(ROOT, "srm_logo.png")
if os.path.exists(SRM_LOGO):
    # create the paragraph through python-docx so the image relation is wired
    logo_para = d.add_paragraph()
    logo_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    logo_para.paragraph_format.space_before = Pt(0)
    logo_para.paragraph_format.space_after = Pt(2)
    logo_para.add_run().add_picture(SRM_LOGO, width=Inches(1.1))
    # then move that paragraph element to the top of the body
    body = d.element.body
    body.remove(logo_para._p)
    body.insert(0, logo_para._p)


# ── Margins, page numbers, NO page borders ─────────────────────────────────
for section in d.sections:
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)
    remove_page_borders(section)
    add_page_number_footer(section)


d.save(OUT)
print(f"Saved: {OUT}")
print(f"Size: {os.path.getsize(OUT):,} bytes")
