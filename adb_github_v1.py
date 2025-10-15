# %%
import os
import pandas as pd
os.chdir('/Users/sjkimm/Library/CloudStorage/GoogleDrive-smrisgood@gmail.com/My Drive/School/Research/PM/ADB')
print("Current working directory:", os.getcwd())

# %%
df_project = pd.read_csv('adb_426.csv')
df_plr = pd.read_csv('WB_PLR.csv')
df_gdp = pd.read_csv('WB_GDPDeflator.csv')

# %% [markdown]
# # Preprocessing

# %% [markdown]
# ## Initial Cost Conversion

# %% [markdown]
# ### 1. PLR Adjustment

# %%
regional_keywords = ['Africa', 'Eastern and Southern Africa', 'Western and Central Africa', 'Sub-Saharan Africa',
    'Sub-Saharan Africa (IDA & IBRD countries)', 'Sub-Saharan Africa (excluding high income)', 'World', 'Caribbean', 'OECS Countries']
df_project['year_for_plr'] = df_project['approvalyear'].astype(str)
df_project['totalcost_initial_adj1_plr'] = None
failure_reasons = {}
extrapolation_details = {}
success_step1 = 0
failure_step1 = 0
for idx, row in df_project.iterrows():
    country = row['countryshortname']
    year = row['year_for_plr']
    initial_cost = row['totalcost_initial']
    if pd.isna(country):
        failure_reasons[idx] = 'Missing country'
        failure_step1 += 1
        continue
    if pd.isna(year) or year == '<NA>' or year == 'nan':
        failure_reasons[idx] = 'Missing year'
        failure_step1 += 1
        continue
    if pd.isna(initial_cost) or initial_cost == 0:
        failure_reasons[idx] = 'Missing/zero initial cost'
        failure_step1 += 1
        continue
    if country in regional_keywords:
        failure_reasons[idx] = 'Regional project'
        failure_step1 += 1
        continue
    plr_row = df_plr[df_plr['countryshortname'] == country]
    if plr_row.empty:
        failure_reasons[idx] = 'Country not in PLR data'
        failure_step1 += 1
        continue
    if year not in df_plr.columns:
        failure_reasons[idx] = f'Year {year} not in PLR columns'
        failure_step1 += 1
        continue
    plr_value = plr_row[year].values[0]
    if pd.isna(plr_value):
        extrapolated_plr, details = get_extrapolated_plr(country, year, df_plr)
        if extrapolated_plr is not None:
            df_project.at[idx, 'totalcost_initial_adj1_plr'] = round(initial_cost / extrapolated_plr, 2)
            failure_reasons[idx] = 'Used extrapolated PLR'
            if country not in extrapolation_details:
                extrapolation_details[country] = []
            extrapolation_details[country].append({'year': year, 'details': details, 'value': extrapolated_plr})
            success_step1 += 1
        else:
            failure_reasons[idx] = 'PLR value is NaN, extrapolation failed'
            failure_step1 += 1
    elif plr_value == 0:
        failure_reasons[idx] = 'PLR value is zero'
        failure_step1 += 1
    else:
        df_project.at[idx, 'totalcost_initial_adj1_plr'] = round(initial_cost / plr_value, 2)
        success_step1 += 1
print(f"Successfully adjusted: {success_step1}")
print(f"Failed adjustments: {failure_step1}")
if failure_step1 > 0:
    print("\nFailure reasons:")
    from collections import Counter
    reason_counts = Counter(failure_reasons.values())
    for reason, count in reason_counts.most_common():
        print(f"  {reason}: {count}")
if extrapolation_details:
    print("\n" + "="*80)
    print("PLR EXTRAPOLATION DETAILS")
    print("="*80)
    for country, details_list in sorted(extrapolation_details.items()):
        print(f"\n{country}:")
        for detail in details_list:
            print(f"  Year {detail['year']}: {detail['details']}")
            print(f"    Extrapolated value: {detail['value']:.4f}")
else:
    print("\nNo PLR extrapolations were needed.")
print("\nSample results:")
print(df_project[['countryshortname', 'year_for_plr', 'totalcost_initial', 'totalcost_initial_adj1_plr']].head(5))

# %%
# troubleshooting - investigate missing countries (identify rows with missing countries)

missing_countries = df_project[df_project['countryshortname'].isna()]
print(f"\nTotal rows with missing countries: {len(missing_countries)}")
print(missing_countries[['projectid', 'countryshortname', 'countrycode', 'regionname', 'approvalyear', 'totalcost_initial', 'totalcost_final']].to_string())

# for idx in missing_countries.index:
#     country_code = df_project.loc[idx, 'countrycode']
#     region = df_project.loc[idx, 'regionname']
#     print(f"\nRow {idx}:")
#     print(f"  Country code: {country_code}, Region: {region}")
#     plr_match = df_plr[df_plr['countrycode'] == country_code]
#     if not plr_match.empty:
#         print(f"  Found in PLR: {plr_match['countryshortname'].values[0]}")
#     else:
#         print(f"  Not found in PLR by country code")
# print(f"\nImpact: {len(missing_countries)} out of {len(df_project)} projects ({len(missing_countries)/len(df_project)*100:.1f}%)")

# %%
# making a column that indicatese whether or not to include in later analysis
df_project['include'] = True
missing_countries = df_project['countryshortname'].isna() # excluding regional projects
df_project.loc[missing_countries, 'include'] = False
print(f"\n {missing_countries.sum()} rows with missing countries as include=False")

print("\nRows marked for exclusion:")
print(df_project[df_project['include'] == False][['projectid', 'countryshortname', 'countrycode', 'regionname', 'approvalyear', 'include']])

print(f"\nTotal projects: {len(df_project)}, Included: {df_project['include'].sum()}, Excluded:  {(~df_project['include']).sum()}")

# %%
df_project['totalcost_initial_adj2_2019'] = None
failure_reasons_step2 = {}
extrapolation_details_step2 = {}
success_step2 = 0
failure_step2 = 0
for idx, row in df_project.iterrows():
    if not row['include']:
        failure_reasons_step2[idx] = 'Excluded from analysis'
        failure_step2 += 1
        continue
    if pd.isna(row['totalcost_initial_adj1_plr']):
        failure_reasons_step2[idx] = 'Step 1 failed (NA)'
        failure_step2 += 1
        continue
    country = row['countryshortname']
    year = row['year_for_plr']
    cost_adj1 = row['totalcost_initial_adj1_plr']
    if pd.isna(country):
        failure_reasons_step2[idx] = 'Missing country'
        failure_step2 += 1
        continue
    gdp_row = df_gdp[df_gdp['countryshortname'] == country]
    if gdp_row.empty:
        failure_reasons_step2[idx] = 'Country not in GDP data'
        failure_step2 += 1
        continue
    if year not in df_gdp.columns or '2019' not in df_gdp.columns:
        failure_reasons_step2[idx] = f'Year {year} or 2019 not in GDP columns'
        failure_step2 += 1
        continue
    gdp_approval_year = gdp_row[year].values[0]
    gdp_2019 = gdp_row['2019'].values[0]
    if pd.isna(gdp_approval_year):
        gdp_approval_year, details = get_extrapolated_gdp(country, year, df_gdp)
        if gdp_approval_year is not None:
            if country not in extrapolation_details_step2:
                extrapolation_details_step2[country] = []
            extrapolation_details_step2[country].append({'year': year, 'type': 'approval_year', 'details': details, 'value': gdp_approval_year})
    if pd.isna(gdp_2019):
        gdp_2019, details = get_extrapolated_gdp(country, '2019', df_gdp)
        if gdp_2019 is not None:
            if country not in extrapolation_details_step2:
                extrapolation_details_step2[country] = []
            extrapolation_details_step2[country].append({'year': '2019', 'type': 'base_year', 'details': details, 'value': gdp_2019})
    if pd.isna(gdp_approval_year):
        failure_reasons_step2[idx] = f'GDP deflator for {year} is NaN'
        failure_step2 += 1
        continue
    if pd.isna(gdp_2019):
        failure_reasons_step2[idx] = 'GDP deflator for 2019 is NaN'
        failure_step2 += 1
        continue
    if gdp_approval_year == 0:
        failure_reasons_step2[idx] = f'GDP deflator for {year} is zero'
        failure_step2 += 1
        continue
    df_project.at[idx, 'totalcost_initial_adj2_2019'] = round(cost_adj1 * (gdp_2019 / gdp_approval_year), 2)
    success_step2 += 1
if failure_step2 > 0:
    print("\nFailure reasons:")
    from collections import Counter
    reason_counts = Counter(failure_reasons_step2.values())
    for reason, count in reason_counts.most_common():
        print(f"  {reason}: {count}")
if extrapolation_details_step2:
    print("\n" + "="*80)
    print("GDP DEFLATOR EXTRAPOLATION DETAILS")
    print("="*80)
    for country, details_list in sorted(extrapolation_details_step2.items()):
        print(f"\n{country}:")
        for detail in details_list:
            print(f"  Year {detail['year']} ({detail['type']}): {detail['details']}")
            print(f"    Extrapolated value: {detail['value']:.4f}")
else:
    print("\nNo GDP extrapolations were needed.")
