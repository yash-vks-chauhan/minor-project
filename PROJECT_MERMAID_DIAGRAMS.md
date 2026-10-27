# Project Mermaid Diagrams

This file contains Mermaid code for the major system diagrams for the project:
"Digital Inclusion as a Driver of Circular Economy Behavior in India".

Note:
- Mermaid does not support native UML use case, component, or deployment diagrams.
- Those are represented here as structured `flowchart` diagrams so they remain renderable in Mermaid.

## 1. Data Flow Diagram (DFD)

```mermaid
flowchart LR
    R["Researcher"]

    subgraph Sources["Government Data Sources"]
        TRAI["TRAI<br/>Tele-density"]
        RBI["RBI<br/>Per Capita NSDP"]
        NITI["NITI Aayog<br/>SDG Index"]
        NPCI["NPCI / Dataful<br/>UPI per capita"]
        CPCB["CPCB<br/>E-waste processed"]
        CENSUS["Census 2011<br/>Literacy, Urbanization, Population"]
    end

    P1["Web Scraping and Data Collection"]
    D1[("Raw Source Tables / Files")]
    P2["Validation, Cleaning, and Standardization"]
    P3["Inner Join and Unified Dataset Creation"]
    D2[("Unified Dataset<br/>16 states x 15 variables")]
    P4["Composite Index Engineering<br/>DAS, CEBS, DCI"]
    D3[("Analytical Dataset")]
    P5["EDA and Visualization"]
    P6["Statistical Hypothesis Testing<br/>OLS, controls, mediation, threshold"]
    P7["Robustness Defense<br/>bootstrap, HC3, permutation, sensitivity"]
    P8["ML Validation<br/>LOO-CV, nested CV, repeated K-Fold"]
    P9["Explainability and Clustering<br/>SHAP, K-Means, PCA"]
    D4[("Figures, Result Files, Reports")]
    P10["IEEE Paper / Final Report"]

    R --> P1
    TRAI --> P1
    RBI --> P1
    NITI --> P1
    NPCI --> P1
    CPCB --> P1
    CENSUS --> P1

    P1 --> D1 --> P2 --> P3 --> D2 --> P4 --> D3
    D3 --> P5 --> D4
    D3 --> P6 --> P7 --> D4
    D3 --> P8 --> P9 --> D4
    D4 --> P10 --> R
```

## 2. Component Diagram

```mermaid
flowchart LR
    subgraph SRC["Project Components"]
        C1["01_data_engineering.py"]
        C2["02_eda_visualizations.py"]
        C3["03_statistical_analysis.py"]
        C4["04_reviewer_defense.py"]
        C5["05_predictive_modeling.py"]
        C6["06_advanced_ml.py"]
    end

    RAW[("Raw government datasets")]
    DATA[("unified_state_dataset.csv")]
    EDAF[("EDA figures<br/>fig1-fig8")]
    STATS[("Statistical results")]
    DEFENSE[("Robustness outputs<br/>fig10-fig12")]
    MLRES[("ML outputs<br/>fig13-fig16")]
    ADVRES[("SHAP / clustering / PCA<br/>fig17-fig22")]
    PAPER[("paper.tex / final report")]

    RAW --> C1 --> DATA
    DATA --> C2 --> EDAF
    DATA --> C3 --> STATS
    C3 --> C4
    DATA --> C4 --> DEFENSE
    DATA --> C5 --> MLRES
    C4 --> C5
    DATA --> C6
    C5 --> C6 --> ADVRES

    EDAF --> PAPER
    STATS --> PAPER
    DEFENSE --> PAPER
    MLRES --> PAPER
    ADVRES --> PAPER
```

## 3. Use Case Diagram

```mermaid
flowchart LR
    Researcher["Researcher"]
    Portals["Government Portals"]
    Pipeline["ML Pipeline"]

    UC1([Scrape verified state-wise data])
    UC2([Validate and clean data])
    UC3([Merge data with inner join])
    UC4([Compute DAS, CEBS, and DCI])
    UC5([Run EDA and create figures])
    UC6([Test H1, H2, and H3])
    UC7([Run robustness checks])
    UC8([Validate findings with ML])
    UC9([Explain predictions with SHAP])
    UC10([Cluster states and run PCA])
    UC11([Generate final report and paper])

    Researcher --> UC1
    Researcher --> UC4
    Researcher --> UC5
    Researcher --> UC6
    Researcher --> UC7
    Researcher --> UC8
    Researcher --> UC9
    Researcher --> UC10
    Researcher --> UC11

    Portals --> UC1
    Portals --> UC2
    Pipeline --> UC8
    Pipeline --> UC9
    Pipeline --> UC10

    UC1 --> UC2 --> UC3 --> UC4 --> UC5 --> UC6 --> UC7 --> UC8 --> UC9 --> UC10 --> UC11
```

