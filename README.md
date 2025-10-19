# ADB Infrastructure Projects Analysis

This repository contains analysis of Asian Development Bank (ADB) infrastructure projects for CMSE830 (Fall 2025).

## 📊 Live Dashboard

- **Streamlit App**: [View Dashboard](https://cmse830fds-midterm-adbprojects.streamlit.app/)
- **Project Folder**: [`Midterm/`](./Midterm)

## 📂 Repository Structure
```
├── Midterm/
│   ├── app2.py                          # Streamlit dashboard
│   ├── adb_projects_clean_final.csv     # Clean dataset (310 projects)
│   ├── processing_ida_eda_all_codes.py  # Full preprocessing code
│   ├── requirements.txt
│   └── Merging&Preprocessing/           # Raw data and preprocessing scripts
│       ├── adb_sov_projects.csv         # Original ADB project data
│       ├── adb_success_rate.csv         # Financial & performance data
│       ├── adb_country_code.csv         # Country codes & regions
│       ├── WB_PLR.csv                   # World Bank Prime Lending Rate
│       └── WB_GDPDeflator.csv           # World Bank GDP Deflator
└── README.md
```

## 🎯 Project Overview

This analysis examines **310 ADB sovereign infrastructure projects** completed between 1970-2019, focusing on:
- Project delays and cost overruns
- Risk analysis (environmental and social safeguards)
- Sector-based performance comparisons
- Regional patterns across Asia-Pacific

## 📊 Dataset Summary

| Metric | Value |
|--------|-------|
| **Projects** | 310 |
| **Countries** | 30+ |
| **Sectors** | Energy, Transportation, Water |
| **Time Period** | 1970-2019 (pre-COVID) |
| **Total Investment** | $82.5B (2019 USD) |

### Key Features
- **Duration Metrics**: Initial planned vs. actual duration, delays
- **Cost Metrics**: Initial vs. final costs (adjusted to 2019 constant USD)
- **Risk Categories**: Environmental, Social (Indigenous Peoples, Resettlement)
- **Project Sizes**: Small (<$100M), Medium ($100M-$500M), Large ($500M-$1B), Mega (≥$1B)

## 🔧 Data Processing

The dataset was created through:
1. **Merging** multiple ADB data sources (527 → 424 projects)
2. **Cost Adjustment** to 2019 constant USD using World Bank PLR and GDP Deflator
3. **Quality Control**: Removing incomplete data and outliers
4. **Filtering**: Pre-COVID projects with duration >2 years
5. **Feature Engineering**: Duration, delay, cost overrun metrics

**Final dataset**: 310 projects with complete financial, temporal, and performance data.

<details>
<summary>📖 Detailed Preprocessing Documentation</summary>

### Data Sources
1. **ADB Projects** (527 records): Project metadata, sectors, safeguards
2. **ADB Financial** (1,019 records): Costs, dates, performance ratings
3. **Country Codes** (225 entries): Regional classifications
4. **World Bank PLR**: Prime Lending Rate (1960-2024)
5. **World Bank GDP Deflator**: Price level changes (1960-2024)

### Preprocessing Steps

#### 1. Data Merging
- Matched 424/527 projects using multiple strategies:
  - Exact project ID matching (386 projects)
  - ID + name matching (2 projects)
  - Fuzzy matching at 80% similarity (11 projects)
  - Lower threshold fuzzy matching at 75% (3-4 projects)
- Dropped 109 unmatched projects (missing financial data)

#### 2. Feature Engineering
```python
# Duration metrics (years)
duration_initial = (closingdate_initial - approvaldate) / 365.25
duration_final = (closingdate_final - approvaldate) / 365.25
delay = duration_final - duration_initial

# Cost metrics
cost_overrun = totalcost_final - totalcost_initial
```

#### 3. Cost Adjustment to 2019 Constant USD
Two-step process:
```python
# Step 1: PLR adjustment (borrowing costs)
cost_adj1 = cost / PLR(year, country)

# Step 2: GDP deflator adjustment (inflation)
cost_adj2 = cost_adj1 × (GDP_2019 / GDP_year)
```

#### 4. Quality Control
- Fixed 3 projects with negative durations (data entry errors)
- Manually filled 31 missing cost values from completion reports
- Removed outliers using z-score analysis (threshold: |z| > 3)

#### 5. Filtering
- Pre-COVID only (closed ≤ 2019): 341 projects
- Duration > 2 years: 338 projects
- Complete economic indicators: 320 projects
- After outlier removal: **310 final projects**

### Data Quality
✅ Complete financial data (initial & final costs)  
✅ All costs in 2019 constant USD  
✅ No missing values in key variables  
✅ Pre-COVID timeline (excludes pandemic effects)  
✅ Substantial projects only (>2 years duration)

</details>

## 🚀 Quick Start

### View the Dashboard
Visit the [live Streamlit app](https://cmse830fds-midterm-adbprojects.streamlit.app/)

### Run Locally
```bash
cd Midterm
pip install -r requirements.txt
streamlit run app2.py
```

## 📧 Contact

For questions about this analysis, please open an issue in this repository.

---

**Course**: CMSE830 Foundations of Data Science  
**Semester**: Fall 2025
