import streamlit as st

st.set_page_config(
    page_title="Infrastructure Project ESG Risk Analysis",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Large-scale Infrastructure Project: ESG Risk Analysis")
st.caption("Demo app — under construction")
st.write(
    """
    This Streamlit app will analyze ESG-related risks in large-scale infrastructure project documents
    using text analysis / NLP methods.
    """
)

# create tab
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Project Overview",
    "📌 Key Findings Summary",
    "⚠️ Risk Analysis",
    "👀 Additional Analysis",
    "📊 Data & Processing"
])

with tab5:
    st.markdown("""
    ## Data Preprocessing
    ### 1. Cost Conversion to 2019 USD
    #### 1-1 Overview
    Converting World Bank project costs to comparable 2019 USD values using a two-step adjustment process.
    #### 1-2 Step 1: PLR (Price Level Ratio) Adjustment
    **Purpose:** Convert nominal USD to PPP-equivalent USD (country-specific purchasing power adjustment)
    **Formula:**
```
    planned_cost_adj1_plr = planned_cost / PLR_value
```
    **Data Source:** World Bank PLR data (266 countries)
    **Handling Missing Data:**
    - Backward/forward extrapolation using 3-year smoothed growth rates
    - Interpolation between available years
    - Multi-country projects: Average PLR across countries (identified by semicolon-separated country names)
    **Result:**
    | Method | Count |
    |--------|-------|
    | Actual PLR values | 458 |
    | Extrapolated/Interpolated | 4 |
    | **Total** | **462** |
    #### 1-3 Step 2: US PPI (Producer Price Index) Adjustment
    **Purpose:** Inflate to 2019 USD for temporal comparability
    **Formula:**
```
    ppi_factor = PPI_2019 / PPI_approval_year
    planned_cost_adj2_ppi = planned_cost × ppi_factor
```
    **Data Source:** IMF International Financial Statistics - US Producer Price Index (1988-2019)
    **Sample PPI Factors:**
    | Year | Factor | Year | Factor |
    |------|--------|------|--------|
    | 1988 | 2.06x  | 2005 | 1.40x  |
    | 1992 | 1.88x  | 2010 | 1.19x  |
    | 1997 | 1.73x  | 2015 | 1.08x  |
    | 2000 | 1.66x  | 2019 | 1.00x  |
    **Rationale for US PPI over country-specific GDP deflator:**
    - Project costs are denominated in USD, not local currency
    - PLR already captures country-specific purchasing power
    - US PPI is stable (adjustment ratios: 1.0x - 2.1x) vs GDP deflator which produced extreme outliers due to hyperinflation in countries like Angola, Brazil, Turkey
    - PPI better reflects infrastructure/construction inputs than CPI
    **Result:** 462/462 projects successfully adjusted (approval years 1989-2014 all within PPI coverage)
    #### 1-4 Combined Adjustment
```
    planned_cost_adj_both = planned_cost_adj1_plr × ppi_factor
```
    ##### Total Adjustment Ratio Statistics (final/original)
    | Metric | Value |
    |--------|-------|
    | Min | 1.13x |
    | Max | 16.95x |
    | Mean | 4.91x |
    | Median | 4.35x |
    ##### Final Cost Distribution (2019 USD, millions)
    | Metric | Value |
    |--------|-------|
    | Min | $4.90M |
    | 25th percentile | $301.16M |
    | Median | $799.85M |
    | 75th percentile | $1,797.38M |
    | Mean | $1,720.41M |
    | Max | $34,584.26M |
    ### 2. Megaproject Classification
    | Threshold | Count | Percentage |
    |-----------|-------|------------|
    | ≥$1B | 198 | 42.9% |
    | ≥$500M | 280 | 60.6% |
    | <$500M | 182 | 39.4% |
    **Projects near $1B threshold ($900M-$1,100M):** 24
    **Total projects:** 462
    **Selected for analysis: 280 (≥$500M threshold)**
    """)