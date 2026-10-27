"""Generate clean Minor Project Word report from paper.tex and result artifacts."""

import os
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = "/Users/yashchauhan/Desktop/minor project"
FIG = os.path.join(ROOT, "figures")
OUT = os.path.join(ROOT, "output", "doc", "Minor_Project_Report_Final.docx")
SRM_LOGO = os.path.join(ROOT, "srm_logo.png")
ARCH_DIAGRAM = os.path.join(ROOT, "diagram_02_component.png")
DATA_FLOW_DIAGRAM = os.path.join(ROOT, "diagram_01_data_flow.png")

doc = Document()

# ── Page & base style ───────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.18)
    section.right_margin = Cm(2.54)

base = doc.styles["Normal"]
base.font.name = "Times New Roman"
base.font.size = Pt(12)
base.paragraph_format.line_spacing = 1.5
base.paragraph_format.space_after = Pt(6)

for h, sz in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 12), ("Heading 4", 12)):
    s = doc.styles[h]
    s.font.name = "Times New Roman"
    s.font.size = Pt(sz)
    s.font.bold = True
    s.font.color.rgb = RGBColor(0, 0, 0)
    s.paragraph_format.space_before = Pt(12)
    s.paragraph_format.space_after = Pt(6)
    s.paragraph_format.page_break_before = False
    s.paragraph_format.keep_with_next = True


def set_cell_bg(cell, color_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color_hex)
    tc_pr.append(shd)


def add_page_break():
    doc.add_page_break()


def add_page_borders(section):
    """Add a black 1/2 pt border on all four sides of every page in this section."""
    sectPr = section._sectPr
    # remove existing pgBorders if present
    for el in sectPr.findall(qn("w:pgBorders")):
        sectPr.remove(el)
    pg_borders = OxmlElement("w:pgBorders")
    pg_borders.set(qn("w:offsetFrom"), "page")
    pg_borders.set(qn("w:display"), "allPages")
    pg_borders.set(qn("w:zOrder"), "front")
    for side in ("top", "left", "bottom", "right"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "12")          # 1.5 pt
        b.set(qn("w:space"), "24")
        b.set(qn("w:color"), "000000")
        pg_borders.append(b)
    sectPr.append(pg_borders)


def add_page_number_footer(section):
    """Insert 'Page X' centered in the footer using a PAGE field."""
    footer = section.footer
    # clear any existing paragraphs (footer always has at least one)
    p = footer.paragraphs[0]
    p.text = ""
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Page ")
    run.font.name = "Times New Roman"
    run.font.size = Pt(10)

    # field for PAGE
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

    new_run = p.add_run()
    new_run.font.name = "Times New Roman"
    new_run.font.size = Pt(10)
    rPr = new_run._r
    rPr.append(fld_begin)
    rPr.append(instr)
    rPr.append(fld_sep)
    rPr.append(txt)
    rPr.append(fld_end)


def set_table_borders(table, color="000000", sz="6"):
    """Apply solid black borders to all sides of every cell in a table."""
    tbl = table._tbl
    tblPr = tbl.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)
    # remove existing tblBorders
    for el in tblPr.findall(qn("w:tblBorders")):
        tblPr.remove(el)
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), sz)
        b.set(qn("w:space"), "0")
        b.set(qn("w:color"), color)
        borders.append(b)
    tblPr.append(borders)


def heading(text, level=1):
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.name = "Times New Roman"
    return p


