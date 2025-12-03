import streamlit as st
from pathlib import Path
import pandas as pd

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
    st.title("📊 Data & Processing")
    
    # Create sub-tabs for better organization
    subtab1, subtab2 = st.tabs(["Raw Data", "Preprocessing Steps"])
    
    with subtab1:
        # Section 1: Project Metadata
        st.header("1. Project Metadata")
        
        from pathlib import Path
        DATA_PATH = Path(__file__).parent / "cost_converted_462projects.csv"
        df = pd.read_csv(DATA_PATH)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Projects", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            st.metric("Year Range", f"{df['approval_year'].min()} - {df['approval_year'].max()}")
        
        st.dataframe(df.head(100), use_container_width=True)
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Dataset",
            data=csv,
            file_name='cost_converted_462projects.csv',
            mime='text/csv',
        )
        
        with st.expander("View Column Schema"):
            schema_df = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes.astype(str).values,
                'Non-Null': df.notna().sum().values
            })
            st.dataframe(schema_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Section 2: Project Text Data
        st.header("2. Project Text Data")
        st.info("🚧 Coming soon - Project document text data")
        # Add your text data loading here later
    
    with subtab2:
        st.header("Data Preprocessing")
        
        st.markdown("""
        This summarizes the data preprocessing steps performed to convert World Bank project costs 
        to comparable **2019 USD values** for analysis.
        """)
        
        st.markdown("---")
        
        # 1. Overview
        st.subheader("1. Cost Conversion Overview")
        st.markdown("Converting World Bank project costs to comparable 2019 USD values using a two-step adjustment process.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Projects", "462")
        with col2:
            st.metric("Approval Years", "1989 - 2014")
        with col3:
            st.metric("Target Year", "2019 USD")
        
        st.markdown("---")
        
# 2. Step 1: PLR Adjustment
        st.subheader("2. Step 1: PLR (Price Level Ratio) Adjustment")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Purpose**")
            st.info("Convert nominal USD to PPP-equivalent USD (country-specific purchasing power adjustment)")
            st.markdown("**Formula**")
            st.latex(r"\text{planned\_cost\_adj1\_plr} = \frac{\text{planned\_cost}}{\text{PLR\_value}}")
        
        with col2:
            st.markdown("**Data Source**")
            st.caption("World Bank PLR data (266 countries)")
        
        # Highlighted missing data handling
        st.markdown("**Handling Missing Data**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.warning("**Backward Extrapolation**\n\nUsing 3-year smoothed growth rates for years before available data")
        with col2:
            st.warning("**Forward Extrapolation**\n\nUsing 3-year smoothed growth rates for years after available data")
        with col3:
            st.warning("**Interpolation**\n\nLinear interpolation between available years; Multi-country projects averaged")
        
        st.markdown("**Result**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Actual PLR Values", "458")
        with col2:
            st.metric("Extrapolated/Interpolated", "4")
        with col3:
            st.metric("Total", "462")
        
        with st.expander("View World Bank PLR Data"):
            wb_plr = pd.read_csv(BASE / "WB_PLR.csv")
            st.dataframe(wb_plr, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # 3. Step 2: US PPI Adjustment
        st.subheader("3. Step 2: US PPI (Producer Price Index) Adjustment")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Purpose**")
            st.info("Inflate to 2019 USD for temporal comparability")
            st.markdown("**Formula**")
            st.latex(r"\text{ppi\_factor} = \frac{\text{PPI}_{2019}}{\text{PPI}_{\text{approval\_year}}}")
            st.latex(r"\text{planned\_cost\_adj2\_ppi} = \text{planned\_cost} \times \text{ppi\_factor}")
        
        with col2:
            st.markdown("**Data Source**")
            st.caption("IMF International Financial Statistics - US Producer Price Index (1988-2019)")
            st.markdown("**Rationale for US PPI over GDP deflator**")
            st.markdown("""
            - Project costs denominated in USD, not local currency
            - PLR already captures country-specific purchasing power
            - US PPI is stable (1.0x - 2.1x) vs GDP deflator extreme outliers
            - PPI better reflects infrastructure/construction inputs
            """)
        
        with st.expander("View IMF US PPI Data"):
            ppi = pd.read_csv(BASE / "IMF_US_PPI.csv")
            st.dataframe(ppi, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # 4. Combined Adjustment
        st.subheader("4. Combined Adjustment")
        
        st.latex(r"\text{planned\_cost\_adj\_both} = \text{planned\_cost\_adj1\_plr} \times \text{ppi\_factor}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Adjustment Ratio Statistics (final/original)**")
            ratio_data = pd.DataFrame({
                'Metric': ['Min', 'Max', 'Mean', 'Median'],
                'Value': ['1.13x', '16.95x', '4.91x', '4.35x']
            })
            st.dataframe(ratio_data, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("**Final Cost Distribution (2019 USD)**")
            cost_data = pd.DataFrame({
                'Metric': ['Min', '25th %', 'Median', '75th %', 'Mean', 'Max'],
                'Value': ['$4.90M', '$301.16M', '$799.85M', '$1,797.38M', '$1,720.41M', '$34,584.26M']
            })
            st.dataframe(cost_data, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # 5. Megaproject Classification
        st.subheader("5. Megaproject Classification")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("≥$1B", "198", "42.9%")
        with col2:
            st.metric("≥$500M", "280", "60.6%")
        with col3:
            st.metric("<$500M", "182", "39.4%")
        
        st.markdown("**Projects near $1B threshold ($900M - $1,100M):** 24")
        
        st.success("**Selected for analysis: 280 projects (≥$500M threshold)**")