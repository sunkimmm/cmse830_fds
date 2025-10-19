import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import numpy as np
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Infrastructure Project Risk Analysis",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    h1 {color: #2c3e50; padding-bottom: 1rem;}
    h2 {color: #34495e; padding-top: 1rem;}
    .stAlert {margin-top: 1rem; margin-bottom: 1rem;}
    </style>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    import os
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'adb_projects_clean_final.csv')
    df = pd.read_csv(csv_path)
    
    # Create derived columns based on your analysis
    df['size_binary'] = df['project_size'].map({
        'medium': 'Non-Mega (<$1B)',
        'large': 'Non-Mega (<$1B)',
        'mega': 'Mega (≥$1B)'
    })
    
    # Add risk_level if you have risk_category column
    if 'risk_category' in df.columns:
        risk_level_map = {
            'No Risk': 0,
            'Environmental Only': 1,
            'Social Only': 1,
            'Both': 2
        }
        df['risk_level'] = df['risk_category'].map(risk_level_map)
    
    # Create social_severity column (maximum of indigenous and resettlement risks)
    if 'safe_ind' in df.columns and 'safe_res' in df.columns:
        def get_max_severity(row):
            severities = []
            if pd.notna(row['safe_ind']) and row['safe_ind'] in ['A', 'B', 'C']:
                severities.append(row['safe_ind'])
            if pd.notna(row['safe_res']) and row['safe_res'] in ['A', 'B', 'C']:
                severities.append(row['safe_res'])
            
            if not severities:
                return None
            # Return the highest severity (A > B > C)
            if 'A' in severities:
                return 'A'
            elif 'B' in severities:
                return 'B'
            else:
                return 'C'
        
        df['social_severity'] = df.apply(get_max_severity, axis=1)
    
    return df

df = load_data()

# Sidebar
st.sidebar.title("🏗️ Infrastructure Project Risk Analysis")
st.sidebar.markdown("---")
st.sidebar.info(
    """
    Analysis of Asian Development Bank infrastructure projects examining
    how project size and risk interact to affect delays.
    
    **Key Focus**: Large vs Mega projects and Risk Analysis
    """
)

# ADD GLOBAL FILTERS HERE
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filters")

# Sector filter
sector_options = ['All Sectors'] + sorted(df['sector1'].unique().tolist())
selected_sector = st.sidebar.selectbox(
    "Select Sector",
    options=sector_options,
    index=0,
    key='global_sector_filter'
)

# Project Size filter (Large vs Mega)
size_options = ['All Sizes', 'Large ($500M-$1B)', 'Mega (≥$1B)']
selected_size = st.sidebar.selectbox(
    "Select Project Size",
    options=size_options,
    index=0,
    key='global_size_filter'
)

# Apply filters to create filtered dataframe
df_filtered = df.copy()

if selected_sector != 'All Sectors':
    df_filtered = df_filtered[df_filtered['sector1'] == selected_sector]

if selected_size == 'Large ($500M-$1B)':
    df_filtered = df_filtered[df_filtered['project_size'] == 'large']
elif selected_size == 'Mega (≥$1B)':
    df_filtered = df_filtered[df_filtered['project_size'] == 'mega']

# Display filter summary in sidebar
st.sidebar.markdown("---")
st.sidebar.metric("Filtered Projects", len(df_filtered))
st.sidebar.metric("Avg Delay", f"{df_filtered['delay'].mean():.2f}y" if len(df_filtered) > 0 else "N/A")
st.sidebar.metric("Avg Cost", f"${df_filtered['totalcost_initial_adj'].mean():.0f}M" if len(df_filtered) > 0 else "N/A")

