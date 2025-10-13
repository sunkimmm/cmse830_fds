Why you chose your dataset
What you've learned from IDA/EDA
What preprocessing steps you've completed
What you've tried with Streamlit so far

# About the project
This project is to examine infrastructure projects

# Data
## Dataset
1. Project Metadata (_projectid_787_alldata.csv_)
    - Source: World Bank
    - 787 projects with sector (Energy/Transportation/Water), region, initial/final costs, and dates (of approval and closing).
    - This data includes projects that were closed between 2000 to 2019, making the total of 20-year span.
    - This is to avoid any confounding factors that could manifest in project cost and schedule due to Covid-19.
2. Price Level Ration data (_WB_PLR.csv_): 
    - Source: World Bank
    - Price Level Ratio data for 266 countries from 1990 to 2024
    - This is to convert the nominal cost for 'place' (i.e., country). A large portion of an infrastructure project's cost is for local labor, local materials, and land acquisition. These are "non-tradable" goods and services, and their prices vary dramatically between countries. A nominal $500 million in Kenya commands a vastly larger quantity of these inputs than $500 million in the United States. Therefore, it is necessary to put costs of projects on the equal footing by converting the project's cost that reflects its own national economy's scale to the USD-equivalent cost. 
3. GDP Deflator data (_WB_GDPDeflator.csv_)
    - Source: World Bank
    - GDP deflator data for 266 countries from 1990 to 2024 for inflation adjustment
    - This is to convert the PLR-adjusted cost of projects for 'time'. What would have cost in 2000 is different from what the same amount of cost can do in today's value. Since the final year of the data is 2019, I converted costs equivalent to the value of 2019.

## Preprocessing

I applied two-step preprocessing to adjust costs.

### For Initial Costs (reference: approval year)
**Step 1: PLR Adjustment** - Convert local currency to USD equivalent
- Formula: `Adjusted = Nominal / PLR_ratio`
- Example: Burkina Faso 2001 project with 206M nominal → 752M USD-equivalent

**Step 2: GDP Deflator** - Adjust to 2019 constant dollars  
- Formula: `2019_USD = Step1_USD × (GDP_2019 / GDP_approval_year)`
- Converts all projects to comparable 2019 purchasing power

### For Final Costs (reference: closing year)
- Same two-step process using closing year instead of approval year
- Captures actual spending patterns at project completion


### Handling Missing Data

### Regional Projects (30 cases)
Multi-country projects (e.g., "Africa", "Eastern and Southern Africa") marked as NA - cannot apply country-specific adjustments.

### Missing Economic Indicators (25 cases)
When PLR/GDP data unavailable for specific country-years:
- **Extrapolation method**: Calculate growth rate from available years, project backwards/forwards
- Applied to: Argentina, Djibouti, South Sudan, Kosovo, Yemen
- Example: Kosovo 2006 PLR extrapolated back from 2008 using 1.69% annual rate


### Outlier Treatment
#### Problem: Hyperinflation Distortions
Early 1990s hyperinflation created extreme adjustment ratios:
- Brazil 1991: 189,847× multiplier → $49 trillion adjusted (unrealistic)
- 23 projects with >100× adjustment ratios

#### Solution: Z-Score Flagging
- Calculate z-score for adjustment ratios: `(ratio - mean) / std`
- Flag outliers where |z-score| > 3 (99.7th percentile)
- **Result**: 1 initial cost outlier, 14 final cost outliers flagged
- **Approach**: Keep values but flag for exclusion in analysis


## Final Output Variables

| Variable | Description |
|----------|-------------|
| `totalcost_initial_adjusted` | Initial cost in 2019 USD (millions), 2 decimals |
| `totalcost_final_adjusted` | Final cost in 2019 USD (millions), 2 decimals |
| `is_megaproject` | Boolean: initial cost ≥ $1 billion |
| `is_outlier_initial_zscore` | Boolean: hyperinflation-affected initial cost |
| `is_outlier_final_zscore` | Boolean: hyperinflation-affected final cost |
| `is_clean_project` | Boolean: has both costs, no outliers (analysis-ready) |
