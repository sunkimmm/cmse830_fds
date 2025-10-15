import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="ADB Project Analysis",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    h1 {
        color: #2c3e50;
        padding-bottom: 1rem;
    }
    h2 {
        color: #34495e;
        padding-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('adb_clean_416.csv') 
    return df

df_clean1 = load_data()

# Sidebar
st.sidebar.title("🏗️ Large-scale Infrastructure Project Analysis")
st.sidebar.markdown("---")
st.sidebar.info(
    """
    This dashboard analyzes Asian Development Bank infrastructure projects 
    across Energy, Transportation, and Water sectors from 2002-2019.
    """
)
st.sidebar.markdown("---")

# Filters
st.sidebar.subheader("🔍 Filters")

# Sector filter - DROPDOWN
all_sectors = sorted(df_clean1['sector1'].unique())
selected_sector = st.sidebar.selectbox(
    "Select Sector",
    options=['All Sectors'] + all_sectors,
    help="Filter projects by sector"
)

st.sidebar.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "📈 Temporal Trends", 
    "⚡ Performance Metrics",
    "⚠️ Project Risks",
    "📋 Data"
])

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================
with tab1:
    st.title("📊 Project Overview")

    # Apply filter
    filtered_df = df_clean1.copy()
    if selected_sector != 'All Sectors':  # ✅ NEW - singular
        filtered_df = filtered_df[filtered_df['sector1'] == selected_sector]
    
    # Key metrics at the top
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Projects", len(filtered_df))
    with col2:
        st.metric("Countries", filtered_df['countryshortname'].nunique())
    with col3:
        total_investment_b = filtered_df['totalcost_initial_adj'].sum() / 1000
        st.metric("Total Investment", f"${total_investment_b:.1f}B")
    with col4:
        avg_cost_b = filtered_df['totalcost_initial_adj'].mean() / 1000
        st.metric("Avg Project Cost", f"${avg_cost_b:.2f}B")
    
    st.markdown("---")
    
    # Geographic Maps
    st.subheader("🗺️ Geographic Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Choropleth map with ISO-3
        country_total = filtered_df.groupby('countryshortname').agg({
            'projectid': 'count',
            'sector1': lambda x: ', '.join(x.value_counts().index[:3])
        }).reset_index()
        country_total.columns = ['countryshortname', 'total_projects', 'main_sectors']
        
        # ISO-3 country code mapping
        country_iso_map = {
            'Afghanistan': 'AFG', 'Armenia': 'ARM', 'Azerbaijan': 'AZE',
            'Bangladesh': 'BGD', 'Bhutan': 'BTN', 'Cambodia': 'KHM',
            'China': 'CHN', 'Fiji': 'FJI', 'Georgia': 'GEO',
            'India': 'IND', 'Indonesia': 'IDN', 'Kazakhstan': 'KAZ',
            'Kiribati': 'KIR', 'Kyrgyz Republic': 'KGZ', 
            "Lao People's Democratic Republic": 'LAO',
            'Maldives': 'MDV', 'Marshall Islands': 'MHL',
            'Micronesia, Federated States of': 'FSM',
            'Mongolia': 'MNG', 'Myanmar': 'MMR', 'Nauru': 'NRU',
            'Nepal': 'NPL', 'Pakistan': 'PAK', 'Palau': 'PLW',
            'Papua New Guinea': 'PNG', 'Philippines': 'PHL',
            'Samoa': 'WSM', 'Solomon Islands': 'SLB',
            'Sri Lanka': 'LKA', 'Tajikistan': 'TJK',
            'Thailand': 'THA', 'Timor-Leste': 'TLS',
            'Tonga': 'TON', 'Turkmenistan': 'TKM',
            'Tuvalu': 'TUV', 'Uzbekistan': 'UZB',
            'Vanuatu': 'VUT', 'Viet Nam': 'VNM'
        }
        
        country_total['iso_code'] = country_total['countryshortname'].map(country_iso_map)
        
        fig_choropleth = px.choropleth(
            country_total,
            locations='iso_code',
            locationmode='ISO-3',
            color='total_projects',
            hover_name='countryshortname',
            hover_data={'iso_code': False, 'countryshortname': False, 'total_projects': True, 'main_sectors': True},
            color_continuous_scale='YlGn',
            title='Project Count by Country',
            labels={'total_projects': 'Projects', 'main_sectors': 'Main Sectors'}
        )
        fig_choropleth.update_layout(
            geo=dict(
                scope='asia',
                projection_type='natural earth',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                coastlinecolor='rgb(204, 204, 204)',
                showcountries=True,
                countrycolor='rgb(204, 204, 204)'
            ),
            height=500,
            font=dict(family='Arial')
        )
        st.plotly_chart(fig_choropleth, use_container_width=True)
    
    with col2:
        # Bubble map
        country_data = filtered_df.groupby(['countryshortname']).agg({
            'projectid': 'count',
            'totalcost_initial_adj': 'sum',
            'sector1': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Mixed'
        }).reset_index()
        country_data.columns = ['country', 'project_count', 'total_cost', 'dominant_sector']
        
        country_coords = {
            'Afghanistan': (33.9391, 67.7100), 'Armenia': (40.0691, 45.0382),
            'Azerbaijan': (40.1431, 47.5769), 'Bangladesh': (23.6850, 90.3563),
            'Bhutan': (27.5142, 90.4336), 'Cambodia': (12.5657, 104.9910),
            'China': (35.8617, 104.1954), 'Fiji': (-17.7134, 178.0650),
            'Georgia': (42.3154, 43.3569), 'India': (20.5937, 78.9629),
            'Indonesia': (-0.7893, 113.9213), 'Kazakhstan': (48.0196, 66.9237),
            'Kiribati': (-3.3704, -168.7340), 'Kyrgyz Republic': (41.2044, 74.7661),
            "Lao People's Democratic Republic": (19.8563, 102.4955),
            'Maldives': (3.2028, 73.2207), 'Marshall Islands': (7.1315, 171.1845),
            'Micronesia, Federated States of': (7.4256, 150.5508),
            'Mongolia': (46.8625, 103.8467), 'Myanmar': (21.9162, 95.9560),
            'Nauru': (-0.5228, 166.9315), 'Nepal': (28.3949, 84.1240),
            'Pakistan': (30.3753, 69.3451), 'Palau': (7.5150, 134.5825),
            'Papua New Guinea': (-6.3150, 143.9555), 'Philippines': (12.8797, 121.7740),
            'Samoa': (-13.7590, -172.1046), 'Solomon Islands': (-9.6457, 160.1562),
            'Sri Lanka': (7.8731, 80.7718), 'Tajikistan': (38.8610, 71.2761),
            'Thailand': (15.8700, 100.9925), 'Timor-Leste': (-8.8742, 125.7275),
            'Tonga': (-21.1789, -175.1982), 'Turkmenistan': (38.9697, 59.5563),
            'Tuvalu': (-7.1095, 177.6493), 'Uzbekistan': (41.3775, 64.5853),
            'Vanuatu': (-15.3767, 166.9592), 'Viet Nam': (14.0583, 108.2772)
        }
        
        country_data['lat'] = country_data['country'].map(lambda x: country_coords.get(x, (None, None))[0])
        country_data['lon'] = country_data['country'].map(lambda x: country_coords.get(x, (None, None))[1])
        country_data = country_data.dropna(subset=['lat', 'lon'])
        
        colors_sector = {'Energy': '#e74c3c', 'Transportation': '#3498db', 'Water': '#2ecc71'}
        
        fig_bubble = px.scatter_geo(
            country_data,
            lat='lat', lon='lon',
            size='project_count',
            color='dominant_sector',
            hover_name='country',
            hover_data={'project_count': True, 'total_cost': ':.2f', 'lat': False, 'lon': False},
            color_discrete_map=colors_sector,
            title='Dominant Sector by Country',
            size_max=50
        )
        fig_bubble.update_geos(
            scope='asia',
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
            showcountries=True,
            countrycolor='rgb(204, 204, 204)'
        )
        fig_bubble.update_layout(height=500, font=dict(family='Arial'))
        st.plotly_chart(fig_bubble, use_container_width=True)
    
    st.markdown("---")
    
    # Project Distribution
    st.subheader("📊 Project Distribution")
    
    fig_dist = make_subplots(
        rows=1, cols=3,
        subplot_titles=('By Project Size', 'By Sector', 'By Region'),
        horizontal_spacing=0.12
    )
    
    # By Size
    size_counts = filtered_df['project_size'].value_counts()
    total_projects = size_counts.sum()
    size_percentages = (size_counts / total_projects * 100).round(1)
    size_colors = {'small': '#3498db', 'major': '#f39c12', 'mega': '#e74c3c'}
    color_list_size = [size_colors.get(size, '#95a5a6') for size in size_counts.index]
    text_labels_size = [f"{pct}%<br>({count})" for pct, count in zip(size_percentages.values, size_counts.values)]
    
    fig_dist.add_trace(
        go.Bar(
            x=size_counts.index, y=size_percentages.values,
            marker=dict(color=color_list_size, line=dict(color='black', width=1)),
            text=text_labels_size, textposition='auto',
            textfont=dict(size=12, color='white', family='Arial'),
            opacity=0.8, showlegend=False
        ),
        row=1, col=1
    )
    
    # By Sector
    sector_counts = filtered_df['sector1'].value_counts()
    sector_percentages = (sector_counts / total_projects * 100).round(1)
    sector_colors = {'Energy': '#e74c3c', 'Transportation': '#3498db', 'Water': '#2ecc71'}
    color_list_sector = [sector_colors.get(sector, '#95a5a6') for sector in sector_counts.index]
    text_labels_sector = [f"{pct}%<br>({count})" for pct, count in zip(sector_percentages.values, sector_counts.values)]
    
    fig_dist.add_trace(
        go.Bar(
            x=sector_counts.index, y=sector_percentages.values,
            marker=dict(color=color_list_sector, line=dict(color='black', width=1)),
            text=text_labels_sector, textposition='auto',
            textfont=dict(size=12, color='white', family='Arial'),
            opacity=0.8, showlegend=False
        ),
        row=1, col=2
    )
    
    # By Region
    region_counts = filtered_df['regionname'].value_counts().sort_values(ascending=False)
    region_percentages = (region_counts / total_projects * 100).round(1)
    text_labels_region = [f"{pct}%<br>({count})" for pct, count in zip(region_percentages.values, region_counts.values)]
    
    fig_dist.add_trace(
        go.Bar(
            x=region_counts.index, y=region_percentages.values,
            marker=dict(color='steelblue', line=dict(color='black', width=1)),
            text=text_labels_region, textposition='auto',
            textfont=dict(size=10, color='white', family='Arial'),
            opacity=0.8, showlegend=False
        ),
        row=1, col=3
    )
    
    fig_dist.update_xaxes(title_text='Project Size', tickfont=dict(size=11), row=1, col=1, categoryorder='array', categoryarray=['small', 'major', 'mega'])
    fig_dist.update_xaxes(title_text='Sector', tickfont=dict(size=11), row=1, col=2)
    fig_dist.update_xaxes(title_text='Region', tickfont=dict(size=9), tickangle=-45, row=1, col=3)
    
    fig_dist.update_yaxes(title_text='Percentage (%)', gridcolor='lightgray', gridwidth=0.5, row=1, col=1)
    fig_dist.update_yaxes(title_text='Percentage (%)', gridcolor='lightgray', gridwidth=0.5, row=1, col=2)
    fig_dist.update_yaxes(title_text='Percentage (%)', gridcolor='lightgray', gridwidth=0.5, row=1, col=3)
    
    fig_dist.update_layout(
        title=dict(
            text='Distribution of Projects<br><sub>Small: <$500M | Major: $500M-$1B | Mega: ≥$1B</sub>',
            font=dict(size=18, family='Arial', color='black'),
            x=0.5, xanchor='center'
        ),
        plot_bgcolor='white', height=550, font=dict(family='Arial')
    )
    
    st.plotly_chart(fig_dist, use_container_width=True)
    
    st.markdown("---")
    
    # Temporal Distribution
    st.subheader("📅 Temporal Distribution")
    
    approval_distribution = filtered_df['approvalyear'].value_counts().sort_index()
    closing_distribution = filtered_df['closingyear'].value_counts().sort_index()
    
    fig_temporal = go.Figure()
    fig_temporal.add_trace(go.Bar(
        x=approval_distribution.index, y=approval_distribution.values,
        name='Approval Year',
        marker=dict(color='steelblue', line=dict(color='black', width=1)),
        opacity=0.7
    ))
    fig_temporal.add_trace(go.Bar(
        x=closing_distribution.index, y=closing_distribution.values,
        name='Closing Year',
        marker=dict(color='coral', line=dict(color='black', width=1)),
        opacity=0.7
    ))
    fig_temporal.update_layout(
        title=dict(
            text='Distribution of Projects by Approval and Closing Year',
            font=dict(size=16, family='Arial', color='black'),
            x=0.5, xanchor='center'
        ),
        xaxis=dict(
            title=dict(text='Year', font=dict(size=14, family='Arial')),
            tickmode='linear', dtick=1, tickfont=dict(family='Arial')
        ),
        yaxis=dict(
            title=dict(text='Number of Projects', font=dict(size=14, family='Arial')),
            gridcolor='lightgray', gridwidth=0.5
        ),
        plot_bgcolor='white', height=500, font=dict(family='Arial'),
        barmode='overlay',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    st.plotly_chart(fig_temporal, use_container_width=True)
# ============================================================================
# TAB 2: TEMPORAL TRENDS
# ============================================================================
with tab2:
    st.title("📈 Temporal Trends")
    
    projects_by_year = df_clean1.groupby(['approvalyear', 'sector1']).size().reset_index(name='count')
    avg_cost_by_year = df_clean1.groupby(['approvalyear', 'sector1'])['totalcost_initial_adj'].mean().reset_index(name='avg_cost')
    
    fig_trends = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Number of Projects Over Time', 'Average Project Cost Over Time'),
        horizontal_spacing=0.12
    )
    
    sector_colors = {'Energy': '#d95f02', 'Transportation': '#57c4ad', 'Water': '#0571b0'}
    
    for sector in sorted(df_clean1['sector1'].unique()):
        sector_data_count = projects_by_year[projects_by_year['sector1'] == sector]
        fig_trends.add_trace(
            go.Scatter(
                x=sector_data_count['approvalyear'], y=sector_data_count['count'],
                mode='lines+markers', name=sector,
                line=dict(width=3, color=sector_colors.get(sector, '#95a5a6')),
                marker=dict(size=8, color=sector_colors.get(sector, '#95a5a6'), line=dict(width=1, color='black')),
                legendgroup=sector, showlegend=True
            ),
            row=1, col=1
        )
        
        sector_data_cost = avg_cost_by_year[avg_cost_by_year['sector1'] == sector]
        fig_trends.add_trace(
            go.Scatter(
                x=sector_data_cost['approvalyear'], y=sector_data_cost['avg_cost'],
                mode='lines+markers', name=sector,
                line=dict(width=3, color=sector_colors.get(sector, '#95a5a6')),
                marker=dict(size=8, color=sector_colors.get(sector, '#95a5a6'), line=dict(width=1, color='black')),
                legendgroup=sector, showlegend=False,
                hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Avg Cost: $%{y:.2f}M<extra></extra>'
            ),
            row=1, col=2
        )
    
    fig_trends.update_xaxes(title_text='Approval Year', tickmode='linear', dtick=2, row=1, col=1)
    fig_trends.update_xaxes(title_text='Approval Year', tickmode='linear', dtick=2, row=1, col=2)
    fig_trends.update_yaxes(title_text='Number of Projects', gridcolor='lightgray', row=1, col=1)
    fig_trends.update_yaxes(title_text='Average Cost (Million USD, 2019)', gridcolor='lightgray', row=1, col=2)
    
    fig_trends.update_layout(
        title=dict(text='Project Trends Over Time by Sector', font=dict(size=18, family='Arial'), x=0.5, xanchor='center'),
        plot_bgcolor='white', height=500, font=dict(family='Arial'),
        legend=dict(orientation='h', yanchor='bottom', y=1.03, xanchor='right', x=0.6),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_trends, use_container_width=True)

# ============================================================================
# TAB 3: PERFORMANCE METRICS
# ============================================================================
with tab3:
    st.title("⚡ Performance Metrics")
    
    st.subheader("Average Project Metrics by Sector")
    
    avg_cost_all = df_clean1.groupby('sector1')['totalcost_initial_adj'].mean()
    avg_duration_all = df_clean1.groupby('sector1')['duration_years'].mean()
    avg_delay_all = df_clean1.groupby('sector1')['delay'].mean()
    
    sector_order = ['Energy', 'Transportation', 'Water']
    
    fig_metrics = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Average Cost', 'Average Duration', 'Average Delay'),
        horizontal_spacing=0.12
    )
    
    sector_colors = {'Energy': '#d95f02', 'Transportation': '#57c4ad', 'Water': '#0571b0'}
    
    fig_metrics.add_trace(
        go.Bar(
            x=sector_order, y=[avg_cost_all[sector] for sector in sector_order],
            marker=dict(color=[sector_colors.get(sector, '#95a5a6') for sector in sector_order], line=dict(color='black', width=1)),
            text=[f'${avg_cost_all[sector]:.0f}M' for sector in sector_order],
            textposition='auto', textfont=dict(size=12, color='white', family='Arial'),
            opacity=0.8, showlegend=False
        ),
        row=1, col=1
    )
    
    fig_metrics.add_trace(
        go.Bar(
            x=sector_order, y=[avg_duration_all[sector] for sector in sector_order],
            marker=dict(color=[sector_colors.get(sector, '#95a5a6') for sector in sector_order], line=dict(color='black', width=1)),
            text=[f'{avg_duration_all[sector]:.1f}y' for sector in sector_order],
            textposition='auto', textfont=dict(size=12, color='white', family='Arial'),
            opacity=0.8, showlegend=False
        ),
        row=1, col=2
    )
    
    fig_metrics.add_trace(
        go.Bar(
            x=sector_order, y=[avg_delay_all[sector] for sector in sector_order],
            marker=dict(color=[sector_colors.get(sector, '#95a5a6') for sector in sector_order], line=dict(color='black', width=1)),
            text=[f'{avg_delay_all[sector]:.1f}y' for sector in sector_order],
            textposition='auto', textfont=dict(size=12, color='white', family='Arial'),
            opacity=0.8, showlegend=False
        ),
        row=1, col=3
    )
    
    fig_metrics.update_xaxes(title_text='Sector', row=1, col=1)
    fig_metrics.update_xaxes(title_text='Sector', row=1, col=2)
    fig_metrics.update_xaxes(title_text='Sector', row=1, col=3)
    fig_metrics.update_yaxes(title_text='Million USD', gridcolor='lightgray', row=1, col=1)
    fig_metrics.update_yaxes(title_text='Years', gridcolor='lightgray', row=1, col=2)
    fig_metrics.update_yaxes(title_text='Years', gridcolor='lightgray', row=1, col=3)
    
    fig_metrics.update_layout(
        title=dict(text='Project Metrics by Sector (All Projects)', font=dict(size=18, family='Arial'), x=0.5, xanchor='center'),
        plot_bgcolor='white', height=500, font=dict(family='Arial')
    )
    
    st.plotly_chart(fig_metrics, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Delay vs Cost by Sector")
    
    fig_scatter = px.scatter(
        df_clean1,
        x='totalcost_initial_adj', y='delay',
        color='project_size',
        facet_col='sector1',
        title='Delay vs Cost by Sector (colored by project size)',
        labels={'delay': 'Delay (years)', 'totalcost_initial_adj': 'Initial Cost (Millions)'},
        category_orders={'project_size': ['small', 'major', 'mega']},
        opacity=0.6
    )
    fig_scatter.update_layout(height=600)
    st.plotly_chart(fig_scatter, use_container_width=True)

# ============================================================================
# TAB 4: PROJECT RISKS
# ============================================================================
with tab4:
    st.title("⚠️ Project Risks")
    
    st.subheader("Risk Level Distribution by Project Size")
    
    df_clean1_risk_filtered = df_clean1[
        ~df_clean1['safe_env'].isin(['FI']) & 
        ~df_clean1['safe_indigenous'].isin(['FI']) & 
        ~df_clean1['safe_resettle'].isin(['FI'])
    ].copy()
    
    risk_categories = ['safe_env', 'safe_indigenous', 'safe_resettle']
    risk_labels = ['Environmental', 'Indigenous Peoples', 'Resettlement']
    risk_levels = ['A', 'B', 'C', 'D']
    size_order = ['small', 'major', 'mega']
    
    fig_risk_size = make_subplots(
        rows=1, cols=3,
        subplot_titles=risk_labels,
        horizontal_spacing=0.1
    )
    
    risk_colors = {'A': '#db4325', 'B': '#dea247', 'C': '#bbd4a6', 'D': '#57c4ad'}
    
    for col_idx, (risk_col, risk_label) in enumerate(zip(risk_categories, risk_labels), 1):
        for risk_level in risk_levels:
            level_data = []
            for size in size_order:
                size_data = df_clean1_risk_filtered[df_clean1_risk_filtered['project_size'] == size]
                risk_count = (size_data[risk_col] == risk_level).sum()
                risk_pct = (risk_count / len(size_data) * 100)
                level_data.append(risk_pct)
            fig_risk_size.add_trace(
                go.Bar(
                    x=size_order, y=level_data,
                    name=f'Level {risk_level}',
                    marker=dict(color=risk_colors[risk_level], line=dict(color='black', width=1)),
                    text=[f'{val:.0f}%' if val > 5 else '' for val in level_data],
                    textposition='inside', textfont=dict(size=10, color='white', family='Arial'),
                    legendgroup=risk_level, showlegend=(col_idx == 1), opacity=0.8
                ),
                row=1, col=col_idx
            )
        fig_risk_size.update_xaxes(title_text='Project Size', row=1, col=col_idx)
        fig_risk_size.update_yaxes(title_text='Percentage (%)', gridcolor='lightgray', row=1, col=col_idx)
    
    fig_risk_size.update_layout(
        title=dict(text='Risk Level Distribution by Project Size', font=dict(size=18, family='Arial'), x=0.5, xanchor='center'),
        barmode='stack', plot_bgcolor='white', height=550, font=dict(family='Arial'),
        legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5),
        margin=dict(t=130)
    )
    
    st.plotly_chart(fig_risk_size, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Delay Comparison: Low Risk vs High Risk Projects")
    
    fig_risk_delay = make_subplots(
        rows=1, cols=3,
        subplot_titles=risk_labels,
        horizontal_spacing=0.1
    )
    
    for col_idx, (risk_col, risk_label) in enumerate(zip(risk_categories, risk_labels), 1):
        df_filtered = df_clean1[~df_clean1[risk_col].isin(['FI'])].copy()  # Changed here
        df_filtered['risk_group'] = df_filtered[risk_col].apply(lambda x: 'D (No Impact)' if x == 'D' else 'A/B/C (Impact)')
        
        for group in ['D (No Impact)', 'A/B/C (Impact)']:
            group_data = df_filtered[df_filtered['risk_group'] == group]
            fig_risk_delay.add_trace(
                go.Box(
                    y=group_data['delay'], name=group,
                    boxmean='sd',
                    marker=dict(color='#95a5a6' if group == 'D (No Impact)' else '#e74c3c'),
                    showlegend=(col_idx == 1)
                ),
                row=1, col=col_idx
            )
        
        fig_risk_delay.update_xaxes(tickangle=-30, row=1, col=col_idx)
        fig_risk_delay.update_yaxes(title_text='Delay (years)', gridcolor='lightgray', row=1, col=col_idx)
    
    fig_risk_delay.update_layout(
        title=dict(text='Delay Comparison: Level D vs Levels A/B/C (All Projects)', font=dict(size=18, family='Arial'), x=0.5, xanchor='center'),  # Changed title
        plot_bgcolor='white', height=600, font=dict(family='Arial'),
        legend=dict(orientation='h', yanchor='bottom', y=1.04, xanchor='center', x=0.5)
    )
    
    st.plotly_chart(fig_risk_delay, use_container_width=True)
    
    st.info("💡 **Key Finding**: Projects with 'No Impact' (Level D) ratings show longer delays compared to projects with higher risk ratings across all project sizes, suggesting that lower-risk classifications may lead to insufficient planning and oversight.")
# ============================================================================
# TAB 5: DATA
# ============================================================================
with tab5:
    st.title("📋 Data")
    
    st.info("📖 **Please refer to the README file for detailed preprocessing and data adjustment methodology.**")
    
    st.subheader("Dataset Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", len(df_clean1))
    with col2:
        st.metric("Total Columns", len(df_clean1.columns))
    with col3:
        st.metric("Memory Usage", f"{df_clean1.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    st.markdown("---")
    
    # Data preview
    st.subheader("Data Preview")
    st.dataframe(df_clean1.head(20), use_container_width=True)
    
    st.markdown("---")
    
    # Column information
    st.subheader("Column Information")
    col_info = pd.DataFrame({
        'Column': df_clean1.columns,
        'Type': df_clean1.dtypes.values,
        'Non-Null Count': df_clean1.count().values,
        'Null Count': df_clean1.isnull().sum().values
    })
    st.dataframe(col_info, use_container_width=True)
    
    st.markdown("---")
    
    # Download options
    st.subheader("Download Data")
    
    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')
    
    csv = convert_df(df_clean1)
    
    st.download_button(
        label="📥 Download Full Dataset as CSV",
        data=csv,
        file_name='adb_clean_416.csv',
        mime='text/csv',
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #7f8c8d; padding: 1rem;'>
        <p>ADB Infrastructure Project Analysis Dashboard | Data: Asian Development Bank (2002-2019)</p>
    </div>
    """,
    unsafe_allow_html=True
)