print("\nSample results:")
print(df_project[['countryshortname', 'year_for_plr', 'totalcost_initial', 'totalcost_initial_adj1_plr', 'totalcost_initial_adj2_2019']].head(5))
print(f"Total projects: {len(df_project)}, Included: {df_project['include'].sum()}")
print(f"Fully adjusted: {df_project['totalcost_initial_adj2_2019'].notna().sum()}")
print(f"Failed: {df_project['totalcost_initial_adj2_2019'].isna().sum()}")

# %% [markdown]
# ## Same for final cost

# %%
from collections import Counter, defaultdict

df_project['year_for_closing'] = df_project['closingyear'].astype(str)
df_project['totalcost_final_adj1_plr'] = None
failure_reasons_final_step1 = {}
extrapolation_details_step1 = defaultdict(list) 
success_step1 = 0
failure_step1 = 0

for idx, row in df_project.iterrows():
    if not row['include']:
        failure_reasons_final_step1[idx] = 'Excluded from analysis'
        failure_step1 += 1
        continue
    country = row['countryshortname']
    year = row['year_for_closing']
    final_cost = row['totalcost_final']
    if pd.isna(country):
        failure_reasons_final_step1[idx] = 'Missing country'
        failure_step1 += 1
        continue
    if pd.isna(final_cost) or final_cost == 0:
        failure_reasons_final_step1[idx] = 'Missing/zero final cost'
        failure_step1 += 1
        continue
    plr_row = df_plr[df_plr['countryshortname'] == country]
    if plr_row.empty:
        failure_reasons_final_step1[idx] = 'Country not in PLR data'
        failure_step1 += 1
        continue
    if year not in df_plr.columns:
        failure_reasons_final_step1[idx] = f'Year {year} not in PLR columns'
        failure_step1 += 1
        continue
    plr_value = plr_row[year].values[0]
    if pd.isna(plr_value):
        extrapolated_plr, details = get_extrapolated_plr(country, year, df_plr)
        if extrapolated_plr is not None:
            df_project.at[idx, 'totalcost_final_adj1_plr'] = round(final_cost / extrapolated_plr, 2)
            failure_reasons_final_step1[idx] = 'Used extrapolated PLR'
            # Store extrapolation details
            extrapolation_details_step1[country].append({
                'year': year,
                'details': details,
                'value': extrapolated_plr
            })
            success_step1 += 1
        else:
            failure_reasons_final_step1[idx] = 'PLR value is NaN, extrapolation failed'
            failure_step1 += 1
    elif plr_value == 0:
        failure_reasons_final_step1[idx] = 'PLR value is zero'
        failure_step1 += 1
    else:
        df_project.at[idx, 'totalcost_final_adj1_plr'] = round(final_cost / plr_value, 2)
        success_step1 += 1

print(f"Step 1 Complete: {success_step1} successful, {failure_step1} failed")

if failure_step1 > 0:
    reason_counts = Counter(failure_reasons_final_step1.values())
    for reason, count in reason_counts.most_common():
        print(f"  {reason}: {count}")

# Print extrapolation details
if extrapolation_details_step1:
    print("\n" + "="*80)
    print("PLR EXTRAPOLATION DETAILS (Step 1)")
    print("="*80)
    for country, details_list in sorted(extrapolation_details_step1.items()):
        print(f"\n{country}:")
        for detail in details_list:
            print(f"  Year {detail['year']}: {detail['details']}")
            print(f"    Extrapolated value: {detail['value']:.4f}")

# ============================================================================
# STEP 2: GDP Deflator
# ============================================================================

df_project['totalcost_final_adj2_2019'] = None
failure_reasons_final_step2 = {}
extrapolation_details_step2 = defaultdict(list)  # Track GDP extrapolation details
success_step2 = 0
failure_step2 = 0

for idx, row in df_project.iterrows():
    if not row['include']:
        failure_reasons_final_step2[idx] = 'Excluded from analysis'
        failure_step2 += 1
        continue
    if pd.isna(row['totalcost_final_adj1_plr']):
        failure_reasons_final_step2[idx] = 'Step 1 failed (NA)'
        failure_step2 += 1
        continue
    country = row['countryshortname']
    year = row['year_for_closing']
    cost_adj1 = row['totalcost_final_adj1_plr']
    gdp_row = df_gdp[df_gdp['countryshortname'] == country]
    if gdp_row.empty:
        failure_reasons_final_step2[idx] = 'Country not in GDP data'
        failure_step2 += 1
        continue
    if year not in df_gdp.columns or '2019' not in df_gdp.columns:
        failure_reasons_final_step2[idx] = f'Year {year} or 2019 not in GDP columns'
        failure_step2 += 1
        continue
    
    gdp_closing_year = gdp_row[year].values[0]
    gdp_2019 = gdp_row['2019'].values[0]
    
    # Track if extrapolation was used
    extrapolated_closing = False
    extrapolated_2019 = False
    
    if pd.isna(gdp_closing_year):
        gdp_closing_year, details = get_extrapolated_gdp(country, year, df_gdp)
        if gdp_closing_year is not None:
            extrapolated_closing = True
            extrapolation_details_step2[country].append({
                'year': year,
                'type': 'closing_year',
                'details': details,
                'value': gdp_closing_year
            })
    
    if pd.isna(gdp_2019):
        gdp_2019, details = get_extrapolated_gdp(country, '2019', df_gdp)
        if gdp_2019 is not None:
            extrapolated_2019 = True
            extrapolation_details_step2[country].append({
                'year': '2019',
                'type': 'base_year',
                'details': details,
                'value': gdp_2019
            })
    
    if pd.isna(gdp_closing_year) or pd.isna(gdp_2019) or gdp_closing_year == 0:
        failure_reasons_final_step2[idx] = 'Invalid GDP deflator'
        failure_step2 += 1
        continue
    
    df_project.at[idx, 'totalcost_final_adj2_2019'] = round(cost_adj1 * (gdp_2019 / gdp_closing_year), 2)
    success_step2 += 1

print(f"\nStep 2 Complete: {success_step2} successful, {failure_step2} failed")

if failure_step2 > 0:
    reason_counts = Counter(failure_reasons_final_step2.values())
    for reason, count in reason_counts.most_common():
        print(f"  {reason}: {count}")

# Print GDP extrapolation details
if extrapolation_details_step2:
    print("\n" + "="*80)
    print("GDP DEFLATOR EXTRAPOLATION DETAILS (Step 2)")
    print("="*80)
    for country, details_list in sorted(extrapolation_details_step2.items()):
        print(f"\n{country}:")
        for detail in details_list:
            print(f"  Year {detail['year']} ({detail['type']}): {detail['details']}")
            print(f"    Extrapolated value: {detail['value']:.4f}")

# %%
initial_adjustment_ratio = df_project['totalcost_initial_adj2_2019'] / df_project['totalcost_initial']
final_adjustment_ratio = df_project['totalcost_final_adj2_2019'] / df_project['totalcost_final']
print("\nAdjustment ratios calculated")
print(f"Valid initial ratios: {initial_adjustment_ratio.notna().sum()}")
print(f"Valid final ratios: {final_adjustment_ratio.notna().sum()}")
print("Initial Cost Adjustment:")
print(initial_adjustment_ratio.describe())
print("Final Cost Adjustment Ratio:")
print(final_adjustment_ratio.describe())
def calculate_zscore(series):
    mean = series.mean()
    std = series.std()
    return (series - mean) / std
initial_ratio_zscore = calculate_zscore(initial_adjustment_ratio)
final_ratio_zscore = calculate_zscore(final_adjustment_ratio)
z_threshold = 3
is_outlier_initial_zscore = np.abs(initial_ratio_zscore) > z_threshold
is_outlier_final_zscore = np.abs(final_ratio_zscore) > z_threshold
print(f"Outlier Detection (z-score threshold: {z_threshold})")
if is_outlier_initial_zscore.sum() > 0:
    print(f"\nInitial cost outliers: {is_outlier_initial_zscore.sum()}")
    outlier_indices = is_outlier_initial_zscore[is_outlier_initial_zscore].index
    outliers_df = df_project.loc[outlier_indices, ['projectid', 'countryshortname', 'approvalyear', 'totalcost_initial', 'totalcost_initial_adj2_2019']].copy()
    outliers_df['initial_adjustment_ratio'] = initial_adjustment_ratio.loc[outlier_indices]
    outliers_df['initial_ratio_zscore'] = initial_ratio_zscore.loc[outlier_indices]
    outliers_df = outliers_df.sort_values('initial_ratio_zscore', ascending=False)
    print(outliers_df.to_string())
if is_outlier_final_zscore.sum() > 0:
    print(f"Final cost outliers: {is_outlier_final_zscore.sum()}")
    outlier_indices = is_outlier_final_zscore[is_outlier_final_zscore].index
    outliers_df = df_project.loc[outlier_indices, ['projectid', 'countryshortname', 'closingyear', 'totalcost_final', 'totalcost_final_adj2_2019']].copy()
    outliers_df['final_adjustment_ratio'] = final_adjustment_ratio.loc[outlier_indices]
    outliers_df['final_ratio_zscore'] = final_ratio_zscore.loc[outlier_indices]
    outliers_df = outliers_df.sort_values('final_ratio_zscore', ascending=False)
    print(outliers_df.to_string())
