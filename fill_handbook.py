"""Fill the SRMIST Project Hand Book with this minor project's details."""

import os
import shutil
from copy import deepcopy
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn

ROOT = "/Users/yashchauhan/Desktop/minor project"
SRC = os.path.join(ROOT, "Project Hand Book.docx")
OUT = os.path.join(ROOT, "output", "doc", "Project_Hand_Book_Filled.docx")

shutil.copyfile(SRC, OUT)
d = Document(OUT)


def set_cell_text(cell, text, bold=False, size=11):
    # remove all paragraphs except the first, then set its content
    tc = cell._tc
    paras = cell.paragraphs
    # clear runs in first paragraph
    p0 = paras[0]
    for r in list(p0.runs):
        r._r.getparent().remove(r._r)
    # remove additional paragraphs
    for extra in paras[1:]:
        extra._p.getparent().remove(extra._p)
    run = p0.add_run(text)
    run.bold = bold
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)


def append_cell_para(cell, text, bold=False, size=11):
    p = cell.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)


# ── Table 0 — Project info / Supervisor ─────────────────────────────────────
t0 = d.tables[0]
# Title (row 0): col 2 holds the value (cells 2,3,4 are merged)
set_cell_text(t0.rows[0].cells[2],
              "Digital Inclusion and Circular Economy Behavior in Indian States: "
              "A Digital Circularity Index and Explainable XGBoost Analysis",
              bold=True)
# Project Site / Location
set_cell_text(t0.rows[1].cells[2],
              "SRM Institute of Science and Technology, Kattankulathur Campus, "
              "Tamil Nadu, India")

# Supervisor block (col 1) — rows 5-10
set_cell_text(t0.rows[5].cells[1], "Dr. Suresh Kumar", bold=True)        # Name
set_cell_text(t0.rows[6].cells[1], "Associate Professor")                 # Designation
set_cell_text(t0.rows[7].cells[1], "Computational Intelligence")          # Department
# row 8 Campus already has 'Kattankulathur'
set_cell_text(t0.rows[9].cells[1], "—")                                   # Telephone
set_cell_text(t0.rows[10].cells[1], "sureshk5@srmist.edu.in")             # E-mail

# Co-Supervisor / External Supervisor stay blank with '—'
for r in (5, 6, 7, 9, 10):
    set_cell_text(t0.rows[r].cells[3], "—")
    set_cell_text(t0.rows[r].cells[4], "—")
set_cell_text(t0.rows[8].cells[3], "—")
set_cell_text(t0.rows[8].cells[4], "—")


# ── Table 1 — Students ──────────────────────────────────────────────────────
t1 = d.tables[1]
# Row 1 = student 1 (Yash), Row 2 = student 2 (Shreya)
yash = ("Yash Chauhan", "RA2311026010170", "CINTEL", "—", "yash.vks.chauhan@gmail.com")
shreya = ("Shreya Srivastava", "RA2311026010186", "CINTEL", "—", "shreya@srmist.edu.in")

for col, val in enumerate(yash):
    set_cell_text(t1.rows[1].cells[col], val)
for col, val in enumerate(shreya):
    set_cell_text(t1.rows[2].cells[col], val)
# leave rows 3,4 empty (only two students)
for r in (3, 4):
    for c in range(5):
        set_cell_text(t1.rows[r].cells[c], "—")


# ── Table 2 — Mission / Problem / Assumptions / Stakeholders ────────────────
t2 = d.tables[2]
# Existing degree/program rows (0,1,2) already correct; only refresh empties.

# Mission Statement (row 3 header, row 4 body — body cell is merged across cols)
mission = (
    "To deliver a reproducible, evidence-driven study that quantifies the "
    "relationship between digital inclusion and circular-economy behavior across "
    "16 Indian states by constructing a Digital Circularity Index (DCI) and "
    "validating it through classical statistics, leak-free machine learning, "
    "and SHAP-based explainability — so that policy decisions on Digital India "
    "and Swachh Bharat can be informed by a single, integrated analytical lens."
)
set_cell_text(t2.rows[4].cells[0], mission)

