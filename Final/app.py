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
    "👀 Project Summary",
    "Project Metadata & Preprocessing",
    "Project Text Data & NLP Analysis",
    "⚠️ Risk Analysis",
    "Additional Analysis",
])

BASE = Path(__file__).parent

with tab1:
    st.title("👀 Project Summary")

with tab2:
    st.title("Project Metadata & Preprocessing")
    
    # Create sub-tabs for better organization
    subtab1, subtab2 = st.tabs(["Raw Data", "Preprocessing"])
    
    with subtab1:
        st.header("Metadata for Projects")
        st.markdown("""
        Source: World Bank
        This data was complied using various data sources in World Bank.
        """)
        DATA_PATH = BASE / "cost_converted_462projects.csv"
        df = pd.read_csv(DATA_PATH)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Projects", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            st.metric("Year Range", f"{df['approval_year'].min()} - {df['approval_year'].max()}")
        
        st.dataframe(df.head(100), use_container_width=True)
        
        with st.expander("View Column Schema"):
            schema_df = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes.astype(str).values,
                'Non-Null': df.notna().sum().values
            })
            st.dataframe(schema_df, use_container_width=True, hide_index=True)
    
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
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Large-scale Projects (Project Cost ≥$500M)", "280", "60.6%")
        with col2:
            st.metric("Regular Projects (Project Cost <$500M)", "182", "39.4%")
        
        st.success("**Selected for analysis: 280 projects (≥$500M threshold)**")
        
        with st.expander("View Final Project List"):
            final_projects = pd.read_csv(BASE / "fin_project_metadata_280.csv")
            st.dataframe(final_projects, use_container_width=True, hide_index=True)

with tab3:
    st.title("Project Text Data & NLP Analysis")
    
    # Create sub-tabs
    subtab1, subtab2 = st.tabs(["Raw Text Data", "Text Preprocessing"])
    
    with subtab1:
        st.header("Text Data for Projects")
        
        st.markdown("""
        Source: World Bank
        Each project has two key documents that are analyzed:
        - **Project Appraisal Document (PAD)**: Written at planning stage
        - **Implementation Completion Report (ICR)**: Written after project completion
        """)
        st.subheader("Sample Documents")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Project Appraisal Document (at Planning stage)**")
            with open(BASE / "P130164_PAD.pdf", "rb") as f:
                st.download_button("📥 Download Sample PAD", f, file_name="P130164_PAD.pdf")
        
        with col2:
            st.markdown("**Implementation Completion Report (after completion)**")
            with open(BASE / "P130164_ICR.pdf", "rb") as f:
                st.download_button("📥 Download Sample ICR", f, file_name="P130164_ICR.pdf")
        
        st.markdown("---")
        
        st.subheader("Text Data Overview")
        # Load text data if available
        # text_data = pd.read_json(BASE / "text_data_sample.json")
        # st.dataframe(text_data, use_container_width=True)
        st.info("🚧 Text data preview coming soon")
    
    with subtab2:
        st.header("Text Preprocessing Steps")
        st.info("🚧 Text preprocessing documentation coming soon")
        # Add your text preprocessing steps here later

with tab4:
    st.title("⚠️ Risk Analysis")

with tab5:
    st.title("Additional Analysis")