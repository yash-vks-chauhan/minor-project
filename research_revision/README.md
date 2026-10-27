Research revision and conference preparation
============================================

Prepared on 26 October 2026. The revised paper is **Digital Access, Sustainability Indicators and Formal E-Waste Processing in Indian States**. Start with `manuscript/main.pdf`; `manuscript/main.tex` is its editable source. The confirmed submission order is **Yash Chauhan, Suresh Kumar Chelliah, Shreya Srivastava**, with Yash as corresponding author and presenter. The author-review master includes their affiliation, emails, confirmed contribution roles, and no-external-funding/no-conflicts statements. It is not a venue-formatted proceedings paper or a claim of acceptance.

All changes are isolated in this folder. The original scientific files are preserved; `baseline/manifest.json` and `results/validation.json` document this. The earlier venue report outside this folder was corrected to remove an incorrect assertion about Excel input paths. Those paths were valid in the original code.

What changed and what the results support
----------------------------------------

- Reconciled public sources, replacing 13 of the original 16 UPI values with the values currently displayed in the cited secondary map. The source provides no revision history, so this does not establish why the old values differed.
- Pinned the income series to a named Economic Survey vintage; nine values differ from the older, inadequately pinned series. Vintage differences are not evidence of fabrication.
- Expanded the complete-case sample from 16 to 22 states using the government e-waste table. Six states remain excluded because the relevant entries are absent or dashed. Missing values are not zero.
- Removed shared income components from the descriptive digital and circularity-related indices; implemented actual min-max normalization. Converted e-waste totals to tonnes per million projected residents. Population and urban shares are explicitly July 2021 projections.
- Replaced invalid single-observation inner R-squared tuning with four-fold inner tuning by negative MSE inside an outer leave-one-state-out loop. Evaluated the original SDG score and log e-waste intensity separately.
- Revised the claims: unadjusted Pearson r=0.779, with an income-adjusted digital coefficient whose HC3 interval includes zero (p=0.162). Digital-only ElasticNet outer R-squared is 0.658 for SDG and 0.292 for log e-waste intensity. XGBoost is not the best-performing algorithm in these comparisons.
- Removed unsupported causal, household-behavior, threshold, and universal-index-novelty claims. Acknowledged the 2026 Giraldi et al. Digital Circularity Index paper and the limits of mixed reference years, broad SDG measurement, secondary UPI estimates, and the small ecological sample.

The changed conclusions require the revised manuscript and revised abstracts to travel together. Do not submit an old manuscript with a new abstract.

Conference sequence
-------------------

**Three applications were submitted on 26 October 2026. IOCE is Sciforum-217212, Pending MDPI check; WEAVE and Urban e-Planning were sent by email and verified in Gmail's Sent folder. Organizer confirmations and acceptances have not been verified.** The user confirmed the final Yash-first order, corresponding/presenting author, contribution roles, no external funding, no conflicts, and no previous submission before IOCE. Public-display consent was accepted after the user's instruction. Receipts, exact submitted texts/emails, and attachment hashes are saved under each venue directory. No full manuscript has been submitted. Future applications must account for all three existing abstract submissions.

| Order | Venue and deadline | Prepared file | Initial requirement | Current status |
|---|---|---|---|---|
| 1 | IOCE 2027 — submitted 26 October 2026 | `submissions/01-ioce2027/submitted_abstract.txt` | Form counts the version with AI disclosure as 280/300 | Sciforum-217212 — Pending MDPI check |
| 2 | WEAVE 2027 — 30 November 2026, 23:59 CET | `submissions/02-weave2027/extended_abstract_blind.pdf` | 800–1500-word anonymous extended abstract; 941 submitted excluding references | Sent at 22:42 IST; Gmail ID 1a17932f192eff47; await organizer confirmation |
| 3 | TiP 2027 — 10 January 2027 | `submissions/03-tip2027/extended_abstract.pdf` | At most 700 words excluding references; 535 prepared | Form inspected; simultaneous consideration prohibited by its call |
| 4 | Urban e-Planning 2027 — 15 January 2027 | `submissions/04-urban-eplanning2027/Urban_ePlanning_2027_Yash_Chauhan.docx` | Official Word form; 206-word abstract, 99-word biography | Sent at 22:47 IST; Gmail ID 1a1793793543aa3b; await organizer confirmation |

