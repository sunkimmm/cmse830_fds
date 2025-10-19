# About the project
This project is to examine large-scale infrastructure projects in three different sectors (energy, transportation, and water), and how they have evolved over time. Specifically, I am interested in environmental and social risks and how they impact the project performance.


# Data Merging and Preprocessing
## Overview
This document summarizes the data merging and preprocessing steps performed to create a clean dataset of 310 Asian Development Bank (ADB) sovereign projects for analysis.

## 1. Initial Datasets

### Source Data
- **df_adb_1** (`adb_sov_projects.csv`): 527 projects
  - Project identifiers (projectid, projectid_head, projectname)
  - Country information
  - Project modality and status
  - Approval dates and approval numbers
  - Sector classifications (sector1, sector1a)
  - Safeguard categories (safe_env, safe_ind, safe_res)

- **df_adb_2** (`adb_success_rate.csv`): 1,019 entries
  - Multiple project identifier columns (projectid, projectid1-4)
  - Country codes and names
  - Financial data (approved, disbursed, committed amounts)
  - Date information (approval, effective, closing dates - initial and final)
  - Total project costs (initial and final)
  - Project performance ratings

- **df_region** (`adb_country_code.csv`): 225 entries
  - Regional member information
  - Country codes (Alpha-3 and ADB-specific)
  - Subregion classifications

- **df_plr** (`WB_PLR.csv`): 266 countries
  - Prime Lending Rate data from 1960-2024
  - World Bank indicator for borrowing costs

- **df_gdp** (`WB_GDPDeflator.csv`): 266 countries
  - GDP Deflator data from 1960-2024
  - World Bank indicator for price level changes

## 2. Merging df_adb_1 and df_adb_2

### Objective
Merge project-level data (df_adb_1) with financial and performance data (df_adb_2) while maintaining df_adb_1 as the base dataset.

### Merging Strategy

#### Step 1: Exact Project ID Matching
- **Method**: Matched df_adb_1['projectid'] against df_adb_2['projectid', 'projectid1', 'projectid2', 'projectid3', 'projectid4']
- **Result**: 386 matches
- **Columns extracted**: countrycode, closingdate_initial, closingdate_final, totalcost_initial, totalcost_final

#### Step 2: projectid_head + projectname Matching
- **Method**: For unmatched rows, matched on both projectid_head and exact projectname
- **Result**: 2 additional matches

#### Step 3: projectid_head + approvaldate Matching
- **Method**: For remaining unmatched rows, matched on both projectid_head and approvaldate
- **Result**: 0 additional matches

#### Step 4: Fuzzy Matching (80% Similarity Threshold)
- **Method**: For rows with matching projectid_head but different project names, calculated string similarity
- **Rationale**: Account for minor naming differences (e.g., "GMS:" vs "Greater Mekong Subregion:")
- **Result**: 11 additional matches

#### Step 5: Lower Threshold Fuzzy Matching (75% Similarity)
- **Method**: Lowered similarity threshold to capture borderline cases
- **Result**: 3-4 additional matches

#### Final Merging Results
- **Total matched**: 424 projects
- **Unmatched**: 109 projects
  - 96 projects: No matching projectid_head in df_adb_2
  - 13 projects: Matching projectid_head but very different names (likely different project phases)
- **Decision**: Dropped all 109 unmatched projects as they lacked essential financial data


## 3. Region Data Integration

### Objective
Fill missing region information in the merged dataset.

### Method
- Matched df_merged['countrycode'] with df_region['ADB Country Code']
- Extracted df_region['Subregion'] for matched countries
- **Result**: All 424 projects now have region information


## 4. Manual Data Collection

### Missing Cost Data
- **Identified**: 41 projects with missing totalcost_initial or totalcost_final
- **Action**: Manually reviewed Project Completion Reports
- **Filled**: 31 projects with data from reports
- **Unavailable**: 10 projects (data not available even in completion reports)
- **Result**: 414 projects with complete cost data (10 projects dropped)


## 5. Feature Engineering

### Created Columns

#### Duration Metrics (in years, rounded to 2 decimal places)
```python
duration_initial = (closingdate_initial - approvaldate) / 365.25
duration_final = (closingdate_final - approvaldate) / 365.25
delay = (closingdate_final - closingdate_initial) / 365.25
```

#### Cost Metrics
```python
cost_overrun = totalcost_final - totalcost_initial
cost_overrun_mark = cost_overrun > 0  # Boolean
delay_mark = delay > 0  # Boolean
```

#### Temporal Features
```python
approval_year = year from approvaldate
closing_year = year from closingdate_final
beforecovid = closing_year <= 2019  # Boolean
```


## 6. Data Quality Corrections

### Negative Duration Corrections
- **Issue**: 3 projects had negative durations (closing date before approval date)
- **Action**: Manually verified and corrected dates for:
  - projectid 31280-013
  - projectid 41682-039
  - projectid 43141-044
- **Result**: All durations now positive


## 7. Dataset Filtering

### Filter 1: Project Completion Timing
- **Criteria**: Keep only projects where `beforecovid == True` (closed by 2019)
- **Rationale**: Exclude COVID-19 impacts on project performance
- **Result**: 341 projects retained

