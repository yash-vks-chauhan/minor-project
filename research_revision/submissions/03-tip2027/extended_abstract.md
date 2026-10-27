# DIGITAL ACCESS, SUSTAINABILITY INDICATORS AND FORMAL E-WASTE PROCESSING IN INDIAN STATES

## Background/Motivation

Digital inclusion and circular economy policies may share information and coordination needs, but an apparent connection can reflect common development conditions. A general sustainability score and a measure of material processing are not interchangeable. This study examines that distinction through an exploratory comparison of Indian states, with practical relevance to the sustainability of data-driven economies.

## Purpose

The study asks whether digital access is associated with a circularity-related proxy, whether the relationship remains clear after income adjustment, and whether digital indicators predict broad sustainability and formal e-waste processing with similar strength. The objective is to support more careful measurement and policy interpretation, rather than estimate a causal return to connectivity investment.

## Theoretical framework

Circular economy performance should be connected to material loops rather than assumed from general development (Geissdoerfer et al., 2017). Composite indices require explicit normalization, weights, and sensitivity checks (OECD et al., 2008). Giraldi et al. (2026) already develop a Digital Circularity Index for Italian metropolitan cities. This study complements that work through Indian-state indicators and separate outcome validation; it does not claim that the index name is new.

## Design/methodology/approach

Seven traceable input tables cover telecommunications, secondary digital payment estimates, income, SDG scores, formal e-waste collected and processed, and projected population characteristics. Twenty-two states have complete observations. Six are excluded because their e-waste values are absent or dashed, without treating missingness as zero. Sources span FY2021-22 to FY2024-25. Population and urban shares are published July 2021 projections, not census enumerations.

Digital access combines normalized tele-density and UPI transactions/person. The circularity-related proxy combines formal e-waste tonnes per million residents and the SDG composite. Income is excluded from both definitions. Pearson and Spearman association, bootstrap resampling, permutation testing, and HC3 regressions are accompanied by weight and state-deletion sensitivities. Predictive targets are the original SDG score and log e-waste intensity, analyzed separately. Four algorithms use outer leave-one-state-out evaluation and four-fold inner tuning by negative mean squared error, with preprocessing fitted inside training folds.

## Findings and conclusions

Digital access and the combined proxy show Pearson r=0.779 and Spearman rho=0.810, with a bootstrap interval of 0.617-0.901 for Pearson correlation. After log-income adjustment, the digital-access coefficient is uncertain (HC3 p=0.162). The unlogged e-waste-only association is weaker (Pearson r=0.365; p=0.095). Digital-only ElasticNet achieves outer R-squared of 0.658 for SDG scores and 0.292 for log e-waste intensity. XGBoost does not improve these results. The pattern supports a descriptive development connection, with more limited evidence for an independent circular-processing relationship.

## Research, practical and social implications

Environmental and digital programs may benefit from compatible reporting and service information, but this study cannot identify an infrastructure investment effect or a policy threshold. Formal processing can include inter-state material transfers and omit informal activity. Digital measures postdate the e-waste period, preventing prospective forecasting and causal claims. Rounded payment estimates, projected denominators, missing-state selection, and the small ecological sample further constrain interpretation. Future research should align years and use direct repair, reuse, and recovery measures.

## Originality/value

The contribution is an auditable state comparison that separates broad sustainability from formal material-processing outcomes and documents income adjustment and nested validation. Its value is in clarifying what a digital-sustainability association can support, including when a more complex model adds little.

## Keywords

Digital inclusion; circular economy; sustainability indicators; e-waste; India.

## References

Geissdoerfer, M., Savaget, P., Bocken, N. M. P., & Hultink, E. J. (2017). The circular economy: A new sustainability paradigm? Journal of Cleaner Production, 143, 757-768. https://doi.org/10.1016/j.jclepro.2016.12.048

Giraldi, L., Rossi, L., & Olivieri, M. (2026). Digital platforms and composite measurement of an urban circular economy: Developing the digital circularity index. Technology in Society, 86, 103322. https://doi.org/10.1016/j.techsoc.2026.103322

OECD/European Union/EC-JRC. (2008). Handbook on constructing composite indicators: Methodology and user guide. OECD Publishing. https://doi.org/10.1787/9789264043466-en