# Problem / Product Description (row 5 header, rows 6-12 body)
problem_paragraphs = [
    "India is simultaneously expanding digital infrastructure (tele-density "
    "above 85%, UPI exceeding 14 billion monthly transactions) and pursuing "
    "circular-economy goals across 11 priority sectors under NITI Aayog's "
    "strategy. Yet research on these two agendas has stayed largely separate: "
    "Digital India studies focus on growth and financial inclusion, while CE "
    "studies focus on waste-management and Extended Producer Responsibility.",

    "There is no state-level composite that links digital access with "
    "circular-economy outcomes, and no defensible small-n analytical pipeline "
    "that pairs OLS with leak-free machine-learning validation. As a result, "
    "policy makers cannot say whether connectivity investment also functions "
    "as a sustainability investment — a question with direct implications for "
    "cross-ministry budget allocation.",

    "This project addresses that gap by integrating seven verified government "
    "data sources (TRAI, RBI, NITI Aayog, NPCI, CPCB, Census of India, "
    "Dataful) into a 16-state dataset, constructing three composite indices "
    "(Digital Access Score, CE Behavior Score, Digital Circularity Index), "
    "and testing three hypotheses (H1 association, H2 UPI mediation, H3 "
    "tele-density threshold) using OLS, bootstrap, HC3, permutation, "
    "mediation, piecewise regression, seven-model LOO-CV, leak-free nested-CV "
    "XGBoost, SHAP explainability, and K-Means clustering.",

    "Deliverables: a unified state-level dataset with full provenance, 22 "
    "publication-ready figures, an IEEE-format conference paper, a "
    "reproducible Python code base, and a defense-ready minor project report.",
]
# row 6 holds the body — write first paragraph there, append subsequent paragraphs
set_cell_text(t2.rows[6].cells[0], problem_paragraphs[0])
for extra in problem_paragraphs[1:]:
    append_cell_para(t2.rows[6].cells[0], extra)

# Rows 7-12 are extra blank lines for the same body section — fill with '—' so
# they are not visibly empty
for r in range(7, 13):
    if t2.rows[r].cells[0].text.strip() == "":
        set_cell_text(t2.rows[r].cells[0], "—")

# Assumptions and Constraints (row 13 header, row 14 body)
assumptions = [
    "A1. Inner-join across the seven sources yields exactly 16 states with "
    "complete observations; no imputation is performed.",
    "A2. Min–max normalisation to [0, 100] and the documented weight schemes "
    "(DAS 40/30/30, CEBS 35/40/25) are appropriate for a transparent "
    "composite-index construction.",
    "A3. Cross-sectional state-level data supports correlational inference "
    "(H1) but not causal claims; mediation (H2) and threshold (H3) results "
    "are interpreted with that limit in mind.",
    "C1. n = 16 is small — every model is validated under LOO-CV or nested "
    "LOO-CV, and reviewer-defense statistics (HC3, bootstrap 10k, "
    "permutation 10k) are mandatory.",
    "C2. Census 2011 is the most recent available source for literacy and "
    "urbanisation; downstream interpretation accounts for this lag.",
    "C3. Reproducibility requires fixed random seeds (seed = 42) and saved "
    "intermediate CSVs at every pipeline boundary.",
]
set_cell_text(t2.rows[14].cells[0], assumptions[0])
for extra in assumptions[1:]:
    append_cell_para(t2.rows[14].cells[0], extra)

# Stakeholders (row 15 header, row 16 body)
stakeholders = [
    "Primary: Project supervisor (Dr. Suresh Kumar) and the Department of "
    "Computational Intelligence, SRMIST.",
    "Academic: Project Review Committee, IEEE conference reviewers (paper "
    "submission), peer researchers in ICT4D and circular-economy analytics.",
    "Policy: NITI Aayog (SDG India Index team), Ministry of Electronics & IT "
    "(Digital India), Ministry of Environment (Swachh Bharat / EPR), state "
    "planning departments.",
    "Data providers: TRAI, RBI, NPCI, CPCB, Census of India, NITI Aayog, "
    "Dataful — whose published datasets feed the unified state-level table.",
    "End users: Policy analysts and researchers using the DCI as a "
    "diagnostic tool for cross-ministry planning.",
]
set_cell_text(t2.rows[16].cells[0], stakeholders[0])
for extra in stakeholders[1:]:
    append_cell_para(t2.rows[16].cells[0], extra)