is_clean_adjustment = ~is_outlier_initial_zscore & ~is_outlier_final_zscore
df_project.loc[is_outlier_initial_zscore | is_outlier_final_zscore, 'include'] = False
print(f"\nMarked {(is_outlier_initial_zscore | is_outlier_final_zscore).sum()} outliers as excluded")
print(f"\nTotal projects: {len(df_project)}")
print(f"Initial cost outliers: {is_outlier_initial_zscore.sum()}, Final cost outliers: {is_outlier_final_zscore.sum()}")
print(f"Clean projects (no outliers): {is_clean_adjustment.sum()}")
print(f"Clean percentage: {is_clean_adjustment.sum() / len(df_project) * 100:.1f}%")
print(f"Included in analysis: {df_project['include'].sum()}")
print(f"Excluded from analysis: {(~df_project['include']).sum()}")

# %%
# Create ADB funding ratio
df_project['adb_funding_ratio'] = df_project['approved_amount_adb'] / df_project['totalcost_initial']
print("\nCreated adb_funding_ratio column")
print("\nADB Funding Ratio Statistics:")
print(df_project['adb_funding_ratio'].describe())
print("\nSample of ADB funding ratios:")
print(df_project[['projectid', 'countryshortname', 'approved_amount_adb', 'totalcost_initial', 'adb_funding_ratio']].head(5))
over_100_pct = df_project[df_project['adb_funding_ratio'] > 1]
print(f"\nProjects where ADB funds > total initial cost: {len(over_100_pct)}")
if len(over_100_pct) > 0:
    print("Sample cases:")
    print(over_100_pct[['projectid', 'countryshortname', 'approved_amount_adb', 'totalcost_initial', 'adb_funding_ratio']].head(5))
print(f"Mean: {df_project['adb_funding_ratio'].mean():.2%}")
print(f"Median: {df_project['adb_funding_ratio'].median():.2%}")
print(f"Min: {df_project['adb_funding_ratio'].min():.2%}")
print(f"Max: {df_project['adb_funding_ratio'].max():.2%}")
import plotly.express as px
fig = px.histogram(
    df_project,
    x='adb_funding_ratio',
    nbins=50,
    title='Distribution of ADB Funding Ratio',
    labels={'adb_funding_ratio': 'ADB Funding Ratio (ADB Amount / Total Initial Cost)'}
)
fig.add_vline(x=1.0, line_dash="dash", line_color="red", annotation_text="100%")
fig.update_layout(height=500, width=1000)
fig.show()

# %%
df_clean = df_project[df_project['include']].copy()
print(f"Original dataset: {len(df_project)} projects")
print(f"Clean dataset (included): {len(df_clean)} projects")
print(f"Excluded: {len(df_project) - len(df_clean)} projects")
df_clean = df_clean[df_clean['duration_years'] > 2].copy()
print(f"After filtering duration > 2 years: {len(df_clean)} projects")
print("All costs are in millions USD")
df_clean['totalcost_initial_adj'] = df_clean['totalcost_initial_adj2_2019'].apply(
    lambda x: round(x, 2) if pd.notna(x) else None
)
df_clean['totalcost_final_adj'] = df_clean['totalcost_final_adj2_2019'].apply(
    lambda x: round(x, 2) if pd.notna(x) else None
)

# %%
# Classifying projects according to size
def classify_project_size(cost):
    if pd.notna(cost):
        if cost >= 1_000:
            return 'mega'
        elif cost >= 500:
            return 'major'
        else:
            return 'small'
    return None
df_clean['project_size'] = df_clean['totalcost_initial_adj'].apply(classify_project_size)
print("\nProject size distribution:")
print(df_clean['project_size'].value_counts())
for size in ['mega', 'major', 'small']:
    size_df = df_clean[df_clean['project_size'] == size]
    if len(size_df) > 0:
        print(f"\n{size.upper()} projects (top 5 by cost):")
        top_projects = size_df.nlargest(5, 'totalcost_initial_adj')
        print(top_projects[['projectid', 'countryshortname', 'totalcost_initial_adj', 'project_size']])

# %%
df_clean.describe()

# %%
df_clean.to_csv('adb_clean_416.csv', index=False)

# %% [markdown]
# # EDA

# %% [markdown]
# ## Including all project sizes

# %%
df_clean1 = pd.read_csv('adb_clean_416.csv')

# %%
import plotly.graph_objects as go

approval_distribution = df_clean1['approvalyear'].value_counts().sort_index()
closing_distribution = df_clean1['closingyear'].value_counts().sort_index()

fig = go.Figure()
fig.add_trace(go.Bar(
    x=approval_distribution.index,
    y=approval_distribution.values,
    name='Approval Year',
    marker=dict(
        color='steelblue',
        line=dict(color='black', width=1)
    ),
    opacity=0.7
))
fig.add_trace(go.Bar(
    x=closing_distribution.index,
    y=closing_distribution.values,
    name='Closing Year',
    marker=dict(
        color='coral',
        line=dict(color='black', width=1)
    ),
    opacity=0.7
))
fig.update_layout(
    title=dict(
        text='Distribution of Projects by Approval and Closing Year',
        font=dict(size=16, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title=dict(text='Year', font=dict(size=14, family='Arial', color='black')),
        tickmode='linear',
        tick0=min(approval_distribution.index.min(), closing_distribution.index.min()),
        dtick=1,
        tickfont=dict(family='Arial')
    ),
    yaxis=dict(
        title=dict(text='Number of Projects', font=dict(size=14, family='Arial', color='black')),
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial')
    ),
    plot_bgcolor='white',
    width=1000,
    height=500,
    font=dict(family='Arial'),
    barmode='overlay',  #group, overlay
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=1,
        font=dict(family='Arial')
    )
)
fig.show()

# %%
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=('By Project Size', 'By Sector', 'By Region'),
    horizontal_spacing=0.12
)

# 1. By Size
size_counts = df_clean1['project_size'].value_counts()
total_projects = size_counts.sum()
size_percentages = (size_counts / total_projects * 100).round(1)
size_colors = {'small': '#3498db', 'major': '#f39c12', 'mega': '#e74c3c'}
color_list_size = [size_colors.get(size, '#95a5a6') for size in size_counts.index]
text_labels_size = [f"{pct}%<br>({count})" for pct, count in zip(size_percentages.values, size_counts.values)]

fig.add_trace(
    go.Bar(
        x=size_counts.index,
        y=size_percentages.values,
        marker=dict(color=color_list_size, line=dict(color='black', width=1)),
        text=text_labels_size,
        textposition='auto',
        textfont=dict(size=12, color='white', family='Arial'),
        opacity=0.8,
        showlegend=False
    ),
    row=1, col=1
)

# 2. By Sector
sector_counts = df_clean1['sector1'].value_counts()
sector_percentages = (sector_counts / total_projects * 100).round(1)
sector_colors = {'Energy': '#e74c3c', 'Transport': '#3498db', 'Water': '#2ecc71'}
color_list_sector = [sector_colors.get(sector, '#95a5a6') for sector in sector_counts.index]
text_labels_sector = [f"{pct}%<br>({count})" for pct, count in zip(sector_percentages.values, sector_counts.values)]

fig.add_trace(
    go.Bar(
        x=sector_counts.index,
        y=sector_percentages.values,
        marker=dict(color=color_list_sector, line=dict(color='black', width=1)),
        text=text_labels_sector,
        textposition='auto',
        textfont=dict(size=12, color='white', family='Arial'),
        opacity=0.8,
        showlegend=False
    ),
    row=1, col=2
)

# 3. By Region
region_counts = df_clean1['regionname'].value_counts().sort_values(ascending=False)
region_percentages = (region_counts / total_projects * 100).round(1)
text_labels_region = [f"{pct}%<br>({count})" for pct, count in zip(region_percentages.values, region_counts.values)]

fig.add_trace(
    go.Bar(
        x=region_counts.index,
        y=region_percentages.values,
        marker=dict(color='steelblue', line=dict(color='black', width=1)),
        text=text_labels_region,
        textposition='auto',
        textfont=dict(size=10, color='white', family='Arial'),
        opacity=0.8,
        showlegend=False
    ),
    row=1, col=3
)

# Update axes
fig.update_xaxes(title_text='Project Size', tickfont=dict(size=11), row=1, col=1, categoryorder='array', categoryarray=['small', 'major', 'mega'])
fig.update_xaxes(title_text='Sector', tickfont=dict(size=11), row=1, col=2)
fig.update_xaxes(title_text='Region', tickfont=dict(size=9), tickangle=-45, row=1, col=3)

fig.update_yaxes(title_text='Percentage (%)', gridcolor='lightgray', gridwidth=0.5, tickfont=dict(size=11), row=1, col=1)
fig.update_yaxes(title_text='Percentage (%)', gridcolor='lightgray', gridwidth=0.5, tickfont=dict(size=11), row=1, col=2)
fig.update_yaxes(title_text='Percentage (%)', gridcolor='lightgray', gridwidth=0.5, tickfont=dict(size=11), row=1, col=3)

