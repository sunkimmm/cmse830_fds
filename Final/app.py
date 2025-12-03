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
    " Risk Analysis",
    
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
    st.markdown("Hoover over the map to see detailed information for each country.")
    
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
    
    # Sector and Region Distribution
    st.subheader("Project Distribution by Sector and Region")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sector_counts = final_projects['sector1'].value_counts().reset_index()
        sector_counts.columns = ['Sector', 'Count']
        fig_sector = px.pie(sector_counts, values='Count', names='Sector',
                           color_discrete_sequence=px.colors.qualitative.Set2,
                           hole=0.3)
        fig_sector.update_traces(textposition='inside', textinfo='percent+label', textfont_size=16)
        fig_sector.update_layout(showlegend=False, margin=dict(t=30, b=20, l=20, r=20),
                                title=dict(text='Projects by Sector', font=dict(size=20)))
        st.plotly_chart(fig_sector, use_container_width=True)
    
    with col2:
        region_counts = final_projects['regionname'].value_counts().reset_index()
        region_counts.columns = ['Region', 'Count']
        fig_region = px.pie(region_counts, values='Count', names='Region',
                           color_discrete_sequence=px.colors.qualitative.Pastel,
                           hole=0.3)
        fig_region.update_traces(textposition='inside', textinfo='percent+label', textfont_size=16)
        fig_region.update_layout(showlegend=False, margin=dict(t=30, b=20, l=20, r=20),
                                title=dict(text='Projects by Region', font=dict(size=20)))
        st.plotly_chart(fig_region, use_container_width=True)
    
    st.markdown("---")
    
    # Cost distribution by sector
    st.subheader("Project Cost Distribution by Sector")
    
    fig_box = px.box(final_projects, x='sector1', y='base+contingency',
                    color='sector1',
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    labels={'sector1': 'Sector', 'base+contingency': 'Project Cost (USD Million)'})
    fig_box.update_layout(showlegend=False, margin=dict(t=30, b=20, l=20, r=20))
    st.plotly_chart(fig_box, use_container_width=True)
    
    st.markdown("---")
    
    # Timeline
    st.subheader("Projects Over Time")
    
    year_sector = final_projects.groupby(['approval_year', 'sector1']).size().reset_index(name='count')
    fig_timeline = px.bar(year_sector, x='approval_year', y='count', color='sector1',
                         color_discrete_sequence=px.colors.qualitative.Set2,
                         labels={'approval_year': 'Approval Year', 'count': 'Number of Projects', 'sector1': 'Sector'})
    fig_timeline.update_layout(margin=dict(t=30, b=20, l=20, r=20))
    st.plotly_chart(fig_timeline, use_container_width=True)

with tab2:
    st.title("ESG Risks in Infrastructure Projects")
    st.markdown("##### Large-scale infrastructure projects are physically large, complex, unique, involves a lot of stakeholders and shareholders, and have great impacts on society. Due to this nature, they inherently involve various environmental, social, and governance (ESG) challenges. According to World Bank, those risks can be categorized into the following categories.")
    st.markdown("##### To see what risks exist in projects, relevant terms were existed from the following two World Bank documents.")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(BASE / "es.png", caption="Environmental & Social Risks", width=400)
    with col2:
        st.image(BASE / "gov.png", caption="Governance Risks", width=400)
    
    st.markdown("---")

    # Load seed terms
    seed_terms = pd.read_csv(BASE / "seed_final.csv")  # adjust filename
    
    st.subheader("ESG Risk Categories and Seed Terms")
    
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

with tab4:
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

with tab5:
    st.title(" Risk Analysis")