def para(text, bold=False, italic=False, align=None, size=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    if size:
        run.font.size = Pt(size)
    if align is not None:
        p.alignment = align
    return p


def bullet(text, style="List Bullet"):
    p = doc.add_paragraph(text, style=style)
    return p


def numbered(text):
    return doc.add_paragraph(text, style="List Number")


def make_table(headers, rows, widths=None, header_bg="E7E6E6"):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(0, 0, 0)
        set_cell_bg(hdr[i], header_bg)
        hdr[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    for ri, row in enumerate(rows, start=1):
        cells = t.rows[ri].cells
        for ci, val in enumerate(row):
            cells[ci].text = ""
            p = cells[ci].paragraphs[0]
            r = p.add_run(str(val))
            r.font.size = Pt(11)
            r.font.color.rgb = RGBColor(0, 0, 0)
            cells[ci].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    if widths:
        for row in t.rows:
            for ci, w in enumerate(widths):
                row.cells[ci].width = w
    set_table_borders(t)
    # spacing after table
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(6)
    return t


def add_figure(path, caption, width_in=5.8):
    if not os.path.exists(path):
        para(f"[Figure missing: {os.path.basename(path)}]", italic=True,
             align=WD_ALIGN_PARAGRAPH.CENTER)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    run.add_picture(path, width=Inches(width_in))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(14)
    cap.paragraph_format.keep_with_next = False
    r = cap.add_run(caption)
    r.italic = True
    r.font.size = Pt(11)


# ============================================================================
# COVER PAGE
# ============================================================================
# SRMIST logo at the top
if os.path.exists(SRM_LOGO):
    logo_p = doc.add_paragraph()
    logo_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    logo_p.paragraph_format.space_before = Pt(0)
    logo_p.paragraph_format.space_after = Pt(6)
    logo_run = logo_p.add_run()
    logo_run.add_picture(SRM_LOGO, width=Inches(1.7))

inst_p = doc.add_paragraph()
inst_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = inst_p.add_run("SRM INSTITUTE OF SCIENCE AND TECHNOLOGY")
r.bold = True
r.font.size = Pt(14)
r.font.name = "Times New Roman"

inst_sub = doc.add_paragraph()
inst_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = inst_sub.add_run("Kattankulathur, Tamil Nadu, India")
r.font.size = Pt(11)

doc.add_paragraph()

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run("MINOR PROJECT REPORT")
r.bold = True
r.font.size = Pt(22)
r.font.name = "Times New Roman"

doc.add_paragraph()

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub.add_run("Digital Inclusion and Circular Economy Behavior in Indian States:\n"
                "A Digital Circularity Index and Explainable XGBoost Analysis")
r.bold = True
r.font.size = Pt(16)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Submitted by")
r.font.size = Pt(12)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Yash Chauhan  •  Shreya Srivastava")
r.bold = True
r.font.size = Pt(14)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Under the guidance of")
r.font.size = Pt(12)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Prof. Suresh Kumar")
r.bold = True
r.font.size = Pt(13)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Department of Computational Intelligence\n"
              "SRM Institute of Science and Technology\n"
              "Kattankulathur, Tamil Nadu, India")
r.bold = True
r.font.size = Pt(12)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("April 2026")
r.bold = True
r.font.size = Pt(12)

add_page_break()

# ============================================================================
# ABSTRACT (page v)
# ============================================================================
heading("ABSTRACT", level=1)
para(
    "India is simultaneously expanding digital infrastructure and pursuing circular "
    "economy (CE) goals, yet the relationship between these two agendas remains "
    "underexplored at the state level. This study integrates seven official government "
    "data sources to construct a Digital Circularity Index (DCI) for 16 Indian states. "
    "The analysis combines Ordinary Least Squares (OLS) regression, robustness testing, "
    "mediation analysis, threshold analysis, leak-free nested cross-validation, "
    "SHAP-based explainability, and K-Means clustering.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
para(
    "Across every method tried, states with stronger digital access consistently show "
    "better circular economy outcomes. The OLS model yields r = 0.781 (p < 0.001, "
    "R² = 0.610), and the leak-free nested-CV XGBoost still reaches R² = 0.511. The "
    "association survives non-parametric and permutation-based checks, while "
    "tele-density emerges as a stronger driver than digital payments. K-Means clustering "
    "separates the 16 states into two distinct typologies — Digital Leaders and "
    "Emerging States — with a 2.5× DCI gap.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
para(
    "The findings suggest that digital inclusion and sustainability policy should be "
    "treated as interconnected agendas rather than separate tracks. The work contributes "
    "a reproducible state-level composite index, cross-method statistical and machine "
    "learning validation, and state-specific policy interpretation through SHAP and "
    "clustering.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

para("Keywords: Circular economy, Digital Circularity Index (DCI), Digital inclusion, "
     "XGBoost, SHAP, Policy analytics, India.",
     italic=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

add_page_break()

# ============================================================================
# TABLE OF CONTENTS
# ============================================================================
heading("TABLE OF CONTENTS", level=1)

toc_rows = [
    ("ABSTRACT", "", "v"),
    ("TABLE OF CONTENTS", "", "vi"),
    ("LIST OF FIGURES", "", "vii"),
    ("LIST OF TABLES", "", "viii"),
    ("ABBREVIATIONS", "", "ix"),
    ("CHAPTER 1", "INTRODUCTION", "1"),
    ("", "1.1  Introduction to Project", "2"),
    ("", "1.2  Problem Statement and Description", "3"),
    ("", "1.3  Motivation", "4"),
    ("", "1.4  Sustainable Development Goal of the Project", "5"),
    ("CHAPTER 2", "LITERATURE SURVEY", "6"),
    ("", "2.1  Overview of the Research Area", "7"),
    ("", "2.2  Existing Models and Frameworks", "8"),
    ("", "2.3  Limitations Identified from Literature Survey (Research Gaps)", "11"),
    ("", "2.4  Research Objectives", "12"),
    ("", "2.5  Product Backlog (Key User Stories with Desired Outcomes)", "13"),
    ("", "2.6  Plan of Action (Project Road Map)", "15"),
    ("CHAPTER 3", "SPRINT PLANNING AND EXECUTION METHODOLOGY", "21"),
    ("", "3.1  Sprint I — Data Engineering, EDA & Statistical Validation", "21"),
    ("", "      3.1.1  Objectives with User Stories of Sprint I", "23"),
    ("", "      3.1.2  Functional Document", "25"),
    ("", "      3.1.3  Architecture Document", "28"),
    ("", "      3.1.4  Outcome of Objectives / Result Analysis", "29"),
    ("", "      3.1.5  Sprint Retrospective", "30"),
    ("", "3.2  Sprint II — Machine Learning, Explainability & Clustering", "31"),
    ("", "      3.2.1  Objectives with User Stories of Sprint II", "32"),
    ("", "      3.2.2  Functional Document", "33"),
    ("", "      3.2.3  Architecture Document", "34"),
    ("", "      3.2.4  Outcome of Objectives / Result Analysis", "35"),
    ("", "      3.2.5  Sprint Retrospective", "36"),
    ("CHAPTER 6", "RESULTS AND DISCUSSIONS", "37"),
    ("", "6.1  Project Outcomes (Performance Evaluation, Comparisons, Testing Results)", "38"),
    ("CHAPTER 7", "CONCLUSION AND FUTURE ENHANCEMENT", "39"),
    ("REFERENCES", "", "40"),
]

t = doc.add_table(rows=1 + len(toc_rows), cols=3)
t.style = "Table Grid"
t.alignment = WD_TABLE_ALIGNMENT.CENTER

# header row
toc_hdr = t.rows[0].cells
for j, h in enumerate(("Chapter", "Title", "Page")):
    toc_hdr[j].text = ""
    hp = toc_hdr[j].paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER if j != 2 else WD_ALIGN_PARAGRAPH.RIGHT
    hr = hp.add_run(h)
    hr.bold = True
    hr.font.size = Pt(11)
    set_cell_bg(toc_hdr[j], "E7E6E6")
    toc_hdr[j].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

for i, row in enumerate(toc_rows, start=1):
    cells = t.rows[i].cells
    for j, val in enumerate(row):
        cells[j].text = ""
        p = cells[j].paragraphs[0]
        r = p.add_run(val)
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(0, 0, 0)
        is_chapter = val.startswith("CHAPTER") or val in ("ABSTRACT",
                                                            "TABLE OF CONTENTS",
                                                            "LIST OF FIGURES",
                                                            "LIST OF TABLES",
                                                            "ABBREVIATIONS",
                                                            "REFERENCES") or row[1] in (
            "INTRODUCTION", "LITERATURE SURVEY",
            "SPRINT PLANNING AND EXECUTION METHODOLOGY",
            "RESULTS AND DISCUSSIONS", "CONCLUSION AND FUTURE ENHANCEMENT")
        if is_chapter:
            r.bold = True
        if j == 2:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

for row in t.rows:
    row.cells[0].width = Inches(1.1)
    row.cells[1].width = Inches(4.4)
    row.cells[2].width = Inches(0.6)
set_table_borders(t)

add_page_break()

# ============================================================================
# LIST OF FIGURES
# ============================================================================
heading("LIST OF FIGURES", level=1)

figures_list = [
    ("Figure 1.1", "Project scope — connecting Digital India with Circular Economy", "2"),
    ("Figure 2.1", "Correlation heatmap of all numeric variables", "9"),
    ("Figure 2.2", "Literature mapping — research gaps", "11"),
    ("Figure 3.1", "High-level system architecture of the research pipeline", "28"),
    ("Figure 3.2", "Data flow diagram across 7 government sources", "29"),
    ("Figure 3.3", "DCI ranking across 16 Indian states", "30"),
    ("Figure 3.4", "Digital Access Score vs. CE Behavior Score (scatter, OLS fit)", "30"),
    ("Figure 3.5", "Distributions of raw variables", "31"),
    ("Figure 3.6", "UPI transaction trends", "32"),
    ("Figure 3.7", "Component / module architecture of Sprint II", "34"),
    ("Figure 3.8", "ML model comparison — LOO-CV", "35"),
    ("Figure 3.9", "Actual vs. predicted CEBS — best model", "35"),
    ("Figure 3.10", "SHAP beeswarm — global feature importance", "36"),
    ("Figure 3.11", "SHAP waterfall — Haryana (highest) vs. Bihar (lowest)", "36"),
    ("Figure 3.12", "K-Means clustering — two state typologies", "36"),
    ("Figure 6.1", "Bootstrap confidence intervals (10,000 resamples)", "38"),
    ("Figure 6.2", "Weight sensitivity analysis", "38"),
    ("Figure 6.3", "Extended sample validation (n = 21)", "38"),
]

t = doc.add_table(rows=1 + len(figures_list), cols=3)
t.style = "Table Grid"
t.alignment = WD_TABLE_ALIGNMENT.CENTER

fig_hdr = t.rows[0].cells
for j, h in enumerate(("Figure No.", "Caption", "Page")):
    fig_hdr[j].text = ""
    hp = fig_hdr[j].paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER if j != 2 else WD_ALIGN_PARAGRAPH.RIGHT
    hr = hp.add_run(h)
    hr.bold = True
    hr.font.size = Pt(11)
    set_cell_bg(fig_hdr[j], "E7E6E6")
    fig_hdr[j].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

for i, row in enumerate(figures_list, start=1):
    cells = t.rows[i].cells
    for j, val in enumerate(row):
        cells[j].text = ""
        p = cells[j].paragraphs[0]
        r = p.add_run(val)
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(0, 0, 0)
        if j == 0:
            r.bold = True
        if j == 2:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

for row in t.rows:
    row.cells[0].width = Inches(1.0)
    row.cells[1].width = Inches(4.6)
    row.cells[2].width = Inches(0.5)
set_table_borders(t)

add_page_break()

# ============================================================================
# LIST OF TABLES
# ============================================================================
heading("LIST OF TABLES", level=1)

tables_list = [
    ("Table 2.1", "Summary of existing models and frameworks", "8"),
    ("Table 2.2", "Research gaps identified from literature", "11"),
    ("Table 2.3", "Product backlog — epics and user stories", "13"),
    ("Table 2.4", "Plan of action — project roadmap (Gantt view)", "15"),
    ("Table 3.1", "Data sources and variables (Sprint I)", "25"),
    ("Table 3.2", "Sprint I user stories and acceptance criteria", "23"),
    ("Table 3.3", "Descriptive statistics of composite indices", "29"),
    ("Table 3.4", "OLS regression results — primary model", "29"),
    ("Table 3.5", "Robustness diagnostics", "29"),
    ("Table 3.6", "Sprint I retrospective", "30"),
    ("Table 3.7", "Sprint II user stories and acceptance criteria", "32"),
    ("Table 3.8", "ML model comparison — LOO-CV results", "35"),
    ("Table 3.9", "Nested LOO-CV results (leak-free)", "35"),
    ("Table 3.10", "SHAP global feature importance", "35"),
    ("Table 3.11", "K-Means cluster profiles", "36"),
    ("Table 3.12", "Sprint II retrospective", "36"),
    ("Table 6.1", "Mediation analysis results", "38"),
    ("Table 6.2", "Threshold (piecewise) analysis", "38"),
]

t = doc.add_table(rows=1 + len(tables_list), cols=3)
t.style = "Table Grid"
t.alignment = WD_TABLE_ALIGNMENT.CENTER

tbl_hdr = t.rows[0].cells
for j, h in enumerate(("Table No.", "Caption", "Page")):
    tbl_hdr[j].text = ""
    hp = tbl_hdr[j].paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER if j != 2 else WD_ALIGN_PARAGRAPH.RIGHT
    hr = hp.add_run(h)
    hr.bold = True
    hr.font.size = Pt(11)
    set_cell_bg(tbl_hdr[j], "E7E6E6")
    tbl_hdr[j].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

for i, row in enumerate(tables_list, start=1):
    cells = t.rows[i].cells
    for j, val in enumerate(row):
        cells[j].text = ""
        p = cells[j].paragraphs[0]
        r = p.add_run(val)
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(0, 0, 0)
        if j == 0:
            r.bold = True
        if j == 2:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

for row in t.rows:
    row.cells[0].width = Inches(1.0)
    row.cells[1].width = Inches(4.6)
    row.cells[2].width = Inches(0.5)
set_table_borders(t)

add_page_break()

# ============================================================================
# ABBREVIATIONS
# ============================================================================
heading("ABBREVIATIONS", level=1)

abbr = [
    ("CE", "Circular Economy"),
    ("CEBS", "Circular Economy Behavior Score"),
    ("CPCB", "Central Pollution Control Board"),
    ("DAS", "Digital Access Score"),
    ("DCI", "Digital Circularity Index"),
    ("EDA", "Exploratory Data Analysis"),
    ("EPR", "Extended Producer Responsibility"),
    ("HC3", "Heteroskedasticity-Consistent Standard Errors (type 3)"),
    ("ICT", "Information and Communication Technology"),
    ("IEEE", "Institute of Electrical and Electronics Engineers"),
    ("LOO-CV", "Leave-One-Out Cross-Validation"),
    ("ML", "Machine Learning"),
    ("NITI Aayog", "National Institution for Transforming India"),
    ("NPCI", "National Payments Corporation of India"),
    ("NSDP", "Net State Domestic Product"),
    ("OLS", "Ordinary Least Squares"),
    ("PCA", "Principal Component Analysis"),
    ("RBI", "Reserve Bank of India"),
    ("RF", "Random Forest"),
    ("RMSE", "Root Mean Squared Error"),
    ("SDG", "Sustainable Development Goal"),
    ("SHAP", "Shapley Additive Explanations"),
    ("SVR", "Support Vector Regression"),
    ("TRAI", "Telecom Regulatory Authority of India"),
    ("UPI", "Unified Payments Interface"),
    ("VIF", "Variance Inflation Factor"),
    ("XGBoost", "Extreme Gradient Boosting"),
]
make_table(["Abbreviation", "Full Form"], abbr,
           widths=[Inches(1.6), Inches(4.6)])

add_page_break()

# ============================================================================
# CHAPTER 1 — INTRODUCTION
# ============================================================================
heading("CHAPTER 1 — INTRODUCTION", level=1)

heading("1.1  Introduction to Project", level=2)
para(
    "Since the launch of the Digital India programme in 2015, India has dramatically "
    "expanded broadband penetration, mobile connectivity, and the Unified Payments "
    "Interface (UPI) across a population of 1.4 billion people. Monthly UPI "
    "transactions now exceed 14 billion, and national tele-density is above 85%. "
    "In parallel, India generates roughly 62 million tonnes of waste annually and "
    "ranks among the world's top three e-waste producers; NITI Aayog's circular "
    "economy (CE) strategy now spans 11 priority sectors.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
para(
    "This project, titled \"Digital Inclusion and Circular Economy Behavior in Indian "
    "States\", is a data-driven research initiative that investigates whether digital "
    "inclusion drives circular economy outcomes at the state level. The work "
    "integrates seven official government data sources — TRAI, RBI, NITI Aayog, NPCI, "
    "CPCB, Census of India, and Dataful — covering 16 Indian states with 100% "
    "verified observations, and constructs three novel composite indices: a Digital "
    "Access Score (DAS), a CE Behavior Score (CEBS), and the Digital Circularity "
    "Index (DCI).",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
para(
    "The analytical pipeline combines classical statistics (OLS, non-parametric "
    "tests, bootstrap, mediation, piecewise regression) with machine learning "
    "(seven LOO-CV models, XGBoost with nested CV) and model-agnostic explainability "
    "(SHAP), and closes with K-Means clustering of state typologies. The final "
    "deliverables include 22 publication-ready figures, a defense-ready IEEE "
    "conference paper, and a reproducible code base.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

heading("1.2  Problem Statement and Description", level=2)
para(
    "India is pursuing two major national agendas in parallel — rapid digitization "
    "under Digital India and a transition to a circular economy under Swachh Bharat "
    "and NITI Aayog's 11-sector CE strategy. Research on Digital India has focused "
    "mainly on growth, employment, and financial inclusion, while CE research has "
    "stayed centered on waste-management technology and Extended Producer "
    "Responsibility (EPR) policy. Very little state-level work has asked whether "
    "stronger digital access is actually associated with better environmental "
    "performance.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

para("The core research problem addressed by this project is therefore:",
     align=WD_ALIGN_PARAGRAPH.JUSTIFY)

p = doc.add_paragraph()
p.paragraph_format.left_indent = Inches(0.35)
r = p.add_run(
    "\"Does digital inclusion — measured through tele-density, UPI adoption, and "
    "economic capacity — predict circular-economy behavior across Indian states, "
    "and if so, through what mechanisms?\"")
r.italic = True
r.bold = True

para(
    "To operationalise this problem, three testable hypotheses are defined:",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
bullet("H1 — States with higher Digital Access Scores will also have higher CE "
       "Behavior Scores.")
bullet("H2 — UPI adoption mediates this relationship, i.e., digital payments are "
       "the channel through which digital access affects CE behavior.")
bullet("H3 — There is a tele-density threshold beyond which CE behavior improves "
       "sharply.")

heading("1.3  Motivation", level=2)
para(
    "Three motivations drive this work:",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
numbered(
    "Policy coherence. Digital India and Swachh Bharat are usually treated as "
    "independent policy tracks. If digital infrastructure measurably lifts CE "
    "outcomes, then connectivity investment is not only a telecom intervention "
    "but also a sustainability intervention — a finding with direct implications "
    "for budget allocation.")
numbered(
    "State-level evidence gap. State SDG scores range widely from 57 to 79, "
    "Bihar's tele-density is around 55.8% while Kerala exceeds 120%, yet no "
    "composite index ties digital access to circular economy outcomes at the "
    "sub-national level. This project fills that gap.")
numbered(
    "Methodological rigor under small-n. With only 16 states in the clean merged "
    "dataset, naive modeling overfits. The project demonstrates a defensible "
    "workflow that combines bootstrap, LOO-CV, nested CV, and SHAP, which is "
    "itself a reusable template for other small-n, policy-relevant research "
    "questions.")

heading("1.4  Sustainable Development Goal of the Project", level=2)
para(
    "The project directly contributes to multiple United Nations Sustainable "
    "Development Goals (SDGs) adopted as part of the 2030 Agenda:",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

sdg_rows = [
    ("SDG 9", "Industry, Innovation and Infrastructure — tele-density and UPI act as "
              "proxies for digital infrastructure and innovation capacity."),
    ("SDG 11", "Sustainable Cities and Communities — urbanisation and waste handling "
               "directly inform the CEBS component."),
    ("SDG 12", "Responsible Consumption and Production — e-waste processed per "
               "capita is a core input to the CE Behavior Score."),
    ("SDG 13", "Climate Action — improved CE behavior reduces emissions from landfill "
               "and virgin-material extraction."),
    ("SDG 17", "Partnerships for the Goals — the study uses data from seven public "
               "institutions and supports cross-ministry coordination."),
]
make_table(["SDG", "Relevance to Project"], sdg_rows,
           widths=[Inches(1.0), Inches(5.2)])

para(
    "The central policy message — that digital inclusion and circular economy "
    "agendas should be treated as connected rather than separate — is consistent "
    "with NITI Aayog's SDG India Index 2023-24 direction and the UN's integrated "
    "SDG framework.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

add_page_break()

# ============================================================================
# CHAPTER 2 — LITERATURE SURVEY
# ============================================================================
heading("CHAPTER 2 — LITERATURE SURVEY", level=1)

heading("2.1  Overview of the Research Area", level=2)
para(
    "The study sits at the intersection of three research streams: (1) digital "
    "inclusion and ICT-for-development, (2) circular economy and industrial "
    "ecology, and (3) data-driven policy analytics. Between 2015 and 2024, India "
    "pushed tele-density beyond 85% nationally, with urban pockets crossing 130%. "
    "Since 2016, UPI has grown into the world's largest real-time digital payments "
    "system. Yet regional disparities remain stark — Bihar sits around 55.8% "
    "tele-density while Kerala exceeds 120%.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
para(
    "On the circular economy side, the Ellen MacArthur Foundation popularised the "
    "framework, and Geissdoerfer et al. (2017) later distinguished it more "
    "clearly from the broader idea of sustainability. In India, NITI Aayog "
    "translated that agenda into an 11-sector strategy, but implementation "
    "remains uneven: the country generates roughly 1.71 million tonnes of e-waste "
    "annually, only part of which enters formal recycling channels, and state SDG "
    "scores still range from 57 to 79.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
para(
    "Avgerou and Heeks argue that ICTs reshape development through multiple "
    "channels — governance, markets, information flow, and institutional "
    "functioning. If that view holds, digital access should plausibly affect CE "
    "behavior through several mechanisms rather than one isolated pathway. "
    "However, state-level empirical evidence connecting Digital India with "
    "circular-economy outcomes remains limited — the gap this study addresses.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

heading("2.2  Existing Models and Frameworks", level=2)
para(
    "Table 2.1 summarises the most relevant models and frameworks reviewed from "
    "the literature, grouped by their analytical purpose.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

existing_models = [
    ("Ellen MacArthur\nFoundation (2013)",
     "Circular Economy",
     "Conceptual 'butterfly' framework separating biological and technical cycles.",
     "Qualitative, not linked to digital infrastructure."),
    ("Geissdoerfer et al.\n(2017)",
     "Circular Economy vs.\nSustainability",
     "Systematic review that separates CE from the broader sustainability idea.",
     "Framework-level, no empirical state-level model."),
    ("NITI Aayog (2021, 2024)",
     "CE Strategy /\nSDG India Index",
     "11-sector CE roadmap and sub-national SDG Index (Kerala 79 vs. Bihar 57).",
     "Policy document; no linkage model to digital inclusion."),
    ("Avgerou (2010);\nHeeks (2017)",
     "ICT4D",
     "ICTs act on governance, markets, and institutions — multi-channel theory.",
     "Theoretical, not specialised to Indian CE outcomes."),
    ("Baron & Kenny (1986);\nSobel test",
     "Mediation Analysis",
     "Classical four-step approach for testing mediator variables.",
     "Low power with small samples; sensitive to distributional assumptions."),
    ("Lundberg & Lee (2017)",
     "SHAP",
     "Unified, game-theoretic framework for model-agnostic explainability.",
     "Requires careful handling for small n; expensive for high-dimensional data."),
    ("XGBoost\n(Chen & Guestrin)",
     "Gradient Boosting",
     "Regularised tree ensembles with strong performance on tabular data.",
     "Needs nested CV when tuning on small n."),
]

make_table(["Model / Framework", "Area", "Key Contribution", "Limitation"],
           existing_models,
           widths=[Inches(1.4), Inches(1.3), Inches(2.0), Inches(1.8)])

heading("2.3  Limitations Identified from Literature Survey (Research Gaps)", level=2)
para(
    "The literature review surfaces four concrete gaps that this project is "
    "designed to close (Table 2.2).",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

gaps = [
    ("G1",
     "No state-level composite linking digital inclusion and circular economy exists for India.",
     "Build a Digital Circularity Index (DCI) from 7 verified sources."),
    ("G2",
     "Most Digital India studies stop at access/adoption; CE studies stop at waste-flow metrics.",
     "Model DCI = f(DAS, CEBS) jointly, not in isolation."),
    ("G3",
     "Small-n, policy-relevant studies in India rarely pair OLS with leak-free ML validation.",
     "Combine OLS + 7-model LOO-CV + nested-CV XGBoost + SHAP."),
    ("G4",
     "Limited state typology work that blends econometrics with clustering.",
     "Use K-Means (k=2, silhouette-selected) + PCA to profile Digital Leaders vs. Emerging States."),
]
make_table(["ID", "Gap", "How This Project Closes It"], gaps,
           widths=[Inches(0.5), Inches(3.1), Inches(2.8)])

heading("2.4  Research Objectives", level=2)
para(
    "Following the research gaps, the objectives of the project are expressed as "
    "five Epics that also structure the product backlog in Section 2.5:",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
numbered("Objective O1 — Build a unified, verified, state-level dataset from seven "
         "official government sources, with explicit provenance and zero imputation.")
numbered("Objective O2 — Construct three composite indices (DAS, CEBS, DCI) using "
         "transparent min–max normalisation and justifiable weight schemes.")
numbered("Objective O3 — Test the primary hypothesis H1 using OLS and non-parametric "
         "methods, plus bootstrap, HC3 robust errors, permutation tests, and weight "
         "sensitivity analysis.")
numbered("Objective O4 — Validate the relationship using out-of-sample predictive "
         "machine learning, with LOO-CV across seven models and leak-free nested "
         "LOO-CV for XGBoost.")
numbered("Objective O5 — Explain individual state behavior through SHAP and identify "
         "natural state typologies through K-Means clustering + PCA, closing the loop "
         "with policy implications.")

heading("2.5  Product Backlog (Key User Stories with Desired Outcomes)", level=2)
para(
    "The product backlog organises the research objectives into epics and "
    "actionable user stories. Each story has a clear 'desired outcome' column that "
    "doubles as its acceptance criterion.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

backlog = [
    ("E1-US1",
     "Epic 1 — Data Engineering",
     "As a researcher, I want to merge 7 government sources via inner-join so I "
     "can work with one traceable dataset.",
     "Unified 16-state × 15-variable CSV, 0 missing values."),
    ("E1-US2",
     "Epic 1 — Data Engineering",
     "As a researcher, I want normalised composite indices (DAS, CEBS, DCI) with "
     "documented weights.",
     "Min–max normalised variables + three composite columns with weight "
     "justification."),
    ("E2-US1",
     "Epic 2 — EDA",
     "As a researcher, I want 8+ publication-ready EDA figures so I can spot "
     "patterns before hypothesis testing.",
     "Figures 1–8 generated: heatmap, scatter, DCI ranking, distributions, "
     "boxplots, UPI trends, regression panels, UPI vs SDG."),
    ("E3-US1",
     "Epic 3 — Statistics",
     "As a researcher, I want to test H1 with OLS + full diagnostics.",
     "OLS: β₁ = 0.551, R² = 0.610, p < 0.001; Breusch-Pagan, Durbin-Watson, "
     "Cook's D reported."),
    ("E3-US2",
     "Epic 3 — Statistics",
     "As a researcher, I want robustness checks so reviewers cannot dismiss the "
     "finding on small-n or distributional grounds.",
     "HC3 p = 1.1×10⁻⁵, permutation p = 0.0001, bootstrap CI [0.648, 0.979]."),
    ("E3-US3",
     "Epic 3 — Statistics",
     "As a researcher, I want to test H2 (UPI mediation) and H3 (tele-density "
     "threshold).",
     "Sobel z = −0.241 (no mediation); piecewise breakpoint at 118.77% with "
     "R² = 0.723."),
    ("E4-US1",
     "Epic 4 — ML Validation",
     "As a researcher, I want 7 ML models under LOO-CV to confirm the signal "
     "survives out-of-sample.",
     "Full-model LOO-CV: Lasso R² = 0.568; digital-only: ElasticNet R² = 0.364."),
    ("E4-US2",
     "Epic 4 — ML Validation",
     "As a researcher, I want nested LOO-CV to remove hyperparameter leakage.",
     "Nested-CV XGBoost R² = 0.511, p = 0.002."),
    ("E5-US1",
     "Epic 5 — Explainability",
     "As a researcher, I want SHAP values so I can explain state-level behavior.",
     "Global importance: tele-density (5.01) and NSDP (4.88) top ranks; per-state "
     "waterfall plots for Haryana and Bihar."),
    ("E5-US2",
     "Epic 5 — Clustering",
     "As a policy analyst, I want data-driven state typologies.",
     "K-Means k = 2: Digital Leaders (DCI 46.7) vs. Emerging States (DCI 18.3); "
     "2.5× gap."),
]
make_table(["Story ID", "Epic", "User Story", "Desired Outcome / Acceptance"],
           backlog,
           widths=[Inches(0.7), Inches(1.3), Inches(2.1), Inches(2.3)])

heading("2.6  Plan of Action (Project Road Map)", level=2)
para(
    "The six-week sprint plan, summarised in Table 2.4, maps directly to the five "
    "epics above and to the two sprint windows that structure Chapter 3.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

roadmap = [
    ("Week 1", "01 Feb – 08 Feb 2026", "Sprint I / Epic 1",
     "Source data from TRAI, RBI, NITI Aayog, NPCI, CPCB, Census, Dataful. "
     "Merge via inner-join; compute DAS, CEBS, DCI."),
    ("Week 2", "10 Feb – 14 Feb 2026", "Sprint I / Epic 2",
     "Generate 8 EDA figures; identify correlations and outliers."),
    ("Week 3", "15 Feb – 21 Feb 2026", "Sprint I / Epic 3 (part 1)",
     "OLS regression, diagnostics, multiple regression with controls, VIF check."),
    ("Week 4", "22 Feb – 28 Feb 2026", "Sprint I / Epic 3 (part 2)",
     "Robustness suite: bootstrap (10k), HC3, permutation (10k), weight "
     "sensitivity, mediation, piecewise regression, extended sample (n = 21)."),
    ("Week 5", "01 Mar – 07 Mar 2026", "Sprint II / Epic 4",
     "7 ML models under LOO-CV; XGBoost with nested LOO-CV; 4-fold stability "
     "across 400 splits."),
    ("Week 6", "08 Mar – 15 Mar 2026", "Sprint II / Epic 5 + Writing",
     "SHAP beeswarm, bar, and waterfall plots; K-Means (k=2) + PCA biplot; IEEE "
     "paper and project report."),
]
make_table(["Week", "Dates", "Sprint / Epic", "Deliverables"], roadmap,
           widths=[Inches(0.7), Inches(1.4), Inches(1.5), Inches(2.8)])

add_page_break()

# ============================================================================
# CHAPTER 3 — SPRINT PLANNING AND EXECUTION METHODOLOGY
# ============================================================================
heading("CHAPTER 3 — SPRINT PLANNING AND EXECUTION METHODOLOGY", level=1)

para(
    "The project follows an Agile / Scrum-inspired execution model with two "
    "three-week sprints. Sprint I focuses on data engineering, exploratory "
    "analysis, and classical statistical validation. Sprint II focuses on machine "
    "learning validation, explainability, and state-typology clustering. Each "
    "sprint is documented below with its objectives, functional document, "
    "architecture view, outcomes, and retrospective.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

# ── Sprint I ────────────────────────────────────────────────────────────────
heading("3.1  Sprint I — Data Engineering, EDA & Statistical Validation", level=2)

para("Sprint Duration: 01 February 2026 – 21 February 2026 (3 weeks)",
     bold=True)
para("Sprint Goal: Build a verified 16-state dataset, compute composite indices, "
     "generate publication-grade EDA, and produce a defense-ready statistical test "
     "of H1, H2, and H3.",
     align=WD_ALIGN_PARAGRAPH.JUSTIFY)

heading("3.1.1  Objectives with User Stories of Sprint I", level=3)

sprint1_us = [
    ("S1-US1",
     "As a researcher, I want to ingest all 7 government sources with explicit "
     "provenance so the pipeline is reproducible.",
     "01_data_engineering.py produces a merged CSV with no missing values."),
    ("S1-US2",
     "As a researcher, I want DAS, CEBS, and DCI computed with documented weight "
     "schemes (40/30/30 and 35/40/25).",
     "Three composite-index columns added to the final dataset."),
    ("S1-US3",
     "As a researcher, I want 8 publication-ready EDA figures.",
     "Figures fig1–fig8 generated in /figures/."),
    ("S1-US4",
     "As a researcher, I want OLS on CEBS ~ DAS with full diagnostics.",
     "β₁ = 0.551, R² = 0.610, p < 0.001, with Breusch-Pagan, Durbin-Watson, "
     "Cook's D."),
    ("S1-US5",
     "As a reviewer-proof scientist, I want robustness (HC3, permutation, "
     "bootstrap, weight sensitivity).",
     "Robustness report committed to /results/."),
    ("S1-US6",
     "As a researcher, I want mediation and threshold tests for H2 and H3.",
     "Sobel z = −0.241; piecewise breakpoint at 118.77% tele-density."),
]
make_table(["Story ID", "User Story", "Acceptance / Outcome"],
           sprint1_us,
           widths=[Inches(0.8), Inches(3.0), Inches(2.4)])

heading("3.1.2  Functional Document", level=3)

para("Scope.", bold=True)
para(
    "Sprint I implements the full data engineering and statistical validation "
    "pipeline. It reads raw CSV/Excel files, merges them, derives composite "
    "scores, produces EDA artifacts, and executes the statistical battery that "
    "supports H1, H2, and H3.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

para("Inputs / Data Sources.", bold=True)
data_sources = [
    ("TRAI (2024)", "Tele-density (%)", "Quarterly Indicator Report"),
    ("RBI (2024–25)", "Per Capita NSDP (INR)", "Handbook of Statistics, Table 9"),
    ("NITI Aayog (2023–24)", "SDG India Index Score", "SDG India Index & Dashboard"),
    ("NPCI / Dataful (2024–25)", "UPI per-capita transactions", "Monthly UPI product stats"),
    ("CPCB (2021–22)", "E-waste processed (tonnes)", "Annual e-waste report"),
    ("Census of India (2011)", "Literacy rate (%)", "Primary Census Abstract"),
    ("Census of India (2011)", "Urban population (%)", "Primary Census Abstract"),
]
make_table(["Source (Year)", "Variable", "Document / Table"], data_sources,
           widths=[Inches(1.8), Inches(2.2), Inches(2.2)])

para("Functional Requirements.", bold=True)
bullet("FR1: Inner-join merge on the State key; fail the build if any source is missing.")
bullet("FR2: Min–max normalisation of each raw variable to [0, 100].")
bullet("FR3: Compute DAS = 0.40·T̂d + 0.30·Ûpc + 0.30·N̂pc.")
bullet("FR4: Compute CEBS = 0.35·Êpc + 0.40·Ssdg + 0.25·N̂pc.")
bullet("FR5: Compute DCI = (DAS × CEBS) / 100.")
bullet("FR6: OLS of CEBS on DAS with Breusch-Pagan, Durbin-Watson, Cook's distance.")
bullet("FR7: Robustness battery — HC3, bootstrap CIs (10k), permutation (10k), "
       "weight sensitivity across 7 schemes.")
bullet("FR8: Mediation test (Baron & Kenny + Sobel) and piecewise threshold regression.")

para("Non-Functional Requirements.", bold=True)
bullet("NFR1: Reproducibility — fixed random seeds and saved intermediate CSVs.")
bullet("NFR2: Traceability — every figure/table maps to a specific script and result file.")
bullet("NFR3: Publication-grade outputs — 300 DPI figures.")

para("Key Formulas.", bold=True)
para("  x̂ᵢ = (xᵢ − xₘᵢₙ) / (xₘₐₓ − xₘᵢₙ) × 100")
para("  DAS = 0.40·T̂d + 0.30·Ûpc + 0.30·N̂pc")
para("  CEBS = 0.35·Êpc + 0.40·Ssdg + 0.25·N̂pc")
para("  DCI = (DAS × CEBS) / 100")
para("  CEBSᵢ = β₀ + β₁·DASᵢ + εᵢ    (primary OLS)")

heading("3.1.3  Architecture Document", level=3)
para(
    "Sprint I is implemented as a linear, file-first pipeline so every step "
    "produces a durable, inspectable artifact. The architecture has four layers: "
    "(1) ingestion, (2) merge & feature construction, (3) analysis, and (4) "
    "reporting.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

arch1_rows = [
    ("Layer 1 — Ingestion",
     "Reads raw CSV/XLSX for TRAI, RBI, NITI, NPCI, CPCB, Census, Dataful.",
     "01_data_engineering.py"),
    ("Layer 2 — Merge & Features",
     "Inner-join on State; min–max normalisation; DAS / CEBS / DCI construction.",
     "01_data_engineering.py → /data/trai_state_data_final_v2.csv"),
    ("Layer 3 — EDA",
     "Correlation heatmap, scatter + OLS, DCI ranking, distributions, UPI trends.",
     "02_eda_visualizations.py → /figures/fig1–fig8"),
    ("Layer 4 — Statistics",
     "OLS, multiple regression, diagnostics, robustness, mediation, threshold.",
     "03_statistical_analysis.py, 04_reviewer_defense.py → /results/"),
]
make_table(["Architectural Layer", "Responsibility", "Implementation / Output"],
           arch1_rows,
           widths=[Inches(1.6), Inches(2.5), Inches(2.1)])

add_figure(ARCH_DIAGRAM,
           "Figure 3.1  High-level system architecture of the research pipeline — "
           "ingestion, feature construction, statistical analysis, machine learning, "
           "and reporting layers.",
           width_in=5.6)

add_figure(DATA_FLOW_DIAGRAM,
           "Figure 3.2  Data flow diagram across the seven government data sources "
           "feeding the unified 16-state dataset.",
           width_in=5.6)

para("Component interactions:", bold=True)
bullet("Each script reads from /data/ and writes to /results/ or /figures/ only — "
       "no in-memory state crosses script boundaries.")
bullet("Every figure has a matching .txt or .csv results file so numbers in the "
       "paper can be traced back to the exact run.")
bullet("A fixed random seed (42) is used wherever stochastic resampling is "
       "involved (bootstrap, permutation).")

heading("3.1.4  Outcome of Objectives / Result Analysis", level=3)

para("Descriptive Statistics.", bold=True)
para("Table 3.3 summarises DAS, CEBS, and DCI for the 16 states retained in the "
     "final dataset.",
     align=WD_ALIGN_PARAGRAPH.JUSTIFY)
make_table(["Statistic", "DAS", "CEBS", "DCI"],
           [("Mean", "64.95", "46.98", "32.52"),
            ("Std. Dev.", "19.69", "13.90", "17.40"),
            ("Min", "30.27", "27.23", "8.24"),
            ("Max", "94.40", "87.30", "72.97"),
            ("Median", "67.02", "47.78", "32.42")],
           widths=[Inches(1.5), Inches(1.3), Inches(1.3), Inches(1.3)])

add_figure(os.path.join(FIG, "fig3_dci_ranking.jpg"),
           "Figure 3.3  DCI ranking across 16 Indian states. Haryana leads "
           "(72.97), Bihar lags (8.24).")

add_figure(os.path.join(FIG, "fig1_correlation_heatmap.jpg"),
           "Figure 2.1  Correlation heatmap of all numeric variables. Darker "
           "colors indicate stronger correlations.")

para("Primary OLS Result (H1).", bold=True)
para("The fitted model is: CEBS = 11.158 + 0.551 · DAS. A one-point increase in "
     "DAS is associated with ~0.55 points on CEBS, and the model explains 61% of "
     "the variance.",
     align=WD_ALIGN_PARAGRAPH.JUSTIFY)

make_table(["Metric", "Value"],
           [("R²", "0.610"),
            ("Adjusted R²", "0.583"),
            ("β₁ (slope)", "0.551"),
            ("SE(β₁)", "0.118"),
            ("t-statistic", "4.684"),
            ("p-value", "0.000352"),
            ("F-statistic", "21.94"),
            ("95% CI for β₁", "[0.299, 0.804]"),
            ("Pearson r", "0.781")],
           widths=[Inches(2.5), Inches(2.0)])

add_figure(os.path.join(FIG, "fig2_digital_vs_ce_scatter.jpg"),
           "Figure 3.4  Digital Access Score vs. CE Behavior Score "
           "(r = 0.781, p < 0.001).")

para("Robustness Diagnostics.", bold=True)
make_table(["Test", "Value", "Result"],
           [("Spearman ρ", "0.912", "p < 0.001"),
            ("Kendall τ", "0.783", "p < 0.001"),
            ("Shapiro-Wilk", "Skew = 2.72", "Non-normal"),
            ("Breusch-Pagan LM", "1.539", "p = 0.215"),
            ("Durbin-Watson", "2.025", "No autocorrelation"),
            ("Cook's distance", "Dₘₐₓ = 4.16 (Haryana)", "1 influential point"),
            ("Permutation p", "0.0001", "Significant"),
            ("HC3 robust p", "1.1 × 10⁻⁵", "Significant"),
            ("Bootstrap CI (r)", "[0.648, 0.979]", "Excludes 0"),
            ("Bootstrap CI (β₁)", "[0.395, 0.836]", "Excludes 0")],
           widths=[Inches(2.0), Inches(2.2), Inches(1.8)])

para("Discussion.", bold=True)
para(
    "The evidence for H1 is strong and method-robust. A five-control specification "
    "lifts R² to 0.763 but triggers multicollinearity (VIF 10.57 for DAS, 9.47 "
    "for NSDP), so the bivariate model remains the cleaner headline test.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

heading("3.1.5  Sprint Retrospective", level=3)
retro1 = [
    ("What went well",
     "Inner-join strategy produced 100% clean data with zero imputation. EDA "
     "figures directly exposed the DAS-CEBS pattern and justified H1. Robustness "
     "battery (HC3, permutation, bootstrap) ran end-to-end in one sprint."),
    ("What didn't go well",
     "Residual non-normality (Shapiro skew = 2.72) and Haryana's Cook's D = 4.16 "
     "required extra defensive analysis. Piecewise regression was unstable above "
     "the breakpoint because only 2–3 states sit there."),
    ("What we learned",
     "Reporting non-parametric rank tests alongside OLS pre-empts reviewer "
     "objections. Documenting weight choices is as important as documenting the "
     "model itself."),
    ("Action items for Sprint II",
     "(1) Use nested LOO-CV for all ML so hyperparameter tuning is not biased; "
     "(2) Report SHAP globally and per-state; (3) Prefer models that degrade "
     "gracefully at n = 16 (linear families, RF, XGBoost)."),
]
make_table(["Category", "Notes"], retro1,
           widths=[Inches(1.8), Inches(4.4)])

add_page_break()

# ── Sprint II ───────────────────────────────────────────────────────────────
heading("3.2  Sprint II — Machine Learning, Explainability & Clustering", level=2)

para("Sprint Duration: 22 February 2026 – 15 March 2026 (3 weeks)",
     bold=True)
para("Sprint Goal: Confirm the OLS signal using out-of-sample ML, quantify "
     "feature importance using SHAP, and uncover state typologies through "
     "K-Means clustering.",
     align=WD_ALIGN_PARAGRAPH.JUSTIFY)

heading("3.2.1  Objectives with User Stories of Sprint II", level=3)

sprint2_us = [
    ("S2-US1",
     "As a researcher, I want 7 ML baselines under LOO-CV so I can compare "
     "predictive validity.",
     "Full-model Lasso R² = 0.568; digital-only ElasticNet R² = 0.364."),
    ("S2-US2",
     "As a researcher, I want leak-free nested LOO-CV for XGBoost.",
     "XGBoost R² = 0.511, p = 0.002."),
    ("S2-US3",
     "As a researcher, I want stability across 400 splits (100×4 KFold).",
     "RF median R² = 0.603."),
    ("S2-US4",
     "As a researcher, I want SHAP global and per-state explanations.",
     "Tele-density ranked #1 (mean |φ| = 5.01); NSDP #2 (4.88)."),
    ("S2-US5",
     "As a policy analyst, I want data-driven state clusters.",
     "K-Means (k=2, silhouette-selected) separates Digital Leaders (DCI 46.7) "
     "from Emerging States (DCI 18.3)."),
]
make_table(["Story ID", "User Story", "Acceptance / Outcome"],
           sprint2_us,
           widths=[Inches(0.8), Inches(3.0), Inches(2.4)])

heading("3.2.2  Functional Document", level=3)

para("Scope.", bold=True)
para(
    "Sprint II consumes the verified dataset from Sprint I and produces "
    "out-of-sample validation, explainability artifacts, and state typologies. "
    "It is built around three modules: a cross-validation harness, a SHAP "
    "explainer, and a K-Means + PCA clustering engine.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

para("Functional Requirements.", bold=True)
bullet("FR9: LOO-CV harness comparing 7 regressors on both digital-only and full "
       "feature sets.")
bullet("FR10: Nested LOO-CV wrapper (outer LOO, inner 4-fold GridSearch) to "
       "remove hyperparameter optimism for XGBoost.")
bullet("FR11: Repeated K-Fold CV (100×4 = 400 splits) for stability assessment.")
bullet("FR12: SHAP beeswarm, bar, and waterfall plots for all 16 states.")
bullet("FR13: K-Means clustering with silhouette selection of k, PCA biplot for "
       "visualisation, and cluster profile table.")

para("Models Evaluated.", bold=True)
bullet("Linear Regression, Ridge, Lasso, ElasticNet (linear family)")
bullet("SVR with RBF kernel (non-linear baseline)")
bullet("Random Forest, Gradient Boosting, XGBoost (tree ensembles)")

para("Key Formulas.", bold=True)
para("  R²(LOO) = 1 − Σᵢ (yᵢ − ŷ₋ᵢ)² / Σᵢ (yᵢ − ȳ)²")
para("  f(x) = φ₀ + Σⱼ φⱼ(x)      (SHAP additive explanation)")

heading("3.2.3  Architecture Document", level=3)
para(
    "Sprint II is a three-module architecture sitting on top of the Sprint I "
    "dataset:",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
arch2_rows = [
    ("Module A — CV Harness",
     "Scikit-learn Pipeline + LeaveOneOut / GridSearchCV for leak-free tuning; "
     "writes per-model R², RMSE, and Pearson r.",
     "05_predictive_modeling.py, 06_advanced_ml.py → /results/"),
    ("Module B — SHAP Explainer",
     "shap.Explainer on the tuned XGBoost; generates beeswarm, bar, and "
     "waterfall plots for all 16 states.",
     "06_advanced_ml.py → /figures/fig17-19"),
    ("Module C — Clustering Engine",
     "StandardScaler + KMeans with silhouette scan over k ∈ {2…6}; PCA(2) biplot.",
     "06_advanced_ml.py → /figures/fig20-21"),
]
make_table(["Module", "Responsibility", "Implementation / Output"],
           arch2_rows,
           widths=[Inches(1.8), Inches(2.6), Inches(1.8)])

heading("3.2.4  Outcome of Objectives / Result Analysis", level=3)

para("LOO-CV Results (7 models).", bold=True)
make_table(["Model", "Digital-Only R²", "Digital-Only r", "Full R²", "Full r"],
           [("ElasticNet", "0.364", "0.603", "0.534", "0.731"),
            ("Lasso", "0.347", "0.606", "0.568", "0.758"),
            ("Ridge", "0.338", "0.597", "0.536", "0.743"),
            ("Random Forest", "0.326", "0.575", "0.490", "0.703"),
            ("Linear Reg.", "0.301", "0.585", "0.442", "0.713"),
            ("SVR (RBF)", "0.286", "0.554", "0.425", "0.700"),
            ("Gradient Boost", "0.161", "0.542", "0.445", "0.687")],
           widths=[Inches(1.3), Inches(1.2), Inches(1.1), Inches(1.1), Inches(1.0)])

add_figure(os.path.join(FIG, "fig13_model_comparison.jpg"),
           "Figure 3.8  ML model comparison — LOO-CV R² across digital-only and "
           "full feature sets.")

para("Nested LOO-CV (Leak-Free).", bold=True)
make_table(["Model", "Nested R²", "RMSE", "r"],
           [("XGBoost", "0.511", "9.41", "0.721"),
            ("Random Forest", "0.504", "9.48", "0.711"),
            ("ElasticNet", "0.471", "9.78", "0.723"),
            ("Ridge", "0.445", "10.03", "0.714"),
            ("Lasso", "0.443", "10.05", "0.713"),
            ("SVR", "−0.023", "13.61", "−0.593")],
           widths=[Inches(1.8), Inches(1.4), Inches(1.2), Inches(1.2)])

add_figure(os.path.join(FIG, "fig14_actual_vs_predicted.jpg"),
           "Figure 3.9  Actual vs. predicted CEBS — best nested-CV model.")

para("SHAP Global Feature Importance.", bold=True)
make_table(["Rank", "Feature", "Mean |φ|"],
           [("1", "Tele-density (%)", "5.012"),
            ("2", "Per Capita NSDP", "4.883"),
            ("3", "Population (Mn)", "1.714"),
            ("4", "Urban (%)", "1.677"),
            ("5", "Literacy Rate (%)", "0.998"),
            ("6", "UPI per capita", "0.914")],
           widths=[Inches(0.8), Inches(3.0), Inches(1.5)])

add_figure(os.path.join(FIG, "fig17_shap_beeswarm.jpg"),
           "Figure 3.10  SHAP beeswarm plot — each dot is one state-feature "
           "pair; red = high value, blue = low value.")

add_figure(os.path.join(FIG, "fig19_shap_waterfall.jpg"),
           "Figure 3.11  SHAP waterfall explanations for Haryana (highest CE) "
           "and Bihar (lowest CE).")

para("K-Means Clustering (State Typologies).", bold=True)
make_table(["Cluster", "n", "DAS", "CEBS", "DCI"],
           [("Digital Leaders", "8", "82.0", "56.7", "46.7"),
            ("Emerging States", "8", "47.9", "37.2", "18.3"),
            ("Gap", "—", "34.1", "19.5", "28.4")],
           widths=[Inches(1.8), Inches(0.6), Inches(1.0), Inches(1.0), Inches(1.0)])

add_figure(os.path.join(FIG, "fig20_clustering.jpg"),
           "Figure 3.12  K-Means clustering with hierarchical dendrogram and "
           "cluster radar profiles. Two distinct state typologies emerge.")

heading("3.2.5  Sprint Retrospective", level=3)
retro2 = [
    ("What went well",
     "Nested LOO-CV delivered a defensible R² = 0.511 on XGBoost. SHAP results "
     "agreed qualitatively with OLS coefficients — tele-density and NSDP as the "
     "top drivers. K-Means k = 2 separated states with a 2.5× DCI gap, which "
     "translated cleanly into the policy section."),
    ("What didn't go well",
     "SVR under nested CV fell below the mean-prediction baseline (R² = −0.023), "
     "highlighting the hazard of non-linear kernels at n = 16. UPI's importance "
     "ranked last in SHAP, contradicting an early assumption."),
    ("What we learned",
     "At n = 16, regularised linear models and tree ensembles are the only safe "
     "choices. Methods should be selected to fail visibly rather than silently. "
     "SHAP makes small-sample results interpretable enough for policy audiences."),
    ("Action items",
     "(1) Extend validation to 21-state sample by dropping e-waste from CEBS; "
     "(2) Report both RF and XGBoost to show that the signal is not a single-"
     "model artifact; (3) Add PCA biplot to give reviewers a geometric view of "
     "the clustering."),
]
make_table(["Category", "Notes"], retro2,
           widths=[Inches(1.8), Inches(4.4)])

add_page_break()

# ============================================================================
# CHAPTER 6 — RESULTS AND DISCUSSIONS
# ============================================================================
heading("CHAPTER 6 — RESULTS AND DISCUSSIONS", level=1)

heading("6.1  Project Outcomes (Performance Evaluation, Comparisons, Testing Results)", level=2)

para("Integrated performance view.", bold=True)
para(
    "Combining Sprints I and II, the study produces a multi-method, cross-validated "
    "view of the digital-access / CE-behavior relationship. The OLS model gives "
    "r = 0.781, R² = 0.610, while leak-free nested-CV XGBoost reaches R² = 0.511 "
    "— the usual in-sample-vs-out-of-sample gap. Table 6 below is the single-glance "
    "scorecard used to defend the work.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

make_table(["Evaluation Track", "Best Metric", "Value", "Verdict"],
           [("Parametric (OLS, bivariate)", "R²", "0.610", "Supports H1"),
            ("Parametric (OLS, +5 controls)", "R²", "0.763", "High but multicollinear"),
            ("Non-parametric (Spearman ρ)", "ρ", "0.912", "Supports H1"),
            ("Bootstrap (10,000 resamples)", "95% CI for r", "[0.648, 0.979]", "Excludes 0"),
            ("Permutation test", "p", "0.0001", "Significant"),
            ("HC3 robust SE", "p", "1.1 × 10⁻⁵", "Significant"),
            ("LOO-CV (7 models)", "Full-model R² (Lasso)", "0.568", "Confirms out-of-sample"),
            ("Nested LOO-CV", "XGBoost R²", "0.511", "Leak-free, p = 0.002"),
            ("Repeated K-Fold (400 splits)", "RF median R²", "0.603", "Stable"),
            ("Extended sample (n = 21)", "OLS R²", "0.927", "Signal strengthens"),
            ("K-Means clustering", "DCI gap", "46.7 vs 18.3 (2.5×)", "Two typologies"),
            ("SHAP global importance", "Top feature", "Tele-density (5.01)", "Drives H1")],
           widths=[Inches(2.0), Inches(1.8), Inches(1.4), Inches(1.2)])

para("Mediation Analysis (H2).", bold=True)
para(
    "Table 6.1 reports the Baron & Kenny / Sobel mediation results. The evidence "
    "does not support UPI mediation: the Sobel test is not significant, and the "
    "direct effect remains significant after controlling for UPI.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
make_table(["Path", "β", "p-value", "Significant?"],
           [("c (total): X → Y", "0.505", "0.0004", "Yes"),
            ("a: X → M", "1.499", "0.003", "Yes"),
            ("b: M → Y | X", "−0.017", "0.813", "No"),
            ("c′ (direct): X → Y | M", "0.530", "0.004", "Yes"),
            ("Indirect (a × b)", "−0.026", "—", "—"),
            ("Sobel z", "−0.241", "0.810", "No")],
           widths=[Inches(2.4), Inches(1.0), Inches(1.2), Inches(1.4)])

para("Threshold Analysis (H3).", bold=True)
para(
    "The piecewise regression estimates a tele-density breakpoint at 118.77%. "
    "Below it, the slope is steep and positive (β₁ = 0.635, p = 0.0001); above "
    "it, the slope flips negative (β₂ = −8.738, p = 0.047), but only 2–3 states "
    "sit above the breakpoint so we would not over-read the reversal. The "
    "piecewise model fits better than the linear one (R² = 0.723 vs. 0.610), "
    "giving qualified support for H3.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
make_table(["Segment", "Slope (β)", "p-value", "Interpretation"],
           [("Below 118.77% tele-density", "0.635", "0.0001", "Strong positive effect"),
            ("Above 118.77% tele-density", "−8.738", "0.047", "Reversal (only 2–3 states)"),
            ("Full piecewise model", "R² = 0.723", "—", "Better than linear (0.610)")],
           widths=[Inches(2.2), Inches(1.2), Inches(1.1), Inches(1.7)])

para("Robustness Visualisations.", bold=True)
add_figure(os.path.join(FIG, "fig10_bootstrap_ci.jpg"),
           "Figure 6.1  Bootstrap distribution of Pearson r (10,000 resamples). "
           "The 95% CI [0.648, 0.979] excludes zero.")
add_figure(os.path.join(FIG, "fig11_weight_sensitivity.jpg"),
           "Figure 6.2  Weight sensitivity analysis across 7 alternative DAS "
           "weight schemes. Six of seven preserve a significant Pearson "
           "correlation.")
add_figure(os.path.join(FIG, "fig12_extended_sample.jpg"),
           "Figure 6.3  Extended sample validation (n = 21, e-waste removed "
           "from CEBS). r = 0.963, OLS R² = 0.927.")

para("Discussion — do the methods agree?", bold=True)
para(
    "Broadly, yes. OLS (61% variance explained), nested-CV XGBoost (51%), "
    "bootstrap, permutation, and HC3 all point the same direction. For a 16-state "
    "sample, that consistency is meaningful evidence against a simple overfitting "
    "story.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
para("What drives the relationship?", bold=True)
para(
    "Random Forest favors NSDP, SHAP favors tele-density, but both agree on the "
    "top two drivers. UPI is the unexpected result — smallest SHAP contribution "
    "and no mediation effect — suggesting that digital access acts less through "
    "payments alone than through broader infrastructure and institutional "
    "capacity.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
para("Two Indias in CE performance.", bold=True)
para(
    "Clustering reveals a sharp divide: one group is strong on both digital "
    "access and CE outcomes, the other weak on both. A DCI gap of 46.7 vs. 18.3 "
    "is not a mild gradient — it argues for differentiated policy playbooks.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

para("Policy implications.", bold=True)
numbered("Digital India and Swachh Bharat should be treated less as separate tracks "
         "and more as connected systems.")
numbered("Connectivity investment in lagging states should count as environmental "
         "capacity-building, not just telecom.")
numbered("Because UPI is not the mediating channel, digital inclusion policy should "
         "extend beyond payments to reporting systems, e-governance, and digital "
         "literacy.")
numbered("Digital Leaders can move toward advanced monitoring; Emerging States need "
         "basic infrastructure first — no single national playbook.")
numbered("SHAP highlights state-specific constraints, suggesting that uniform "
         "interventions will miss important differences.")

add_page_break()

# ============================================================================
# CHAPTER 7 — CONCLUSION AND FUTURE ENHANCEMENT
# ============================================================================
heading("CHAPTER 7 — CONCLUSION AND FUTURE ENHANCEMENT", level=1)

heading("7.1  Conclusion", level=2)
para(
    "This minor project finds a consistent state-level association between "
    "digital access and circular-economy behavior in India. Across the 16 states "
    "retained in the final dataset, the pattern remains visible under both "
    "statistical and machine-learning approaches: the primary OLS model gives "
    "r = 0.781 (p < 0.001, R² = 0.610), and the leak-free nested-CV XGBoost "
    "still reaches R² = 0.511. Tele-density emerges as a stronger driver than "
    "digital payments, and K-Means clustering reinforces the same message by "
    "separating states into two groups with a 2.5× DCI gap.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)
para(
    "The three hypotheses land as follows: H1 is strongly supported; H2 (UPI "
    "mediation) is not supported; H3 receives qualified support with a "
    "tele-density breakpoint near 119%. Taken together, the results argue that "
    "digital inclusion and circular-economy policy should be treated as "
    "connected rather than separate agendas.",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY)

heading("7.2  Limitations", level=2)
bullet("Small sample (n = 16) because only states with complete observations "
       "across all seven sources are retained. Haryana's Cook's D = 4.16 shows "
       "sensitivity to influential cases, though bootstrap CIs and the 21-state "
       "validation reduce concern.")
bullet("Cross-sectional design — the study supports association, not causation. "
       "Panel data would be needed for stronger causal claims.")
bullet("Measurement constraints — literacy and urbanisation still come from "
       "Census 2011; NSDP enters both DAS and CEBS; state averages compress "
       "within-state variation.")
bullet("Composite-index weights are researcher-chosen; while six of seven weight "
       "variants still yield a significant result, the choice is not data-driven.")

heading("7.3  Future Enhancement", level=2)
numbered("Move to panel data and district-level granularity to enable causal "
         "designs and capture within-state heterogeneity.")
numbered("Expand the CE index beyond e-waste to include plastic recovery, EPR "
         "compliance, material-circularity ratios, and formal recycling capacity.")
numbered("Introduce Bayesian hierarchical models suited for small-n, grouped data.")
numbered("Generalise the framework to other federal economies with comparable "
         "administrative data (e.g., Brazil, Indonesia).")
numbered("Build a live policy dashboard that updates DAS, CEBS, and DCI as new "
         "government releases arrive, with SHAP explanations per state.")
numbered("Extend explainability to causal SHAP variants and counterfactual "
         "policy simulation.")

add_page_break()

# ============================================================================
# REFERENCES
# ============================================================================
heading("REFERENCES", level=1)

refs = [
    "[1] NPCI, \"UPI Product Statistics (Monthly),\" National Payments "
    "Corporation of India, Mumbai, 2025. Available: "
    "https://www.npci.org.in/what-we-do/upi/product-statistics",
    "[2] TRAI, \"Indian Telecom Services Performance Indicators Report: "
    "April-June 2024,\" Telecom Regulatory Authority of India, New Delhi, 2024.",
    "[3] CPCB, \"Annual Report on Implementation of E-Waste (Management) "
    "Rules, 2016 for FY 2021-22,\" Central Pollution Control Board, MoEF&CC, "
    "Government of India, 2023.",
    "[4] NITI Aayog, \"Circular Economy in India: Rethinking Growth for "
    "Long-Term Prosperity,\" Government of India, New Delhi, 2021.",
    "[5] Ministry of Electronics & IT, \"Digital India Programme: Progress "
    "and Initiatives,\" Government of India, 2023.",
    "[6] M. Geissdoerfer, P. Savaget, N. M. Bocken, and E. J. Hultink, \"The "
    "Circular Economy — A new sustainability paradigm?\" Journal of Cleaner "
    "Production, vol. 143, pp. 757–768, 2017.",
    "[7] Ellen MacArthur Foundation, \"Towards the Circular Economy: Economic "
    "and Business Rationale for an Accelerated Transition,\" 2013.",
    "[8] NITI Aayog, \"SDG India Index & Dashboard 2023-24,\" 4th ed., "
    "National Institution for Transforming India, Government of India, 2024.",
    "[9] C. Avgerou, \"Discourses on ICT and development,\" Information "
    "Technologies and International Development, vol. 6, no. 3, pp. 1–18, 2010.",
    "[10] R. Heeks, Information and Communication Technology for Development "
    "(ICT4D). Routledge, 2017.",
    "[11] RBI, \"Handbook of Statistics on Indian Economy 2024-25, Table 9: "
    "Per Capita Net State Domestic Product,\" Reserve Bank of India, Mumbai, 2025.",
    "[12] Dataful Insights, \"Here is How UPI Usage Differs Across Indian "
    "States,\" Factly Media & Research, Jan. 23, 2026.",
    "[13] Census of India, \"Primary Census Abstract: Literacy Rate, Level of "
    "Urbanization, Population,\" Office of the Registrar General & Census "
    "Commissioner, Ministry of Home Affairs, Government of India, 2011.",
    "[14] R. M. Baron and D. A. Kenny, \"The moderator-mediator variable "
    "distinction in social psychological research: Conceptual, strategic, and "
    "statistical considerations,\" Journal of Personality and Social "
    "Psychology, vol. 51, no. 6, pp. 1173–1182, 1986.",
    "[15] S. M. Lundberg and S.-I. Lee, \"A Unified Approach to Interpreting "
    "Model Predictions,\" in Advances in Neural Information Processing "
    "Systems (NeurIPS), vol. 30, 2017.",
    "[16] T. Chen and C. Guestrin, \"XGBoost: A Scalable Tree Boosting "
    "System,\" in Proc. 22nd ACM SIGKDD Conf. on Knowledge Discovery and Data "
    "Mining, 2016, pp. 785–794.",
    "[17] L. Breiman, \"Random Forests,\" Machine Learning, vol. 45, pp. "
    "5–32, 2001.",
    "[18] H. Zou and T. Hastie, \"Regularization and variable selection via "
    "the elastic net,\" Journal of the Royal Statistical Society, Series B, "
    "vol. 67, no. 2, pp. 301–320, 2005.",
    "[19] J. MacQueen, \"Some methods for classification and analysis of "
    "multivariate observations,\" in Proc. 5th Berkeley Symp. on Mathematical "
    "Statistics and Probability, vol. 1, 1967, pp. 281–297.",
    "[20] F. Pedregosa et al., \"Scikit-learn: Machine Learning in Python,\" "
    "Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.",
]

for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.4)
    p.paragraph_format.first_line_indent = Inches(-0.4)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(ref)
    r.font.size = Pt(11)

# ── Page borders & page numbers on every page ───────────────────────────────
for section in doc.sections:
    add_page_borders(section)
    add_page_number_footer(section)

# Save
doc.save(OUT)
print(f"Saved: {OUT}")
print(f"Size: {os.path.getsize(OUT):,} bytes")