Official links, costs, presentation conditions, eligibility caveats, and remaining fields are in each venue's `submission_fields.md` and `submissions/SEQUENCE.md`. Participation/submission being free does not automatically make an optional journal publication free. IOCE's later proceedings route is advertised as free and separately reviewed; its discounted Environments journal route is paid. WEAVE's proceedings fees/publisher are not yet established. Urban e-Planning's journal discount is not a waiver. Conditional CORE, NVU, and ECO4ALL candidates remain subject to the checks in `SEQUENCE.md`.

**Next journal prepared:** the user selected Circular Economy and Sustainability's no-APC subscription route. The separate, validated nine-page journal manuscript and complete submission packet are in `submissions/06-circular-economy-sustainability/`. The original revised master and scientific outputs are unchanged. This journal has not been submitted: all three authors have approved the journal version, and the Editorial Manager draft is filled. Both required consents are complete and the portal has built the PDF. Draft reference CIES-S-26-01756 is Needs Approval; access to the generated PDF is needed for review before final submission. CORE's disabled submission links and abstract-eligibility rule were queried by email; that inquiry is not a paper submission.

IOCE used a browser submission form; Urban e-Planning used the organizer's official Word form submitted by email. `abstract_body.txt` separates each abstract from its title for accurate word counts. The review PDFs and `abstract.txt` include titles. AI assistance was disclosed in IOCE's submitted abstract and in both submission emails. Only confirmed author roles, declarations and contact details were entered. Urban's required full attendance remains to be confirmed before registration.

Files and verification
----------------------

- `DATA_PROVENANCE.md`: source URLs, precise table/page locators, vintages, extraction limits, input corrections, and units.
- `ANALYSIS_PROTOCOL.md`: exploratory specification recorded before the revised analysis ran; not a preregistration.
- `data/raw/`, `data/revised_state_dataset.csv`, `data/sample_coverage.csv`: transcriptions, complete-case data, and every exclusion.
- `evidence/`: archived government material, source tables, and SHA-256 manifest. The UPI map required browser inspection and manual transcription; a live source connection is not needed to rerun models from the saved CSV.
- `results/`: statistics, sensitivity analyses, outer predictions, all 352 fold records, held-out SHAP values, and independent validation. There are 1,408 audited inner folds and 18 prediction groups including two training-mean baselines.
- `results/submission_format_checks.json` and `qa/`: word-limit checks and rendered PDF review material.
- `requirements.lock.txt`: exact installed Python package versions. XGBoost on macOS also needs an available OpenMP runtime (`libomp`).

Reproduction from this project checkout
--------------------------------------

Use the existing `.venv-research` at the project root, or create an isolated Python environment from the lockfile. The scripts below are run from `/Users/yashchauhan/Desktop/minor project`. Input rebuilding and the original-file preservation check refer to the original project's source CSVs and baseline manifest, so this revision folder alone is not advertised as a portable independent archive.

```sh
.venv-research/bin/python research_revision/src/rebuild_inputs.py
.venv-research/bin/python research_revision/src/analyze.py --stage all --jobs 2
.venv-research/bin/python research_revision/src/validate_revision.py
.venv-research/bin/python research_revision/src/build_manuscript_tables.py
tectonic --keep-logs research_revision/manuscript/main.tex
.venv-research/bin/python research_revision/src/render_submission_pdfs.py
.venv-research/bin/python research_revision/src/check_artifacts.py
```

The nested-model cache is keyed by the revised dataset, analysis protocol, and analysis script. A change to any of them invalidates cached folds. A figure or manuscript edit alone does not require refitting models. The conference renderer uses system Times New Roman fonts; its paths are recorded in the script. Tectonic compiles the multi-file LaTeX master; Poppler renders the PDFs for visual review.

Before external submission, enter confirmed declarations in the relevant system, inspect the actual final form, and record its confirmation number and exact submitted-file hash. An opened page, local PDF, saved draft, or abstract acceptance is not proof of a completed submission, presentation invitation, or full-paper acceptance.