fig.update_layout(
    title=dict(
        text='Distribution of Projects<br><sub>Small: <$500M | Major: $500M-$1B | Mega: ≥$1B</sub>',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1600,
    height=550,
    font=dict(family='Arial')
)

fig.show()

# %%
import plotly.express as px

country_sector_counts = df_clean1.groupby(['countryshortname', 'sector1']).size().reset_index(name='count')
country_total = df_clean1.groupby('countryshortname').agg({
    'projectid': 'count',
    'sector1': lambda x: ', '.join(x.value_counts().index[:3])
}).reset_index()
country_total.columns = ['countryshortname', 'total_projects', 'main_sectors']

print("\nProjects by Country:")
print(country_total.sort_values('total_projects', ascending=False).to_string(index=False))

fig = px.choropleth(
    country_total,
    locations='countryshortname',
    locationmode='country names',
    color='total_projects',
    hover_name='countryshortname',
    hover_data={'countryshortname': False, 'total_projects': True, 'main_sectors': True},
    color_continuous_scale='YlGn',  # YlGnBu
    title='Geographic Distribution of Projects',
    labels={'total_projects': 'Number of Projects', 'main_sectors': 'Main Sectors'}
)

fig.update_layout(
    geo=dict(
        scope='asia',
        projection_type='natural earth',
        showland=True,
        landcolor='rgb(243, 243, 243)',
        coastlinecolor='rgb(204, 204, 204)',
        showcountries=True,
        countrycolor='rgb(204, 204, 204)'
    ),
    width=1200,
    height=700,
    font=dict(family='Arial')
)

fig.show()

# %%
country_data = df_clean1.groupby(['countryshortname']).agg({
    'projectid': 'count',
    'totalcost_initial_adj': 'sum',
    'sector1': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Mixed'
}).reset_index()
country_data.columns = ['country', 'project_count', 'total_cost', 'dominant_sector']

country_coords = {
    # South Asia
    'Afghanistan': (33.9391, 67.7100),
    'Bangladesh': (23.6850, 90.3563),
    'Bhutan': (27.5142, 90.4336),
    'India': (20.5937, 78.9629),
    'Maldives': (3.2028, 73.2207),
    'Nepal': (28.3949, 84.1240),
    'Pakistan': (30.3753, 69.3451),
    'Sri Lanka': (7.8731, 80.7718),
    
    # Southeast Asia
    'Brunei Darussalam': (4.5353, 114.7277),
    'Cambodia': (12.5657, 104.9910),
    'Indonesia': (-0.7893, 113.9213),
    'Lao PDR': (19.8563, 102.4955),
    'Laos': (19.8563, 102.4955),
    "Lao People's Democratic Republic": (19.8563, 102.4955),  # Added
    'Malaysia': (4.2105, 101.9758),
    'Myanmar': (21.9162, 95.9560),
    'Philippines': (12.8797, 121.7740),
    'Singapore': (1.3521, 103.8198),
    'Thailand': (15.8700, 100.9925),
    'Timor-Leste': (-8.8742, 125.7275),
    'Viet Nam': (14.0583, 108.2772),
    'Vietnam': (14.0583, 108.2772),
    
    # East Asia
    'China': (35.8617, 104.1954),
    "China, People's Republic of": (35.8617, 104.1954),
    'Hong Kong': (22.3193, 114.1694),
    'Japan': (36.2048, 138.2529),
    'Korea, Republic of': (35.9078, 127.7669),
    'Mongolia': (46.8625, 103.8467),
    'Taiwan': (23.6978, 120.9605),
    
    # Central and West Asia
    'Armenia': (40.0691, 45.0382),
    'Azerbaijan': (40.1431, 47.5769),
    'Georgia': (42.3154, 43.3569),
    'Kazakhstan': (48.0196, 66.9237),
    'Kyrgyz Republic': (41.2044, 74.7661),
    'Kyrgyzstan': (41.2044, 74.7661),
    'Tajikistan': (38.8610, 71.2761),
    'Turkmenistan': (38.9697, 59.5563),
    'Uzbekistan': (41.3775, 64.5853),
    
    # Pacific
    'Cook Islands': (-21.2367, -159.7777),
    'Fiji': (-17.7134, 178.0650),
    'Kiribati': (-3.3704, -168.7340),
    'Marshall Islands': (7.1315, 171.1845),
    'Micronesia': (7.4256, 150.5508),
    'Micronesia, Federated States of': (7.4256, 150.5508),  # Added
    'Nauru': (-0.5228, 166.9315),
    'Palau': (7.5150, 134.5825),
    'Papua New Guinea': (-6.3150, 143.9555),
    'Samoa': (-13.7590, -172.1046),
    'Solomon Islands': (-9.6457, 160.1562),
    'Tonga': (-21.1789, -175.1982),
    'Tuvalu': (-7.1095, 177.6493),
    'Vanuatu': (-15.3767, 166.9592)
}
country_data['lat'] = country_data['country'].map(lambda x: country_coords.get(x, (None, None))[0])
country_data['lon'] = country_data['country'].map(lambda x: country_coords.get(x, (None, None))[1])

# Check which countries are missing coordinates
missing_coords = country_data[country_data['lat'].isna()]
if len(missing_coords) > 0:
    print("Countries missing coordinates:")
    print(missing_coords['country'].tolist())

country_data = country_data.dropna(subset=['lat', 'lon'])

colors_sector = {'Energy': '#e74c3c', 'Transport': '#3498db', 'Water': '#2ecc71'}

fig = px.scatter_geo(
    country_data,
    lat='lat',
    lon='lon',
    size='project_count',
    color='dominant_sector',
    hover_name='country',
    hover_data={
        'project_count': True, 
        'total_cost': ':.2f', 
        'dominant_sector': True,
        'lat': False, 
        'lon': False
    },
    color_discrete_map=colors_sector,
    title='Geographic Distribution of Projects by Country',
    size_max=50,
    labels={'project_count': 'Projects', 'total_cost': 'Total Cost (M USD)', 'dominant_sector': 'Dominant Sector'}
)

fig.update_geos(
    scope='asia',
    projection_type='natural earth',
    showland=True,
    landcolor='rgb(243, 243, 243)',
    coastlinecolor='rgb(204, 204, 204)',
    showcountries=True,
    countrycolor='rgb(204, 204, 204)',
    center=dict(lat=15, lon=100)
)

fig.update_layout(
    width=1200,
    height=700,
    font=dict(family='Arial')
)

fig.show()

print(f"\nTotal countries plotted: {len(country_data)}")
print(f"Total projects: {country_data['project_count'].sum()}")

# %%
projects_by_year = df_clean1.groupby(['approvalyear', 'sector1']).size().reset_index(name='count')
avg_cost_by_year = df_clean1.groupby(['approvalyear', 'sector1'])['totalcost_initial_adj'].mean().reset_index(name='avg_cost')

fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Number of Projects Over Time', 'Average Project Cost Over Time'),
    horizontal_spacing=0.12
)

sector_colors = {'Energy': '#d95f02', 'Transportation': '#57c4ad', 'Water': '#0571b0'}

for sector in sorted(df_clean1['sector1'].unique()):
    sector_data_count = projects_by_year[projects_by_year['sector1'] == sector]
    fig.add_trace(
        go.Scatter(
            x=sector_data_count['approvalyear'],
            y=sector_data_count['count'],
            mode='lines+markers',
            name=sector,
            line=dict(width=3, color=sector_colors.get(sector, '#95a5a6')),
            marker=dict(size=8, color=sector_colors.get(sector, '#95a5a6'), line=dict(width=1, color='black')),
            legendgroup=sector,
            showlegend=True
        ),
        row=1, col=1
    )
    
    sector_data_cost = avg_cost_by_year[avg_cost_by_year['sector1'] == sector]
    fig.add_trace(
        go.Scatter(
            x=sector_data_cost['approvalyear'],
            y=sector_data_cost['avg_cost'],
            mode='lines+markers',
            name=sector,
            line=dict(width=3, color=sector_colors.get(sector, '#95a5a6')),
            marker=dict(size=8, color=sector_colors.get(sector, '#95a5a6'), line=dict(width=1, color='black')),
            legendgroup=sector,
            showlegend=False,
            hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Avg Cost: $%{y:.2f}M<extra></extra>'
        ),
        row=1, col=2
    )

fig.update_xaxes(
    title_text='Approval Year',
    tickmode='linear',
    dtick=2,
    tickfont=dict(family='Arial', size=11),
    row=1, col=1
)
fig.update_xaxes(
    title_text='Approval Year',
    tickmode='linear',
    dtick=2,
    tickfont=dict(family='Arial', size=11),
    row=1, col=2
)

fig.update_yaxes(
    title_text='Number of Projects',
    gridcolor='lightgray',
    gridwidth=0.5,
    tickfont=dict(family='Arial', size=11),
    row=1, col=1
)
fig.update_yaxes(
    title_text='Average Cost (Million USD, 2019)',
    gridcolor='lightgray',
    gridwidth=0.5,
    tickfont=dict(family='Arial', size=11),
    row=1, col=2
)

fig.update_layout(
    title=dict(
        text='Project Trends Over Time by Sector',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1400,
    height=500,
    font=dict(family='Arial'),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.03,
        xanchor='right',
        x=0.6,
        font=dict(family='Arial', size=12)
    ),
    hovermode='x unified'
)

fig.show()

# %%
for size in ['small', 'major', 'mega']:
    size_data = df_clean1[df_clean1['project_size'] == size]
    mean_delay = size_data['delay'].mean()
    median_delay = size_data['delay'].median()
    std_delay = size_data['delay'].std()
    count = len(size_data)
    delayed_projects = (size_data['delay'] > 0).sum()
    delayed_pct = (delayed_projects / count * 100)
    print(f"\n{size.upper()} projects (n={count}):")
    print(f"  Mean delay: {mean_delay:.2f} years")
    print(f"  Median delay: {median_delay:.2f} years")
    print(f"  Std deviation: {std_delay:.2f} years")
    print(f"  Projects with delay: {delayed_projects} ({delayed_pct:.1f}%)")