# ── Sprint section text (paragraphs 9, 44, 67) ──────────────────────────────
sprint_blocks = {
    9: [
        "Sprint 1 — Data Engineering, EDA & Statistical Validation",
        "Duration: 01 Feb 2026 – 21 Feb 2026 (3 weeks)",
        "Goal: Build a verified 16-state dataset, compute the DAS / CEBS / DCI "
        "composite indices, generate publication-grade EDA, and produce a "
        "defense-ready statistical test of H1, H2 and H3.",
        "",
        "Yash Chauhan (RA2311026010170):",
        "• Source ingestion from TRAI, RBI, NITI Aayog, NPCI (01_data_engineering.py).",
        "• Inner-join merge on the State key; min–max normalisation; "
        "construction of DAS, CEBS, DCI columns.",
        "• OLS regression of CEBS on DAS with full diagnostics "
        "(Breusch-Pagan, Durbin-Watson, Cook's distance).",
        "• Robustness battery: HC3 robust SE, bootstrap CIs (10,000 resamples), "
        "permutation test (10,000 resamples).",
        "",
        "Shreya Srivastava (RA2311026010186):",
        "• Source ingestion from CPCB, Census of India and Dataful; "
        "data-quality QA and provenance logging.",
        "• EDA figures fig1–fig8: correlation heatmap, DAS-vs-CEBS scatter, "
        "DCI ranking, distributions, boxplots, UPI trends, regression panels, "
        "UPI-vs-SDG.",
        "• Mediation analysis (Baron & Kenny, Sobel) and piecewise threshold "
        "regression for H2 / H3.",
        "• Weight-sensitivity analysis across seven alternative DAS schemes; "
        "extended-sample (n = 21) validation.",
        "",
        "Daily Scrum highlights — Sprint 1:",
        "• 03 Feb: Inner-join produces 16 clean states, 0 missing values; "
        "DAS-CEBS-DCI columns committed.",
        "• 09 Feb: r = 0.781, R² = 0.610, p < 0.001 confirmed on primary OLS.",
        "• 14 Feb: HC3 p = 1.1×10⁻⁵; bootstrap 95% CI [0.648, 0.979] excludes 0.",
        "• 18 Feb: Mediation Sobel z = −0.241 (no UPI mediation); piecewise "
        "breakpoint at 118.77% tele-density.",
        "• 21 Feb: Sprint 1 retrospective committed; outputs handed off to Sprint 2.",
    ],
    44: [
        "Sprint 2 — Machine Learning, Explainability & Clustering",
        "Duration: 22 Feb 2026 – 08 Mar 2026 (2.5 weeks)",
        "Goal: Confirm the OLS signal using out-of-sample ML, quantify feature "
        "importance via SHAP, and uncover state typologies through K-Means.",
        "",
        "Yash Chauhan (RA2311026010170):",
        "• Seven-model LOO-CV harness (Linear, Ridge, Lasso, ElasticNet, SVR, "
        "Random Forest, Gradient Boosting) on digital-only and full features.",
        "• Leak-free nested LOO-CV wrapper for XGBoost — outer LOO, inner "
        "4-fold GridSearchCV.",
        "• Repeated K-Fold CV stability check (100 × 4 = 400 splits).",
        "",
        "Shreya Srivastava (RA2311026010186):",
        "• SHAP global and per-state explanations: beeswarm, bar, waterfall "
        "plots for all 16 states (focus on Haryana and Bihar).",
        "• K-Means clustering with silhouette-selected k = 2; PCA(2) biplot "
        "for geometric interpretation.",
        "• Cluster profile table (Digital Leaders vs. Emerging States).",
        "",
        "Daily Scrum highlights — Sprint 2:",
        "• 24 Feb: Lasso full-model LOO-CV R² = 0.568; ElasticNet digital-only R² = 0.364.",
        "• 28 Feb: Nested-CV XGBoost R² = 0.511, p = 0.002.",
        "• 02 Mar: SHAP top features — tele-density (mean |φ| = 5.01), NSDP (4.88).",
        "• 05 Mar: K-Means k = 2 yields a 2.5× DCI gap (46.7 vs. 18.3).",
        "• 08 Mar: Sprint 2 retrospective; ML and clustering outputs handed to writing.",
    ],
    67: [
        "Sprint 3 — Documentation, Paper Submission & Review Defense",
        "Duration: 09 Mar 2026 – 25 Apr 2026 (~6 weeks)",
        "Goal: Compile the IEEE-format paper, finalise the minor project "
        "report, and prepare reviewer-defense materials.",
        "",
        "Yash Chauhan (RA2311026010170):",
        "• IEEE conference paper draft (Abstract, Introduction, Methods, "
        "Results, Discussion, Conclusion); reference list in IEEE style.",
        "• Final minor project report with seven chapters, table of contents, "
        "list of figures, list of tables, and abbreviations index.",
        "• Reproducibility audit — fixed seeds, saved CSV outputs at every "
        "boundary, README with run instructions.",
        "",
        "Shreya Srivastava (RA2311026010186):",
        "• 22 publication-ready figures at 300 DPI; figure captions cross-"
        "checked against results files.",
        "• Reviewer-defense Q&A: small-n justification, multicollinearity "
        "(VIF), HC3 vs. OLS, nested-CV vs. flat CV.",
        "• Policy-implications section drawing on SHAP and clustering: "
        "Digital Leaders vs. Emerging States playbooks.",
        "",
        "Daily Scrum highlights — Sprint 3:",
        "• 14 Mar: Paper Section 1–3 drafted; figures 1–12 finalised.",
        "• 22 Mar: Paper Sections 4–6 drafted; nested-CV table and SHAP plots embedded.",
        "• 02 Apr: Internal review pass on paper; minor report TOC/LoF/LoT generated.",
        "• 17 Apr: Final report ready (page borders, page numbers, B/W tables, "
        "architecture diagram added).",
        "• 25 Apr: Handbook compiled, sprint retros archived, submission packet ready.",
    ],
}


