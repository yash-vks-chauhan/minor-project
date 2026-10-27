Revision record — 26 October 2026
=================================

| Original issue | Revised treatment | Evidence / output |
|---|---|---|
| Sixteen-state sample depended on the local spreadsheet's narrower e-waste coverage | Use all complete observations in the official FY2021–22 table: 22 states; retain explicit exclusions | `DATA_PROVENANCE.md`, `data/sample_coverage.csv` |
| State UPI inputs did not match the cited current chart for 13 legacy states | Inspect state-name/value popups; use only published whole numbers and identify the source as secondary | `data/raw/upi_percapita_2024_25.csv`, `results/input_changes.csv` |
| Income source lacked a pinned table vintage | Use Economic Survey 2025–26 Table 1.11A, FY2023–24 column, vintage 1 August 2025 | Archived one-page PDF and income CSV |
| Income was a component of both indices | Remove income from both; retain it as a regression covariate and augmented predictor | Protocol, index formula, `src/rebuild_inputs.py` |
| Paper described min-max normalization while code divided by maxima | Apply the displayed min-max formula consistently | Revised dataset and independent validation |
| Total e-waste tonnage was presented too broadly as behavior/circularity | Use population-adjusted formal collected/processed activity; explain transfers, informal omissions, and the lack of a generation denominator | Manuscript methods and limitations |
| Extended controls mixed 2011 urban shares/literacy with newer data | Use consistently dated July 2021 population and urban-share projections; omit literacy | MoHFW Tables 11/13, raw CSVs |
| Inner LOO scored by R-squared is undefined with one-observation folds | Four-fold inner negative-MSE tuning inside outer state holdouts, with fitting inside training folds | `results/nested_cv_audit.json`, all fold records |
| Predicted composite could be dominated by broad development and sample normalization | Predict SDG and log e-waste separately on their original/log units; keep the DCI descriptive | All model/feature outcomes in `nested_cv_results.csv` |
| XGBoost and causal/threshold/behavior claims exceeded support | Report regularized linear models' stronger observed performance and uncertain income-adjusted estimates | Revised master and all four abstracts |
| Digital Circularity Index name was presented as novel | Cite Giraldi, Rossi, and Olivieri (2026), and distinguish this Indian-state measurement exercise | Revised introduction and references |
| Research-assistant review incorrectly said Excel file paths were wrong | Correct the prior venue-review report: the original code's `DATA_DIR = BASE_DIR` makes those paths valid | `../output/research/venue-review-2026-10-26.md` |
| Multiple submissions risked incompatible originality/publication commitments | Prepare local venue-specific drafts and proceed one venue at a time, checking the applicable rules before dispatch | `submissions/SEQUENCE.md` |

The original scientific manuscripts, scripts, and data were not edited. Their preserved hashes are checked by `src/validate_revision.py`. Input corrections, source-vintage changes, scientific reinterpretation, and the correction to the assistant's earlier path diagnosis are distinguished rather than treated as the same kind of error.