### Filter 2: Project Duration
- **Criteria**: Keep only projects where `duration_final > 2 years`
- **Rationale**: Focus on substantial multi-year projects
- **Result**: 338 projects retained (98.3% of pre-COVID projects)

### Filter 3: Economic Indicator Availability
- **Criteria**: Keep only countries present in both df_plr and df_gdp
- **Action**: 
  - Identified countries in df_project missing from PLR or GDP datasets
  - Dropped projects from countries without complete economic indicator data
- **Result**: Dataset further reduced for cost adjustment feasibility


## 8. Cost Adjustments to 2019 Constant Dollars

### Objective
Adjust all project costs to 2019 constant dollars to enable fair comparisons across time and countries.

### Two-Step Adjustment Process

#### For Initial Costs (at Approval)

**Step 1: Prime Lending Rate (PLR) Adjustment**
```python
totalcost_initial_adj1_plr = totalcost_initial / PLR(approval_year, country)
```
- **Purpose**: Adjust for country-specific borrowing costs
- **Data source**: World Bank Prime Lending Rate by country and year

**Step 2: GDP Deflator Adjustment to 2019 Base**
```python
totalcost_initial_adj2_2019 = totalcost_initial_adj1_plr × (GDP_deflator_2019 / GDP_deflator_approval_year)
```
- **Purpose**: Adjust for inflation to 2019 constant prices
- **Data source**: World Bank GDP Deflator by country and year

#### For Final Costs (at Closing)

**Step 1: Prime Lending Rate (PLR) Adjustment**
```python
totalcost_final_adj1_plr = totalcost_final / PLR(closing_year, country)
```

**Step 2: GDP Deflator Adjustment to 2019 Base**
```python
totalcost_final_adj2_2019 = totalcost_final_adj1_plr × (GDP_deflator_2019 / GDP_deflator_closing_year)
```

### Adjustment Results
- Successfully adjusted costs for projects with available PLR and GDP deflator data
- Some projects failed adjustment due to:
  - Missing PLR values for specific country-year combinations
  - Missing GDP deflator values
  - Countries not in World Bank datasets


## 9. Outlier Detection and Removal

### Methodology: Z-Score Analysis

#### Adjustment Ratio Calculation
```python
initial_adjustment_ratio = totalcost_initial_adj2_2019 / totalcost_initial
final_adjustment_ratio = totalcost_final_adj2_2019 / totalcost_final
```

#### Z-Score Outlier Detection
```python
z_score = (value - mean) / standard_deviation
outlier_threshold = 3  # Projects with |z-score| > 3
```

### Outlier Removal
- **Criteria**: Remove projects with outlier adjustment ratios in either initial or final costs
- **Rationale**: Extreme adjustment ratios may indicate data quality issues or exceptional circumstances
- **Result**: Projects with clean, reasonable adjustment ratios retained


## 10. Final Feature Creation

### Simplified Cost Columns
```python
totalcost_initial_adj = round(totalcost_initial_adj2_2019, 2)
totalcost_final_adj = round(totalcost_final_adj2_2019, 2)
```

### Project Size Classification
Based on adjusted initial cost (totalcost_initial_adj):
- **Small**: < $100M
- **Medium**: $100M - $500M
- **Large**: $500M - $1,000M
- **Mega**: ≥ $1,000M

## 11. Final Dataset Characteristics

### Dataset Size
- **Final projects**: 310
- **Reduction from original**: 527 → 310 (58.8% retention rate)

### Completeness
- **All projects have**:
  - Complete financial data (initial and final costs)
  - Adjusted costs in 2019 constant dollars
  - Duration metrics (initial, final, delay)
  - Cost overrun calculations
  - Region and country information
  - Sector classifications
  - Safeguard categories
  - Project size classification

### Quality Criteria Met
✓ Closed before 2020 (pre-COVID)  
✓ Duration > 2 years  
✓ Complete cost data (initial and final)  
✓ Successful cost adjustment to 2019 constant dollars  
✓ No outlier adjustment ratios  
✓ Available economic indicators (PLR and GDP deflator)

## 12. Column Cleanup

### Dropped Columns
- Unnamed index columns (Unnamed: 0, Unnamed: 0.1)
- projectid_head (redundant identifier)
- beforecovid (all True after filtering)
- Intermediate calculation columns

### Final Schema (36 columns)
1. Project identifiers and metadata (6 columns)
2. Financial data - nominal (2 columns)
3. Financial data - adjusted (6 columns)
4. Duration metrics (3 columns)
5. Cost performance metrics (2 columns)
6. Performance flags (2 columns)
7. Temporal features (5 columns)
8. Geographic information (3 columns)
9. Sector and safeguard information (6 columns)
10. Derived features (1 column: project_size)

## Summary

This preprocessing workflow transformed raw project data from multiple sources into a clean, analysis-ready dataset. The final dataset of 310 projects represents substantial, multi-year ADB sovereign projects completed before COVID-19, with costs standardized to 2019 constant dollars for meaningful cross-project and cross-temporal comparisons. All projects have complete financial, temporal, and performance data suitable for exploratory data analysis and inferential statistical analysis.
