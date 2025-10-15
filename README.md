# About the project
This project is to examine large-scale infrastructure projects in three different sectors (energy, transportation, and water), and how they have evolved over time. Specifically, I am interested in environmental and social risks and how they impact the project delay. But in this exploratory phase, I am looking at the data from multiple perspectives.

# Data
## Dataset
1. Project data (_adb_426.csv_)
    - Source: Asian Development Bank
    - 426 projects with sector (Energy/Transportation/Water), country, region, initial/final costs, dates (initial/actual closing date, approval date), and preliminary evaluation of environmental and social impact assessmemt in A, B, C, and D. This letter scale is ordinal, from A meaning the highest risk, and C meaning minimal risk, and D meaning no impact/risk.
    - This data includes projects that were closed between 2002 and 2019, making the total of 18-year span. This is to avoid any confounding factors that could manifest in project cost and schedule due to Covid-19.
    - **This is the data that I preprocessed using the following two.**
2. Price Level Ration data (_WB_PLR.csv_): 
    - Source: World Bank
    - Price Level Ratio data for 266 countries from 1990 to 2024
    - This is to convert the nominal cost for 'place' (i.e., country). A large portion of an infrastructure project's cost is for local labor, local materials, and land acquisition. These are "non-tradable" goods and services, and their prices vary dramatically between countries. A nominal $500 million in Kenya commands a vastly larger quantity of these inputs than $500 million in the United States. Therefore, it is necessary to put costs of projects on the equal footing by converting the project's cost that reflects its own national economy's scale to the USD-equivalent cost.
3. GDP Deflator data (_WB_GDPDeflator.csv_)
    - Source: World Bank
    - GDP deflator data for 266 countries from 1990 to 2024 for inflation adjustment
    - This is to convert the PLR-adjusted cost of projects for 'time'. What would have cost in 2002 is different from what the same amount of cost can do in today's value. Since the final year of the data is 2019, I converted costs equivalent to the value of 2019.

## Preprocessing
1. Excluded multi-country projects (n=5) from the analysis because for those, project cost conversion is not posssible and imputation is also not possible.
2. I applied two-step ==preprocessing== of the data to adjust costs to the 2019-USD-equivalent value for comparison across projects. It was done for both _initial_ total cost and _final_ total cost.
3. Outliers were excluded.
4. Any project that took less than 2 years (duration_years) were dropped, considering the definition of 'large-scale infrastructure projects' as the ones that take at least a few years (a widely-accepted definition in practice and in the literature).
5. Projects were categorized by size based on adjusted initial cost:
   - Small: < $500M
   - Major: $500M - $1B  
   - Mega: ≥ $1B
6. From 426 original data points, 10 were excluded, and 416 left.

### 2-step Cost Adjustments
#### For Initial Costs
**Step 1: PLR Adjustment**
- What was done: Convert local currency to USD equivalent at the _approval year_
- Formula: `Adjusted = Nominal / PLR_ratio`
- Example: Burkina Faso 2001 project with 206M nominal → 752M USD-equivalent
**Step 2: GDP Deflator**
- What was done: Adjust to 2019 constant dollars to reflect the time value of money
- Formula: `2019_USD = Step1_USD × (GDP_2019 / GDP_approval_year)`
- Converts all projects to comparable 2019 purchasing power
#### For Final Costs (reference: closing year)
- Same two-step process using _closing year_ instead of approval year
- Captures actual spending patterns at project completion

### Outlier Treatment
#### Problem: Hyperinflation Distortions
Early 1990s hyperinflation created extreme adjustment ratios:
- Uzbekistan 1998-2007 (3 unique projects): Adjustment ratio z-score >3, excluded from the data
- While technically correct, maybe the project cost is not as precise as others and being 3 projects, they were excluded.
#### Solution: Z-Score Flagging
- Calculate z-score for adjustment ratios: `(ratio - mean) / std`
- Flag outliers where |z-score| > 3 (99.7th percentile)
- **Result**: 3 initial cost outlier, 2 final cost outliers flagged (2 of them are overlapping projects, 3 in total)
- **Approach**: Keep values but flag for exclusion in analysis

### Missing Data Treatment
- **Environmental/Social Risk Ratings**: Projects with 'FI' (Further Investigation) ratings 
  were excluded from risk-specific analyses as these represent incomplete assessments
- **Performance Ratings**: Analysis of IED ratings used only projects with complete 
  evaluation data (excluded 'na', 'nr', and null values)

### Final Analytical Sample
- **Total projects**: 416 (from 426 original)
- **Excluded**: 10 projects (5 multi-country, 3 outliers, 2 duration < 2 years)
- **By size**: Small: 119, Major: 78, Mega: 219
- **By sector**: Energy: 122, Transport: 197, Water: 97
- **By region**: South Asia: 141, Central and West Asia: 89, East Asia: 83, Southeast Asia: 76, Pacific: 27
