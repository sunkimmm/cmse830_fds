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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Research Introduction",
    "Infrastructure Projects Introduction",
    "ESG Risks Seed Term Extraxtion",
    "Project Metadata",
    "Project Text Data",
    "Analysis",
    
])

BASE = Path(__file__).parent

with tab1:
    st.header("Research Overview")
    st.markdown("##### This research investigates ESG-related risks in large-scale infrastructure construction projects, combining metadata (e.g., region, country, project sector, cancellation of subprojects, cost, duration, etc.) and text data that are extracted from project documents. I first develop an ESG Taxonomy (i.e., dictionary) from the extracted text data using NLP considering TFIDF scores and N-gram extractions, conduct contextual embedding using Transformer-based NLP model, and run regression to see how ESG risks influence various infrastructure project performance outcomes.")
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
            Dictionary expansion via semantic similarity → <i>See Tab 4</i>
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
            Measure risk mentions during project implementation → <i>See Tab 6</i>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="sub-box" style="border-left-color: #11998e;">
            <b>Performance Impact</b><br>
            Analyze relationship with project outcomes → <i>See Tab 6</i>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

with tab2:
    st.header("Infrastructure Projects Overview")
    st.markdown("##### This research uses data from the World Bank, specifically, sovereign infrastructure development projects that the World Bank funded. This page shows the introductory overview of the infrastructure projects, and some basic summary statistics.")
    st.markdown("---")
    st.subheader("Summary Statistics")
    final_projects = pd.read_csv(BASE / "fin_project_metadata_280.csv")
    
    # Key metrics at the top
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Total Projects", len(final_projects))
    with col2:
        st.metric("Regions", final_projects['regionname'].nunique())
    with col3:
        st.metric("Countries", final_projects['countryname'].nunique())
    with col4:
        total_investment = final_projects['planned_cost_adj_both'].sum() / 1000
        st.metric("Total Investment", f"${total_investment:.1f}B")
    with col5:
        avg_cost = final_projects['planned_cost_adj_both'].mean()
        st.metric("Avg Project Cost", f"${avg_cost:.0f}M")
    with col6:
        avg_duration = final_projects['duration_actual'].mean() / 12
        st.metric("Avg Duration", f"{avg_duration:.1f} years")
    
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
    st.subheader("Sector Information")
    sector_colors = {'Energy': '#FF6B6B', 'Transportation': '#A9C25E', 'Water': '#45B7D1'}
    sector_colors_light = {'Energy': '#FFD4D4', 'Transportation': '#DDE8B9', 'Water': '#C5E8F2'}
    col1, col2 = st.columns([1, 1])
    with col1:
        sector_counts = final_projects['sector1'].value_counts()
        fig_sector = go.Figure(data=[go.Pie(
            labels=sector_counts.index,
            values=sector_counts.values,
            hole=0.4,
            marker_colors=[sector_colors.get(s, '#888888') for s in sector_counts.index],
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(size=14),
            hovertemplate='<b>%{label}</b><br>Projects: %{value}<br>Proportion: %{percent}<extra></extra>'
        )])
        fig_sector.update_layout(
            title=dict(text='Project Distribution by Sector', font=dict(size=16)),
            height=350,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_sector, use_container_width=True)
    with col2:
        selected_sector = st.radio("Select a sector for details:", list(sector_colors.keys()), horizontal=True, key="sector_radio")
        sector_df = final_projects[final_projects['sector1'] == selected_sector]
        color = sector_colors[selected_sector]
        color_light = sector_colors_light[selected_sector]
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Projects", len(sector_df))
        with m2:
            st.metric("Avg Cost", f"${sector_df['base+contingency'].mean():.0f}M")
        with m3:
            st.metric("Avg Duration", f"{sector_df['duration_planned'].mean()/12:.1f} yrs")
        # Top regions for selected sector
        top_regions = sector_df['countryname'].value_counts().head(5)
        fig_region = go.Figure(data=[go.Bar(
            x=top_regions.values,
            y=top_regions.index,
            orientation='h',
            marker_color=color,
            hovertemplate='<b>%{y}</b><br>Projects: %{x}<extra></extra>'
        )])
        fig_region.update_layout(
            title=dict(text=f'Top Countries for {selected_sector}', font=dict(size=14)),
            height=220,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title='Number of Projects',
            yaxis=dict(autorange='reversed')
        )
        st.plotly_chart(fig_region, use_container_width=True)


    st.markdown("---")
    
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
    subtab1, subtab2 = st.tabs(["Data & Processing", "Result"])
    with subtab1:
        st.header("ESG Risks in Infrastructure Projects")
        st.markdown("##### Large-scale infrastructure projects are physically large, complex, unique, involve a lot of stakeholders and shareholders, and have great impacts on society. Due to this nature, they inherently involve various environmental, social, and governance (ESG) challenges. According to World Bank, those risks can be categorized into the following categories.")        

        
        with st.container(border=True):
            col1, col2= st.columns([1, 4])
            with col1:
                st.image(BASE / "es.png", width=200)
                st.markdown("📄 [View source](https://thedocs.worldbank.org/en/doc/837721522762050108-0290022018/original/ESFFramework.pdf)")
            with col2:
                st.markdown("##### Environmental")
                st.markdown("""
    <span style="color:#000000;">• E1: Resource Efficiency and Pollution Prevention</span><br>
    <span style="color:#000000;">• E2: Biodiversity Conservation and Living Natural Resources</span>
                """, unsafe_allow_html=True)
                st.markdown("##### Social")
                st.markdown("""
    <span style="color:#000000;">• S1: Labor and Working Conditions</span><br>
    <span style="color:#000000;">• S2: Community Health and Safety</span><br>
    <span style="color:#000000;">• S3: Land Acquisition and Involuntary Resettlement</span><br>
    <span style="color:#000000;">• S4: Indigenous Peoples</span><br>
    <span style="color:#000000;">• S5: Cultural Heritage</span>
                """, unsafe_allow_html=True)

        with st.container(border=True):
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(BASE / "gov.png", width=200)
                st.markdown("📄 [View source](https://thedocs.worldbank.org/en/doc/96550c14d62154355b6edc367d4d7f33-0080012021/original/Infrastructure-Governance-Assessment-Framework-December-2020.pdf)")
            with col2:
                st.markdown("##### Governance")
                st.markdown("""
    <span style="color:#000000;">• G1: Legal Framework and Institutional Capacity</span><br>
    <span style="color:#000000;">• G2: Financial and Economic</span><br>
    <span style="color:#000000;">• G3: Procurement and Contract Management</span><br>
    <span style="color:#000000;">• G4: Operations and Performance</span><br>
    <span style="color:#000000;">• G5: Transparency and Integrity</span>
                """, unsafe_allow_html=True)
        
        # Load and display seed source documents
        st.subheader("Source Documents for Term Extraction")
        st.markdown("From the source document, each category (E1-G5) was considered as one document, and terms were extracted from each document. Cleaned and n-gram preserved text is shown below.")
        st.caption("E: Environmental, S: Social, G: Governance")
        seed_source = pd.read_json(BASE / "seed_streamlit.json")
        st.dataframe(seed_source[['pillar', 'code', 'description']], use_container_width=True, hide_index=True)
        selected_row = st.selectbox(
            "Select a category to view full text:",
            options=seed_source['code'].tolist(),
            format_func=lambda x: f"{seed_source[seed_source['code']==x]['pillar'].values[0]} - {x}: {seed_source[seed_source['code']==x]['description'].values[0]}"
        )
        with st.expander(f"View full text for: {selected_row}"):
            full_text = seed_source[seed_source['code'] == selected_row]['text'].values[0]
            st.markdown(f"<div style='background-color:#f0f0f0; padding:15px; border-radius:10px; max-height:400px; overflow-y:auto;'>{full_text}</div>", unsafe_allow_html=True)
        st.markdown("---")

        # Text Data Preprocessing Section
        st.subheader("Text Data Preprocessing")
        st.markdown("##### Step 1. Basic Cleaning")
        st.markdown("""
        Typo correction, special character removal, hyphenated- and non-hyphenated term consistency correction, etc.
        """)
        st.markdown("##### Step 2. N-gram Extraction & Preservation")
        
        st.markdown("""
        Bigrams and trigrams were extracted using specific POS (Part-of-Speech) patterns to capture meaningful multi-word terms relevant to ESG risks.
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
        
        st.markdown("###### Filtering and Selection Process")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("**1: Pattern Matching**\n\nExtract n-grams matching the defined POS patterns using spaCy NLP")
        
        with col2:
            st.info("**2: Frequency Filtering**\n\nPreserve important n-grams based on percentile thresholds and document frequency")
        
        with col3:
            st.info("**3: TF-IDF Scoring**\n\nRank and select final terms based on TF-IDF scores across categories")

        st.markdown("---")
    with subtab2:
        # Load seed terms
        seed_terms = pd.read_csv(BASE / "seed_final_314.csv")
        st.header("Seed Term Extraction Result")
        st.markdown("##### Important terms are extracted from the corpus for each pillar, and for each category. Categories include different themes, so sub-categories were created based on embedding scores using transformer-based MPNET model, clustering, and manual curation.")
        st.markdown("---")
        st.markdown("Select a category to view extracted seed terms.")
        col1, col2 = st.columns(2)
        pillar_order = ['E', 'S', 'G']
        pillar_labels = {'E': 'Environmental', 'S': 'Social', 'G': 'Governance'}
        pillar_colors = {'E': '#81C784', 'S': '#64B5F6', 'G': '#FFB74D'}
        pillar_colors_light = {'E': '#C8E6C9', 'S': '#BBDEFB', 'G': '#FFE0B2'}
        with col1:
            selected_pillar = st.selectbox(
                "Select Pillar",
                options=pillar_order,
                format_func=lambda x: pillar_labels[x],
                key="seed_pillar"
            )
        with col2:
            categories = seed_terms[seed_terms['Pillar'] == selected_pillar]['Category'].unique()
            selected_category = st.selectbox(
                "Select Category",
                options=categories,
                key="seed_category"
            )
        # Extract category code (e.g., "E1" from "E1: Pollution Prevention...")
        category_code = selected_category.split(":")[0].strip()
        dendrogram_path = BASE / f"dendrogram_{category_code}_horizontal.png"
        # Show dendrogram

        filtered_df = seed_terms[
            (seed_terms['Pillar'] == selected_pillar) & 
            (seed_terms['Category'] == selected_category)
        ]
        subcategories = filtered_df['Subcategory'].unique()
        color = pillar_colors[selected_pillar]
        color_light = pillar_colors_light[selected_pillar]
        st.markdown(f"**{len(filtered_df)} terms across {len(subcategories)} subcategories:**")
        pillar_tag_colors = {'E': '#C8E6C9', 'S': '#BBDEFB', 'G': '#FFE0B2'}
        tag_color = pillar_tag_colors[selected_pillar]
        for subcat in subcategories:
            terms = filtered_df[filtered_df['Subcategory'] == subcat]['Term'].tolist()
            st.markdown(f"**{subcat}** ({len(terms)} terms)")
            tags_html = " ".join([
                f'<span style="background-color:{tag_color}; padding:5px 10px; margin:3px; border-radius:15px; display:inline-block; font-size:13px;">{term}</span>' 
                for term in terms
            ])
            st.markdown(tags_html, unsafe_allow_html=True)
            st.markdown("")
        st.markdown(f"Click the following expander to see dendrogram - subcategories clustered together.")
        with st.expander(f"📊 View Dendrogram for {category_code}", expanded=False):
            if dendrogram_path.exists():
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(str(dendrogram_path), use_container_width=True)
            else:
                st.warning(f"Dendrogram image not found for {category_code}")
        st.markdown("---")

with tab4:
    subtab1, subtab2 = st.tabs(["Data & Processing", "Result"])
    with subtab1:
        st.header("Data Processing for Metadata")
        st.markdown("##### This page summarizes the data preprocessing steps, including cost conversion and missing data handling to convert World Bank project costs to comparable **2019 USD values** for analysis. Project cost data are in nominal value at the year of approval, but the data spans from 1989 to 2012 (for the approval year) or 1999 to 2019 (for the completion year). For apple-to-apple comparison, every value was converted to 2019, to adjust for the following discrepancies. Essentially, it takes care of _What was the economic scale and resource commitment of this project within its own national economy?_ question.")
        st.markdown("""
        - Purchasing Power Parity adjustment: What $500M USD buys in developing countries is different from what it buys in developed countries.
        - Temporal adjustment: What $500M buys in 2001 is different from what it buys in 2019.
        """)
        st.markdown("---")
            
        # 1. Overview
        st.subheader("Input data: ")                
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Projects", "462")
        with col2:
            avg_cost = final_projects['base+contingency'].mean()
            st.metric("Avg Cost (at appraisal)", f"${avg_cost:.0f}M")
        with col3:
            st.metric("Approval Year Range", f"{final_projects['approval_year'].min()} - {final_projects['approval_year'].max()}")
        with col4:
            st.metric("Completion Year Range", f"{final_projects['closingyear'].min()} - {final_projects['closingyear'].max()}")

            
        # 2. Step 1: PLR Adjustment
        st.markdown("#### Step 1: PLR (Price Level Ratio) Adjustment")
            
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
        st.markdown("#### Step 2: US PPI (Producer Price Index) Adjustment")
            
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
        st.markdown("#### Combined Adjustment")
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
        st.info("**Note:** Adjusted figures are NOT used in the analysis. They were only used to classify whether a project qualifies as 'large-scale' in 2019 USD-equivalent dollars. The threshold for 'large-scale' is **$500M USD**, following the US Department of Transportation definition. For further cost-related analysis, only the **'cost change'** variable (directly from World Bank) will be used.")
        
        # st.markdown("Final project list can be downloaded in the next tab.")

        st.markdown("---")
    with subtab2:
        # st.markdown("##### In this page, you can see the processed metadata.")
        # st.markdown("""
        # Source: World Bank\n
        # This data was complied using various data sources in World Bank.
        # """)
        # DATA_PATH = BASE / "cost_converted_462projects.csv"
        # df = pd.read_csv(DATA_PATH)
            
        # col1, col2, col3 = st.columns(3)
        # with col1:
        #     st.metric("Projects", len(df))
        # with col2:
        #     st.metric("Columns", len(df.columns))
        # with col3:
        #     st.metric("Year Range", f"{df['approval_year'].min()} - {df['approval_year'].max()}")
            
        # st.dataframe(df.head(100), use_container_width=True)

        st.header("Project Metadata (Processed)")
        final_projects = pd.read_csv(BASE / "fin_project_metadata_280.csv")
            
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Projects", len(final_projects))
        with col2:
            avg_cost = final_projects['planned_cost_adj_both'].mean()
            st.metric("Avg Cost", f"${avg_cost:.0f}M")
        with col3:
            st.metric("Approval Year Range", f"{final_projects['approval_year'].min()} - {final_projects['approval_year'].max()}")
        with col4:
            st.metric("Completion Year Range", f"{final_projects['closingyear'].min()} - {final_projects['closingyear'].max()}")
            
        st.dataframe(final_projects, use_container_width=True, hide_index=True)
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Cost Comparison: Before vs After Processing")
            sector_colors = {'Energy': '#FF6B6B', 'Transportation': '#A9C25E', 'Water': '#45B7D1'}
            sector_colors_light = {'Energy': '#FFD4D4', 'Transportation': '#DDE8B9', 'Water': '#C5E8F2'}
            selected_sector = st.radio("Select a sector:", list(sector_colors.keys()), horizontal=True, key="cost_sector_radio")
            sector_df = final_projects[final_projects['sector1'] == selected_sector]
            avg_initial = sector_df['base+contingency'].mean()
            avg_adjusted = sector_df['planned_cost_adj_both'].mean()
            avg_ratio = (avg_adjusted / avg_initial) * 100
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Projects", len(sector_df))
            with m2:
                st.metric("Avg Initial Cost", f"${avg_initial:.0f}M")
            with m3:
                st.metric("Avg Adjusted Cost", f"${avg_adjusted:.0f}M")
            with m4:
                st.metric("Avg Cost Ratio", f"{avg_ratio:.1f}%")
            st.info("**Note:** Adjusted figures are NOT used in the analysis. They were only used to classify whether a project qualifies as 'large-scale' in 2019 USD-equivalent dollars. The threshold for 'large-scale' is **$500M USD**, following the US Department of Transportation definition. For further cost-related analysis, only the **'cost change'** variable (directly from World Bank) will be used.")
        
        with col2:
            st.subheader("Project Timeline: Approval vs Completion Year")
            approval_counts = final_projects['approval_year'].value_counts().sort_index().reset_index()
            approval_counts.columns = ['Year', 'Count']
            completion_counts = final_projects['closingyear'].value_counts().sort_index().reset_index()
            completion_counts.columns = ['Year', 'Count']
            fig_year = go.Figure()
            fig_year.add_trace(go.Bar(
                x=approval_counts['Year'],
                y=approval_counts['Count'],
                name='Approval Year',
                marker_color='#00CC96'
            ))
            fig_year.add_trace(go.Bar(
                x=completion_counts['Year'],
                y=completion_counts['Count'],
                name='Completion Year',
                marker_color='#AB63FA'
            ))
            fig_year.update_layout(
                barmode='group',
                xaxis_title='Year',
                yaxis_title='Number of Projects',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
                margin=dict(t=50, b=20, l=20, r=20),
                height=400
            )
            st.plotly_chart(fig_year, use_container_width=True)
            #st.caption(f"Approval: {int(final_projects['approval_year'].min())}–{int(final_projects['approval_year'].max())} | Completion: {int(final_projects['closingyear'].min())}–{int(final_projects['closingyear'].max())}")
        st.markdown("---")
    

with tab5:
    subtab1, subtab2 = st.tabs(["Data & Processing", "Result"])
    with subtab1:
        st.header("Data Processing for Text Data")
        st.markdown("##### This page summarizes the data preprocessing steps for the text data extracted from the project-related reports from the World Bank. For each of the 280 projects, we use two types of projects, that allow us to see _what happened during the project.")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Project Appraisal Document (PAD)**: Written at planning stage")
            with open(BASE / "P130164_PAD.pdf", "rb") as f:
                st.download_button("📥 Download Sample PAD", f, file_name="P130164_PAD.pdf")
        with col2:
            st.markdown("**Implementation Completion Report (ICR)**: Written after project completion")
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
        st.Ngr("Text Preprocessing")
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
        st.subheader("N-gram Processing")
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
        
        st.markdown("---")
        st.subheader("Embedding Analysis & Final ESG Taxonomy")
        esg_dict = pd.read_csv(BASE / "esg_dictionary_final_2407.csv")
        col1, col2 = st.columns(2)
        with col1:
            st.info("""**1. Embedding**
    - 314 seed terms + 8,067 corpus candidates \n
    - Model: `all-mpnet-base-v2` (768-dim)\n
    - Source: World Bank ESF + InfraSAP""")
        with col2:
            st.info("""**2. Subcategory Clustering**
    - K-means within each ESG category\n
    - Silhouette score for optimal k (2–7)\n
    - Creates semantic subgroups""")
        col1, col2 = st.columns(2)
        with col1:
            st.success("""**3. Dictionary Expansion**
    - Dual threshold filtering (both ≥ 0.55):\n
    - Seed-term similarity\n
    - Subcategory centroid similarity\n
    - Single-category assignment only""")
        with col2:
            st.success("""**4. Manual Curation**
    - Removed problematic seed terms\n
    - Blacklisted ~40 noise terms\n
    - Final quality control pass""")
        st.markdown("---")
    with subtab2:
        st.markdown("##### Final Result")
        res_col1, res_col2, res_col3, res_col4 = st.columns(4)
        with res_col1:
            st.metric("Seed Terms", f"{len(esg_dict[esg_dict['is_seed'] == True]):,}")
        with res_col2:
            st.metric("Expanded Terms", f"{len(esg_dict[esg_dict['is_seed'] == False]):,}")
        with res_col3:
            st.metric("Total Dictionary", f"{len(esg_dict):,}")
        with res_col4:
            st.metric("Categories", esg_dict['category'].nunique())
        st.caption("Thresholds chosen based on silhouette analysis — all categories show positive coherence.")
        st.markdown("---")
        # Define colors and labels once
        pillar_colors = {'E': '#81C784', 'S': '#64B5F6', 'G': '#FFB74D'}
        pillar_colors_light = {'E': '#C8E6C9', 'S': '#BBDEFB', 'G': '#FFE0B2'}
        pillar_labels = {'E': 'Environmental', 'S': 'Social', 'G': 'Governance'}
        cat_display = {
            'ESS3_P': 'E1', 'ESS3_R': 'E2', 'ESS6': 'E3',
            'ESS2': 'S1', 'ESS4': 'S2', 'ESS5': 'S3', 'ESS7': 'S4', 'ESS8': 'S5',
            'DIM1': 'G1', 'DIM2_3': 'G2', 'DIM6': 'G3', 'DIM7': 'G4', 'DIM8_9': 'G5'
        }
        st.subheader("Term Distribution by Pillar and Category")
        dist_df = esg_dict.groupby(['pillar', 'category_display', 'is_seed']).size().reset_index(name='count')
        dist_pivot = dist_df.pivot_table(index=['pillar', 'category_display'], columns='is_seed', values='count', fill_value=0).reset_index()
        dist_pivot = dist_pivot.rename(columns={True: "Seed", False: "Expanded"})
        if "Seed" not in dist_pivot.columns:
            dist_pivot["Seed"] = 0
        if "Expanded" not in dist_pivot.columns:
            dist_pivot["Expanded"] = 0
        dist_pivot['Total'] = dist_pivot['Seed'] + dist_pivot['Expanded']
        dist_pivot = dist_pivot.sort_values(['pillar', 'Total'], ascending=[True, False])
        fig = go.Figure()
        for pillar in ['E', 'S', 'G']:
            pdf = dist_pivot[dist_pivot['pillar'] == pillar]
            fig.add_trace(go.Bar(
                name=f"{pillar_labels[pillar]} - Seed",
                y=pdf['category_display'].astype(str).tolist(),
                x=pdf['Seed'],
                orientation='h',
                marker_color=pillar_colors[pillar],
                legendgroup=pillar,
                hovertemplate='%{y}<br>Seed: %{x}<extra></extra>'
            ))
            fig.add_trace(go.Bar(
                name=f"{pillar_labels[pillar]} - Expanded",
                y=pdf['category_display'].astype(str).tolist(),
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
            filtered_by_pillar = esg_dict[esg_dict['pillar'] == selected_pillar]
            category_displays = filtered_by_pillar['category_display'].unique().tolist()
            selected_category_display = st.selectbox(
                "Select Category",
                options=category_displays,
                key="subtab2_category"
            )
        filtered_df = esg_dict[
            (esg_dict['pillar'] == selected_pillar) &
            (esg_dict['category_display'] == selected_category_display)
        ]
        seed_terms_list = filtered_df[filtered_df['is_seed'] == True]['term'].tolist()
        expanded_terms_list = filtered_df[filtered_df['is_seed'] == False]['term'].tolist()
        st.markdown(f"**{len(filtered_df)} terms in {selected_category_display}** ({len(seed_terms_list)} seed, {len(expanded_terms_list)} expanded)")
        color_seed = pillar_colors[selected_pillar]
        color_expanded = pillar_colors_light[selected_pillar]
        subcategories = filtered_df['subcategory'].unique()
        for subcat in subcategories:
            subcat_df = filtered_df[filtered_df['subcategory'] == subcat]
            subcat_seeds = subcat_df[subcat_df['is_seed'] == True]['term'].tolist()
            subcat_expanded = subcat_df[subcat_df['is_seed'] == False]['term'].tolist()
            st.markdown(f"**{subcat}** ({len(subcat_seeds)} seed, {len(subcat_expanded)} expanded)")
            seed_html = " ".join([
                f'<span style="background-color:{color_seed}; padding:5px 10px; margin:3px; border-radius:15px; display:inline-block; font-size:13px; font-weight:500;">{term}</span>'
                for term in subcat_seeds
            ])
            expanded_html = " ".join([
                f'<span style="background-color:{color_expanded}; padding:5px 10px; margin:3px; border-radius:15px; display:inline-block; font-size:13px;">{term}</span>'
                for term in subcat_expanded
            ])
            st.markdown(seed_html + " " + expanded_html, unsafe_allow_html=True)
            st.markdown("")
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"<span style='background-color:{color_seed}; padding:4px 8px; border-radius:10px;'>■</span> **Seed Terms**", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<span style='background-color:{color_expanded}; padding:4px 8px; border-radius:10px;'>■</span> **Expanded Terms**", unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("Interactive Cluster Visualization")
        viz_df = pd.read_csv(BASE / "esg_dictionary_viz.csv")
        viz_col1, viz_col2 = st.columns([1, 3])
        with viz_col1:
            viz_pillar = st.radio("Select Pillar", ['E', 'S', 'G'], 
                                format_func=lambda x: pillar_labels[x],
                                key="viz_pillar")
            pillar_categories = viz_df[viz_df['pillar'] == viz_pillar]['category'].unique().tolist()
            cat_to_display = {
                'ESS3_P': 'E1: Pollution Prevention and Management',
                'ESS3_R': 'E2: Resource Efficiency',
                'ESS6': 'E3: Biodiversity Conservation',
                'ESS2': 'S1: Labor and Working Conditions',
                'ESS4': 'S2: Community Health and Safety',
                'ESS5': 'S3: Land Acquisition and Involuntary Resettlement',
                'ESS7': 'S4: Indigenous Peoples',
                'ESS8': 'S5: Cultural Heritage',
                'DIM1': 'G1: Legal Framework and Institutional Capacity',
                'DIM2_3': 'G2: Financial and Economic',
                'DIM6': 'G3: Procurement and Contract Management',
                'DIM7': 'G4: Operations and Performance',
                'DIM8_9': 'G5: Transparency and Integrity'
            }
            st.markdown("**Categories**")
            selected_cats = []
            for cat in pillar_categories:
                if st.checkbox(cat_to_display.get(cat, cat), value=True, key=f"viz_cat_{cat}"):
                    selected_cats.append(cat)
        with viz_col2:

            fig = go.Figure()
            other_df = viz_df[viz_df['pillar'] != viz_pillar]
            fig.add_trace(go.Scatter(
                x=other_df['x'], y=other_df['y'],
                mode='markers',
                marker=dict(size=6, color='lightgray', opacity=0.3),
                name='Other pillars',
                hoverinfo='skip'
            ))
            all_colors = px.colors.qualitative.Set2 + px.colors.qualitative.Set3 + px.colors.qualitative.Pastel1
            color_idx = 0
            for cat in selected_cats:
                cat_df = viz_df[viz_df['category'] == cat]
                cat_display = cat_to_display.get(cat, cat)
                subcategories = cat_df['subcategory'].unique()
                for subcat in subcategories:
                    subcat_df = cat_df[cat_df['subcategory'] == subcat]
                    fig.add_trace(go.Scatter(
                        x=subcat_df['x'], y=subcat_df['y'],
                        mode='markers',
                        marker=dict(size=8, color=all_colors[color_idx % len(all_colors)], opacity=0.7),
                        name=subcat,
                        legendgroup=cat,
                        legendgrouptitle_text=cat_display,
                        text=subcat_df['term'],
                        hovertemplate='<b>%{text}</b><br>' + subcat + '<extra></extra>'
                    ))
                    color_idx += 1
            fig.update_layout(
                height=600,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showline=True, linecolor='black', title='Dimension 1'),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showline=True, linecolor='black', title='Dimension 2'),
                legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.02, title='Categories', tracegroupgap=10),
                margin=dict(l=20, r=20, t=20, b=20),
                plot_bgcolor='white'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")

with tab6:
    st.header("Analysis")
    subtab1, subtab2 = st.tabs(["Initial/Exploratory Data Analysis", "Regression Analysis"])
    with subtab1:
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
    with subtab2:
        st.markdown("---")