# Color schemes (consistent across all charts)
sector_colors = {'Energy': '#d95f02', 'Transportation': '#57c4ad', 'Water': '#0571b0'}
risk_level_colors = {0: '#fcc5c0', 1: '#fa9fb5', 2: '#c51b8a'}
size_colors = {'medium': '#dfe318', 'large': '#8bd646', 'mega': '#2fb47c'}

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Project Overview",
    "⚠️ Risk Analysis",
    "👀 Additional Analysis",
    "📊 Data & Processing"
])

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================
with tab1:
    st.title("🔍 Project Overview")
    
    # Key metrics at the top
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Projects", len(df))
    with col2:
        st.metric("Countries", df['countryname'].nunique())
    with col3:
        total_investment = df['totalcost_initial_adj'].sum() / 1000
        st.metric("Total Investment", f"${total_investment:.1f}B")
    with col4:
        avg_delay = df['delay'].mean()
        st.metric("Average Delay", f"{avg_delay:.2f} years")
    
    st.markdown("---")
    
    # Geographic Maps
    st.subheader("Geographic Distribution")
    
    # Prepare data for choropleth maps
    country_total = df.groupby('countryname').agg({
        'projectid': 'count',
        'sector1': lambda x: ', '.join(x.value_counts().index[:3])
    }).reset_index()
    country_total.columns = ['countryname', 'total_projects', 'main_sectors']
    
    country_avg_cost = df.groupby('countryname').agg({
        'projectid': 'count',
        'totalcost_initial_adj': 'mean',
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
        scope='asia',
        projection_type='natural earth',
        showland=True,
        landcolor='rgb(243, 243, 243)',
        coastlinecolor='rgb(204, 204, 204)',
        showcountries=True,
        countrycolor='rgb(204, 204, 204)'
    )
    
    fig_maps.update_layout(
        title_text='Geographic Distribution of Projects by Country',
        title_x=0.5,
        height=600,
        font=dict(family='Arial'),
        showlegend=False
    )
    
    st.plotly_chart(fig_maps, use_container_width=True)
    
    st.info("💡 **Insight**: India has the greatest number of projects, but China has projects with higher average cost per project.")
    
    st.markdown("---")
    
    # Bubble map by sector
    st.subheader("Projects by Country and Sector")
    
    # Aggregate by country AND sector
    country_sector_data = df.groupby(['countryname', 'sector1']).agg({
        'projectid': 'count',
        'totalcost_initial_adj': 'sum'
    }).reset_index()
    country_sector_data.columns = ['country', 'sector', 'project_count', 'total_cost']
    
    country_coords = {
        'Afghanistan': (33.9391, 67.7100), 'Bangladesh': (23.6850, 90.3563),
        'Bhutan': (27.5142, 90.4336), 'India': (20.5937, 78.9629),
        'Maldives': (3.2028, 73.2207), 'Nepal': (28.3949, 84.1240),
        'Pakistan': (30.3753, 69.3451), 'Sri Lanka': (7.8731, 80.7718),
        'Brunei Darussalam': (4.5353, 114.7277), 'Cambodia': (12.5657, 104.9910),
        'Indonesia': (-0.7893, 113.9213), 'Lao PDR': (19.8563, 102.4955),
        'Laos': (19.8563, 102.4955), "Lao People's Democratic Republic": (19.8563, 102.4955),
        'Malaysia': (4.2105, 101.9758), 'Myanmar': (21.9162, 95.9560),
        'Philippines': (12.8797, 121.7740), 'Singapore': (1.3521, 103.8198),
        'Thailand': (15.8700, 100.9925), 'Timor-Leste': (-8.8742, 125.7275),
        'Viet Nam': (14.0583, 108.2772), 'Vietnam': (14.0583, 108.2772),
        'China': (35.8617, 104.1954), "China, People's Republic of": (35.8617, 104.1954),
        'Hong Kong': (22.3193, 114.1694), 'Japan': (36.2048, 138.2529),
        'Korea, Republic of': (35.9078, 127.7669), 'Mongolia': (46.8625, 103.8467),
        'Taiwan': (23.6978, 120.9605), 'Armenia': (40.0691, 45.0382),
        'Azerbaijan': (40.1431, 47.5769), 'Georgia': (42.3154, 43.3569),
        'Kazakhstan': (48.0196, 66.9237), 'Kyrgyz Republic': (41.2044, 74.7661),
        'Kyrgyzstan': (41.2044, 74.7661), 'Tajikistan': (38.8610, 71.2761),
        'Turkmenistan': (38.9697, 59.5563), 'Uzbekistan': (41.3775, 64.5853),
        'Cook Islands': (-21.2367, -159.7777), 'Fiji': (-17.7134, 178.0650),
        'Kiribati': (-3.3704, -168.7340), 'Marshall Islands': (7.1315, 171.1845),
        'Micronesia': (7.4256, 150.5508), 'Micronesia, Federated States of': (7.4256, 150.5508),
        'Nauru': (-0.5228, 166.9315), 'Palau': (7.5150, 134.5825),
        'Papua New Guinea': (-6.3150, 143.9555), 'Samoa': (-13.7590, -172.1046),
        'Solomon Islands': (-9.6457, 160.1562), 'Tonga': (-21.1789, -175.1982),
        'Tuvalu': (-7.1095, 177.6493), 'Vanuatu': (-15.3767, 166.9592)
    }
    
    # Add coordinates
    np.random.seed(114)
    country_sector_data['lat'] = country_sector_data['country'].map(lambda x: country_coords.get(x, (None, None))[0])
    country_sector_data['lon'] = country_sector_data['country'].map(lambda x: country_coords.get(x, (None, None))[1])
    
    # Add small random offset to prevent exact overlap
    country_sector_data['lat'] = country_sector_data['lat'] + np.random.uniform(-0.3, 0.3, len(country_sector_data))
    country_sector_data['lon'] = country_sector_data['lon'] + np.random.uniform(-0.3, 0.3, len(country_sector_data))
    
    country_sector_data = country_sector_data.dropna(subset=['lat', 'lon'])
    
    fig_bubble = px.scatter_geo(
        country_sector_data,
        lat='lat', lon='lon', size='project_count', color='sector',
        hover_name='country',
        hover_data={'sector': True, 'project_count': True, 'total_cost': ':.2f', 'lat': False, 'lon': False},
        color_discrete_map=sector_colors,
        title='Geographic Distribution of Projects by Country and Sector',
        size_max=40,
        labels={'project_count': 'Projects', 'total_cost': 'Total Cost (M USD)', 'sector': 'Sector'}
    )
    
    fig_bubble.update_geos(
        scope='asia', projection_type='natural earth',
        showland=True, landcolor='rgb(243, 243, 243)',
        coastlinecolor='rgb(204, 204, 204)',
        showcountries=True, countrycolor='rgb(204, 204, 204)',
        center=dict(lat=15, lon=100)
    )
    
    fig_bubble.update_layout(height=700, font=dict(family='Arial'))
    
    st.plotly_chart(fig_bubble, use_container_width=True)
    st.info("💡 **Insight**: In most countries, transportation is the dominant sector. In India, Energy projects are the second most dominant sector while in China, Water is the second most dominant sector." \
    "Overall, Transportation is the most common, followed by Energy projects.")
    st.markdown("---")
    
    # Distribution charts
    st.subheader("Project Distribution")
    
    # Summary statistics by sector
    col1, col2, col3 = st.columns(3)
    
    with col1:
        energy_data = df[df['sector1'] == 'Energy']
        st.metric("Energy Projects", len(energy_data), f"{energy_data['delay'].mean():.2f}y avg delay")
    
    with col2:
        transport_data = df[df['sector1'] == 'Transportation']
        st.metric("Transportation Projects", len(transport_data), f"{transport_data['delay'].mean():.2f}y avg delay")
    
    with col3:
        water_data = df[df['sector1'] == 'Water']
        st.metric("Water Projects", len(water_data), f"{water_data['delay'].mean():.2f}y avg delay")
    
    st.markdown("---")

    fig_dist = make_subplots(
        rows=1, cols=2, 
        subplot_titles=('Projects by Sector', 'Projects by Region and Sector'), 
        horizontal_spacing=0.1
    )
    
    sector_order = ['Energy', 'Transportation', 'Water']
    sector_counts = df['sector1'].value_counts()
    sector_counts = sector_counts.reindex(sector_order, fill_value=0)
    
    # Add first subplot (Projects by Sector)
    fig_dist.add_trace(
        go.Bar(
            x=sector_counts.index, y=sector_counts.values,
            marker=dict(color=[sector_colors.get(sector, '#95a5a6') for sector in sector_counts.index], line=dict(width=0)),
            text=sector_counts.values, textposition='auto',
            textfont=dict(size=14, color='white', family='Arial'),
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Add second subplot (Projects by Region and Sector)
    region_counts = df['region'].value_counts().sort_values(ascending=False)
    regions = region_counts.index
    
    for sector in sector_order:
        sector_by_region = df[df['sector1'] == sector].groupby('region').size()
        sector_by_region = sector_by_region.reindex(regions, fill_value=0)
        
        fig_dist.add_trace(
            go.Bar(
                x=regions, y=sector_by_region.values,
                name=sector,
                marker=dict(color=sector_colors[sector], line=dict(width=0)),
                showlegend=True, legendgroup='sector'
            ),
            row=1, col=2
        )
    
    # Update axes
    fig_dist.update_xaxes(title_text='Sector', tickfont=dict(size=14), row=1, col=1)
    fig_dist.update_xaxes(title_text='Region', tickfont=dict(size=14), tickangle=-30, row=1, col=2)
    fig_dist.update_yaxes(title_text='Number of Projects', gridcolor='lightgray', row=1, col=1)
    fig_dist.update_yaxes(title_text='Number of Projects', gridcolor='lightgray', row=1, col=2)
    
    # Update layout
    fig_dist.update_layout(
        title=dict(
            text='Distribution of Projects by Sector and Region',
            font=dict(size=18, family='Arial', color='black'),
            x=0.5, xanchor='center'
        ),
        plot_bgcolor='white', height=500, font=dict(family='Arial'),
        barmode='stack',
        legend=dict(title=dict(text='Sector'), x=1.0, y=0.95, xanchor='left')
    )
    
    st.plotly_chart(fig_dist, use_container_width=True)

    #st.title("Project Sector Analysis")
    
    #st.markdown("### How do delays vary across sectors?")
    
    # Raincloud plots for delay and initial duration by sector
    st.subheader("Initial Duration and Delay Distribution by Sector")

    fig_combined = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Initial Planned Duration Distribution', 'Project Delay Distribution'),
        horizontal_spacing=0.12
    )

    sector_order = ['Energy', 'Transportation', 'Water']

    # Add initial duration violin plots (left panel)
    for sector in sector_order:
        sector_data = df[df['sector1'] == sector]
        
        fig_combined.add_trace(go.Violin(
            y=sector_data['duration_initial'],
            x=[sector] * len(sector_data),
            name=sector,
            box_visible=True,
            meanline_visible=True,
            points='all',
            pointpos=-0.5,
            jitter=0.3,
            marker=dict(color=sector_colors[sector]),
            scalemode='width',
            width=0.6,
            side='positive',
            line=dict(color=sector_colors[sector], width=2),
            showlegend=False
        ), row=1, col=1)

    # Add delay violin plots (right panel)
    for sector in sector_order:
        sector_data = df[df['sector1'] == sector]
        
        fig_combined.add_trace(go.Violin(
            y=sector_data['delay'],
            x=[sector] * len(sector_data),
            name=sector,
            box_visible=True,
            meanline_visible=True,
            points='all',
            pointpos=-0.5,
            jitter=0.3,
            marker=dict(color=sector_colors[sector]),
            scalemode='width',
            width=0.6,
            side='positive',
            line=dict(color=sector_colors[sector], width=2),
            showlegend=False
        ), row=1, col=2)

    # Update axes
    fig_combined.update_xaxes(
        title_text='Sector', 
        tickfont=dict(family='Arial', size=12),
        categoryorder='array',
        categoryarray=sector_order,
        row=1, col=1
    )
    fig_combined.update_xaxes(
        title_text='Sector', 
        tickfont=dict(family='Arial', size=12),
        categoryorder='array',
        categoryarray=sector_order,
        row=1, col=2
    )

    fig_combined.update_yaxes(
        title_text='Initial Duration (years)', 
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=12),
        row=1, col=1
    )
    fig_combined.update_yaxes(
        title_text='Delay (years)', 
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=12),
        row=1, col=2
    )

    # Update layout
    fig_combined.update_layout(
        title=dict(
            text='Initial Duration and Delay Distribution by Sector',
            font=dict(size=18, family='Arial', color='black'),
            x=0.5,
            xanchor='center'
        ),
        plot_bgcolor='white',
        height=600,
        font=dict(family='Arial')
    )

    st.plotly_chart(fig_combined, use_container_width=True)
    st.info("💡 **Insight**: On average, water projects tend to have the longest project implementation duration, followed by transportation and energy projects. However, there are no significant differences in delays among sectors.")

    st.markdown("---")
    
    # Three-panel bar chart: Cost, Duration, Delay
    st.subheader("Project Metrics by Sector")
    
    avg_cost = df.groupby('sector1')['totalcost_initial_adj'].mean().sort_values(ascending=False)
    avg_duration = df.groupby('sector1')['duration_final'].mean().reindex(avg_cost.index)
    avg_delay = df.groupby('sector1')['delay'].mean().reindex(avg_cost.index)
    
    fig_metrics = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Average Cost', 'Average Duration', 'Average Delay'),
        horizontal_spacing=0.12
    )
    
    # Cost
    fig_metrics.add_trace(
        go.Bar(
            x=avg_cost.index,
            y=avg_cost.values,
            marker=dict(
                color=[sector_colors.get(sector, '#95a5a6') for sector in avg_cost.index],
                line=dict(width=0)
            ),
            text=[f'${val:.0f}M' for val in avg_cost.values],
            textposition='auto',
            textfont=dict(size=12, color='white', family='Arial'),
            opacity=0.8,
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Duration
    fig_metrics.add_trace(
        go.Bar(
            x=avg_duration.index,
            y=avg_duration.values,
            marker=dict(
                color=[sector_colors.get(sector, '#95a5a6') for sector in avg_duration.index],
                line=dict(width=0)
            ),
            text=[f'{val:.1f}y' for val in avg_duration.values],
            textposition='auto',
            textfont=dict(size=12, color='white', family='Arial'),
            opacity=0.8,
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Delay
    fig_metrics.add_trace(
        go.Bar(
            x=avg_delay.index,
            y=avg_delay.values,
            marker=dict(
                color=[sector_colors.get(sector, '#95a5a6') for sector in avg_delay.index],
                line=dict(width=0)
            ),
            text=[f'{val:.1f}y' for val in avg_delay.values],
            textposition='auto',
            textfont=dict(size=12, color='white', family='Arial'),
            opacity=0.8,
            showlegend=False
        ),
        row=1, col=3
    )
    
    # Update axes
    fig_metrics.update_xaxes(title_text='Sector', tickfont=dict(family='Arial', size=11), 
                            title_font=dict(size=12, family='Arial'), row=1, col=1)
    fig_metrics.update_xaxes(title_text='Sector', tickfont=dict(family='Arial', size=11), 
                            title_font=dict(size=12, family='Arial'), row=1, col=2)
    fig_metrics.update_xaxes(title_text='Sector', tickfont=dict(family='Arial', size=11), 
                            title_font=dict(size=12, family='Arial'), row=1, col=3)
    
    fig_metrics.update_yaxes(title_text='Million USD', gridcolor='lightgray', gridwidth=0.5, 
                            tickfont=dict(family='Arial', size=11), 
                            title_font=dict(size=12, family='Arial'), row=1, col=1)
    fig_metrics.update_yaxes(title_text='Years', gridcolor='lightgray', gridwidth=0.5, 
                            tickfont=dict(family='Arial', size=11), 
                            title_font=dict(size=12, family='Arial'), row=1, col=2)
    fig_metrics.update_yaxes(title_text='Years', gridcolor='lightgray', gridwidth=0.5, 
                            tickfont=dict(family='Arial', size=11), 
                            title_font=dict(size=12, family='Arial'), row=1, col=3)
    
    fig_metrics.update_layout(
        title=dict(
            text='Project Metrics by Sector',
            font=dict(size=18, family='Arial', color='black'),
            x=0.5,
            xanchor='center'
        ),
        plot_bgcolor='white',
        height=500,
        font=dict(family='Arial')
    )
    
    st.plotly_chart(fig_metrics, use_container_width=True)
    st.info("""
    💡 **Insight**: 
    - On average, Energy projects have the highest project cost but has the highest delay.  - On average, Water projects have the lowest project cost, but takes the longest with moderate delay.
    """)

# ============================================================================
# TAB 2: RISK ANALYSIS
# ============================================================================
with tab2:
    st.title("⚠️ Risk Analysis")
    
    st.markdown("""
    This section examines how different types of risks affect project delays.
    ADB categorizes projects based on their potential environmental and social impacts.
    """)
    
    st.markdown("---")
    
    # ========================================================================
    # RISK TYPE INTRODUCTION
    # ========================================================================
    st.header("Understanding Environmental and Social Risks")
    
    st.markdown("""
    Infrastructure projects are assessed for three types of risks before approval.
    These assessments help ensure projects minimize harm and maximize sustainable development.
    """)
    
    st.markdown("---")
    
    # Environmental Risk
    st.subheader("Environmental Risk")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Environmental Risk** assesses projects' potential impact on the environment across:
        
        - Greenhouse gas emissions
        - Biodiversity and natural habitats
        - Pollution (air, water, soil)
        - Ecosystem services
        - Natural resource management
        
        Projects are categorized from **Level A (High Impact)** to **Level D (No Impact)** 
        based on the significance and irreversibility of potential environmental effects.
        """)
    
    with col2:
        st.image(
            "https://www.adb.org/sites/default/files/page/655306/images/img-environmental-safeguards.jpg",
            caption="Source: Asian Development Bank",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Social Risk Section
    st.subheader("Social Risk")
    
    st.markdown("""
    Social risks encompass two critical areas that affect communities around development projects:
    """)
    
    # Indigenous Peoples
    st.markdown("#### Indigenous Peoples")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Indigenous Peoples Risk** assesses projects' potential impact on indigenous peoples 
        in the development area:
        
        - Cultural identity and dignity
        - Traditional livelihood systems
        - Human rights and self-determination
        - Cultural uniqueness and heritage
        - Access to ancestral lands and resources
        
        This ensures projects respect and protect the rights, customs, and cultural heritage 
        of indigenous communities.
        """)
    
    with col2:
        st.image(
            "https://www.adb.org/sites/default/files/page/655306/images/img-indigenous-peoples.jpg",
            caption="Source: Asian Development Bank",
            use_container_width=True
        )
    
    st.markdown("")
    
    # Involuntary Resettlement
    st.markdown("#### Involuntary Resettlement")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Involuntary Resettlement Risk** assesses projects' impact on people who must be 
        displaced due to development:
        
        - Physical displacement from homes and land
        - Economic displacement and livelihood loss
        - Compensation and rehabilitation requirements
        - Alternative development pathways
        - Restoration of living standards
        - Continuous monitoring of affected people
        
        This ensures displaced persons are assisted in improving or at least restoring 
        their livelihoods and living standards.
        """)
    
    with col2:
        st.image(
            "https://www.adb.org/sites/default/files/page/655306/images/img-involuntary-resettlement.jpg",
            caption="Source: Asian Development Bank",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Risk Classification System
    st.subheader("Risk Classification System")
    
    st.markdown("""
    All three risk types use the same classification system:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Level A**  
        🔴 High Impact
        
        Significant adverse impacts that are diverse, irreversible, or unprecedented
        """)
    
    with col2:
        st.markdown("""
        **Level B**  
        🟡 Medium Impact
        
        Adverse impacts that are less significant, site-specific, and mostly reversible
        """)
    
    with col3:
        st.markdown("""
        **Level C**  
        🟢 Low Impact
        
        Minimal or no adverse impacts
        """)
    
    st.markdown("---")
    
    st.info("""
    💡 **Note**: This analysis first examines projects with Environmental and Social risks, and then proceed to a deeper analysis with more granular risk level represented in A, B, and C classifications.""")
    
    st.markdown("---")
    
    # ========================================================================
    # RISK DISTRIBUTION BY SECTOR
    # ========================================================================
    st.header("Risk Distribution by Sector")
    
    # st.markdown("### How are risks distributed across sectors?")
    
    # Risk profile by sector
    sector_order = ['Energy', 'Transportation', 'Water']
    sectors_filtered = [s for s in sector_order if s in df['sector1'].unique()]
    
    risk_categories = ['env_risk', 'soc_risk', 'both']
    risk_labels = {'env_risk': 'Environmental Risk', 'soc_risk': 'Social Risk', 'both': 'Both Risks'}
    risk_colors_new = {'env_risk': '#1b9e77', 'soc_risk': '#e6ab02', 'both': '#a6761d'}
    
    fig_risk_sector = go.Figure()
    
    for risk_type in risk_categories:
        risk_data = []
        for sector in sectors_filtered:
            sector_data = df[df['sector1'] == sector]
            
            if risk_type == 'both':
                risk_count = ((sector_data['env_risk'] == 1) & (sector_data['soc_risk'] == 1)).sum()
            else:
                risk_count = sector_data[risk_type].sum()
            
            total_projects = len(sector_data)
            risk_pct = (risk_count / total_projects * 100) if total_projects > 0 else 0
            risk_data.append(risk_pct)
        
        fig_risk_sector.add_trace(go.Bar(
            x=sectors_filtered,
            y=risk_data,
            name=risk_labels[risk_type],
            marker=dict(color=risk_colors_new[risk_type], line=dict(width=0)),
            text=[f'{val:.1f}%' if val > 5 else '' for val in risk_data],
            textposition='inside',
            textfont=dict(size=13, color='white', family='Arial'),
            opacity=0.8
        ))
    
    fig_risk_sector.update_layout(
        title=dict(
            text='Risk Profile by Sector',
            font=dict(size=16, family='Arial', color='black'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(text='Sector', font=dict(size=14, family='Arial')),
            tickfont=dict(family='Arial', size=14)
        ),
        yaxis=dict(
            title=dict(text='Percentage of Projects (%)', font=dict(size=14, family='Arial')),
            gridcolor='lightgray',
            gridwidth=0.5,
            tickfont=dict(family='Arial', size=14)
        ),
        plot_bgcolor='white',
        height=550,
        font=dict(family='Arial'),
        barmode='group',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(family='Arial', size=14)
        )
    )
    
    st.plotly_chart(fig_risk_sector, use_container_width=True)
    st.info("""
    💡 **Insight**: Environmental risk is the most common across sectors, and most of the projects are subject to both risks.
    """)
    st.markdown("---")
    
    # ========================================================================
    # DURATION AND DELAY BY RISK LEVEL AND SECTOR
    # ========================================================================
    st.header("Duration and Delay by Risk Level")
    
    st.markdown("### How do risk levels affect project duration and delays across sectors?")
    
    risk_levels = [0, 1, 2]
    risk_level_labels = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}
    sectors = ['Energy', 'Transportation', 'Water']
    
    # Heatmap 1: Risk Level × Sector (Duration)
    heatmap_data_sector_duration = []
    heatmap_text_sector_duration = []
    
    for risk_level in risk_levels:
        row_data = []
        row_text = []
        for sector in sectors:
            projects = df[(df['risk_level'] == risk_level) & (df['sector1'] == sector)]
            avg_duration = projects['duration_final'].mean()
            count = len(projects)
            row_data.append(avg_duration if count > 0 else np.nan)
            row_text.append(f'{avg_duration:.2f}y<br>(n={count})' if count > 0 else 'N/A')
        heatmap_data_sector_duration.append(row_data)
        heatmap_text_sector_duration.append(row_text)
    
    # Heatmap 2: Risk Level × Sector (Delay)
    heatmap_data_sector_delay = []
    heatmap_text_sector_delay = []
    
    for risk_level in risk_levels:
        row_data = []
        row_text = []
        for sector in sectors:
            projects = df[(df['risk_level'] == risk_level) & (df['sector1'] == sector)]
            avg_delay = projects['delay'].mean()
            count = len(projects)
            row_data.append(avg_delay if count > 0 else np.nan)
            row_text.append(f'{avg_delay:.2f}y<br>(n={count})' if count > 0 else 'N/A')
        heatmap_data_sector_delay.append(row_data)
        heatmap_text_sector_delay.append(row_text)
    
    # Create subplots
    fig_heatmaps = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Average Duration by Risk Level and Sector',
                        'Average Delay by Risk Level and Sector'),
        horizontal_spacing=0.20,
        specs=[[{'type': 'heatmap'}, {'type': 'heatmap'}]]
    )
    
    # Add Duration heatmap
    fig_heatmaps.add_trace(
        go.Heatmap(
            z=heatmap_data_sector_duration,
            x=sectors,
            y=[risk_level_labels[i] for i in risk_levels],
            text=heatmap_text_sector_duration,
            texttemplate='%{text}',
            textfont=dict(size=11, family='Arial'),
            colorscale='Reds',
            colorbar=dict(title='Duration<br>(years)', x=0.43, len=0.8),
            hovertemplate='Sector: %{x}<br>Risk: %{y}<br>Duration: %{z:.2f}y<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add Delay heatmap
    fig_heatmaps.add_trace(
        go.Heatmap(
            z=heatmap_data_sector_delay,
            x=sectors,
            y=[risk_level_labels[i] for i in risk_levels],
            text=heatmap_text_sector_delay,
            texttemplate='%{text}',
            textfont=dict(size=11, family='Arial'),
            colorscale='Reds',
            colorbar=dict(title='Delay<br>(years)', x=1.01, len=0.8),
            hovertemplate='Sector: %{x}<br>Risk: %{y}<br>Delay: %{z:.2f}y<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Update axes
    fig_heatmaps.update_xaxes(title='Sector', tickfont=dict(family='Arial', size=11), row=1, col=1)
    fig_heatmaps.update_xaxes(title='Sector', tickfont=dict(family='Arial', size=11), row=1, col=2)
    fig_heatmaps.update_yaxes(title='Risk Level', tickfont=dict(family='Arial', size=11), row=1, col=1)
    fig_heatmaps.update_yaxes(title='Risk Level', tickfont=dict(family='Arial', size=11), row=1, col=2)
    
    # Update layout
    fig_heatmaps.update_layout(
        title=dict(
            text='Project Duration and Delay by Risk Level and Sector',
            font=dict(size=18, family='Arial', color='black'),
            x=0.5,
            xanchor='center'
        ),
        height=600,
        font=dict(family='Arial')
    )
    
    st.plotly_chart(fig_heatmaps, use_container_width=True)
    st.info("""
    💡 **Insight**:
        Water projects have the highest initially planned project duration. No risk projects have notably shorter duration  - Delay occurs both in Energy and Water projects  - Projects without any pre-evaluated risks also suffer from delays, except for Water projects  - It suggests that Water projects are less prone to unforseen risks that may cause project """)
    st.markdown("---")
    
    # # ========================================================================
    # # LARGE VS MEGA BY RISK LEVEL (KEY FINDING!)
    # # ========================================================================
    # st.header("Large vs Mega Projects by Risk Level")
    
    # # st.markdown("""
    # # ### Does project size interact with risk level to affect delays?
    # # Comparing **Large projects ($500M-$1B)** vs **Mega projects (≥$1B)** across different risk levels.
    # # """)
    
    # # Filter to large and mega only
    # df_large_mega = df[df['project_size'].isin(['large', 'mega'])]
    
    # # Summary statistics table
    # st.subheader("📊 Mean Delay by Size and Risk Level")
    
    # summary_size_risk = []
    # for size, size_label in [('large', 'Large ($500M-$1B)'), ('mega', 'Mega (≥$1B)')]:
    #     for risk_level in [0, 1, 2]:
    #         data = df_large_mega[(df_large_mega['project_size'] == size) & 
    #                              (df_large_mega['risk_level'] == risk_level)]
    #         if len(data) > 0:
    #             summary_size_risk.append({
    #                 'Size': size_label,
    #                 'Risk Level': risk_level_labels[risk_level],
    #                 'Projects': len(data),
    #                 'Mean Delay (years)': data['delay'].mean(),
    #                 'Median Delay (years)': data['delay'].median()
    #             })
    
    # summary_size_risk_df = pd.DataFrame(summary_size_risk)
    # st.dataframe(summary_size_risk_df.style.format({
    #     'Mean Delay (years)': '{:.2f}',
    #     'Median Delay (years)': '{:.2f}'
    # }), use_container_width=True)
    
    # st.markdown("---")
    
    # # Grouped bar chart: Size × Risk Level
    # st.subheader("📈 Delay Comparison: Large vs Mega by Risk Level")
    
    # fig_size_risk = go.Figure()
    
    # for risk_level in [0, 1, 2]:
    #     delays = []
    #     for size, label in [('large', 'Large'), ('mega', 'Mega')]:
    #         data = df_large_mega[(df_large_mega['project_size'] == size) & 
    #                              (df_large_mega['risk_level'] == risk_level)]
    #         delays.append(data['delay'].mean() if len(data) > 0 else 0)
        
    #     fig_size_risk.add_trace(go.Bar(
    #         x=['Large ($500M-$1B)', 'Mega (≥$1B)'],
    #         y=delays,
    #         name=risk_level_labels[risk_level],
    #         marker=dict(color=risk_level_colors[risk_level]),
    #         text=[f'{val:.2f}y' for val in delays],
    #         textposition='auto',
    #         textfont=dict(size=11, color='white')
    #     ))
    
    # fig_size_risk.update_layout(
    #     title='Mean Delay by Project Size and Risk Level',
    #     xaxis_title='Project Size',
    #     yaxis_title='Mean Delay (years)',
    #     barmode='group',
    #     height=550,
    #     plot_bgcolor='white',
    #     font=dict(family='Arial'),
    #     legend=dict(
    #         title=dict(text='Risk Level'),
    #         orientation='h',
    #         yanchor='bottom',
    #         y=1.02,
    #         xanchor='center',
    #         x=0.5
    #     )
    # )
    
    # fig_size_risk.update_yaxes(gridcolor='lightgray')
    
    # st.plotly_chart(fig_size_risk, use_container_width=True)
    
    # st.info("""
    # **Key Observation**: 
    # - Mega projects with single risk show notably higher delays (2.61 years) compared to Large projects with Single Risk (1.59 years)  - Suggests mega projects may be particularly vulnerable when facing a risk
    # """)
    
    # st.markdown("---")
    
    # Environmental-Only vs Social-Only breakdown for Single Risk
    st.subheader("Single Risk Breakdown: Environmental vs Social")
    df_large_mega = df[df['project_size'].isin(['large', 'mega'])]
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Large Projects (Single Risk)**")
        large_single = df_large_mega[(df_large_mega['project_size'] == 'large') & 
                                     (df_large_mega['risk_level'] == 1)]
        
        env_only_large = large_single[large_single['risk_category'] == 'Environmental Only']
        soc_only_large = large_single[large_single['risk_category'] == 'Social Only']
        
        st.metric("Environmental Only", 
                  len(env_only_large),
                  f"{env_only_large['delay'].mean():.2f}y avg" if len(env_only_large) > 0 else "N/A")
        st.metric("Social Only", 
                  len(soc_only_large),
                  f"{soc_only_large['delay'].mean():.2f}y avg" if len(soc_only_large) > 0 else "N/A")
    
    with col2:
        st.markdown("**Mega Projects (Single Risk)**")
        mega_single = df_large_mega[(df_large_mega['project_size'] == 'mega') & 
                                    (df_large_mega['risk_level'] == 1)]
        
        env_only_mega = mega_single[mega_single['risk_category'] == 'Environmental Only']
        soc_only_mega = mega_single[mega_single['risk_category'] == 'Social Only']
        
        st.metric("Environmental Only", 
                  len(env_only_mega),
                  f"{env_only_mega['delay'].mean():.2f}y avg" if len(env_only_mega) > 0 else "N/A")
        st.metric("Social Only", 
                  len(soc_only_mega),
                  f"{soc_only_mega['delay'].mean():.2f}y avg" if len(soc_only_mega) > 0 else "N/A")
    
    st.markdown("---")

    
    # ========================================================================
    # RISK SEVERITY ANALYSIS (A, B, C)
    # ========================================================================
    st.header("Risk Severity Analysis")

    st.markdown("""
    ### How do different severity levels (A, B, C) affect project delays?
    Examining delays across **High (A)**, **Medium (B)**, and **Low (C)** risk severity levels.
    """)

    # Create severity comparison plots
    fig_severity = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Environmental Risk Severity', 'Social Risk Severity'),
        horizontal_spacing=0.15
    )

    severity_colors_map = {'A': '#db4325', 'B': '#dea247', 'C': '#bbd4a6'}
    severity_order = ['C', 'B', 'A']

    # Environmental Risk Severity
    for severity in severity_order:
        env_severity_data = df[df['safe_env'] == severity]
        
        fig_severity.add_trace(
            go.Violin(
                y=env_severity_data['delay'],
                x=[f'Level {severity}'] * len(env_severity_data),
                name=f'Level {severity}',
                box_visible=True,
                meanline_visible=True,
                points='all',
                pointpos=-0.5,
                jitter=0.3,
                marker=dict(color=severity_colors_map[severity]),
                scalemode='width',
                width=0.6,
                side='positive',
                line=dict(color=severity_colors_map[severity], width=2),
                showlegend=False
            ),
            row=1, col=1
        )

    # Social Risk Severity (combined indigenous + resettlement)
    for severity in severity_order:
        soc_severity_data = df[df['social_severity'] == severity]
        
        fig_severity.add_trace(
            go.Violin(
                y=soc_severity_data['delay'],
                x=[f'Level {severity}'] * len(soc_severity_data),
                name=f'Level {severity}',
                box_visible=True,
                meanline_visible=True,
                points='all',
                pointpos=-0.5,
                jitter=0.3,
                marker=dict(color=severity_colors_map[severity]),
                scalemode='width',
                width=0.6,
                side='positive',
                line=dict(color=severity_colors_map[severity], width=2),
                showlegend=False
            ),
            row=1, col=2
        )

    # Update axes
    fig_severity.update_xaxes(
        title='Severity Level',
        categoryorder='array',
        categoryarray=['Level C', 'Level B', 'Level A'],
        row=1, col=1
    )
    fig_severity.update_xaxes(
        title='Severity Level',
        categoryorder='array',
        categoryarray=['Level C', 'Level B', 'Level A'],
        row=1, col=2
    )
    fig_severity.update_yaxes(title='Delay (years)', gridcolor='lightgray', row=1, col=1)
    fig_severity.update_yaxes(title='Delay (years)', gridcolor='lightgray', row=1, col=2)

    fig_severity.update_layout(
        title='Project Delay by Risk Severity Level',
        plot_bgcolor='white',
        height=600,
        font=dict(family='Arial')
    )

    st.plotly_chart(fig_severity, use_container_width=True)

    # Summary statistics by severity
    st.subheader("Delay Statistics by Severity Level")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Environmental Risk**")
        env_severity_summary = []
        for severity in ['C', 'B', 'A']:
            sev_data = df[df['safe_env'] == severity]
            if len(sev_data) > 0:
                env_severity_summary.append({
                    'Level': severity,
                    'Projects': len(sev_data),
                    'Mean Delay': f"{sev_data['delay'].mean():.2f}y",
                    'Median Delay': f"{sev_data['delay'].median():.2f}y"
                })
        st.dataframe(pd.DataFrame(env_severity_summary), use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**Social Risk**")
        soc_severity_summary = []
        for severity in ['C', 'B', 'A']:
            sev_data = df[df['social_severity'] == severity]
            if len(sev_data) > 0:
                soc_severity_summary.append({
                    'Level': severity,
                    'Projects': len(sev_data),
                    'Mean Delay': f"{sev_data['delay'].mean():.2f}y",
                    'Median Delay': f"{sev_data['delay'].median():.2f}y"
                })
        st.dataframe(pd.DataFrame(soc_severity_summary), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ADD BAR CHARTS FOR MEAN DELAY
    st.subheader("Mean Delay Comparison by Severity")

    fig_severity_bars = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Environmental Risk', 'Social Risk'),
        horizontal_spacing=0.15
    )

    # Environmental Risk Bar Chart
    env_means = []
    for severity in ['C', 'B', 'A']:
        sev_data = df[df['safe_env'] == severity]
        env_means.append(sev_data['delay'].mean() if len(sev_data) > 0 else 0)

    fig_severity_bars.add_trace(
        go.Bar(
            x=[f'Level {s}' for s in ['C', 'B', 'A']],
            y=env_means,
            marker=dict(
                color=[severity_colors_map[s] for s in ['C', 'B', 'A']],
                line=dict(width=0)
            ),
            text=[f'{val:.2f}y' for val in env_means],
            textposition='auto',
            textfont=dict(size=12, color='white', family='Arial'),
            opacity=0.8,
            showlegend=False
        ),
        row=1, col=1
    )

    # Social Risk Bar Chart
    soc_means = []
    for severity in ['C', 'B', 'A']:
        sev_data = df[df['social_severity'] == severity]
        soc_means.append(sev_data['delay'].mean() if len(sev_data) > 0 else 0)

    fig_severity_bars.add_trace(
        go.Bar(
            x=[f'Level {s}' for s in ['C', 'B', 'A']],
            y=soc_means,
            marker=dict(
                color=[severity_colors_map[s] for s in ['C', 'B', 'A']],
                line=dict(width=0)
            ),
            text=[f'{val:.2f}y' for val in soc_means],
            textposition='auto',
            textfont=dict(size=12, color='white', family='Arial'),
            opacity=0.8,
            showlegend=False
        ),
        row=1, col=2
    )

    # Update axes
    fig_severity_bars.update_xaxes(
        title='Severity Level',
        categoryorder='array',
        categoryarray=['Level C', 'Level B', 'Level A'],
        tickfont=dict(family='Arial', size=11),
        row=1, col=1
    )
    fig_severity_bars.update_xaxes(
        title='Severity Level',
        categoryorder='array',
        categoryarray=['Level C', 'Level B', 'Level A'],
        tickfont=dict(family='Arial', size=11),
        row=1, col=2
    )
    fig_severity_bars.update_yaxes(
        title='Mean Delay (years)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=11),
        row=1, col=1
    )
    fig_severity_bars.update_yaxes(
        title='Mean Delay (years)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=11),
        row=1, col=2
    )

    fig_severity_bars.update_layout(
        title='Mean Delay by Risk Severity Level',
        plot_bgcolor='white',
        height=500,
        font=dict(family='Arial')
    )

    st.plotly_chart(fig_severity_bars, use_container_width=True)

    st.markdown("---")

    # ========================================================================
    # RISK PLANNING: DURATION VS DELAY
    # ========================================================================
    st.header("Risk Awareness in Project Planning")

    st.markdown("""
    ### Do planners account for risks when estimating project duration?
    Comparing planned duration (initial estimates) vs actual delays across risk levels.
    """)

    # Calculate statistics
    risk_planning_data = []
    for risk_level in [0, 1, 2]:
        risk_data = df[df['risk_level'] == risk_level]
        if len(risk_data) > 0:
            risk_planning_data.append({
                'Risk Level': risk_level_labels[risk_level],
                'Projects': len(risk_data),
                'Mean Initial Duration (years)': risk_data['duration_initial'].mean(),
                'Mean Final Duration (years)': risk_data['duration_final'].mean(),
                'Mean Delay (years)': risk_data['delay'].mean()
            })

    risk_planning_df = pd.DataFrame(risk_planning_data)

    st.subheader("Planning vs Reality")
    st.dataframe(risk_planning_df.style.format({
        'Mean Initial Duration (years)': '{:.2f}',
        'Mean Final Duration (years)': '{:.2f}',
        'Mean Delay (years)': '{:.2f}'
    }), use_container_width=True)

    st.markdown("---")

    # VIOLIN PLOTS - Distribution Comparison
    st.subheader("Distribution Comparison")

    # Create violin plots in subplots (SAME STRUCTURE AS SEVERITY ANALYSIS)
    fig_violins = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Initial Planned Duration', 'Actual Delay'),
        horizontal_spacing=0.15
    )

    # Left: Planned Duration Violins
    for risk_level in [0, 1, 2]:
        risk_data = df[df['risk_level'] == risk_level]
        
        fig_violins.add_trace(
            go.Violin(
                y=risk_data['duration_initial'],
                x=[risk_level_labels[risk_level]] * len(risk_data),
                name=risk_level_labels[risk_level],
                box_visible=True,
                meanline_visible=True,
                points='all',
                pointpos=-0.5,
                jitter=0.3,
                marker=dict(color=risk_level_colors[risk_level]),
                scalemode='width',
                width=0.6,
                side='positive',
                line=dict(color=risk_level_colors[risk_level], width=2),
                showlegend=False
            ),
            row=1, col=1
        )

    # Right: Actual Delay Violins
    for risk_level in [0, 1, 2]:
        risk_data = df[df['risk_level'] == risk_level]
        
        fig_violins.add_trace(
            go.Violin(
                y=risk_data['delay'],
                x=[risk_level_labels[risk_level]] * len(risk_data),
                name=risk_level_labels[risk_level],
                box_visible=True,
                meanline_visible=True,
                points='all',
                pointpos=-0.5,
                jitter=0.3,
                marker=dict(color=risk_level_colors[risk_level]),
                scalemode='width',
                width=0.6,
                side='positive',
                line=dict(color=risk_level_colors[risk_level], width=2),
                showlegend=False
            ),
            row=1, col=2
        )

    # Update axes
    fig_violins.update_xaxes(
        title='Risk Level',
        row=1, col=1
    )
    fig_violins.update_xaxes(
        title='Risk Level',
        row=1, col=2
    )
    fig_violins.update_yaxes(title='Duration (years)', gridcolor='lightgray', row=1, col=1)
    fig_violins.update_yaxes(title='Delay (years)', gridcolor='lightgray', row=1, col=2)

    fig_violins.update_layout(
        title='Distribution by Risk Level',
        plot_bgcolor='white',
        height=600,
        font=dict(family='Arial')
    )

    st.plotly_chart(fig_violins, use_container_width=True)

    st.markdown("---")

    # BAR CHARTS - Mean Values Comparison
    st.subheader("Mean Comparison by Risk Level")

    fig_risk_bars = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Mean Planned Duration', 'Mean Actual Delay'),
        horizontal_spacing=0.15
    )

    # Planned Duration Bar Chart
    duration_means = []
    for risk_level in [0, 1, 2]:
        risk_data = df[df['risk_level'] == risk_level]
        duration_means.append(risk_data['duration_initial'].mean() if len(risk_data) > 0 else 0)

    fig_risk_bars.add_trace(
        go.Bar(
            x=[risk_level_labels[rl] for rl in [0, 1, 2]],
            y=duration_means,
            marker=dict(
                color=[risk_level_colors[rl] for rl in [0, 1, 2]],
                line=dict(width=0)
            ),
            text=[f'{val:.2f}y' for val in duration_means],
            textposition='auto',
            textfont=dict(size=12, color='white', family='Arial'),
            opacity=0.8,
            showlegend=False
        ),
        row=1, col=1
    )

    # Actual Delay Bar Chart
    delay_means = []
    for risk_level in [0, 1, 2]:
        risk_data = df[df['risk_level'] == risk_level]
        delay_means.append(risk_data['delay'].mean() if len(risk_data) > 0 else 0)

    fig_risk_bars.add_trace(
        go.Bar(
            x=[risk_level_labels[rl] for rl in [0, 1, 2]],
            y=delay_means,
            marker=dict(
                color=[risk_level_colors[rl] for rl in [0, 1, 2]],
                line=dict(width=0)
            ),
            text=[f'{val:.2f}y' for val in delay_means],
            textposition='auto',
            textfont=dict(size=12, color='white', family='Arial'),
            opacity=0.8,
            showlegend=False
        ),
        row=1, col=2
    )

    # Update axes
    fig_risk_bars.update_xaxes(
        title='Risk Level',
        tickfont=dict(family='Arial', size=11),
        row=1, col=1
    )
    fig_risk_bars.update_xaxes(
        title='Risk Level',
        tickfont=dict(family='Arial', size=11),
        row=1, col=2
    )
    fig_risk_bars.update_yaxes(
        title='Mean Duration (years)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=11),
        row=1, col=1
    )
    fig_risk_bars.update_yaxes(
        title='Mean Delay (years)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=11),
        row=1, col=2
    )

    fig_risk_bars.update_layout(
        title='Mean Values by Risk Level',
        plot_bgcolor='white',
        height=500,
        font=dict(family='Arial')
    )

    st.plotly_chart(fig_risk_bars, use_container_width=True)

    st.markdown("---")

    # Grouped bar chart comparison
    st.subheader("Duration vs Delay Comparison")

    fig_compare = go.Figure()

    # Planned duration
    durations = [df[df['risk_level'] == rl]['duration_initial'].mean() for rl in [0, 1, 2]]
    fig_compare.add_trace(go.Bar(
        x=[risk_level_labels[rl] for rl in [0, 1, 2]],
        y=durations,
        name='Planned Duration',
        marker=dict(color='#3498db'),
        text=[f'{val:.2f}y' for val in durations],
        textposition='auto'
    ))

    # Actual delay
    delays = [df[df['risk_level'] == rl]['delay'].mean() for rl in [0, 1, 2]]
    fig_compare.add_trace(go.Bar(
        x=[risk_level_labels[rl] for rl in [0, 1, 2]],
        y=delays,
        name='Actual Delay',
        marker=dict(color='#e74c3c'),
        text=[f'{val:.2f}y' for val in delays],
        textposition='auto'
    ))

    fig_compare.update_layout(
        title='Planned Duration vs Actual Delay by Risk Level',
        xaxis_title='Risk Level',
        yaxis_title='Years',
        barmode='group',
        height=500,
        plot_bgcolor='white',
        font=dict(family='Arial'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )
    )

    fig_compare.update_yaxes(gridcolor='lightgray')

    st.plotly_chart(fig_compare, use_container_width=True)

    st.info("""
    💡 **Insight**:  
    Higher risk projects have longer planned durations - planners anticipate complexity  
    However, actual delays remain similar across risk levels - risks are being managed  
    This suggests that risk identification leads to appropriate planning buffers  
    Projects correctly assessed as high-risk receive adequate time allocations upfront
    """)

# ============================================================================
# TAB 3: ADDITIONAL ANALYSIS & KEY FINDINGS
# ============================================================================
with tab3:
    st.title("👀 Additional Analysis")
    
    # ========================================================================
    # INITIAL COST VS DELAY
    # ========================================================================
    st.header("Project Cost vs Delay")
    
    st.markdown("""
    ### How does initial project cost relate to delays?
    Explore the relationship between project cost and delays across sectors and risk categories.
    """)
    
    # Color schemes
    risk_colors = {
        'No Risk': '#fee5d9',
        'Environmental Only': '#1b9e77',
        'Social Only': '#e6ab02',
        'Both': '#a6761d'
    }
    
    fig_cost_delay = go.Figure()
    
    # Add sector data (visible by default) - USING df_filtered
    for sector in ['Energy', 'Transportation', 'Water']:
        sector_data = df_filtered[df_filtered['sector1'] == sector]
        if len(sector_data) > 0:
            fig_cost_delay.add_trace(
                go.Scatter(
                    x=sector_data['totalcost_initial_adj'],
                    y=sector_data['delay'],
                    mode='markers',
                    name=sector,
                    marker=dict(
                        color=sector_colors[sector],
                        size=8,
                        opacity=0.6,
                        line=dict(width=0.5, color='white'),
                        symbol='circle'
                    ),
                    legendgroup='sector',
                    legendgrouptitle_text='Sector',
                    showlegend=True
                )
            )
    
    # Add risk category data (hidden by default) - USING df_filtered
    for risk_cat in ['No Risk', 'Environmental Only', 'Social Only', 'Both']:
        risk_data = df_filtered[df_filtered['risk_category'] == risk_cat]
        if len(risk_data) > 0:
            fig_cost_delay.add_trace(
                go.Scatter(
                    x=risk_data['totalcost_initial_adj'],
                    y=risk_data['delay'],
                    mode='markers',
                    name=risk_cat,
                    marker=dict(
                        color=risk_colors[risk_cat],
                        size=8,
                        opacity=0.6,
                        line=dict(width=0.5, color='white'),
                        symbol='square'
                    ),
                    legendgroup='risk_cat',
                    legendgrouptitle_text='Risk Category',
                    showlegend=True,
                    visible='legendonly'
                )
            )
    
    # Add risk level data (hidden by default) - USING df_filtered
    risk_level_labels = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}
    for risk_level in [0, 1, 2]:
        level_data = df_filtered[df_filtered['risk_level'] == risk_level]
        if len(level_data) > 0:
            fig_cost_delay.add_trace(
                go.Scatter(
                    x=level_data['totalcost_initial_adj'],
                    y=level_data['delay'],
                    mode='markers',
                    name=risk_level_labels[risk_level],
                    marker=dict(
                        color=risk_level_colors[risk_level],
                        size=8,
                        opacity=0.6,
                        line=dict(width=0.5, color='white'),
                        symbol='diamond'
                    ),
                    legendgroup='risk_level',
                    legendgrouptitle_text='Risk Level',
                    showlegend=True,
                    visible='legendonly'
                )
            )
    
    # Add horizontal reference line at y=0
    if len(df_filtered) > 0:
        fig_cost_delay.add_trace(
            go.Scatter(
                x=[df_filtered['totalcost_initial_adj'].min(), df_filtered['totalcost_initial_adj'].max()],
                y=[0, 0],
                mode='lines',
                line=dict(color='gray', width=1, dash='dash'),
                showlegend=False,
                hoverinfo='skip'
            )
        )
    
    # Update layout
    fig_cost_delay.update_layout(
        title=dict(
            text='Initial Cost vs Project Delay<br><sub>Click legend items to toggle between Sector, Risk Category, and Risk Level views</sub>',
            font=dict(size=18, family='Arial', color='black'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='Initial Cost (Million USD, 2019)',
            gridcolor='lightgray',
            gridwidth=0.5,
            tickfont=dict(family='Arial', size=12)
        ),
        yaxis=dict(
            title='Delay (years)',
            gridcolor='lightgray',
            gridwidth=0.5,
            tickfont=dict(family='Arial', size=12)
        ),
        plot_bgcolor='white',
        height=650,
        font=dict(family='Arial'),
        legend=dict(
            orientation='v',
            yanchor='top',
            y=1,
            xanchor='left',
            x=1.02,
            font=dict(family='Arial', size=10),
            tracegroupgap=20
        ),
        hovermode='closest'
    )
    
    st.plotly_chart(fig_cost_delay, use_container_width=True)
    
    st.info("""
    💡 **Insight**: Click on legend items to toggle between different views:  
    - **Sector view** (default): Shows how delays vary across Energy, Transportation, and Water projects  
    - **Risk Category view**: Shows delays by environmental/social risk combinations  
    - **Risk Level view**: Shows delays by number of risks present
    """)
    
    st.warning("""
    ⚠️ **Data Limitation**: More importantly, a manual inspection revealed that the data misses information on 
    whether the project has been cancelled or restructured (downsized or upsized). Need further investigation.
    """)
    
    st.markdown("---")
    
    # ========================================================================
    # REGIONAL ANALYSIS
    # ========================================================================
    st.header("Regional Analysis: Delay by Region")
    
    st.markdown("""
    ### Do project delays vary across different Asian regions?
    Examining regional patterns in project delays and risk distribution.
    """)
    
    if 'region' in df.columns:
        # Summary statistics
        st.subheader("Regional Summary Statistics")
        
        region_summary = []
        for region in sorted(df['region'].unique()):
            region_data = df[df['region'] == region]
            region_summary.append({
                'Region': region,
                'Projects': len(region_data),
                'Mean Delay (years)': region_data['delay'].mean(),
                'Median Delay (years)': region_data['delay'].median(),
                'Std Dev': region_data['delay'].std()
            })
        
        region_summary_df = pd.DataFrame(region_summary)
        st.dataframe(region_summary_df.style.format({
            'Mean Delay (years)': '{:.2f}',
            'Median Delay (years)': '{:.2f}',
            'Std Dev': '{:.2f}'
        }), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Box plot by region
        st.subheader("Delay Distribution by Region")
        
        fig_region = go.Figure()
        
        for region in sorted(df['region'].unique()):
            region_data = df[df['region'] == region]
            
            fig_region.add_trace(go.Box(
                y=region_data['delay'],
                name=region,
                boxmean='sd',
                marker=dict(opacity=0.7),
                line=dict(width=2)
            ))
        
        fig_region.update_layout(
            title=dict(
                text='Project Delay Distribution by Region',
                font=dict(size=18, family='Arial', color='black'),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title='Region',
                tickfont=dict(family='Arial', size=11),
                tickangle=-45,
                title_font=dict(size=14, family='Arial')
            ),
            yaxis=dict(
                title='Delay (years)',
                gridcolor='lightgray',
                gridwidth=0.5,
                tickfont=dict(family='Arial', size=12),
                title_font=dict(size=14, family='Arial')
            ),
            plot_bgcolor='white',
            height=600,
            font=dict(family='Arial'),
            showlegend=False
        )
        
        st.plotly_chart(fig_region, use_container_width=True)
        st.info("""
    💡 **Insight**: Regions have different delays. Further investigation of the contributing factors of heterogeneous delays could be interesting.
    """)
       
    #     # Risk distribution by region
    #     st.subheader("Risk Distribution by Region")
        
    #     with st.expander("View detailed risk breakdown by region"):
    #         for region in sorted(df['region'].unique()):
    #             region_data = df[df['region'] == region]
    #             st.markdown(f"**{region}** (n={len(region_data)})")
                
    #             risk_dist = region_data['risk_level'].value_counts().sort_index()
    #             risk_level_names = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}
                
    #             cols = st.columns(3)
    #             for i, (risk_level, count) in enumerate(risk_dist.items()):
    #                 pct = (count / len(region_data) * 100)
    #                 with cols[i % 3]:
    #                     st.metric(risk_level_names[risk_level], f"{count} ({pct:.1f}%)")
                
    #             st.markdown("---")
        
    #     # Statistical test
    #     region_groups = []
    #     region_names = []
    #     for region in df['region'].unique():
    #         region_data = df[df['region'] == region]['delay'].dropna()
    #         if len(region_data) > 5:
    #             region_groups.append(region_data)
    #             region_names.append(region)
        
    #     if len(region_groups) > 1:
    #         h_stat, p_value = stats.kruskal(*region_groups)
            
    #         if p_value < 0.05:
    #             st.success(f"""
    #             ✅ **Significant Regional Differences Found**  
    #             Kruskal-Wallis H = {h_stat:.3f}, p = {p_value:.4f}  
    #             Project delays differ significantly across regions
    #             """)
    #         else:
    #             st.info(f"""
    #             💡 **No Significant Regional Differences**  
    #             Kruskal-Wallis H = {h_stat:.3f}, p = {p_value:.4f}  
    #             Delays are relatively consistent across regions
    #             """)
    # else:
    #     st.error("Region column not found in dataset.")

# ============================================================================
# TAB 4: DATA & PROCESSING
# ============================================================================
with tab4:
    st.title("📊 Data & Processing")
    
    # Create sub-tabs for better organization
    subtab1, subtab2 = st.tabs(["Raw Data", "Preprocessing Steps"])
    
    with subtab1:
        st.header("Raw Data Preview")
        st.dataframe(df.head(100), use_container_width=True)
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Dataset",
            data=csv,
            file_name='adb_projects_clean_final.csv',
            mime='text/csv',
        )
    
    with subtab2:
        st.header("Data Merging and Preprocessing")
        
        st.markdown("""
        This summarizes the data merging and preprocessing steps performed to create a clean dataset 
        of **310 Asian Development Bank (ADB) sovereign projects** for analysis.
        """)
        
        st.markdown("---")
        
        # 1. Initial Datasets
        st.subheader("1. Initial Datasets")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("**ADB Projects**")
            st.metric("Records", "527")
            st.caption("Project metadata, sectors, safeguards")
        
        with col2:
            st.markdown("**ADB Financial**")
            st.metric("Records", "1,019")
            st.caption("Costs, dates, performance")
        
        with col3:
            st.markdown("**Region Data**")
            st.metric("Records", "225")
            st.caption("Country codes, regions")
        
        with col4:
            st.markdown("**World Bank**")
            st.metric("Countries", "266")
            st.caption("PLR, GDP deflator")
        
        st.markdown("---")
        
        # 2. Data Merging
        st.subheader("2. Data Merging Process")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Matched", "424 projects")
        with col2:
            st.metric("Unmatched", "109 projects")
        with col3:
            st.metric("Retention", "80.5%")
        
        with st.expander("View Merging Steps"):
            merge_steps = pd.DataFrame({
                'Step': ['Exact ID Match', 'ID + Name Match', 'Fuzzy Match (80%)', 'Fuzzy Match (75%)'],
                'Matches': [386, 2, 11, '3-4'],
                'Method': [
                    'Matched projectid across columns',
                    'Matched on ID head and exact name',
                    'String similarity ≥80%',
                    'String similarity ≥75%'
                ]
            })
            st.dataframe(merge_steps, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # 3. Data Collection & Corrections
        st.subheader("3. Manual Data Collection & Quality Corrections")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Missing Cost Data**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Missing", "41")
            with col_b:
                st.metric("Filled", "31")
            st.caption("✓ Reviewed Project Completion Reports")
        
        with col2:
            st.markdown("**Data Quality Issues**")
            st.metric("Negative Durations", "3 projects")
            st.caption("✓ Manually verified and corrected")
        
        st.markdown("---")
        
        # 4. Feature Engineering
        st.subheader("4. Feature Engineering")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Duration Metrics**")
            st.code("""
duration_initial
duration_final
delay
            """)
        
        with col2:
            st.markdown("**Cost Metrics**")
            st.code("""
cost_overrun
cost_overrun_mark
delay_mark
            """)
        
        with col3:
            st.markdown("**Temporal Features**")
            st.code("""
approval_year
closing_year
beforecovid
            """)
        
        st.markdown("---")
        
        # 5. Filtering & Cost Adjustments
        st.subheader("5. Dataset Filtering")
        
        filter_data = pd.DataFrame({
            'Filter': ['Pre-COVID', 'Duration > 2y', 'Economic Data', 'Outlier Removal'],
            'Result': ['341', '338', '320', '310'],
            'Rationale': [
                'Exclude COVID impacts',
                'Focus on substantial projects',
                'Enable cost adjustments',
                'Remove data quality issues'
            ]
        })
        
        st.dataframe(filter_data, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # 6. Cost Adjustments
        st.subheader("6. Cost Adjustments to 2019 Constant Dollars")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Step 1: PLR Adjustment**")
            st.code("cost_adj = cost / PLR(year, country)")
            st.caption("Adjust for borrowing costs")
        
        with col2:
            st.markdown("**Step 2: GDP Deflator**")
            st.code("cost_final = cost_adj × (GDP₂₀₁₉ / GDPᵧₑₐᵣ)")
            st.caption("Adjust for inflation")
        
        st.markdown("---")
        
        # 7. Project Classification
        st.subheader("7. Project Size Classification")
        
        size_data = pd.DataFrame({
            'Category': ['Small', 'Medium', 'Large', 'Mega'],
            'Cost Range': ['< $100M', '$100M - $500M', '$500M - $1B', '≥ $1B']
        })
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(size_data, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("")
            st.markdown("")
            st.info("💡 Classification based on adjusted initial cost")
        
        st.markdown("---")
        
        # 8. Final Dataset
        st.subheader("8. Final Dataset Characteristics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Final Projects", "310")
        with col2:
            st.metric("Original", "527")
        with col3:
            st.metric("Retention", "58.8%")
        with col4:
            st.metric("Columns", "36")
        
        st.markdown("**Quality Criteria:**")
        st.markdown("""
        ✓ Closed before 2020 (pre-COVID)  
        ✓ Duration > 2 years  
        ✓ Complete cost data  
        ✓ Adjusted to 2019 constant dollars  
        ✓ No outliers  
        ✓ Full economic indicators
        """)
        
        st.markdown("---")
        
        # 9. Schema
        with st.expander("View Dataset Schema (36 columns)"):
            schema_data = pd.DataFrame({
                'Category': [
                    'Project identifiers', 'Financial (nominal)', 
                    'Financial (adjusted)', 'Duration metrics',
                    'Cost performance', 'Performance flags',
                    'Temporal features', 'Geographic info',
                    'Sector & safeguard', 'Derived features'
                ],
                'Columns': [6, 2, 6, 3, 2, 2, 5, 3, 6, 1]
            })
            st.dataframe(schema_data, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.caption("Infrastructure Project Risk Analysis | Data: Asian Development Bank")

# # Footer
# st.markdown("---")
# st.caption("Infrastructure Project Risk Analysis | Data: Asian Development Bank")