from scipy import stats
small_delay = df_clean1[df_clean1['project_size'] == 'small']['delay']
major_delay = df_clean1[df_clean1['project_size'] == 'major']['delay']
mega_delay = df_clean1[df_clean1['project_size'] == 'mega']['delay']
f_stat, p_value = stats.f_oneway(small_delay, major_delay, mega_delay)
print(f"\n" + "="*80)
print("ANOVA TEST: Are delays significantly different across project sizes?")
print("="*80)
print(f"F-statistic: {f_stat:.3f}")
print(f"P-value: {p_value:.4f}")
if p_value < 0.05:
    print("→ Project sizes have statistically significant differences in delay")
else:
    print("→ No significant difference between project sizes")
fig = go.Figure()
size_order = ['small', 'major', 'mega']
size_colors = {'small': '#3498db', 'major': '#f39c12', 'mega': '#e74c3c'}
for size in size_order:
    size_data = df_clean1[df_clean1['project_size'] == size]
    fig.add_trace(go.Violin(
        y=size_data['delay'],
        x=[size] * len(size_data),
        name=size,
        box_visible=True,
        meanline_visible=True,
        points='all',
        pointpos=-0.5,
        jitter=0.3,
        marker=dict(color=size_colors[size]),
        scalemode='width',
        width=0.6,
        side='positive',
        line=dict(color=size_colors[size], width=2)
    ))
fig.update_layout(
    title=dict(
        text='Project Delay Distribution by Project Size',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title=dict(text='Project Size', font=dict(size=14, family='Arial')),
        tickfont=dict(family='Arial', size=12),
        categoryorder='array',
        categoryarray=size_order
    ),
    yaxis=dict(
        title=dict(text='Delay (years)', font=dict(size=14, family='Arial')),
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=12)
    ),
    plot_bgcolor='white',
    width=900,
    height=600,
    font=dict(family='Arial'),
    showlegend=False
)
fig.show()

# %%
df_clean1_risk_filtered = df_clean1[
    ~df_clean1['safe_env'].isin(['FI']) & 
    ~df_clean1['safe_indigenous'].isin(['FI']) & 
    ~df_clean1['safe_resettle'].isin(['FI'])
].copy()

risk_categories = ['safe_env', 'safe_indigenous', 'safe_resettle']
risk_labels = ['Environmental', 'Indigenous Peoples', 'Resettlement']
risk_levels = ['A', 'B', 'C', 'D']
size_order = ['small', 'major', 'mega']

fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=risk_labels,
    horizontal_spacing=0.1
)

risk_colors = {'A': '#db4325', 'B': '#dea247', 'C': '#bbd4a6', 'D': '#57c4ad'}

for col_idx, (risk_col, risk_label) in enumerate(zip(risk_categories, risk_labels), 1):
    for risk_level in risk_levels:  # Changed from reversed(risk_levels) to risk_levels
        level_data = []
        for size in size_order:
            size_data = df_clean1_risk_filtered[df_clean1_risk_filtered['project_size'] == size]
            risk_count = (size_data[risk_col] == risk_level).sum()
            risk_pct = (risk_count / len(size_data) * 100)
            level_data.append(risk_pct)
        fig.add_trace(
            go.Bar(
                x=size_order,
                y=level_data,
                name=f'Level {risk_level}',
                marker=dict(color=risk_colors[risk_level], line=dict(color='black', width=1)),
                text=[f'{val:.0f}%' if val > 5 else '' for val in level_data],
                textposition='inside',
                textfont=dict(size=10, color='white', family='Arial'),
                legendgroup=risk_level,
                showlegend=(col_idx == 1),
                opacity=0.8
            ),
            row=1, col=col_idx
        )
    fig.update_xaxes(title_text='Project Size', row=1, col=col_idx, tickfont=dict(family='Arial', size=11))
    fig.update_yaxes(title_text='Percentage (%)', row=1, col=col_idx, gridcolor='lightgray', gridwidth=0.5)

fig.update_layout(
    title=dict(
        text='Risk Level Distribution by Project Size',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    barmode='stack',
    plot_bgcolor='white',
    width=1400,
    height=550,
    font=dict(family='Arial'),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.05,
        xanchor='center',
        x=0.5,
        font=dict(family='Arial', size=11)
    ),
    margin=dict(t=130)
)

fig.show()

# %%
avg_cost_all = df_clean1.groupby('sector1')['totalcost_initial_adj'].mean()
avg_duration_all = df_clean1.groupby('sector1')['duration_years'].mean()
avg_delay_all = df_clean1.groupby('sector1')['delay'].mean()

sector_order = ['Energy', 'Transportation', 'Water']

fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=('Average Cost', 'Average Duration', 'Average Delay'),
    horizontal_spacing=0.12
)

fig.add_trace(
    go.Bar(
        x=sector_order,
        y=[avg_cost_all[sector] for sector in sector_order],
        marker=dict(
            color=[sector_colors.get(sector, '#95a5a6') for sector in sector_order],
            line=dict(color='black', width=1)
        ),
        text=[f'${avg_cost_all[sector]:.0f}M' for sector in sector_order],
        textposition='auto',
        textfont=dict(size=12, color='white', family='Arial'),
        opacity=0.8,
        showlegend=False
    ),
    row=1, col=1
)

fig.add_trace(
    go.Bar(
        x=sector_order,
        y=[avg_duration_all[sector] for sector in sector_order],
        marker=dict(
            color=[sector_colors.get(sector, '#95a5a6') for sector in sector_order],
            line=dict(color='black', width=1)
        ),
        text=[f'{avg_duration_all[sector]:.1f}y' for sector in sector_order],
        textposition='auto',
        textfont=dict(size=12, color='white', family='Arial'),
        opacity=0.8,
        showlegend=False
    ),
    row=1, col=2
)

fig.add_trace(
    go.Bar(
        x=sector_order,
        y=[avg_delay_all[sector] for sector in sector_order],
        marker=dict(
            color=[sector_colors.get(sector, '#95a5a6') for sector in sector_order],
            line=dict(color='black', width=1)
        ),
        text=[f'{avg_delay_all[sector]:.1f}y' for sector in sector_order],
        textposition='auto',
        textfont=dict(size=12, color='white', family='Arial'),
        opacity=0.8,
        showlegend=False
    ),
    row=1, col=3
)

fig.update_xaxes(title_text='Sector', tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=1)
fig.update_xaxes(title_text='Sector', tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=2)
fig.update_xaxes(title_text='Sector', tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=3)

fig.update_yaxes(title_text='Million USD', gridcolor='lightgray', gridwidth=0.5, tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=1)
fig.update_yaxes(title_text='Years', gridcolor='lightgray', gridwidth=0.5, tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=2)
fig.update_yaxes(title_text='Years', gridcolor='lightgray', gridwidth=0.5, tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=3)

