"""Prepare a separate journal packet without changing the scientific master."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import re
import shutil
import subprocess
from xml.sax.saxutils import escape

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

from render_journal_figure import render

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
OUT = REV / 'submissions/06-circular-economy-sustainability'
SRC = OUT / 'source'
SUPP = OUT / 'supplement'
TITLE = 'Digital Access, Sustainability Indicators and Formal E-Waste Processing in Indian States'
AUTHORS = 'Yash Chauhan; Suresh Kumar Chelliah; Shreya Srivastava'
IDENTITY = f'{TITLE}\nJournal: Circular Economy and Sustainability\nAuthors: {AUTHORS}\nCorresponding author: Yash Chauhan, Department of Computational Intelligence, SRM Institute of Science & Technology, Kattankulathur, Tamil Nadu, India; yash.vks.chauhan@gmail.com\n'
ABSTRACT = (
    'Digital inclusion and circular economy policies share an interest in information access and service coordination, '
    'but their empirical association depends on how development indicators are constructed. This exploratory study '
    'combines seven traceable public input tables for 22 Indian states, covering telecommunications, digital payments, '
    'income, sustainability, formal e-waste processing, and projected population characteristics. A digital access score '
    'and a circularity-related proxy are constructed without shared income components. State resampling, '
    'income-adjusted regression, and nested predictive evaluation distinguish broad sustainability performance from '
    'formal material-processing activity. The index association is positive (Pearson r=0.779; Spearman rho=0.810), '
    'but the digital-access coefficient is uncertain after income adjustment (robust p=0.162). Digital-only ElasticNet '
    'achieves pooled outer leave-one-state-out R-squared of 0.658 for the Sustainable Development Goals composite '
    'and 0.292 for log e-waste processing intensity. Extreme gradient boosting does not improve this comparison. '
    'The findings support a descriptive connection with broader development capacity while providing more limited '
    'evidence for formal circular material processing. Mixed reference years, state-level aggregation, rounded '
    'secondary payment estimates, projected denominators, missing-state selection, and the small sample prevent '
    'causal or prospective forecasting claims. Environmental monitoring should distinguish broad sustainability '
    'indicators from direct evidence of collection, repair, reuse, and material recovery.'
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pdf_text(path, title, paragraphs):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('PacketTitle', fontName='Times-Bold', fontSize=14, leading=17, spaceAfter=14, textColor=colors.black))
    styles.add(ParagraphStyle('PacketBody', fontName='Times-Roman', fontSize=10.5, leading=14, spaceAfter=10, alignment=TA_LEFT))
    story = [Paragraph(escape(title), styles['PacketTitle'])]
    story.extend(Paragraph(escape(p).replace('\n', '<br/>'), styles['PacketBody']) for p in paragraphs)
    doc = SimpleDocTemplate(str(path), pagesize=(8.27*inch, 11.69*inch),
                            rightMargin=.85*inch, leftMargin=.85*inch, topMargin=.75*inch,
                            bottomMargin=.75*inch, title=title, author=AUTHORS)
    doc.build(story)


def zip_tree(folder, output):
    with ZipFile(output, 'w', ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(folder.rglob('*')):
            if f.is_file():
                z.write(f, str(f.relative_to(folder)))


def main():
    SRC.mkdir(parents=True, exist_ok=True)
    SUPP.mkdir(parents=True, exist_ok=True)
    baseline = {str(p.relative_to(REV)): sha(p) for p in [REV/'manuscript/main.tex', REV/'manuscript/main.pdf', REV/'data/revised_state_dataset.csv', REV/'src/analyze.py', REV/'ANALYSIS_PROTOCOL.md']}
    assert 150 <= len(ABSTRACT.split()) <= 250
    text = (REV/'manuscript/main.tex').read_text()
    text = text.replace(r'\fancyhead[R]{\small Author review draft}', r'\fancyhead[R]{\small Original research manuscript}')
    text = text.replace(r'\setlength{\headheight}{14pt}', r'\setlength{\headheight}{14pt}'+'\n'+r'\renewcommand{\topfraction}{0.95}'+'\n'+r'\renewcommand{\textfraction}{0.05}'+'\n'+r'\renewcommand{\floatpagefraction}{0.8}')
    text = text.replace(r'\input{generated_results.tex}', r'\usepackage{caption}'+'\n'+r'\captionsetup[figure]{name=Fig.,labelfont=bf,labelsep=space}'+'\n'+r'\input{generated_results.tex}')
    text = text.replace(r'\footnotesize $^{*}$Corresponding author: Yash Chauhan\\[5pt]', r'\footnotesize $^{*}$Corresponding author: Yash Chauhan; ORCID: 0009-0005-4077-5446\\[5pt]')
    text = text.replace(r'\small Revised analysis: 26 October 2026', r'\small Manuscript prepared: 26 October 2026')
    start, end = text.index(r'\begin{abstract}'), text.index(r'\end{abstract}')+len(r'\end{abstract}')
    text = text[:start]+r'\begin{abstract}'+'\n'+ABSTRACT+'\n'+r'\end{abstract}'+text[end:]
    text = text.replace('nested cross-validation.\n', 'nested cross-validation.\n\\textbf{JEL classification:} Q53; O33; C52.\n', 1)
    text = text.replace('while the SDG India Index composite', 'while the Sustainable Development Goals (SDG) India Index composite')
    text = text.replace('Digital Circularity Index for 14 Italian', 'Digital Circularity Index (DCI) for 14 Italian')
    text = text.replace('Table~\\ref{tab:sources} summarizes the seven analytical inputs.', 'Table~\\ref{tab:sources} summarizes the seven analytical inputs. Income is measured by per-capita net state domestic product (NSDP).')
    text = text.replace('The digital access score $D_i$', 'The digital access score (DAS) $D_i$')
    text = text.replace('OLS models estimate', 'Ordinary least-squares (OLS) models estimate')
    text = text.replace('Inference uses HC3 standard errors', 'Inference uses heteroskedasticity-consistent HC3 standard errors')
    text = text.replace('Ridge, ElasticNet, Random Forest, and XGBoost', 'Ridge, ElasticNet, Random Forest, and extreme gradient boosting (XGBoost)')
    text = text.replace('Held-out SHAP summaries', 'Held-out Shapley additive explanations (SHAP) summaries')
    boundary = r'\section{Results}'
    assert boundary in text
    ai = r'''\subsection{Software and generative AI assistance}
Python was used for data preparation and statistical analysis, with NumPy, pandas, SciPy, statsmodels, scikit-learn, XGBoost, and SHAP; exact versions and executable scripts are provided in Online Resource~1. Matplotlib was used to create the figures from the recorded data and results. OpenAI Codex assisted with source checking, Python analysis implementation, manuscript revision, and submission text preparation. Numerical statements are linked to executable outputs and validation records. The human authors retain responsibility for the sources, analysis, interpretation, and final manuscript.

'''
    text = text.replace(boundary, ai+boundary)
    text = text.replace(r'\includegraphics[width=\linewidth]{../figures/association.png}', r'\includegraphics[width=\linewidth]{Fig1.pdf}')
    text = text.replace('Digital access against the combined proxy (left) and log formal e-waste intensity (right). Colour denotes log per-capita NSDP. Each point is a state; selected labels show influential or substantively relevant observations.', 'Digital access against (a) the combined proxy and (b) log formal e-waste intensity. Color denotes the natural logarithm of per-capita net state domestic product. Each point is a state; selected labels identify influential or substantively relevant observations')
    s = text.index(r'\section*{Data, code, and research statements}')
    e = text.index(r'\begin{thebibliography}', s)
    declarations = r'''\section*{Supplementary information}
Online Resource~1 (ESM\_1.zip) contains the seven raw input transcriptions, source extraction records and locators, revised 22-state dataset, coverage decisions, exploratory analysis protocol, executable Python scripts, exact software versions, statistical outputs, outer predictions, tuning splits and parameter audits. Its README identifies the article and authors and explains how to reproduce the analysis. The primary public source reports are linked and identified by hashes rather than redistributed in full.

\section*{Statements and Declarations}
\textbf{Funding.} This research received no external funding.

\textbf{Competing interests.} The authors declare no conflicts of interest.

\textbf{Author contributions.} Yash Chauhan: conceptualization, methodology, software, validation, formal analysis, data curation, writing---original draft, writing---review and editing, and visualization. Suresh Kumar Chelliah: supervision. Shreya Srivastava: investigation and writing---review and editing.

\textbf{Data availability.} The data underlying this exploratory comparison, raw transcriptions, coverage records, source locators, and extraction evidence are provided in Online Resource~1. The publicly available source documents are identified in Table~\ref{tab:sources} and the reference list. No public repository DOI is claimed.

\textbf{Code availability.} The analysis scripts, software versions, recorded cross-validation splits, fitted-parameter selections, and outer predictions are provided in Online Resource~1. The original cached fold records are included to permit output auditing; the README also explains how to refit independently.

\begin{samepage}
\textbf{Ethics and consent.} This study uses publicly available aggregate state-level statistics. It did not recruit participants or use individual-level personal information. No individual consent-to-publication issue arises from these data.
\par\end{samepage}

'''
    text = text[:s]+declarations+text[e:]
    # No undefined TeX-side source paths may remain in the self-contained journal source.
    assert '../' not in text and 'Author review draft' not in text
    (SRC/'main.tex').write_text(text)
    for name in ['generated_results.tex', 'regression_table.tex', 'cv_table.tex', 'state_table.tex']:
        shutil.copy2(REV/'manuscript'/name, SRC/name)
    render(REV/'data/revised_state_dataset.csv', SRC)
    (OUT/'abstract.txt').write_text(ABSTRACT+'\n')

    # Preserve relative paths needed by the unchanged analysis and input-rebuild scripts.
    rels = ['requirements.lock.txt', 'ANALYSIS_PROTOCOL.md', 'DATA_PROVENANCE.md',
            'src/analyze.py', 'src/rebuild_inputs.py', 'src/build_manuscript_tables.py',
            'src/render_journal_figure.py', 'data/revised_state_dataset.csv', 'data/sample_coverage.csv',
            'manuscript/generated_results.tex', 'manuscript/regression_table.tex',
            'manuscript/cv_table.tex', 'manuscript/state_table.tex']
    rels += [str(p.relative_to(REV)) for p in (REV/'data/raw').glob('*.csv')]
    rels += [str(p.relative_to(REV)) for p in (REV/'evidence').glob('*') if p.suffix in ['.json', '.txt', '.jpeg', '.html']]
    rels = [x for x in rels if x != 'evidence/manifest.json']
    rels += [str(p.relative_to(REV)) for p in (REV/'results').glob('*') if p.suffix in ['.csv', '.json'] and p.name not in ['artifact_checks.json', 'submission_format_checks.json', 'validation.json']]
    rels += [str(p.relative_to(REV)) for p in (REV/'results/folds').glob('*.json')]
    for rel in rels:
        dst = SUPP/'research_revision'/rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REV/rel, dst)
    for rel in ['data/raw/niti_sdg_index_2023_24.csv', 'data/unified_state_dataset.csv']:
        dst = SUPP/rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT/rel, dst)
    (SUPP/'research_revision/manuscript').mkdir(exist_ok=True)
    shutil.copy2(REV/'evidence/manifest.json', SUPP/'source_evidence_inventory_original.json')
    readme = IDENTITY+'''
Online Resource 1: Reproducibility data and code

The current analysis uses research_revision/data/revised_state_dataset.csv (22 states).
The root data/ files are retained solely because the original scripts use them to
enumerate all 28 states and document a legacy comparison. The root 16-state file is
NOT the dataset used for the journal's revised estimates or model validation.

Python reference environment: 3.14.7; exact installed versions are in
research_revision/requirements.lock.txt and results/runtime.json. XGBoost may
require a platform OpenMP runtime (libomp on macOS).

From this extracted directory, using your chosen Python environment:
  python -m pip install -r research_revision/requirements.lock.txt
  python research_revision/src/rebuild_inputs.py
  python research_revision/src/analyze.py --stage stats
  python research_revision/src/analyze.py --stage models --jobs 2
  python research_revision/src/analyze.py --stage figures
  python research_revision/src/build_manuscript_tables.py
  python research_revision/src/render_journal_figure.py

The model command reuses the supplied 352 fold records only when the hash of the
dataset, protocol and analysis code matches. For an independent model refit, move
research_revision/results/folds to a different directory before running it; the
command will then refit every outer/inner split. The supplied cached scores are
the original fits, not independent replications. Tuning uses negative mean squared
error in four-fold inner validation and leave-one-state-out outer evaluation.

The complete primary government PDFs are not redistributed. Source URLs, table
and page locators, text extractions and original evidence hashes identify them.
source_evidence_inventory_original.json records the complete local source archive,
including PDFs not supplied here. MANIFEST.json inventories the files actually
included in this supplement. No conference account links, browser screenshots,
submission receipts, local virtual environment, or authentication material is included.

OpenAI Codex assisted source checking, Python analysis implementation, manuscript
revision and submission preparation. The human authors remain responsible for
the work. This is an exploratory reanalysis, not a preregistration or an
independent validation dataset. Study limitations are described in the manuscript.
'''
    (SUPP/'README.txt').write_text(readme)
    manifest = [{'file':str(p.relative_to(SUPP)), 'sha256':sha(p), 'bytes':p.stat().st_size} for p in sorted(SUPP.rglob('*')) if p.is_file() and p.name!='MANIFEST.json']
    (SUPP/'MANIFEST.json').write_text(json.dumps(manifest, indent=2)+'\n')
    zip_tree(SUPP, OUT/'ESM_1.zip')

    cover = [
        '26 October 2026\nEditors-in-Chief\nCircular Economy and Sustainability',
        f'Dear Editors,\nPlease consider "{TITLE}" as an original research article.',
        'The study examines a measurement problem relevant to circular-economy assessment: broad sustainability scores and formal material-processing activity can produce different associations with digital access. Using seven source-reconciled public input tables for 22 Indian states, the paper separates descriptive index association, income adjustment, and outcome-specific nested predictive evaluation. It connects digital infrastructure and regional development with environmental measurement without claiming causal infrastructure effects or novelty for the Digital Circularity Index name.',
        'The descriptive association is positive (Pearson r=0.779), but the digital coefficient is uncertain after income adjustment (robust p=0.162). Digital-only ElasticNet predicts the broad sustainability composite more strongly than log e-waste processing intensity. Mixed years, projected denominators, incomplete reporting and the small ecological sample constrain interpretation. A self-contained data/code supplement and editable LaTeX source accompany the manuscript.',
        'Related conference abstracts have been submitted to IOCE 2027 (Sciforum-217212, pending MDPI check), WEAVE 2027 and Urban e-Planning 2027 (submission emails sent; organizer confirmations pending). No acceptance or publication has been verified. No full manuscript has been submitted to another venue. Copies of the related abstracts are supplied separately for editorial assessment; they are not part of the proposed journal article or its public supplement. A procedural inquiry to CORE 2027 did not include a manuscript.',
        'The research received no external funding; the authors declare no conflicts of interest. OpenAI Codex assisted source checking, Python analysis implementation, manuscript revision and submission text preparation, as disclosed in Methods. Yash Chauhan is first and corresponding author, followed by Suresh Kumar Chelliah and Shreya Srivastava. We seek the subscription publication route with no APC.',
        'Kind regards,\nYash Chauhan\nDepartment of Computational Intelligence\nSRM Institute of Science & Technology, Kattankulathur, India\nyash.vks.chauhan@gmail.com\nORCID: 0009-0005-4077-5446',
    ]
    (OUT/'cover_letter.txt').write_text('\n\n'.join(cover)+'\n')
    pdf_text(OUT/'cover_letter.pdf', 'Cover letter', cover)
    writer = PdfWriter()
    related = [REV/'submissions/01-ioce2027/abstract_body_with_ai_disclosure.txt', REV/'submissions/02-weave2027/extended_abstract_blind.pdf', REV/'submissions/04-urban-eplanning2027/abstract.pdf']
    # IOCE's actual submission includes the AI disclosure, unlike its earlier review PDF.
    ioce = (REV/'submissions/01-ioce2027/submitted_abstract.txt').read_text().strip()
    pdf_text(OUT/'ioce_related_abstract_editor_only.pdf', 'IOCE 2027 related abstract', [TITLE, ioce])
    for path in [OUT/'ioce_related_abstract_editor_only.pdf', related[1], related[2]]:
        writer.append(PdfReader(path))
    writer.add_metadata({'/Title':'Related conference abstracts for editorial assessment only', '/Author':AUTHORS})
    with (OUT/'related_abstracts_editor_only.pdf').open('wb') as f: writer.write(f)
    for rel, digest in baseline.items():
        assert sha(REV/rel)==digest, rel
    record = {'status':'prepared; not submitted', 'journal':'Circular Economy and Sustainability', 'publication_route':'subscription; no APC', 'abstract_words':len(ABSTRACT.split()), 'keywords':6, 'jel_codes':['Q53','O33','C52'], 'master_and_science_hashes_unchanged':baseline, 'supplement_files':len(manifest), 'supplement_bytes':(OUT/'ESM_1.zip').stat().st_size, 'final_journal_version_coauthor_approval':'not yet specifically confirmed; review this prepared version before dispatch', 'sources':{'guidelines':'https://link.springer.com/journal/43615/submission-guidelines', 'fees':'https://link.springer.com/journal/43615/how-to-publish-with-us'}, 'browser_portal':'https://www.editorialmanager.com/cies/default.aspx'}
    (OUT/'preparation_record.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))


if __name__=='__main__': main()