def replace_paragraph_block(start_idx, lines):
    """Overwrite the anchor paragraph at start_idx and the empty paragraphs
    that follow it (up to the next non-empty paragraph). Inserts new empty
    paragraphs after the trailing existing paragraph when more lines remain."""
    from docx.oxml import OxmlElement
    paras = d.paragraphs
    anchor = paras[start_idx]
    end = len(paras)
    for j in range(start_idx + 1, len(paras)):
        if paras[j].text.strip():
            end = j
            break
    # Build the writable slice of paragraph elements (XML elements, not python-docx wrappers)
    targets = [paras[i]._p for i in range(start_idx, end)]
    # If we need more paragraphs than available, append new <w:p/> after the last target
    while len(targets) < len(lines):
        new_p = OxmlElement("w:p")
        targets[-1].addnext(new_p)
        targets.append(new_p)
    # Now write each line into its target element
    from docx.text.paragraph import Paragraph
    for li, line in enumerate(lines):
        p_el = targets[li]
        para_obj = Paragraph(p_el, anchor._parent)
        # clear existing runs
        for r in list(para_obj.runs):
            r._r.getparent().remove(r._r)
        if line:
            run = para_obj.add_run(line)
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
            if li == 0:
                run.bold = True


for idx, lines in sprint_blocks.items():
    replace_paragraph_block(idx, lines)


# ── Worksheet / Data collection paragraph (idx 91) ──────────────────────────
worksheet_lines = [
    "Worksheet / Data Collection / Observations",
    "",
    "Verified primary data sources (16 Indian states, 100% complete observations):",
    "• TRAI (2024) — Tele-density (%) per state, Quarterly Indicator Report.",
    "• RBI (2024-25) — Per Capita NSDP (INR), Handbook of Statistics, Table 9.",
    "• NITI Aayog (2023-24) — SDG India Index Score per state.",
    "• NPCI / Dataful (2024-25) — UPI per-capita transactions, monthly product stats.",
    "• CPCB (2021-22) — E-waste processed (tonnes), Annual e-waste report.",
    "• Census of India (2011) — Literacy rate (%) and Urban population (%).",
    "",
    "Primary outputs of data collection:",
    "• /data/trai_state_data_final_v2.csv — unified 16-state × 15-variable table "
    "with explicit provenance columns.",
    "• /results/ — OLS, robustness, mediation, piecewise, LOO-CV, nested-CV, "
    "SHAP and clustering result files.",
    "• /figures/ fig1–fig22 — 22 publication-ready figures at 300 DPI.",
    "",
    "Key descriptive statistics (final sample, n = 16):",
    "• DAS — mean 64.95, std 19.69, range 30.27 to 94.40, median 67.02.",
    "• CEBS — mean 46.98, std 13.90, range 27.23 to 87.30, median 47.78.",
    "• DCI — mean 32.52, std 17.40, range 8.24 (Bihar) to 72.97 (Haryana).",
    "",
    "Headline observations:",
    "• Pearson r(DAS, CEBS) = 0.781, p < 0.001 — strong positive association.",
    "• OLS R² = 0.610; HC3 robust p = 1.1×10⁻⁵; bootstrap 95% CI for r = [0.648, 0.979].",
    "• Tele-density tops SHAP global importance (5.01); UPI ranks last (0.91), "
    "consistent with non-significant Sobel mediation (z = −0.241).",
    "• K-Means k = 2 separates states into Digital Leaders (DCI 46.7) and "
    "Emerging States (DCI 18.3) — a 2.5× gap.",
]
replace_paragraph_block(91, worksheet_lines)


# ── Research Article paragraph (idx 118 + 120) ──────────────────────────────
article_lines = [
    "Research Article / Publication Details",
    "",
    "Title: Digital Inclusion and Circular Economy Behavior in Indian States: "
    "A Digital Circularity Index and Explainable XGBoost Analysis.",
    "Authors: Yash Chauhan (RA2311026010170), Shreya Srivastava (RA2311026010186); "
    "Supervisor: Dr. Suresh Kumar.",
    "Affiliation: Department of Computational Intelligence, SRM Institute of "
    "Science and Technology, Kattankulathur, Tamil Nadu, India.",
    "Target venue: IEEE conference (paper formatted to IEEE conference template).",
    "Status: Manuscript drafted, figures 1–22 embedded, reference list complete; "
    "submission package prepared (paper24.pdf, paper24.tex).",
    "Patent disclosure: Not applicable.",
    "Supporting artifacts: defense-ready minor project report, reproducible code "
    "base, certificates and proofs attached separately.",
]
replace_paragraph_block(118, article_lines)


d.save(OUT)
print(f"Saved: {OUT}")
print(f"Size: {os.path.getsize(OUT):,} bytes")