fig.update_layout(
    title=dict(
        text='Project Metrics by Sector (All Projects)',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1400,
    height=500,
    font=dict(family='Arial')
)

fig.show()

# %% [markdown]
# ## Only with mega

# %%
df_clean1_mega = df_clean1[df_clean1['project_size'].isin(['mega'])].copy()
print(f"Total projects in df_clean1: {len(df_clean1)}")
print(f"Major and Mega projects only: {len(df_clean1_mega)}")
print(f"\nBreakdown:")
print(df_clean1_mega['project_size'].value_counts())

# %%
import plotly.graph_objects as go
from plotly.subplots import make_subplots
avg_cost = df_clean1_mega.groupby('sector1')['totalcost_initial_adj'].mean().sort_values(ascending=False)
avg_duration = df_clean1_mega.groupby('sector1')['duration_years'].mean().reindex(avg_cost.index)
avg_delay = df_clean1_mega.groupby('sector1')['delay'].mean().reindex(avg_cost.index)
fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=('Average Cost', 'Average Duration', 'Average Delay'),
    horizontal_spacing=0.12
)
fig.add_trace(
    go.Bar(
        x=avg_cost.index,
        y=avg_cost.values,
        marker=dict(
            color=[sector_colors.get(sector, '#95a5a6') for sector in avg_cost.index],
            line=dict(color='black', width=1)
        ),
        text=[f'${val:.0f}M' for val in avg_cost.values],
        textposition='auto',
        textfont=dict(size=12, color='white', family='Arial'),
        opacity=0.8,
        showlegend=False
    ),
    row=1, col=1
)
fig.add_trace(
    go.Bar(
        x=avg_duration.index,
        y=avg_duration.values,
        marker=dict(
            color=[sector_colors.get(sector, '#95a5a6') for sector in avg_duration.index],
            line=dict(color='black', width=1)
        ),
        text=[f'{val:.1f}y' for val in avg_duration.values],
        textposition='auto',
        textfont=dict(size=12, color='white', family='Arial'),
        opacity=0.8,
        showlegend=False
    ),
    row=1, col=2
)
fig.add_trace(
    go.Bar(
        x=avg_delay.index,
        y=avg_delay.values,
        marker=dict(
            color=[sector_colors.get(sector, '#95a5a6') for sector in avg_delay.index],
            line=dict(color='black', width=1)
        ),
        text=[f'{val:.1f}y' for val in avg_delay.values],
        textposition='auto',
        textfont=dict(size=12, color='white', family='Arial'),
        opacity=0.8,
        showlegend=False
    ),
    row=1, col=3
)
fig.update_xaxes(title_text='Sector', tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=1)
fig.update_xaxes(title_text='Sector', tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=2)
fig.update_xaxes(title_text='Sector', tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=3)
fig.update_yaxes(title_text='Million USD', gridcolor='lightgray', gridwidth=0.5, tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=1)
fig.update_yaxes(title_text='Years', gridcolor='lightgray', gridwidth=0.5, tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=2)
fig.update_yaxes(title_text='Years', gridcolor='lightgray', gridwidth=0.5, tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=3)
fig.update_layout(
    title=dict(
        text='Mega Project Metrics by Sector',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1400,
    height=500,
    font=dict(family='Arial')
)
fig.show()
# print("\nMega project metrics by sector:")
# for sector in avg_cost.index:
#     count = len(df_clean1_mega[df_clean1_mega['sector1'] == sector])
#     print(f"\n{sector} (n={count}):")
#     print(f"  Average Cost: ${avg_cost[sector]:.2f}M")
#     print(f"  Average Duration: {avg_duration[sector]:.2f} years")
#     print(f"  Average Delay: {avg_delay[sector]:.2f} years")

# %%
risk_categories = ['safe_env', 'safe_indigenous', 'safe_resettle']
risk_labels = ['Environmental', 'Indigenous Peoples', 'Resettlement']
risk_levels = ['A', 'B', 'C', 'D']
risk_colors = {'A': '#db4325', 'B': '#dea247', 'C': '#bbd4a6', 'D': '#57c4ad'}
fig = go.Figure()
for risk_level in risk_levels:
    level_data = []
    for sector in sectors:
        sector_data = df_clean1_mega_filtered[df_clean1_mega_filtered['sector1'] == sector]
        total_level_count = 0
        for risk_col in risk_categories:
            level_count = (sector_data[risk_col] == risk_level).sum()
            total_level_count += level_count
        total_possible = len(sector_data) * len(risk_categories)
        level_pct = (total_level_count / total_possible * 100)
        level_data.append(level_pct)
    fig.add_trace(go.Bar(
        x=sectors,
        y=level_data,
        name=f'Level {risk_level}',
        marker=dict(color=risk_colors[risk_level], line=dict(color='black', width=1)),
        text=[f'{val:.1f}%' if val > 5 else '' for val in level_data],
        textposition='inside',
        textfont=dict(size=11, color='white', family='Arial'),
        opacity=0.8
    ))
fig.update_layout(
    title=dict(
        text='Overall Risk Profile by Sector',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title=dict(text='Sector', font=dict(size=14, family='Arial', color='black')),
        tickfont=dict(family='Arial', size=12)
    ),
    yaxis=dict(
        title=dict(text='Percentage (%)', font=dict(size=14, family='Arial', color='black')),
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=12)
    ),
    plot_bgcolor='white',
    width=900,
    height=550,
    font=dict(family='Arial'),
    barmode='stack',
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5,
        font=dict(family='Arial', size=11),
        title=dict(text='Risk Level (A: Significant | B: Some | C: Minimal | D: No Impact)', font=dict(size=11, family='Arial')),
        traceorder='normal'
    ),
    margin=dict(t=130)
)
fig.show()
print("\nOverall risk profile summary:")
for sector in sectors:
    sector_data = df_clean1_mega_filtered[df_clean1_mega_filtered['sector1'] == sector]
    print(f"\n{sector} (n={len(sector_data)}):")
    for risk_level in risk_levels:
        total_count = sum((sector_data[risk_col] == risk_level).sum() for risk_col in risk_categories)
        total_possible = len(sector_data) * len(risk_categories)
        pct = (total_count / total_possible * 100)
        print(f"  Level {risk_level}: {total_count}/{total_possible} ({pct:.1f}%)")

# %%
for sector in sectors:
    sector_data = df_clean1_mega_filtered[df_clean1_mega_filtered['sector1'] == sector]
    mean_delay = sector_data['delay'].mean()
    median_delay = sector_data['delay'].median()
    std_delay = sector_data['delay'].std()
    max_delay = sector_data['delay'].max()
    min_delay = sector_data['delay'].min()
    count = len(sector_data)
    delayed_projects = (sector_data['delay'] > 0).sum()
    delayed_pct = (delayed_projects / count * 100)
    print(f"\n{sector} (n={count}):")
    print(f"  Mean delay: {mean_delay:.2f} years")
    print(f"  Median delay: {median_delay:.2f} years")
    print(f"  Std deviation: {std_delay:.2f} years")
    print(f"  Range: {min_delay:.2f} to {max_delay:.2f} years")
    print(f"  Projects with delay: {delayed_projects} ({delayed_pct:.1f}%)")

# %%
# Average delay by risk level
for risk_col, risk_label in zip(risk_categories, risk_labels):
    print(f"\n{risk_label}:")
    for risk_level in risk_levels:
        projects_with_level = df_clean1_mega_filtered[df_clean1_mega_filtered[risk_col] == risk_level]
        avg_delay = projects_with_level['delay'].mean()
        median_delay = projects_with_level['delay'].median()
        count = len(projects_with_level)
        print(f"  Level {risk_level} (n={count}): Mean delay = {avg_delay:.2f} years, Median = {median_delay:.2f} years")

# %%
fig = go.Figure()
for sector in sectors:
    sector_data = df_clean1_mega_filtered[df_clean1_mega_filtered['sector1'] == sector]
    fig.add_trace(go.Violin(
        y=sector_data['delay'],
        x=[sector] * len(sector_data),
        name=sector,
        box_visible=True,
        meanline_visible=True,
        points='all',
        pointpos=-0.5,
        jitter=0.3,
        marker=dict(color=sector_colors.get(sector, '#95a5a6')),
        scalemode='width',
        width=0.6,
        side='positive',
        line=dict(color=sector_colors.get(sector, '#95a5a6'), width=2)
    ))
fig.update_layout(
    title=dict(
        text='Project Delay Distribution by Sector',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title=dict(text='Sector', font=dict(size=14, family='Arial')),
        tickfont=dict(family='Arial', size=12)
    ),
    yaxis=dict(
        title=dict(text='Delay (years)', font=dict(size=14, family='Arial')),
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=12)
    ),
    plot_bgcolor='white',
    width=900,
    height=600,
    font=dict(family='Arial'),
    showlegend=False
)
fig.show()

# %%
fig = make_subplots(rows=1, cols=3, subplot_titles=[f'{label}' for label in risk_labels], horizontal_spacing=0.1)
for col_idx, (risk_col, risk_label) in enumerate(zip(risk_categories, risk_labels), 1):
    for risk_level in risk_levels:
        projects_with_level = df_clean1_mega_filtered[df_clean1_mega_filtered[risk_col] == risk_level]
        fig.add_trace(
            go.Violin(
                y=projects_with_level['delay'],
                x=[risk_level] * len(projects_with_level),
                name=f'Level {risk_level}',
                marker=dict(color=risk_colors[risk_level]),
                box_visible=True,
                meanline_visible=True,
                points='all',
                pointpos=-0.5,
                jitter=0.3,
                scalemode='width',
                width=0.6,
                side='positive',
                legendgroup=risk_level,
                showlegend=False
            ),
            row=1, col=col_idx
        )
    fig.update_yaxes(title_text='Delay (years)', row=1, col=col_idx, gridcolor='lightgray', gridwidth=0.5)
    fig.update_xaxes(title_text='Risk Level', row=1, col=col_idx, tickfont=dict(family='Arial', size=11))
