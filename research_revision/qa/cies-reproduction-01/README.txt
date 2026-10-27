Digital Access, Sustainability Indicators and Formal E-Waste Processing in Indian States
Journal: Circular Economy and Sustainability
Authors: Yash Chauhan; Suresh Kumar Chelliah; Shreya Srivastava
Corresponding author: Yash Chauhan, Department of Computational Intelligence, SRM Institute of Science & Technology, Kattankulathur, Tamil Nadu, India; yash.vks.chauhan@gmail.com

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
