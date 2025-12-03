import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import numpy as np
import plotly.express as px

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
    subtab1, subtab2, subtab3 = st.tabs(["Data Processing", "Data (Raw & Processed)", "Initial/Exploratory Data Analysis"])
    
    with subtab1:
        st.header("Data Processing")
        
        st.markdown("""
        This summarizes the data preprocessing steps performed to convert World Bank project costs 
        to comparable **2019 USD values** for analysis.
        """)
        
        st.markdown("---")
        
        # 1. Overview
        st.subheader("Cost Conversion Overview")
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
        st.subheader("Step 1: PLR (Price Level Ratio) Adjustment")
        
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
        st.subheader("Step 2: US PPI (Producer Price Index) Adjustment")
        
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
        st.subheader("Combined Adjustment")
        
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
        
        st.subheader("Large-scale Project Classification")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Large-scale Projects (Project Cost ≥$500M)", "280", "60.6%")
        with col2:
            st.metric("Regular Projects (Project Cost <$500M)", "182", "39.4%")
        
        st.success("**Selected for analysis: 280 projects (≥$500M threshold)**")
        st.markdown("Final project list can be downloaded in the next tab.")

    with subtab2:
        st.header("Project Metadata (Raw)")
        st.markdown("""
        Source: World Bank\n
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

        st.header("Project Metadata (Processed)")
        final_projects = pd.read_csv(BASE / "fin_project_metadata_280.csv")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Projects", len(final_projects))
        with col2:
            st.metric("Columns", len(final_projects.columns))
        with col3:
            st.metric("Year Range", f"{final_projects['approval_year'].min()} - {final_projects['approval_year'].max()}")
        
        st.dataframe(final_projects, use_container_width=True, hide_index=True)
    
    with subtab3:
        st.header("Initial/Exploratory Data Analysis")
        
        final_projects = pd.read_csv(BASE / "fin_project_metadata_280.csv")
        
        import plotly.express as px
        import plotly.graph_objects as go
        
        st.markdown("---")
        
        # Row 1: Sector Distribution & Cost Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Project Sector Distribution")
            sector_counts = final_projects['sector1'].value_counts().reset_index()
            sector_counts.columns = ['Sector', 'Count']
            fig_sector = px.pie(sector_counts, values='Count', names='Sector', 
                               color_discrete_sequence=px.colors.qualitative.Set2,
                               hole=0.3)
            fig_sector.update_traces(textposition='inside', textinfo='percent+label')
            fig_sector.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_sector, use_container_width=True)
        
        with col2:
            st.subheader("Project Cost Distribution (2019 USD)")
            fig_cost = px.histogram(final_projects, x='base+contingency', 
                                   nbins=20,
                                   labels={'base+contingency': 'Project Cost (USD Million)'},
                                   color_discrete_sequence=['#636EFA'])
            fig_cost.update_layout(
                xaxis_title="Project Cost (USD Million)",
                yaxis_title="Number of Projects",
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_cost, use_container_width=True)
        
        st.markdown("---")
        
# Row 2: Cancellation & Addition
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Project Subcomponent Cancellation")
            cancel_counts = final_projects['cancellation'].value_counts().reset_index()
            cancel_counts.columns = ['Cancellation', 'Count']
            cancel_counts['Cancellation'] = cancel_counts['Cancellation'].astype(str).map({'True': 'Yes', 'False': 'No', 'true': 'Yes', 'false': 'No'})
            fig_cancel = px.pie(cancel_counts, values='Count', names='Cancellation',
                               color='Cancellation',
                               color_discrete_map={'Yes': '#EF553B', 'No': '#00CC96'},
                               hole=0.3)
            fig_cancel.update_traces(textposition='inside', textinfo='percent+label')
            fig_cancel.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_cancel, use_container_width=True)
            
            cancel_count = (final_projects['cancellation'].astype(str).str.lower() == 'true').sum()
            cancel_pct = cancel_count / len(final_projects) * 100
            st.caption(f"{cancel_count} projects ({cancel_pct:.1f}%) had subcomponent cancellations")
        
        with col2:
            st.subheader("Project Subcomponent Expansion")
            # Convert to boolean first, then to Yes/No
            final_projects['addition_label'] = final_projects['addition'].apply(
                lambda x: 'Yes' if x == True or str(x).lower() == 'true' else ('No' if x == False or str(x).lower() == 'false' else 'Unknown')
            )
            add_counts = final_projects['addition_label'].value_counts().reset_index()
            add_counts.columns = ['Addition', 'Count']
            fig_add = px.pie(add_counts, values='Count', names='Addition',
                            color='Addition',
                            color_discrete_map={'Yes': '#636EFA', 'No': '#FECB52', 'Unknown': '#999999'},
                            hole=0.3)
            fig_add.update_traces(textposition='inside', textinfo='percent+label')
            fig_add.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_add, use_container_width=True)
            
            add_count = (final_projects['addition_label'] == 'Yes').sum()
            add_pct = add_count / len(final_projects) * 100
            st.caption(f"{add_count} projects ({add_pct:.1f}%) had subcomponent expansions")
        
        st.markdown("---")
        
        # Summary statistics
        st.subheader("Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Projects", len(final_projects))
        with col2:
            st.metric("Avg Cost", f"${final_projects['base+contingency'].mean():.0f}M")
        with col3:
            st.metric("Cancellation Rate", f"{cancel_pct:.1f}%")
        with col4:
            st.metric("Expansion Rate", f"{add_pct:.1f}%")

with tab3:
    st.title("Project Text Data & NLP Analysis")
    
    # Create sub-tabs
    subtab1, subtab2 = st.tabs(["Raw Text Data", "Text Preprocessing"])
    
    with subtab1:
        st.header("Text Data for Projects")
        
        st.markdown("""
        Source: World Bank\n
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