## 4. Sequence Diagram

```mermaid
sequenceDiagram
    actor Researcher
    participant GP as Government Portals
    participant S1 as 01_data_engineering.py
    participant S2 as 02_eda_visualizations.py
    participant S3 as 03_statistical_analysis.py
    participant S4 as 04_reviewer_defense.py
    participant S5 as 05_predictive_modeling.py
    participant S6 as 06_advanced_ml.py
    participant Paper as paper.tex / Final Report

    Researcher->>S1: Start project pipeline
    S1->>GP: Scrape 7 official sources
    GP-->>S1: State-wise raw data
    S1->>S1: Validate, clean, standardize
    S1->>S1: Inner join across sources
    S1->>S1: Compute DAS, CEBS, DCI
    S1-->>S2: Unified analytical dataset

    S2->>S2: Generate EDA figures and rankings
    S2-->>S3: Dataset + EDA context

    S3->>S3: Run OLS and statistical tests
    S3-->>S4: Primary results

    S4->>S4: Bootstrap, sensitivity, HC3, permutation
    S4-->>S5: Defended findings

    loop LOO-CV / Nested CV
        S5->>S5: Train and validate ML models
    end
    S5-->>S6: Predictions and model outputs

    S6->>S6: Compute SHAP values
    S6->>S6: Run K-Means clustering and PCA
    S6-->>Paper: Advanced ML figures and findings
    S2-->>Paper: EDA figures
    S3-->>Paper: Statistical results
    S4-->>Paper: Robustness results
    S5-->>Paper: ML validation results

    Researcher->>Paper: Compile IEEE paper
    Paper-->>Researcher: Submission-ready deliverables
```

## 5. Deployment Diagram

```mermaid
flowchart TB
    subgraph EXT["External Sources"]
        GOV["Government portals<br/>TRAI, RBI, NITI Aayog, NPCI/Dataful, CPCB, Census"]
    end

    subgraph LOCAL["Local Machine"]
        subgraph ENV["Python 3.11 Environment"]
            L1["pandas, numpy"]
            L2["scipy, statsmodels"]
            L3["scikit-learn, xgboost"]
            L4["shap"]
            L5["matplotlib, seaborn"]
        end

        subgraph CODE["Project Scripts"]
            S1["01_data_engineering.py"]
            S2["02_eda_visualizations.py"]
            S3["03_statistical_analysis.py"]
            S4["04_reviewer_defense.py"]
            S5["05_predictive_modeling.py"]
            S6["06_advanced_ml.py"]
        end

        STORE[("Local data / figures / results")]
    end

    subgraph OUT["Outputs"]
        F1["22 Figures"]
        F2["18 Result Files"]
        F3["Final Paper / Report"]
    end

    GOV --> S1

    L1 --> S1
    L1 --> S2
    L2 --> S3
    L2 --> S4
    L3 --> S5
    L3 --> S6
    L4 --> S6
    L5 --> S2
    L5 --> S5
    L5 --> S6

    S1 --> STORE
    STORE --> S2
    STORE --> S3
    STORE --> S4
    STORE --> S5
    STORE --> S6

    S2 --> F1
    S3 --> F2
    S4 --> F2
    S5 --> F2
    S6 --> F2
    F1 --> F3
    F2 --> F3
```

## 6. Activity / Workflow Diagram

```mermaid
flowchart TD
    A["Identify research gap"] --> B["Select 7 official government data sources"]
    B --> C["Scrape and collect state-wise data"]
    C --> D{"Verified data available<br/>for all required sources?"}
    D -- Yes --> E["Keep state in analysis"]
    D -- No --> F["Exclude state<br/>(no imputation)"]
    E --> G["Create unified dataset"]
    F --> G
    G --> H["Compute DAS, CEBS, DCI"]
    H --> I["Perform EDA"]
    I --> J["Run statistical hypothesis tests"]
    J --> K{"Results robust?"}
    K -- Yes --> L["Run ML validation"]
    K -- No --> M["Recheck weights, diagnostics, assumptions"]
    M --> J
    L --> N["SHAP, K-Means, PCA"]
    N --> O["Policy insights and final paper"]
```

## Suggested Usage In Report

- Chapter on methodology: use the Data Flow Diagram and Activity Diagram.
- Chapter on system design: use the Component Diagram and Deployment Diagram.
- Chapter on execution logic: use the Sequence Diagram.
- Viva or presentation: use the Use Case Diagram for quick explanation.
