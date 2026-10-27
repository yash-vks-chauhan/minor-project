# Digital Access, Sustainability Indicators and Formal E-Waste Processing in Indian States

## Research question and motivation

Digital transformation and circular economy transitions share an interest in information, coordination, and access to services. Digital systems may help actors exchange information, track materials, and organize collection or reuse. However, regions with stronger digital infrastructure may also have higher incomes, more formal industry, or better administrative reporting. A positive digital-sustainability correlation can therefore be easier to obtain than an independent relationship with circular activity. This study asks whether digital access is associated with a circularity-related proxy across Indian states and whether that pattern extends to formal e-waste processing when the outcome is considered separately.

Variation across Indian states exposes a measurement problem relevant to simultaneous digital, ecological, and inclusive transformations: a composite development benchmark and a direct material-processing indicator may support different conclusions. The objective is an exploratory comparison, not a causal investment estimate.

## Conceptual framing and contribution

Circular economy measurement concerns keeping resources in productive use and is not equivalent to a general sustainability score (Geissdoerfer et al., 2017). A digital access proxy based on subscriptions and payments likewise does not observe adoption of particular repair, reuse, or recycling platforms. These distinctions motivate separate analysis of broad development and formal material-processing activity. Explicit normalization, weighting, and sensitivity analysis follow the measurement concerns described in the OECD composite-indicator handbook (OECD et al., 2008).

The Digital Circularity Index name is not claimed as novel. Giraldi et al. (2026) develop an index for 14 Italian metropolitan cities using platform-adoption measures and partial least squares path modelling. This study instead examines general digital access in Indian states and separates the outcomes: predictors of the overall SDG composite need not predict formal processing with comparable strength.

## Data and method

Seven analytical input tables were reconciled from public sources: TRAI tele-density on 30 June 2024; whole-number UPI transactions/person for FY2024-25 published by Dataful using NPCI data; FY2023-24 current-price per-capita NSDP in Economic Survey 2025-26; the SDG India Index 2023-24 composite; CPCB formal e-waste collected and processed in FY2021-22; and population and urban-share projections for 1 July 2021 from the MoHFW Technical Group's 2020 report. The latter are projections, not Census 2021 enumerations.

All 28 states were considered. Twenty-two had complete observations; six were excluded because the cited e-waste table contained no usable value. Missing entries were not converted to zero. Union Territories were excluded to retain a consistent administrative comparison. The source locators, transcriptions, coverage decisions, analysis specification, and executable outputs are retained in an accompanying research package. UPI remains a secondary, rounded series that excludes transactions without state attribution.

The digital access score combines min-max-normalized tele-density and UPI/person in a 4:3 ratio. A circularity-related proxy combines normalized e-waste tonnes per million projected residents and the SDG score in a 7:8 ratio. These ratios retain the earlier relative weights after removing income from both definitions. Their product divided by 100 is a descriptive DCI. Weights were documented before executing this exploratory, non-preregistered reanalysis.

Association is evaluated with Pearson and Spearman coefficients, state bootstrap resampling, permutation testing, and regressions with HC3 standard errors. Log income is included in adjusted specifications. Sensitivities vary weights, omit Haryana, delete each state in turn, and separate the component outcomes. For prediction, the targets are the original SDG composite and log(1 + formal e-waste tonnes per million people), not a full-sample-normalized index. Digital-only predictors are tele-density and UPI/person; augmented models add log income, projected urban share, and log population.

Ridge, ElasticNet, Random Forest, and XGBoost are evaluated with outer leave-one-state-out validation and shuffled four-fold inner tuning by negative mean squared error. Scaling is fitted within training pipelines. R-squared is computed from pooled outer predictions, avoiding an undefined single-observation fold score. An outer-training-mean prediction supplies the baseline. Exact outer and inner splits, finite tuning scores, parameters, and held-out predictions are recorded.

## Findings

The descriptive digital/proxy association is positive: Pearson r=0.779 and Spearman rho=0.810. The state-bootstrap percentile interval for Pearson correlation is 0.617-0.901, and the permutation p-value is 0.00005. Without Haryana, Pearson r is 0.778; across every one-state deletion it ranges from 0.734 to 0.819. Equal component weights give r=0.741. These checks describe sensitivity within the observed cohort, rather than independent replications.

Income adjustment materially changes the inference. The proxy coefficient per ten digital-access points is 3.961, with an HC3 p-value of 0.162; its confidence interval includes zero. For unlogged formal e-waste intensity alone, Pearson r is 0.365 (p=0.095), while Spearman rho is 0.677. The Pearson association increases to 0.642 when e-waste intensity is log-transformed. Outcome definition and skewness therefore matter to interpretation.

Digital-only ElasticNet achieves pooled outer R-squared of 0.658 for SDG scores, compared with 0.292 for log e-waste intensity. Corresponding digital-only XGBoost scores are 0.555 and 0.078. The more flexible model does not improve the observed comparison, and augmented features do not consistently improve predictions. These results support a distinction between broad development predictability and more limited material-processing predictability.

## Implications and limitations

The findings support outcome-specific evaluation of connections among digital access, inclusive development, and circular activity. They do not establish that connectivity independently increases recycling, identify a policy threshold, or validate causal recommendations from model explanations.

Several limits remain. The digital measures postdate the e-waste reporting period, so the prediction exercise is retrospective, not a prospective forecast. Formal processing may include material from other states and excludes unrecorded informal activity. State averages cannot establish individual behavior, and complete-case selection may favor reporting capacity. Rounded UPI estimates, projected population denominators, possible spatial dependence, multiple exploratory specifications, and only 22 observations constrain inference. Future work should align administrative records by year, expand direct repair and recovery measures, and validate models on new regions or later outcomes. Such evidence is needed before a descriptive connection can justify intervention design.

## References

Geissdoerfer, M., Savaget, P., Bocken, N. M. P., & Hultink, E. J. (2017). The circular economy: A new sustainability paradigm? Journal of Cleaner Production, 143, 757-768. https://doi.org/10.1016/j.jclepro.2016.12.048

Giraldi, L., Rossi, L., & Olivieri, M. (2026). Digital platforms and composite measurement of an urban circular economy: Developing the digital circularity index. Technology in Society, 86, 103322. https://doi.org/10.1016/j.techsoc.2026.103322

OECD/European Union/EC-JRC. (2008). Handbook on constructing composite indicators: Methodology and user guide. OECD Publishing. https://doi.org/10.1787/9789264043466-en