fig.update_layout(
    title=dict(
        text='Project Delay Distribution by Risk Level',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1400,
    height=500,
    font=dict(family='Arial'),
    showlegend=False
)
fig.show()

# %%
heatmap_data = []
heatmap_text = []
for risk_col in risk_categories:
    row_data = []
    row_text = []
    for risk_level in risk_levels:
        projects = df_clean1_mega_filtered[df_clean1_mega_filtered[risk_col] == risk_level]
        avg_delay = projects['delay'].mean()
        count = len(projects)
        row_data.append(avg_delay)
        row_text.append(f'{avg_delay:.2f}y<br>(n={count})')
    heatmap_data.append(row_data)
    heatmap_text.append(row_text)
fig = go.Figure(data=go.Heatmap(
    z=heatmap_data,
    x=risk_levels,
    y=risk_labels,
    text=heatmap_text,
    texttemplate='%{text}',
    textfont=dict(size=12, family='Arial'),
    colorscale='Reds',
    colorbar=dict(title='Avg Delay<br>(years)')
))
fig.update_layout(
    title=dict(
        text='Average Project Delay by Risk Type and Level',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(title='Risk Level', tickfont=dict(family='Arial', size=12)),
    yaxis=dict(title='Risk Type', tickfont=dict(family='Arial', size=12)),
    width=800,
    height=500,
    font=dict(family='Arial')
)
fig.show()

# %%
print("\nEnvironmental safeguard vs Delay:")
env_delay = df_clean1.groupby('safe_env')['delay'].agg(['mean', 'median', 'count']).round(2)
print(env_delay)

fig5 = px.scatter(
    df_clean1,
    x='totalcost_initial_adj',
    y='delay',
    color='project_size',
    facet_col='safe_env',
    title='Delay vs Cost by Environmental Safeguard (colored by project size)',
    labels={'delay': 'Delay (years)', 'totalcost_initial_adj': 'Initial Cost (Millions)'},
    category_orders={'safe_env': ['A', 'B', 'C', 'D'], 'project_size': ['small', 'major', 'mega']},
    opacity=0.6
)
fig5.update_layout(height=600, width=1400)
fig5.show()

print("\nIndigenous safeguard vs Delay:")
indigenous_delay = df_clean1.groupby('safe_indigenous')['delay'].agg(['mean', 'median', 'count']).round(2)
print(indigenous_delay)

fig6 = px.scatter(
    df_clean1,
    x='totalcost_initial_adj',
    y='delay',
    color='project_size',
    facet_col='safe_indigenous',
    title='Delay vs Cost by Indigenous Safeguard (colored by project size)',
    labels={'delay': 'Delay (years)', 'totalcost_initial_adj': 'Initial Cost (Millions)'},
    category_orders={'safe_indigenous': ['A', 'B', 'C', 'D'], 'project_size': ['small', 'major', 'mega']},
    opacity=0.6
)
fig6.update_layout(height=600, width=1400)
fig6.show()

print("\nResettlement safeguard vs Delay:")
resettle_delay = df_clean1.groupby('safe_resettle')['delay'].agg(['mean', 'median', 'count']).round(2)
print(resettle_delay)

fig7 = px.scatter(
    df_clean1,
    x='totalcost_initial_adj',
    y='delay',
    color='project_size',
    facet_col='safe_resettle',
    title='Delay vs Cost by Resettlement Safeguard (colored by project size)',
    labels={'delay': 'Delay (years)', 'totalcost_initial_adj': 'Initial Cost (Millions)'},
    category_orders={'safe_resettle': ['A', 'B', 'C', 'D'], 'project_size': ['small', 'major', 'mega']},
    opacity=0.6
)
fig7.update_layout(height=600, width=1400)
fig7.show()


sector_delay = df_clean1.groupby('sector1')['delay'].agg(['mean', 'median', 'count']).round(2)
print(sector_delay)

fig8 = px.scatter(
    df_clean1,
    x='totalcost_initial_adj',
    y='delay',
    color='project_size',
    facet_col='sector1',
    title='Delay vs Cost by Sector (colored by project size)',
    labels={'delay': 'Delay (years)', 'totalcost_initial_adj': 'Initial Cost (Millions)'},
    category_orders={'project_size': ['small', 'major', 'mega']},
    opacity=0.6
)
fig8.update_layout(height=600, width=1400)
fig8.show()

# %%
df_clean1_mega = df_clean1[df_clean1['project_size'] == 'mega'].copy()

sector_delay = df_clean1_mega.groupby('sector1')['delay'].agg(['mean', 'median', 'count']).round(2)
print(sector_delay)

fig8 = px.scatter(
    df_clean1_mega,
    x='totalcost_initial_adj',
    y='delay',
    color='sector1',
    facet_col='sector1',
    title='Delay vs Cost for Mega Projects by Sector',
    labels={'delay': 'Delay (years)', 'totalcost_initial_adj': 'Initial Cost (Millions)'},
    opacity=0.6
)
fig8.update_layout(height=600, width=1400)
fig8.show()

# %%
#df_clean1_mega = df_clean1[df_clean1['project_size'] == 'mega'].copy()
risk_categories = ['safe_env', 'safe_indigenous', 'safe_resettle']
risk_labels = ['Environmental Risk', 'Indigenous Peoples Risk', 'Resettlement Risk']
risk_colors = {'A': '#db4325', 'B': '#dea247', 'C': '#bbd4a6', 'D': '#57c4ad', 'FI': '#95a5a6'}

for risk_col, risk_label in zip(risk_categories, risk_labels):
    print(f"\n{'='*80}")
    print(f"{risk_label.upper()}")
    print('='*80)
    
    risk_delay = df_clean1.groupby(['sector1', risk_col])['delay'].agg(['mean', 'median', 'count']).round(2)
    print(risk_delay)
    
    fig = px.scatter(
        df_clean1,
        x='totalcost_initial_adj',
        y='delay',
        color=risk_col,
        facet_col='sector1',
        title=f'Delay vs Cost for Mega Projects by {risk_label}',
        labels={'delay': 'Delay (years)', 'totalcost_initial_adj': 'Initial Cost (Millions)', risk_col: 'Risk Level'},
        category_orders={risk_col: ['A', 'B', 'C', 'D', 'FI']},
        color_discrete_map=risk_colors,
        opacity=0.7
    )
    fig.update_layout(height=600, width=1400, font=dict(family='Arial'))
    fig.show()

# %%
fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=risk_labels,
    horizontal_spacing=0.1
)

for col_idx, (risk_col, risk_label) in enumerate(zip(risk_categories, risk_labels), 1):
    df_filtered = df_clean1[~df_clean1[risk_col].isin(['FI'])].copy()
    df_filtered['risk_group'] = df_filtered[risk_col].apply(lambda x: 'D (No Impact)' if x == 'D' else 'A/B/C (Impact)')
    
    for group in ['D (No Impact)', 'A/B/C (Impact)']:
        group_data = df_filtered[df_filtered['risk_group'] == group]
        
        fig.add_trace(
            go.Box(
                y=group_data['delay'],
                name=group,
                boxmean='sd',
                marker=dict(color='#95a5a6' if group == 'D (No Impact)' else '#e74c3c'),
                showlegend=(col_idx == 1)
            ),
            row=1, col=col_idx
        )
    
    fig.update_xaxes(tickangle=-30, tickfont=dict(size=10), row=1, col=col_idx)
    fig.update_yaxes(title_text='Delay (years)', gridcolor='lightgray', row=1, col=col_idx)

fig.update_layout(
    title=dict(
        text='Delay Comparison: Level D vs Levels A/B/C',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1400,
    height=600,
    font=dict(family='Arial'),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.04,
        xanchor='center',
        x=0.5
    )
)

fig.show()

# %%
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page config
st.set_page_config(
    page_title="ADB Mega Projects Dashboard",
    page_icon="🏗️",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('mega_projects_rated.csv')

df_mega_rated = load_data()

# Title
st.title("🏗️ ADB Mega Projects Analysis Dashboard")
st.markdown("---")

# Load data (you'll need to pass df_mega_rated to this)
# For now, assuming df_mega_rated is already in memory
# In production, you'd load from CSV: df_mega_rated = pd.read_csv('mega_projects_rated.csv')

# Sidebar filters
st.sidebar.header("Filters")

# Sector filter
sectors = ['All'] + sorted(df_mega_rated['sector1'].unique().tolist())
selected_sector = st.sidebar.selectbox("Select Sector", sectors)

# Country filter
countries = ['All'] + sorted(df_mega_rated['countryshortname'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", countries)

# Time range filter
min_year = int(df_mega_rated['approvalyear'].min())
max_year = int(df_mega_rated['approvalyear'].max())
year_range = st.sidebar.slider("Approval Year Range", min_year, max_year, (min_year, max_year))

# Risk level filter
env_risks = ['All'] + sorted(df_mega_rated['safe_env'].dropna().unique().tolist())
selected_env_risk = st.sidebar.selectbox("Environmental Risk", env_risks)

# Apply filters
df_filtered = df_mega_rated.copy()

if selected_sector != 'All':
    df_filtered = df_filtered[df_filtered['sector1'] == selected_sector]

if selected_country != 'All':
    df_filtered = df_filtered[df_filtered['countryshortname'] == selected_country]

df_filtered = df_filtered[
    (df_filtered['approvalyear'] >= year_range[0]) & 
    (df_filtered['approvalyear'] <= year_range[1])
]

if selected_env_risk != 'All':
    df_filtered = df_filtered[df_filtered['safe_env'] == selected_env_risk]

# Display filter results
st.sidebar.markdown("---")
st.sidebar.metric("Filtered Projects", len(df_filtered))

# Main content
if len(df_filtered) == 0:
    st.warning("No projects match the selected filters. Please adjust your selection.")
else:
    # Overview metrics
    st.header("📊 Overview Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Projects", len(df_filtered))
    with col2:
        avg_cost = df_filtered['totalcost_initial_adj'].mean()
        st.metric("Avg Cost", f"${avg_cost:,.0f}M")
    with col3:
        avg_delay = df_filtered['delay'].mean()
        st.metric("Avg Delay", f"{avg_delay:.1f} yrs")
    with col4:
        avg_perf = df_filtered['ied_composite_score'].mean()
        st.metric("Avg Performance", f"{avg_perf:.2f}/4")
    with col5:
        avg_duration = df_filtered['duration_years'].mean()
        st.metric("Avg Duration", f"{avg_duration:.1f} yrs")
    
    st.markdown("---")
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Cost & Delay", 
        "🎯 Performance", 
        "⚠️ Safeguards", 
        "🌍 Geographic", 
        "📋 Data Table"
    ])
    
    # TAB 1: Cost & Delay
    with tab1:
        st.header("Cost and Delay Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Cost distribution by sector
            fig1 = px.box(
                df_filtered,
                x='sector1',
                y='totalcost_initial_adj',
                title='Cost Distribution by Sector',
                labels={'totalcost_initial_adj': 'Initial Cost (Millions)', 'sector1': 'Sector'},
                color='sector1',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig1.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Delay distribution by sector
            fig2 = px.box(
                df_filtered,
                x='sector1',
                y='delay',
                title='Delay Distribution by Sector',
                labels={'delay': 'Delay (years)', 'sector1': 'Sector'},
                color='sector1',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig2.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Cost vs Delay scatter
        fig3 = px.scatter(
            df_filtered,
            x='totalcost_initial_adj',
            y='delay',
            color='sector1',
            title='Cost vs Delay (by Sector)',
            labels={'totalcost_initial_adj': 'Initial Cost (Millions)', 'delay': 'Delay (years)'},
            hover_data=['projectid', 'countryshortname'],
            opacity=0.7,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    # TAB 2: Performance
    with tab2:
        st.header("Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Performance distribution
            fig4 = px.histogram(
                df_filtered,
                x='ied_composite_score',
                nbins=20,
                title='Performance Score Distribution',
                labels={'ied_composite_score': 'Composite Performance Score'},
                color_discrete_sequence=['#BAE1FF']
            )
            st.plotly_chart(fig4, use_container_width=True)
        
        with col2:
            # Performance by sector
            perf_by_sector = df_filtered.groupby('sector1')['ied_composite_score'].mean().reset_index()
            fig5 = px.bar(
                perf_by_sector,
                x='sector1',
                y='ied_composite_score',
                title='Average Performance by Sector',
                labels={'ied_composite_score': 'Avg Performance Score', 'sector1': 'Sector'},
                color='sector1',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig5.update_layout(showlegend=False)
            st.plotly_chart(fig5, use_container_width=True)
        
        # Delay vs Performance
        fig6 = px.scatter(
            df_filtered,
            x='ied_composite_score',
            y='delay',
            color='sector1',
            title='Performance vs Delay',
            labels={'ied_composite_score': 'Performance Score', 'delay': 'Delay (years)'},
            trendline='ols',
            opacity=0.7,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig6, use_container_width=True)
        
        # Performance dimensions breakdown
        st.subheader("Performance Dimensions Breakdown")
        perf_dims = df_filtered[[
            'ied_relevance_num', 'ied_effectiveness_num', 'ied_efficiency_num',
            'ied_sustainability_num', 'ied_borrower_performance_num',
            'ied_ea_performance_num', 'ied_adb_performance_num'
        ]].mean()
        
        fig7 = px.bar(
            x=perf_dims.index,
            y=perf_dims.values,
            title='Average Scores by Performance Dimension',
            labels={'x': 'Dimension', 'y': 'Average Score (1-4)'},
            color_discrete_sequence=['#BAFFC9']
        )
        fig7.update_xaxes(tickangle=45)
        st.plotly_chart(fig7, use_container_width=True)
    
    # TAB 3: Safeguards
    with tab3:
        st.header("Safeguards Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Environmental safeguard distribution
            env_dist = df_filtered['safe_env'].value_counts()
            fig8 = px.pie(
                values=env_dist.values,
                names=env_dist.index,
                title='Environmental Safeguard Distribution',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig8, use_container_width=True)
        
        with col2:
            # Indigenous safeguard distribution
            ind_dist = df_filtered['safe_indigenous'].value_counts()
            fig9 = px.pie(
                values=ind_dist.values,
                names=ind_dist.index,
                title='Indigenous Safeguard Distribution',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig9, use_container_width=True)
        
        with col3:
            # Resettlement safeguard distribution
            res_dist = df_filtered['safe_resettle'].value_counts()
            fig10 = px.pie(
                values=res_dist.values,
                names=res_dist.index,
                title='Resettlement Safeguard Distribution',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig10, use_container_width=True)
        
        # Safeguards vs Performance
        st.subheader("Safeguards vs Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig11 = px.box(
                df_filtered,
                x='safe_env',
                y='ied_composite_score',
                title='Performance by Environmental Risk',
                labels={'safe_env': 'Environmental Risk', 'ied_composite_score': 'Performance Score'},
                color='safe_env',
                category_orders={'safe_env': ['A', 'B', 'C', 'FI']},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig11.update_layout(showlegend=False)
            st.plotly_chart(fig11, use_container_width=True)
        
        with col2:
            fig12 = px.box(
                df_filtered,
                x='safe_env',
                y='delay',
                title='Delay by Environmental Risk',
                labels={'safe_env': 'Environmental Risk', 'delay': 'Delay (years)'},
                color='safe_env',
                category_orders={'safe_env': ['A', 'B', 'C', 'FI']},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig12.update_layout(showlegend=False)
            st.plotly_chart(fig12, use_container_width=True)
        
        # Sustainability by risk category
        st.subheader("Sustainability Performance by Risk Category")
        
        risk_sustain = df_filtered.groupby(['safe_env', 'safe_indigenous', 'safe_resettle'])['ied_sustainability_num'].mean().reset_index()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            env_sustain = df_filtered.groupby('safe_env')['ied_sustainability_num'].mean().reset_index()
            fig13 = px.bar(
                env_sustain,
                x='safe_env',
                y='ied_sustainability_num',
                title='Sustainability by Environmental Risk',
                labels={'safe_env': 'Env Risk', 'ied_sustainability_num': 'Avg Sustainability'},
                color='safe_env',
                category_orders={'safe_env': ['A', 'B', 'C', 'FI']},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig13.update_layout(showlegend=False)
            st.plotly_chart(fig13, use_container_width=True)
        
        with col2:
            ind_sustain = df_filtered.groupby('safe_indigenous')['ied_sustainability_num'].mean().reset_index()
            fig14 = px.bar(
                ind_sustain,
                x='safe_indigenous',
                y='ied_sustainability_num',
                title='Sustainability by Indigenous Risk',
                labels={'safe_indigenous': 'Indigenous Risk', 'ied_sustainability_num': 'Avg Sustainability'},
                color='safe_indigenous',
                category_orders={'safe_indigenous': ['A', 'B', 'C', 'FI']},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig14.update_layout(showlegend=False)
            st.plotly_chart(fig14, use_container_width=True)
        
        with col3:
            res_sustain = df_filtered.groupby('safe_resettle')['ied_sustainability_num'].mean().reset_index()
            fig15 = px.bar(
                res_sustain,
                x='safe_resettle',
                y='ied_sustainability_num',
                title='Sustainability by Resettlement Risk',
                labels={'safe_resettle': 'Resettle Risk', 'ied_sustainability_num': 'Avg Sustainability'},
                color='safe_resettle',
                category_orders={'safe_resettle': ['A', 'B', 'C', 'FI']},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig15.update_layout(showlegend=False)
            st.plotly_chart(fig15, use_container_width=True)
    
    # TAB 4: Geographic
    with tab4:
        st.header("Geographic Analysis")
        
        # Top countries by number of projects
        top_countries = df_filtered['countryshortname'].value_counts().head(10).reset_index()
        top_countries.columns = ['Country', 'Count']
        
        fig16 = px.bar(
            top_countries,
            x='Count',
            y='Country',
            orientation='h',
            title='Top 10 Countries by Number of Projects',
            color='Count',
            color_continuous_scale='Teal'
        )
        st.plotly_chart(fig16, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Performance by country (top 10)
            country_perf = df_filtered.groupby('countryshortname')['ied_composite_score'].mean().nlargest(10).reset_index()
            fig17 = px.bar(
                country_perf,
                x='ied_composite_score',
                y='countryshortname',
                orientation='h',
                title='Top 10 Countries by Performance',
                labels={'ied_composite_score': 'Avg Performance', 'countryshortname': 'Country'},
                color='ied_composite_score',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig17, use_container_width=True)
        
        with col2:
            # Delay by country (bottom 10 - least delay)
            country_delay = df_filtered.groupby('countryshortname')['delay'].mean().nsmallest(10).reset_index()
            fig18 = px.bar(
                country_delay,
                x='delay',
                y='countryshortname',
                orientation='h',
                title='Top 10 Countries with Least Delay',
                labels={'delay': 'Avg Delay (years)', 'countryshortname': 'Country'},
                color='delay',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig18, use_container_width=True)
        
        # Regional analysis
        st.subheader("Regional Analysis")
        
        region_stats = df_filtered.groupby('regionname').agg({
            'projectid': 'count',
            'totalcost_initial_adj': 'mean',
            'delay': 'mean',
            'ied_composite_score': 'mean'
        }).round(2).reset_index()
        region_stats.columns = ['Region', 'Count', 'Avg Cost ($M)', 'Avg Delay (yrs)', 'Avg Performance']
        
        st.dataframe(region_stats, use_container_width=True)
    
    # TAB 5: Data Table
    with tab5:
        st.header("Project Data")
        
        # Select columns to display
        display_cols = [
            'projectid', 'countryshortname', 'sector1', 'approvalyear', 'closingyear',
            'totalcost_initial_adj', 'delay', 'duration_years',
            'safe_env', 'safe_indigenous', 'safe_resettle',
            'ied_composite_score', 'ied_overall_rating', 'performance_category'
        ]
        
        df_display = df_filtered[display_cols].copy()
        df_display['totalcost_initial_adj'] = df_display['totalcost_initial_adj'].round(2)
        df_display['delay'] = df_display['delay'].round(2)
        df_display['ied_composite_score'] = df_display['ied_composite_score'].round(2)
        
        st.dataframe(df_display, use_container_width=True, height=600)
        
        # Download button
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="adb_mega_projects_filtered.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("**ADB Mega Projects Dashboard** | Data covers projects from {} to {}".format(
    int(df_mega_rated['approvalyear'].min()), 
    int(df_mega_rated['closingyear'].max())
))

# %%



