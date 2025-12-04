from re import S
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

# create tab
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Project Summary",
    "ESG Risks in Projects",
    "Project Metadata & Preprocessing",
    "Project Text Data & NLP Analysis",
    "Regression Analysis",
    
])

BASE = Path(__file__).parent

with tab1:
    st.title("Project Overview")
    st.markdown("##### This project investigates ESG-related risks in large-scale infrastructure construction projects, combining metadata (e.g., region, country, project sector, cost, duration, etc.) and text data that are extracted from project documents. I first develop an ESG Taxonomy (i.e., dictionary) from the extracted text data using NLP that incorporates TFIDF scores and N-gram extractions, conduct contextual embedding using Transformer-based NLP model, and run regression to see how ESG risks influence infrastructure project performance.")
    
    st.markdown("---")
    final_projects = pd.read_csv(BASE / "fin_project_metadata_280.csv")
    
    # Key metrics at the top
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        st.metric("Total Projects", len(final_projects))
    with col2:
        st.metric("Countries", final_projects['countryname'].nunique())
    with col3:
        st.metric("Regions", final_projects['regionname'].nunique())
    with col4:
        total_investment = final_projects['planned_cost_adj_both'].sum() / 1000
        st.metric("Total Investment", f"${total_investment:.1f}B")
    with col5:
        avg_cost = final_projects['planned_cost_adj_both'].mean()
        st.metric("Avg Project Cost", f"${avg_cost:.0f}M")
    with col6:
        avg_duration = final_projects['duration_actual'].mean() / 12
        st.metric("Avg Duration", f"{avg_duration:.1f} years")
    with col7:
        avg_delay = final_projects['delay'].mean() / 12
        st.metric("Avg Delay", f"{avg_delay:.1f} years")
    
    st.markdown("---")
    
    # Geographic Maps
    st.subheader("Geographic Distribution")
    st.markdown("Hover over the map to see detailed information for each country.")
    
    # Prepare data for choropleth maps
    country_total = final_projects.groupby('countryname').agg({
        'projectid': 'count',
        'sector1': lambda x: ', '.join(x.value_counts().index[:3])
    }).reset_index()
    country_total.columns = ['countryname', 'total_projects', 'main_sectors']
    
    country_avg_cost = final_projects.groupby('countryname').agg({
        'projectid': 'count',
        'base+contingency': 'mean',
        'sector1': lambda x: ', '.join(x.value_counts().index[:3])
    }).reset_index()
    country_avg_cost.columns = ['countryname', 'total_projects', 'avg_cost', 'main_sectors']
    
    # Create side-by-side choropleth maps
    fig_maps = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Number of Projects per Country', 'Average Project Cost per Country'),
        specs=[[{'type': 'choropleth'}, {'type': 'choropleth'}]],
        horizontal_spacing=0.01
    )
    
    fig_maps.add_trace(
        go.Choropleth(
            locations=country_total['countryname'],
            locationmode='country names',
            z=country_total['total_projects'],
            customdata=country_total[['total_projects', 'main_sectors']],
            hovertemplate='<b>%{location}</b><br>Total Projects: %{customdata[0]}<br>Main Sectors: %{customdata[1]}<extra></extra>',
            colorscale='Pinkyl',
            colorbar=dict(x=0.4, y=0.8, len=0.5, title='Projects'),
            showscale=True
        ),
        row=1, col=1
    )
    
    fig_maps.add_trace(
        go.Choropleth(
            locations=country_avg_cost['countryname'],
            locationmode='country names',
            z=country_avg_cost['avg_cost'],
            customdata=country_avg_cost[['total_projects', 'avg_cost', 'main_sectors']],
            hovertemplate='<b>%{location}</b><br>Total Projects: %{customdata[0]}<br>Avg Cost: $%{customdata[1]:.2f}M<br>Main Sectors: %{customdata[2]}<extra></extra>',
            colorscale='Pinkyl',
            colorbar=dict(x=0.95, y=0.8, len=0.5, title='Avg Cost (M USD)'),
            showscale=True
        ),
        row=1, col=2
    )
    
    fig_maps.update_geos(
        projection_type='natural earth',
        showland=True,
        landcolor='rgb(243, 243, 243)',
        coastlinecolor='rgb(204, 204, 204)',
        showcountries=True,
        countrycolor='rgb(204, 204, 204)'
    )
    
    fig_maps.update_layout(
        height=500,
        font=dict(family='Arial'),
        showlegend=False
    )
    
    st.plotly_chart(fig_maps, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Research Process")
    st.markdown("""
    <style>
    .main-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 18px 20px;
        border-radius: 10px;
        text-align: center;
    }
    .main-box b {
        font-size: 18px;
    }
    .main-box span {
        font-size: 14px;
    }
    .sub-box {
        background: #f0f2f6;
        padding: 12px 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 5px 0;
    }
    .main-box-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 18px 20px;
        border-radius: 10px;
        text-align: center;
    }
    .main-box-green b {
        font-size: 18px;
    }
    .main-box-green span {
        font-size: 14px;
    }
    .rq-box {
        background: #f8f9fa;
        padding: 10px 15px;
        border-radius: 8px;
        font-style: italic;
        font-size: 14px;
        color: #555;
        margin-top: 8px;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, arrow, col2 = st.columns([5, 1, 5])
    with col1:
        st.markdown("""
        <div class="main-box">
            <b>1. ESG Taxonomy Development</b><br>
            <span>Text Mining & Embedding Analysis</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="rq-box">
            Research Question: What are the ESG-related risks associated with infrastructure projects?
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="sub-box">
            <b>1-1. Seed Term Extraction</b><br>
            Base dictionary formation via TF-IDF & N-grams → <i>See Tab 3</i>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="sub-box">
            <b>1-2. Embedding Analysis</b><br>
            Dictionary expansion via semantic similarity → <i>See Tab 5</i>
        </div>
        """, unsafe_allow_html=True)
    with arrow:
        st.markdown("<div style='display:flex; align-items:center; justify-content:center; height:200px; font-size:40px; color:#667eea;'>→</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="main-box-green">
            <b>2. Regression Analysis</b><br>
            <span>ESG Risk & Project Performance</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="rq-box">
            Research Question: How does ESG risk emergence influence project performance?
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="sub-box" style="border-left-color: #11998e;">
            <b>ESG Risk Emergence</b><br>
            Measure risk mentions during project implementation
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="sub-box" style="border-left-color: #11998e;">
            <b>Performance Impact</b><br>
            Analyze relationship with project outcomes
        </div>
        """, unsafe_allow_html=True)
    # Sector and Region Distribution
    # st.subheader("Project Distribution by Sector and Region")
    
    # col1, col2 = st.columns(2)
    
    # with col1:
    #     sector_counts = final_projects['sector1'].value_counts().reset_index()
    #     sector_counts.columns = ['Sector', 'Count']
    #     fig_sector = px.pie(sector_counts, values='Count', names='Sector',
    #                        color_discrete_sequence=px.colors.qualitative.Set2,
    #                        hole=0.3)
    #     fig_sector.update_traces(textposition='inside', textinfo='percent+label', textfont_size=16)
    #     fig_sector.update_layout(showlegend=False, margin=dict(t=30, b=20, l=20, r=20),
    #                             title=dict(text='Projects by Sector', font=dict(size=20)))
    #     st.plotly_chart(fig_sector, use_container_width=True)
    
    # with col2:
    #     region_counts = final_projects['regionname'].value_counts().reset_index()
    #     region_counts.columns = ['Region', 'Count']
    #     fig_region = px.pie(region_counts, values='Count', names='Region',
    #                        color_discrete_sequence=px.colors.qualitative.Pastel,
    #                        hole=0.3)
    #     fig_region.update_traces(textposition='inside', textinfo='percent+label', textfont_size=16)
    #     fig_region.update_layout(showlegend=False, margin=dict(t=30, b=20, l=20, r=20),
    #                             title=dict(text='Projects by Region', font=dict(size=20)))
    #     st.plotly_chart(fig_region, use_container_width=True)
    
    # st.markdown("---")
    
    # # Cost distribution by sector
    # st.subheader("Project Cost Distribution by Sector")
    
    # fig_box = px.box(final_projects, x='sector1', y='base+contingency',
    #                 color='sector1',
    #                 color_discrete_sequence=px.colors.qualitative.Set2,
    #                 labels={'sector1': 'Sector', 'base+contingency': 'Project Cost (USD Million)'})
    # fig_box.update_layout(showlegend=False, margin=dict(t=30, b=20, l=20, r=20))
    # st.plotly_chart(fig_box, use_container_width=True)
    
    # st.markdown("---")
    
    # # Timeline
    # st.subheader("Projects Over Time")
    
    # year_sector = final_projects.groupby(['approval_year', 'sector1']).size().reset_index(name='count')
    # fig_timeline = px.bar(year_sector, x='approval_year', y='count', color='sector1',
    #                      color_discrete_sequence=px.colors.qualitative.Set2,
    #                      labels={'approval_year': 'Approval Year', 'count': 'Number of Projects', 'sector1': 'Sector'})
    # fig_timeline.update_layout(margin=dict(t=30, b=20, l=20, r=20))
    # st.plotly_chart(fig_timeline, use_container_width=True)


with tab3:
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

with tab2:
    st.title("ESG Risks in Infrastructure Projects")
    st.markdown("##### Large-scale infrastructure projects are physically large, complex, unique, involves a lot of stakeholders and shareholders, and have great impacts on society. Due to this nature, they inherently involve various environmental, social, and governance (ESG) challenges. According to World Bank, those risks can be categorized into the following categories.")
    st.markdown("##### To see what risks exist in projects, relevant terms were extracted from the following two World Bank documents.")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 0.5])
    with col1:
        st.image(BASE / "es.png", width=250)
    with col2:
        st.markdown("**Environmental and Social Management Framework**")
        st.markdown("   Env 1. Resource Efficiency and Pollution Prevention and Management")
        st.markdown("   Env 2. Biodiversity Conservation and Sustainable Management of Living Natural Resources")
        st.markdown("Soc 1. Labor and Working Conditions")
        st.markdown("Soc 2. Community  Health and Safety")
        st.markdown("Soc 3. Land Acquisition, Restrictions on Land Use and Involuntary Resettlement")
        st.markdown("Soc 4. Indigenous Peoples/Sub-Saharan African Historically Underserved Traditional Local Communities")
        st.markdown("Soc 5. Cultural Heritage")
    
    col1, col2, col3 = st.columns([1, 2, 0.5])
    with col1:
        st.image(BASE / "gov.png", width=250)
    with col2:
        st.markdown("**Governance Framework**")
        st.markdown("Gov 1. Legal Framework and Institutional Capacity")
        st.markdown("Gov 2. Economic Efficiency and Value for Money")
        st.markdown("Gov 3. Fiscal Affordability and Sustainability")
        st.markdown("Gov 4. Procurement and Contract Management")
        st.markdown("Gov 5. Contract Management and O&M'")
        st.markdown("Gov 6. Transparency and Information Access")
        st.markdown("Gov 7. Integrity and Misconduct Risk")
    
    st.markdown("---")
    
    # Load and display seed source documents
    st.subheader("Source Documents for Term Extraction")
    seed_source = pd.read_json(BASE / "seed_streamlit.json")
    
    st.dataframe(seed_source[['pillar', 'category', 'description']], use_container_width=True, hide_index=True)
    
    # Dropdown to select a category and view full text
    selected_row = st.selectbox(
        "Select a category to view full text:",
        options=seed_source['category'].tolist(),
        format_func=lambda x: f"{seed_source[seed_source['category']==x]['pillar'].values[0]} - {x}"
    )
    
    with st.expander(f"View full text for: {selected_row}"):
        full_text = seed_source[seed_source['category'] == selected_row]['text_cleaned'].values[0]
        st.markdown(f"<div style='background-color:#f0f0f0; padding:15px; border-radius:10px; max-height:400px; overflow-y:auto;'>{full_text}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    # Text Data Preprocessing Section
    st.subheader("Text Data Preprocessing")
    
    st.markdown("##### N-gram Extraction Process")
    
    st.markdown("""
    For text analysis, bigrams and trigrams were extracted using specific POS (Part-of-Speech) patterns 
    to capture meaningful multi-word terms relevant to ESG risks.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Bigram Patterns (2-word terms)**")
        st.code("""
        bigram_patterns = {
            ('ADJ', 'NOUN'),   # e.g., "environmental impact"
            ('NOUN', 'NOUN')   # e.g., "water supply"
        }
        """, language="python")
    
    with col2:
        st.markdown("**Trigram Patterns (3-word terms)**")
        st.code("""
        trigram_patterns = {
            ('ADJ', 'ADJ', 'NOUN'),    # e.g., "local indigenous community"
            ('ADJ', 'NOUN', 'NOUN'),   # e.g., "environmental impact assessment"
            ('NOUN', 'NOUN', 'NOUN')   # e.g., "water treatment plant"
        }
        """, language="python")
    
    st.markdown("##### Filtering and Selection Process")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Step 1: Pattern Matching**\n\nExtract n-grams matching the defined POS patterns using spaCy NLP")
    
    with col2:
        st.info("**Step 2: Frequency Filtering**\n\nPreserve important n-grams based on percentile thresholds and document frequency")
    
    with col3:
        st.info("**Step 3: TF-IDF Scoring**\n\nRank and select final terms based on TF-IDF scores across categories")

    # Load seed terms
    seed_terms = pd.read_csv(BASE / "seed_final.csv")
    
    st.subheader("ESG Risk Categories and Important Terms")
    st.markdown("##### These terms are extracted from the World Bank documents using TF-IDF scores for each pillar (E/S/G) and for each category. There were total of 14 subcategories, thus each category was considered as one document.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # First dropdown: Pillar (E, S, G order)
        pillar_order = ['E', 'S', 'G']
        pillar_labels = {'E': 'Environmental', 'S': 'Social', 'G': 'Governance'}
        selected_pillar = st.selectbox(
            "Select Pillar",
            options=pillar_order,
            format_func=lambda x: pillar_labels[x]
        )
    
    with col2:
        # Second dropdown: Category (filtered by selected pillar)
        categories = seed_terms[seed_terms['pillar'] == selected_pillar]['category'].unique()
        selected_category = st.selectbox(
            "Select Category",
            options=categories
        )
    
    # Filter terms
    filtered_terms = seed_terms[
        (seed_terms['pillar'] == selected_pillar) & 
        (seed_terms['category'] == selected_category)
    ]['term'].tolist()
    
    st.markdown(f"**{len(filtered_terms)} terms in {selected_category}:**")
    
    # Color by pillar
    pillar_colors = {'E': '#81C784', 'S': '#64B5F6', 'G': '#FFB74D'}
    color = pillar_colors[selected_pillar]
    
    tags_html = " ".join([
        f'<span style="background-color:{color}; padding:6px 12px; margin:4px; border-radius:20px; display:inline-block; font-size:14px;">{term}</span>' 
        for term in filtered_terms
    ])
    st.markdown(tags_html, unsafe_allow_html=True)
    st.markdown("---")

with tab4:
    st.title("Project Text Data & NLP Analysis")
    subtab1, subtab2, subtab3 = st.tabs(["Text Data & Preprocessing", "Final ESG Taxonomy", "Initial/Exploratory Analysis"])
    
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
        text_data = pd.read_json(BASE / "text_data_sample.json")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Projects", len(text_data))
        with col2:
            st.metric("Appraisal Documents", "6,728,587 words", "24,031 avg per project")
        with col3:
            st.metric("Completion Documents", "3,716,244 words", "13,272 avg per project")
        selected_project = st.selectbox("Select a project to view text data, BEFORE and AFTER cleaning and ngram preservation:", options=text_data['projectid'].tolist())
        doc_type = st.radio("Select document type:", ["Appraisal Document", "Completion Document"], horizontal=True)
        row = text_data[text_data['projectid'] == selected_project].iloc[0]
        if doc_type == "Appraisal Document":
            raw_text = row['text_appraisal']
            cleaned_text = row['text_appraisal_ngram']
            raw_color, clean_color = "#e8f4e8", "#d4edda"
        else:
            raw_text = row['text_completion']
            cleaned_text = row['text_completion_ngram']
            raw_color, clean_color = "#e8f0f4", "#d1ecf1"
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📄 Raw Text (BEFORE cleaning)**")
            st.markdown(f"<div style='background-color:{raw_color}; padding:15px; border-radius:10px; max-height:500px; overflow-y:auto; font-size:11px;'>{raw_text}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("**📄 Cleaned Text (AFTER cleaning)**")
            st.markdown(f"<div style='background-color:{clean_color}; padding:15px; border-radius:10px; max-height:500px; overflow-y:auto; font-size:11px;'>{cleaned_text}</div>", unsafe_allow_html=True)
        st.caption("Note: Text truncated to first 2,000 + last 2,000 words. Underscores indicate multi-word terms (n-grams).")
        st.markdown("---")
        st.header("Text Preprocessing")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("🔧 Typo Correction")
            st.markdown("• NLTK dictionary validation for OCR errors")
            st.markdown("• PySpellChecker for typo correction")
            st.markdown("• Flag documents with >15% unknown words")
            st.markdown("• Quality control across 280 projects")
        with col2:
            st.subheader("🇺🇸 Americanize")
            st.markdown("• British → American spelling conversion")
            st.markdown("• 1,700+ word pairs loaded from dictionary")
            st.markdown("• e.g., 'behaviour' → 'behavior', 'colour' → 'color'")
            st.markdown("• Ensures consistency for NLP analysis")
        with col3:
            st.subheader("🔗 N-gram Preservation")
            st.markdown("• Join multi-word terms with underscores")
            st.markdown("• e.g., 'water supply' → 'water_supply'")
            st.markdown("• Compound standardization via frequency analysis")
            st.markdown("• Preserves semantic meaning of phrases")
        st.markdown("---")
        st.header("N-gram Processing")
        st.markdown("##### N-gram Extraction Process")
        st.markdown("""
        For text analysis, bigrams and trigrams were extracted using specific POS (Part-of-Speech) patterns 
        to capture meaningful multi-word terms relevant to ESG risks.
        """)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Bigram Patterns (2-word terms)**")
            st.code("""
        bigram_patterns = {
            ('ADJ', 'NOUN'),   # e.g., "environmental impact"
            ('NOUN', 'NOUN')   # e.g., "water supply"
        }
        """, language="python")
        with col2:
            st.markdown("**Trigram Patterns (3-word terms)**")
            st.code("""
        trigram_patterns = {
            ('ADJ', 'ADJ', 'NOUN'),    # e.g., "local indigenous community"
            ('ADJ', 'NOUN', 'NOUN'),   # e.g., "environmental impact assessment"
            ('NOUN', 'NOUN', 'NOUN')   # e.g., "water treatment plant"
        }
        """, language="python")
        st.markdown("##### Filtering and Selection Process")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("**Step 1: Pattern Matching**\n\nExtract n-grams matching the defined POS patterns using spaCy NLP")
        with col2:
            st.info("**Step 2: Frequency Filtering**\n\nPreserve important n-grams based on percentile thresholds and document frequency")
        with col3:
            st.info("**Step 3: TF-IDF Scoring**\n\nRank and select final terms based on TF-IDF scores across categories")
        st.markdown("##### N-gram Filtering Results")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Bigrams Preserved: 2,033**")
            st.caption("TF-IDF ≥ 99th percentile, Doc Freq 5-100%")
            with st.expander("View top 50 bigrams"):
                bigrams_data = [
                    ("development planning", 0.0296, 11.1), ("expansion program", 0.0296, 18.2),
                    ("monthly progress", 0.0296, 17.1), ("maintenance practices", 0.0296, 18.6),
                    ("financial returns", 0.0295, 15.7), ("payment obligations", 0.0295, 6.8),
                    ("complaint handling", 0.0295, 5.0), ("water companies", 0.0295, 6.4),
                    ("street lighting", 0.0294, 6.8), ("trucking industry", 0.0294, 8.6),
                    ("post_completion phase", 0.0294, 27.9), ("financial aspects", 0.0294, 21.8),
                    ("joint supervision", 0.0294, 8.2), ("rail network", 0.0294, 9.6),
                    ("project sites", 0.0294, 21.4), ("implementation issues", 0.0293, 28.9),
                    ("complex project", 0.0293, 16.4), ("transport conditions", 0.0293, 6.8),
                    ("project budget", 0.0293, 18.2), ("performance indicator", 0.0293, 15.0),
                    ("timely completion", 0.0293, 24.6), ("resettlement compensation", 0.0293, 15.7),
                    ("project operations", 0.0293, 10.0), ("transport systems", 0.0293, 13.2),
                    ("implementation agencies", 0.0293, 18.9), ("electricity production", 0.0293, 12.9),
                    ("performance government", 0.0292, 46.1), ("resettlement sites", 0.0292, 11.8),
                    ("key elements", 0.0292, 24.3), ("qualified staff", 0.0292, 28.9),
                    ("satisfaction survey", 0.0292, 6.1), ("energy production", 0.0292, 13.2),
                    ("maintenance strategy", 0.0292, 9.6), ("original design", 0.0292, 21.4),
                    ("plant operation", 0.0292, 11.1), ("vehicle weight", 0.0291, 5.0),
                    ("service obligations", 0.0291, 16.1), ("road surface", 0.0291, 16.1),
                    ("bad condition", 0.0291, 10.4), ("local economy", 0.0291, 21.4),
                    ("environmental policy", 0.0291, 8.6), ("financial assistance", 0.0291, 23.2),
                    ("bid opening", 0.0291, 16.4), ("financial plan", 0.0290, 13.9),
                    ("wastepaper systems", 0.0290, 6.4), ("supply service", 0.0290, 8.9),
                    ("power transfer", 0.0290, 6.1), ("bid prices", 0.0290, 22.1),
                    ("related activities", 0.0290, 7.1), ("significant improvement", 0.0290, 27.9)
                ]
                bigrams_df = pd.DataFrame(bigrams_data, columns=["term", "tfidf", "doc_freq_%"])
                st.dataframe(bigrams_df, height=400, use_container_width=True, hide_index=True)
        with col2:
            st.markdown("**Trigrams Preserved: 408**")
            st.caption("TF-IDF ≥ 99.5th percentile, Doc Freq 5-100%")
            with st.expander("View top 50 trigrams"):
                trigrams_data = [
                    ("project development objectives", 1.0000, 36.1), ("private sector participation", 0.8092, 57.5),
                    ("resettlement action plan", 0.7621, 21.8), ("vehicle operating costs", 0.7072, 36.8),
                    ("rural water supply", 0.6818, 7.9), ("financial management system", 0.6791, 54.6),
                    ("debt service coverage", 0.6688, 31.4), ("project appraisal document", 0.6618, 5.4),
                    ("national road network", 0.6524, 8.9), ("financial management specialist", 0.6478, 11.4),
                    ("civil works contracts", 0.6314, 52.9), ("power sector reform", 0.6269, 17.1),
                    ("environmental management plan", 0.6187, 22.9), ("project development objective", 0.6107, 43.9),
                    ("task team leader", 0.6040, 10.0), ("core road network", 0.5385, 6.4),
                    ("key performance indicators", 0.5348, 46.1), ("urban water supply", 0.5238, 10.7),
                    ("solid waste management", 0.5125, 11.8), ("environmental impact assessment", 0.5086, 30.0),
                    ("net present value", 0.5020, 51.8), ("total project cost", 0.4906, 47.9),
                    ("project management unit", 0.4844, 10.4), ("management information system", 0.4570, 32.9),
                    ("water supply systems", 0.4509, 12.9), ("road user charges", 0.4247, 17.1),
                    ("wastepaper treatment plant", 0.4216, 11.4), ("service coverage ratio", 0.4212, 23.9),
                    ("renewable energy development", 0.4183, 9.3), ("water supply system", 0.4094, 15.0),
                    ("country assistance strategy", 0.4079, 5.4), ("project implementation plan", 0.4019, 14.3),
                    ("water resources management", 0.3984, 10.0), ("resettlement policy framework", 0.3924, 10.4),
                    ("private sector development", 0.3896, 51.1), ("total project costs", 0.3877, 25.7),
                    ("water quality monitoring", 0.3848, 16.4), ("road safety program", 0.3746, 9.3),
                    ("international competitive bidding", 0.3666, 36.8), ("loan closing date", 0.3565, 33.2),
                    ("power sector restructuring", 0.3563, 6.8), ("standard bidding documents", 0.3504, 32.5),
                    ("project management office", 0.3488, 9.3), ("financial management systems", 0.3420, 29.3),
                    ("road sector development", 0.3407, 5.4), ("project closing date", 0.3379, 31.4),
                    ("economic internal rate", 0.3373, 31.8), ("technical assistance component", 0.3346, 32.1),
                    ("thermal power plant", 0.3345, 9.3), ("national competitive bidding", 0.3343, 18.6)
                ]
                trigrams_df = pd.DataFrame(trigrams_data, columns=["term", "tfidf", "doc_freq_%"])
                st.dataframe(trigrams_df, height=400, use_container_width=True, hide_index=True)
    
    with subtab2:
        st.header("Embedding Analysis & Final ESG Taxonomy")
        esg_dict = pd.read_csv(BASE / "esg_dictionary_final.csv")
        col1, col2 = st.columns(2)
        with col1:
            st.info("""**1. Embedding**
    - 435 seed terms + 7,132 corpus candidates \n
    - Model: `all-mpnet-base-v2` (768-dim)\n
    - Source: World Bank ESF + InfraSAP""")
        with col2:
            st.info("""**2. Subcategory Clustering**
    - K-means within each ESG category
    - Silhouette score for optimal k (2–7)
    - Creates semantic subgroups""")

        col1, col2 = st.columns(2)
        with col1:
            st.success("""**3. Dictionary Expansion**
    - Dual threshold filtering (both ≥ 0.55):
    - Seed-term similarity
    - Subcategory centroid similarity
    - Single-category assignment only""")
        with col2:
            st.success("""**4. Manual Curation**
    - Removed problematic seed terms
    - Blacklisted ~40 noise terms
    - Final quality control pass""")

        st.markdown("---")

        st.markdown("##### 📊 Final Result")
        res_col1, res_col2, res_col3, res_col4 = st.columns(4)

        with res_col1:
            st.metric("Seed Terms", "435")
        with res_col2:
            st.metric("Expanded Terms", f"{len(esg_dict[esg_dict['is_seed'] == False]):,}")
        with res_col3:
            st.metric("Total Dictionary", f"{len(esg_dict):,}")
        with res_col4:
            st.metric("Categories", "14")

        st.caption("Thresholds chosen based on silhouette analysis — all categories show positive coherence.")
        st.markdown("---")

        st.subheader("Term Distribution by Pillar and Category")

        dist_df = (
            esg_dict.groupby(['pillar', 'category', 'is_seed'])
            .size()
            .reset_index(name='count')
        )

        dist_pivot = (
            dist_df.pivot_table(index=['pillar', 'category'], columns='is_seed', values='count', fill_value=0)
            .reset_index()
        )

        # If columns come out as True/False, rename safely:
        dist_pivot = dist_pivot.rename(columns={True: "Seed", False: "Expanded"})
        if "Seed" not in dist_pivot.columns:
            dist_pivot["Seed"] = 0
        if "Expanded" not in dist_pivot.columns:
            dist_pivot["Expanded"] = 0

        dist_pivot['Total'] = dist_pivot['Seed'] + dist_pivot['Expanded']
        dist_pivot = dist_pivot.sort_values(['pillar', 'Total'], ascending=[True, False])

        pillar_colors = {'E': '#81C784', 'S': '#64B5F6', 'G': '#FFB74D'}
        pillar_colors_light = {'E': '#C8E6C9', 'S': '#BBDEFB', 'G': '#FFE0B2'}
        pillar_labels = {'E': 'Environmental', 'S': 'Social', 'G': 'Governance'}

        fig = go.Figure()
        for pillar in ['E', 'S', 'G']:
            pdf = dist_pivot[dist_pivot['pillar'] == pillar]

            fig.add_trace(go.Bar(
                name=f"{pillar_labels[pillar]} - Seed",
                y=pdf['category'].astype(str).tolist(),
                x=pdf['Seed'],
                orientation='h',
                marker_color=pillar_colors[pillar],
                legendgroup=pillar,
                hovertemplate='%{y}<br>Seed: %{x}<extra></extra>'
            ))

            fig.add_trace(go.Bar(
                name=f"{pillar_labels[pillar]} - Expanded",
                y=pdf['category'].astype(str).tolist(),
                x=pdf['Expanded'],
                orientation='h',
                marker_color=pillar_colors_light[pillar],
                legendgroup=pillar,
                hovertemplate='%{y}<br>Expanded: %{x}<extra></extra>'
            ))

        fig.update_layout(
            barmode='stack',
            height=500,
            xaxis_title='Number of Terms',
            yaxis_title='',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Terms", len(esg_dict))
        with col2:
            st.metric("Environmental", len(esg_dict[esg_dict['pillar'] == 'E']))
        with col3:
            st.metric("Social", len(esg_dict[esg_dict['pillar'] == 'S']))
        with col4:
            st.metric("Governance", len(esg_dict[esg_dict['pillar'] == 'G']))

        st.markdown("---")

        # Category term viewer
        st.subheader("Explore Terms by Category")
        col1, col2 = st.columns(2)

        with col1:
            selected_pillar = st.selectbox(
                "Select Pillar",
                options=['E', 'S', 'G'],
                format_func=lambda x: pillar_labels[x],
                key="subtab2_pillar"
            )

        with col2:
            categories = esg_dict[esg_dict['pillar'] == selected_pillar]['category'].unique()
            selected_category = st.selectbox(
                "Select Category",
                options=categories,
                key="subtab2_category"
            )

        filtered_df = esg_dict[
            (esg_dict['pillar'] == selected_pillar) &
            (esg_dict['category'] == selected_category)
        ]

        seed_terms = filtered_df[filtered_df['is_seed'] == True]['term'].tolist()
        expanded_terms = filtered_df[filtered_df['is_seed'] == False]['term'].tolist()

        st.markdown(
            f"**{len(filtered_df)} terms in {selected_category}** "
            f"({len(seed_terms)} seed, {len(expanded_terms)} expanded)"
        )

        color_seed = pillar_colors[selected_pillar]
        color_expanded = pillar_colors_light[selected_pillar]

        seed_html = " ".join([
            f'<span style="background-color:{color_seed}; padding:6px 12px; margin:4px; '
            f'border-radius:20px; display:inline-block; font-size:14px; font-weight:500;">{term}</span>'
            for term in seed_terms
        ])

        expanded_html = " ".join([
            f'<span style="background-color:{color_expanded}; padding:6px 12px; margin:4px; '
            f'border-radius:20px; display:inline-block; font-size:14px;">{term}</span>'
            for term in expanded_terms
        ])

        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(
                f"<span style='background-color:{color_seed}; padding:4px 8px; border-radius:10px;'>■</span> "
                f"**Seed Terms** ({len(seed_terms)})",
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                f"<span style='background-color:{color_expanded}; padding:4px 8px; border-radius:10px;'>■</span> "
                f"**Expanded Terms** ({len(expanded_terms)})",
                unsafe_allow_html=True
            )

        st.markdown(seed_html + " " + expanded_html, unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("Interactive Cluster Visualization")

        # Load viz data (with t-SNE coordinates)
        viz_df = pd.read_csv(BASE / "esg_dictionary_viz.csv")
        cat_info = {
            'ESS3': {'display': 'E1'}, 'ESS6': {'display': 'E2'},
            'ESS2': {'display': 'S1'}, 'ESS4': {'display': 'S2'}, 
            'ESS5': {'display': 'S3'}, 'ESS7': {'display': 'S4'}, 'ESS8': {'display': 'S5'},
            'DIM1': {'display': 'G1'}, 'DIM2': {'display': 'G2'}, 'DIM3': {'display': 'G3'},
            'DIM6': {'display': 'G4'}, 'DIM7': {'display': 'G5'}, 'DIM8': {'display': 'G6'}, 'DIM9': {'display': 'G7'}
        }
        # Pillar selector
        viz_col1, viz_col2 = st.columns([1, 3])
        with viz_col1:
            viz_pillar = st.radio("Select Pillar", ['E', 'S', 'G'], 
                                format_func=lambda x: pillar_labels[x],
                                key="viz_pillar")
            
            # Category multiselect for selected pillar
            pillar_categories = viz_df[viz_df['pillar'] == viz_pillar]['category'].unique().tolist()
            selected_cats = st.multiselect("Categories", pillar_categories, default=pillar_categories, key="viz_cats")

        with viz_col2:
            # Build plot
            fig = go.Figure()
            
            # Gray background (other pillars)
            other_df = viz_df[viz_df['pillar'] != viz_pillar]
            fig.add_trace(go.Scatter(
                x=other_df['x'], y=other_df['y'],
                mode='markers',
                marker=dict(size=6, color='lightgray', opacity=0.3),
                name='Other',
                hoverinfo='skip'
            ))
            
            # Selected categories
            colors = px.colors.qualitative.Set1
            for i, cat in enumerate(selected_cats):
                cat_df = viz_df[viz_df['category'] == cat]
                display_name = cat_info[cat]['display']
                fig.add_trace(go.Scatter(
                    x=cat_df['x'], y=cat_df['y'],
                    mode='markers',
                    marker=dict(size=8, color=colors[i % len(colors)], opacity=0.7),
                    name=display_name,
                    text=cat_df['term'],
                    hovertemplate='<b>%{text}</b><br>' + display_name + '<extra></extra>'
                ))
            
            fig.update_layout(
                height=500,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.02),
                margin=dict(l=20, r=20, t=20, b=20),
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)

    with subtab3:
        #st.header("Initial/Exploratory Analysis")
        st.markdown("## COMING SOON")

with tab5:
    st.title(" Regression Analysis")
    st.markdown("## COMING SOON")