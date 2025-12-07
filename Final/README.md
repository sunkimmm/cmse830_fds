# Large-scale Infrastructure Project: ESG Risk Analysis

A Streamlit application for analyzing Environmental, Social, and Governance (ESG) risks in World Bank infrastructure megaprojects.

## Research Overview

This research investigates how ESG-related challenges influence project performance outcomes (cost overruns, delays, cancellations) in large-scale infrastructure projects. The study combines:
- **Metadata analysis**: Project characteristics, costs, durations, and outcomes for 280 projects (≥$500M)
- **Text mining**: NLP-based extraction and analysis of ESG terminology from project documents

## Key Features

### 1. ESG Taxonomy Development
- 314 manually curated seed terms from World Bank ESG frameworks
- Expanded to 2,407 terms using Word2Vec embeddings and max-similarity matching
- 13 categories across 3 pillars: Environmental (E1-E3), Social (S1-S5), Governance (G1-G5)
- 35 subcategories created via hierarchical clustering

### 2. Data Processing
- **Cost standardization**: PLR (purchasing power parity) + US PPI adjustment to 2019 USD
- **Text preprocessing**: OCR correction, spell checking, n-gram preservation
- **Document sources**: Project Appraisal Documents (PAD) and Implementation Completion Reports (ICR)

### 3. Analysis Capabilities
- Geographic distribution maps (projects by country, average cost)
- ESG term frequency analysis at appraisal vs. completion
- Emergence rate calculation (new issues arising during implementation)
- Regression analysis linking ESG coverage to project outcomes

## Key Findings

| Outcome | ESG Predictor | Effect | Interpretation |
|---------|---------------|--------|----------------|
| Cancellation | S3: Land & Resettlement (Coverage) | OR = 0.10 | 90% lower risk |
| Cancellation | S4: Indigenous Peoples (Coverage) | OR = 0.12 | 88% lower risk |
| Cancellation | G2: Fiscal (Emergence) | OR = 33.9 | 34x higher risk |
| Delay | E3: Biodiversity (Coverage) | -35.4 months | ~3 years less delay |
| Delay | G5: Transparency (Coverage) | +45.2 months | ~4 years more delay |
| Cost Change | — | No significant predictors | ESG does not predict cost overruns |

## Application Structure

| Tab | Description |
|-----|-------------|
| Research Introduction | Overview of research process and questions |
| Infrastructure Projects | Summary statistics and geographic distribution |
| ESG Seed Term Extraction | Taxonomy development methodology and results |
| Project Metadata | Cost conversion and data processing steps |
| Project Text Data | Text preprocessing and dictionary expansion |
| Analysis | EDA, emergence rates, and regression results |

## Data Sources

- **World Bank**: Sovereign infrastructure development project data
- **ESG Frameworks**: IFC Performance Standards, World Bank Environmental and Social Framework, Infrastructure Governance Assessment Framework

## Technical Stack

- **Frontend**: Streamlit
- **Visualization**: Plotly, Plotly Express
- **Data Processing**: Pandas, NumPy, SciPy
- **NLP**: Word2Vec embeddings, MPNET transformer model, spaCy

## Author

S. Kim (sunkim@msu.edu)  
Michigan State University
