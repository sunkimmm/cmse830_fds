# %%
import os
import pandas as pd
import numpy as np
import matplotlib as plt
os.chdir('/Users/sjkimm/Library/CloudStorage/GoogleDrive-smrisgood@gmail.com/My Drive/School/Research/PM/ADB_re2')
print("Current working directory:", os.getcwd())

# %% [markdown]
# # 1. Merging Three Datasets

# %%
df_adb_1 = pd.read_csv('adb_sov_projects.csv')
df_adb_2 = pd.read_csv('adb_success_rate.csv')
df_region = pd.read_csv('adb_country_code.csv')

# %%
df_adb_1.info()

# %%
df_adb_2.info()

# %%
df_adb_2 = df_adb_2.merge(df_adb_1[['projectid_head', 'approvaldate', 'projectid']], on=['projectid_head', 'approvaldate'], how='left')

# %%
df_adb_2['projectid'].info()

# %%
df_adb_2['projectid'] = df_adb_2['projectid'].fillna(df_adb_2['projectid1'])
print(df_adb_2['projectid'].isna().sum())

# %%
# creating a long form
projectid_cols = ['projectid', 'projectid1', 'projectid2', 'projectid3', 'projectid4']
columns_to_keep = ['countrycode', 'region','closingdate_initial', 'closingdate_final', 'totalcost_initial', 'totalcost_final']

dfs_to_concat = []
for pid_col in projectid_cols:
    temp_df = df_adb_2[[pid_col] + columns_to_keep].copy()
    temp_df = temp_df.rename(columns={pid_col: 'projectid_match'})
    temp_df = temp_df.dropna(subset=['projectid_match'])  # Remove rows where this projectid column is null
    dfs_to_concat.append(temp_df)

df_adb_2_long = pd.concat(dfs_to_concat, ignore_index=True)
df_adb_2_long = df_adb_2_long.drop_duplicates(subset=['projectid_match'])
df_merged = df_adb_1.merge(
    df_adb_2_long,
    left_on='projectid',
    right_on='projectid_match',
    how='left'
)

df_merged['matchingresult'] = np.where(df_merged['projectid_match'].notna(), 'matched', 'unmatched')

df_merged = df_merged.drop('projectid_match', axis=1)
print(f"Total rows: {len(df_merged)}")
print(f"Matched: {(df_merged['matchingresult'] == 'matched').sum()}")
print(f"Unmatched: {(df_merged['matchingresult'] == 'unmatched').sum()}")

# %%
unmatched_mask = df_merged['matchingresult'] == 'unmatched'
unmatched_indices = df_merged[unmatched_mask].index
print(f"Starting unmatched count: {unmatched_mask.sum()}")
for idx in unmatched_indices:
    if df_merged.loc[idx, 'matchingresult'] == 'matched':
        continue  
    projectid_head = df_merged.loc[idx, 'projectid_head']
    projectname = df_merged.loc[idx, 'projectname']
    match = df_adb_2[
        (df_adb_2['projectid_head'] == projectid_head) & 
        (df_adb_2['projectname'] == projectname)
    ]
    if len(match) > 0:
        match_row = match.iloc[0]
        df_merged.loc[idx, 'countrycode'] = match_row['countrycode']
        df_merged.loc[idx, 'closingdate_initial'] = match_row['closingdate_initial']
        df_merged.loc[idx, 'closingdate_final'] = match_row['closingdate_final']
        df_merged.loc[idx, 'totalcost_initial'] = match_row['totalcost_initial']
        df_merged.loc[idx, 'totalcost_final'] = match_row['totalcost_final']
        df_merged.loc[idx, 'matchingresult'] = 'matched'
print(f"After projectid_head + projectname matching: {(df_merged['matchingresult'] == 'unmatched').sum()} unmatched")
unmatched_mask = df_merged['matchingresult'] == 'unmatched'
unmatched_indices = df_merged[unmatched_mask].index
for idx in unmatched_indices:
    projectid_head = df_merged.loc[idx, 'projectid_head']
    approvaldate = df_merged.loc[idx, 'approvaldate']
    match = df_adb_2[
        (df_adb_2['projectid_head'] == projectid_head) & 
        (df_adb_2['approvaldate'] == approvaldate)
    ]
    if len(match) > 0:
        match_row = match.iloc[0]
        df_merged.loc[idx, 'countrycode'] = match_row['countrycode']
        df_merged.loc[idx, 'closingdate_initial'] = match_row['closingdate_initial']
        df_merged.loc[idx, 'closingdate_final'] = match_row['closingdate_final']
        df_merged.loc[idx, 'totalcost_initial'] = match_row['totalcost_initial']
        df_merged.loc[idx, 'totalcost_final'] = match_row['totalcost_final']
        df_merged.loc[idx, 'matchingresult'] = 'matched'
print(f"\nFinal matching results:")
print(f"Matched: {(df_merged['matchingresult'] == 'matched').sum()}")
print(f"Unmatched: {(df_merged['matchingresult'] == 'unmatched').sum()}")

# %%
unmatched_rows = df_merged[df_merged['matchingresult'] == 'unmatched'].copy()
print(f"Total unmatched rows: {len(unmatched_rows)}")
print("\n" + "="*80)
print("\nSample of unmatched rows:")
print(unmatched_rows[['projectid_head', 'projectid', 'projectname', 'approvaldate']].head(10))
print("\n" + "="*80)
first_unmatched = unmatched_rows.iloc[0]
print(f"\nLooking at first unmatched row:")
print(f"projectid_head: {first_unmatched['projectid_head']}")
print(f"projectid: {first_unmatched['projectid']}")
print(f"projectname: {first_unmatched['projectname']}")
print(f"approvaldate: {first_unmatched['approvaldate']}")

print("\n" + "-"*80)
matching_head = df_adb_2[df_adb_2['projectid_head'] == first_unmatched['projectid_head']]
print(f"\nRows in df_adb_2 with same projectid_head: {len(matching_head)}")

if len(matching_head) > 0:
    print("\nThese rows have:")
    print(matching_head[['projectid_head', 'projectid', 'projectid1', 'projectname', 'approvaldate']].to_string())

print("\n" + "="*80)
unmatched_with_head_match = 0
unmatched_without_head_match = 0

for idx, row in unmatched_rows.iterrows():
    if len(df_adb_2[df_adb_2['projectid_head'] == row['projectid_head']]) > 0:
        unmatched_with_head_match += 1
    else:
        unmatched_without_head_match += 1

print(f"\nUnmatched rows WITH matching projectid_head in df_adb_2: {unmatched_with_head_match}")
print(f"Unmatched rows WITHOUT matching projectid_head in df_adb_2: {unmatched_without_head_match}")

print("\n" + "="*80)
print("\nOverall statistics:")
print(df_merged['matchingresult'].value_counts())

# %%
unmatched_rows = df_merged[df_merged['matchingresult'] == 'unmatched'].copy()
for i, (idx, row) in enumerate(unmatched_rows.iterrows()):
    if i >= 5:  # Just check first 5 for now
        break
    matching_in_adb2 = df_adb_2[df_adb_2['projectid_head'] == row['projectid_head']]
    if len(matching_in_adb2) > 0:
        print(f"\nCase {i+1}:")
        print(f"df_adb_1 row {idx}:")
        print(f"  projectid: '{row['projectid']}'")
        print(f"  projectname: '{row['projectname']}'")
        print(f"  approvaldate: '{row['approvaldate']}'")
        
        print(f"\ndf_adb_2 matching projectid_head:")
        for _, adb2_row in matching_in_adb2.iterrows():
            print(f"  projectid: '{adb2_row['projectid']}'")
            print(f"  projectid1: '{adb2_row['projectid1']}'")
            print(f"  projectid2: '{adb2_row['projectid2']}'")
            print(f"  projectid3: '{adb2_row['projectid3']}'")
            print(f"  projectid4: '{adb2_row['projectid4']}'")
            print(f"  projectname: '{adb2_row['projectname']}'")
            print(f"  approvaldate: '{adb2_row['approvaldate']}'")
        print("\n  Analysis:")
        adb2_row = matching_in_adb2.iloc[0]
        projectids_to_check = [adb2_row['projectid'], adb2_row['projectid1'], 
                               adb2_row['projectid2'], adb2_row['projectid3'], adb2_row['projectid4']]
        projectid_match = row['projectid'] in [str(x) for x in projectids_to_check if pd.notna(x)]
        print(f"    - projectid matches any column: {projectid_match}")
        projectname_match = row['projectname'] == adb2_row['projectname']
        print(f"    - projectname exact match: {projectname_match}")
        if not projectname_match:
            print(f"      df_adb_1: '{row['projectname']}'")
            print(f"      df_adb_2: '{adb2_row['projectname']}'")
        approvaldate_match = row['approvaldate'] == adb2_row['approvaldate']
        print(f"    - approvaldate exact match: {approvaldate_match}")
        if not approvaldate_match:
            print(f"      df_adb_1: '{row['approvaldate']}'")
            print(f"      df_adb_2: '{adb2_row['approvaldate']}'")
        
        print("-"*100)

# %%
from difflib import SequenceMatcher
def similarity_ratio(str1, str2):
    if pd.isna(str1) or pd.isna(str2):
        return 0
    return SequenceMatcher(None, str(str1).lower(), str(str2).lower()).ratio()
unmatched_mask = df_merged['matchingresult'] == 'unmatched'
unmatched_indices = df_merged[unmatched_mask].index

print(f"Starting fuzzy matching for {len(unmatched_indices)} unmatched rows...")
matched_count = 0

for idx in unmatched_indices:
    if df_merged.loc[idx, 'matchingresult'] == 'matched':
        continue
    projectid_head = df_merged.loc[idx, 'projectid_head']
    projectname = df_merged.loc[idx, 'projectname']
    potential_matches = df_adb_2[df_adb_2['projectid_head'] == projectid_head]
    
    if len(potential_matches) > 0:
        best_match_idx = None
        best_similarity = 0
        
        for _, match_row in potential_matches.iterrows():
            similarity = similarity_ratio(projectname, match_row['projectname'])
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_idx = match_row.name
        
        if best_similarity >= 0.80 and best_match_idx is not None: # If similarity is above threshold (n%), consider it a match
            match_row = df_adb_2.loc[best_match_idx]
            df_merged.loc[idx, 'countrycode'] = match_row['countrycode']
            df_merged.loc[idx, 'closingdate_initial'] = match_row['closingdate_initial']
            df_merged.loc[idx, 'closingdate_final'] = match_row['closingdate_final']
            df_merged.loc[idx, 'totalcost_initial'] = match_row['totalcost_initial']
            df_merged.loc[idx, 'totalcost_final'] = match_row['totalcost_final']
            df_merged.loc[idx, 'matchingresult'] = 'matched'
            matched_count += 1

print(f"Fuzzy matching found {matched_count} additional matches")
print(f"\nFinal matching results:")
print(f"Matched: {(df_merged['matchingresult'] == 'matched').sum()}")
print(f"Unmatched: {(df_merged['matchingresult'] == 'unmatched').sum()}")
remaining_unmatched = df_merged[df_merged['matchingresult'] == 'unmatched']
print(f"\nRemaining {len(remaining_unmatched)} unmatched rows:")
print(remaining_unmatched[['projectid_head', 'projectid', 'projectname', 'approvaldate']].head(10))

# %%
#remaining unmatched rows have ANY match in df_adb_2 by projectid_head
unmatched_rows = df_merged[df_merged['matchingresult'] == 'unmatched'].copy()
no_head_match = []
head_match_but_diff_name = []

for idx, row in unmatched_rows.iterrows():
    matching_in_adb2 = df_adb_2[df_adb_2['projectid_head'] == row['projectid_head']]
    
    if len(matching_in_adb2) == 0:
        no_head_match.append(idx)
    else:
        best_similarity = 0
        for _, adb2_row in matching_in_adb2.iterrows():
            similarity = similarity_ratio(row['projectname'], adb2_row['projectname'])
            best_similarity = max(best_similarity, similarity)
        
        head_match_but_diff_name.append((idx, row['projectid_head'], row['projectname'], best_similarity))

print(f"Rows with NO matching projectid_head in df_adb_2: {len(no_head_match)}")
print(f"Rows WITH matching projectid_head but project name < 80% similar: {len(head_match_but_diff_name)}")

print("\n" + "="*100)
print("\nSample of rows with matching projectid_head but low name similarity:")
print("(These might be different tranches/phases of projects)")
print("-"*100)

for i, (idx, head, name, sim) in enumerate(head_match_but_diff_name[:10]):
    print(f"\n{i+1}. Row {idx} (projectid_head: {head}, similarity: {sim:.2%})")
    print(f"   df_adb_1 name: {name}")
    
    matching = df_adb_2[df_adb_2['projectid_head'] == head]
    for _, m in matching.iterrows():
        print(f"   df_adb_2 name: {m['projectname']} (date: {m['approvaldate']})")

print("\n" + "="*100)
print(f"\nRows that have NO projectid_head match in df_adb_2: {len(no_head_match)}")
print("These projects simply don't exist in df_adb_2")

if len(no_head_match) > 0:
    print("\nSample of these rows:")
    print(df_merged.loc[no_head_match[:10], ['projectid_head', 'projectid', 'projectname', 'approvaldate']])

# %%
# Get the 96 unmatched rows with no projectid_head match
unmatched_rows = df_merged[df_merged['matchingresult'] == 'unmatched'].copy()
no_head_match_indices = []

for idx, row in unmatched_rows.iterrows():
    matching_in_adb2 = df_adb_2[df_adb_2['projectid_head'] == row['projectid_head']]
    if len(matching_in_adb2) == 0:
        no_head_match_indices.append(idx)

no_head_match_rows = df_merged.loc[no_head_match_indices]
print(f"Checking {len(no_head_match_rows)} rows with no projectid_head match...")
print("="*100)

# Extract the projectid_head values to search for
search_heads = set(no_head_match_rows['projectid_head'].astype(str))

# Search through df_adb_2's projectid1-4 columns
matches_found = []

for projectid_head in search_heads:
    # Get first 5 characters
    head_str = str(projectid_head)[:5] if len(str(projectid_head)) >= 5 else str(projectid_head)
    
    # Search in projectid1-4 columns
    for col in ['projectid1', 'projectid2', 'projectid3', 'projectid4']:
        matching_rows = df_adb_2[
            df_adb_2[col].notna() & 
            df_adb_2[col].astype(str).str[:5].eq(head_str)
        ]
        
        if len(matching_rows) > 0:
            matches_found.append({
                'projectid_head': projectid_head,
                'found_in_column': col,
                'num_matches': len(matching_rows),
                'sample_value': matching_rows[col].iloc[0]
            })

# Display results
if len(matches_found) > 0:
    print(f"\nFound {len(matches_found)} potential matches where first 5 chars match!\n")
    
    for i, match in enumerate(matches_found[:20], 1):  # Show first 20
        print(f"{i}. projectid_head {match['projectid_head']} found in df_adb_2['{match['found_in_column']}']")
        print(f"   ({match['num_matches']} matches, sample: {match['sample_value']})")
        
        # Show the actual rows from df_adb_1 with this projectid_head
        adb1_rows = no_head_match_rows[no_head_match_rows['projectid_head'] == match['projectid_head']]
        for _, row in adb1_rows.iterrows():
            print(f"   df_adb_1: {row['projectid']} - {row['projectname'][:60]}...")
        print()
else:
    print("\nNo matches found where first 5 characters match.")

print(f"\nSummary: {len(set([m['projectid_head'] for m in matches_found]))} unique projectid_heads have potential matches")

# %%
# try 75% threshold to catch borderline cases
unmatched_mask = df_merged['matchingresult'] == 'unmatched'
unmatched_indices = df_merged[unmatched_mask].index

print(f"Trying lower threshold (75%) for remaining unmatched rows...")
matched_count = 0
matched_details = []

for idx in unmatched_indices:
    if df_merged.loc[idx, 'matchingresult'] == 'matched':
        continue
    
    projectid_head = df_merged.loc[idx, 'projectid_head']
    projectname = df_merged.loc[idx, 'projectname']
    
    potential_matches = df_adb_2[df_adb_2['projectid_head'] == projectid_head]
    
    if len(potential_matches) > 0:
        best_match_idx = None
        best_similarity = 0
        
        for _, match_row in potential_matches.iterrows():
            similarity = similarity_ratio(projectname, match_row['projectname'])
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_idx = match_row.name
        
        if best_similarity >= 0.75 and best_match_idx is not None:
            match_row = df_adb_2.loc[best_match_idx]
            
            df_merged.loc[idx, 'countrycode'] = match_row['countrycode']
            df_merged.loc[idx, 'closingdate_initial'] = match_row['closingdate_initial']
            df_merged.loc[idx, 'closingdate_final'] = match_row['closingdate_final']
            df_merged.loc[idx, 'totalcost_initial'] = match_row['totalcost_initial']
            df_merged.loc[idx, 'totalcost_final'] = match_row['totalcost_final']
            df_merged.loc[idx, 'matchingresult'] = 'matched'
            matched_count += 1
            matched_details.append({
                'row_idx': idx,
                'projectid_head': projectid_head,
                'similarity': best_similarity,
                'df_adb_1_name': projectname,
                'df_adb_2_name': match_row['projectname']
            })

print(f"Lower threshold found {matched_count} additional matches\n")

if matched_count > 0:
    print("="*100)
    print("Newly matched rows:")
    print("="*100)
    for i, detail in enumerate(matched_details, 1):
        print(f"\n{i}. Row {detail['row_idx']} (projectid_head: {detail['projectid_head']}, similarity: {detail['similarity']:.2%})")
        print(f"   df_adb_1: {detail['df_adb_1_name']}")
        print(f"   df_adb_2: {detail['df_adb_2_name']}")
else:
    print("No additional matches found with 75% threshold")

print(f"\n{'='*100}")
print(f"Updated totals:")
print(f"Matched: {(df_merged['matchingresult'] == 'matched').sum()}")
print(f"Unmatched: {(df_merged['matchingresult'] == 'unmatched').sum()}")

# %%
# drop remaining unmatched
print(f"\nBefore dropping: {len(df_merged)} rows")
df_merged = df_merged[df_merged['matchingresult'] == 'matched'].copy()
print(f"After dropping: {len(df_merged)} rows")

# %%
df_merged.info()

# %%
print(f"Before filling:")
print(f"Total rows in df_merged: {len(df_merged)}")
print(f"Non-null region values: {df_merged['region'].notna().sum()}")
print(f"Null region values: {df_merged['region'].isna().sum()}")
region_mapping = df_region.set_index('ADB Country Code')['Subregion'].to_dict()
df_merged.loc[df_merged['region'].isna(), 'region'] = df_merged.loc[
    df_merged['region'].isna(), 'countrycode'
].map(region_mapping)
print(f"\nAfter filling:")
print(f"Non-null region values: {df_merged['region'].notna().sum()}")
print(f"Null region values: {df_merged['region'].isna().sum()}")
if df_merged['region'].isna().sum() > 0:
    print(f"\nRows with still-missing region:")
    missing_region = df_merged[df_merged['region'].isna()][['countrycode', 'countryname', 'projectname']].head(10)
    print(missing_region)

# %%
df_merged.to_csv('merged_matched_only.csv')

# %% [markdown]
# - For missing values in totalcost_initial and totalcost_final (41 rows), those were manually filled by looking at the Project Completion Reports provided by ADB for each project.
# - 31 cost information were available, and 10 were unavailable => dropped

# %%
df_filled = pd.read_csv('merged_matched_only_filled.csv')
df_filled.info()

# %%
df_filled['approvaldate'] = pd.to_datetime(df_filled['approvaldate'])
df_filled['closingdate_initial'] = pd.to_datetime(df_filled['closingdate_initial'])
df_filled['closingdate_final'] = pd.to_datetime(df_filled['closingdate_final'])
df_filled['duration_initial'] = (df_filled['closingdate_initial'] - df_filled['approvaldate']).dt.days / 365.25
df_filled['duration_final'] = (df_filled['closingdate_final'] - df_filled['approvaldate']).dt.days / 365.25
df_filled['delay'] = (df_filled['closingdate_final'] - df_filled['closingdate_initial']).dt.days / 365.25
df_filled['cost_overrun'] = df_filled['totalcost_final'] - df_filled['totalcost_initial']

print("Sample of calculated columns:")
print(df_filled[['projectid', 'duration_initial', 'duration_final', 'delay', 
                 'totalcost_initial', 'totalcost_final', 'cost_overrun']].head(10))

print("\nStatistics:")
print(f"\nDuration Initial (years):")
print(df_filled['duration_initial'].describe())
print(f"\nDuration Final (years):")
print(df_filled['duration_final'].describe())
print(f"\nDelay (years):")
print(df_filled['delay'].describe())
print(f"\nCost Overrun:")
print(df_filled['cost_overrun'].describe())

# %%
df_filled['cost_overrun_mark'] = df_filled['cost_overrun'] > 0
df_filled['delay_mark'] = df_filled['delay'] > 0
print("Sample of marked columns:")
print(df_filled[['projectid', 'cost_overrun', 'cost_overrun_mark', 'delay', 'delay_mark']].head(10))
print("\nSummary:")
print(f"Projects with cost overrun: {df_filled['cost_overrun_mark'].sum()} ({df_filled['cost_overrun_mark'].sum()/len(df_filled)*100:.1f}%)")
print(f"Projects with delays: {df_filled['delay_mark'].sum()} ({df_filled['delay_mark'].sum()/len(df_filled)*100:.1f}%)")
print(f"Projects with both: {((df_filled['cost_overrun_mark']) & (df_filled['delay_mark'])).sum()}")

# %%
df_filled['closingdate_final'] = pd.to_datetime(df_filled['closingdate_final'])
df_filled['closing_year'] = df_filled['closingdate_final'].dt.year
df_filled['beforecovid'] = df_filled['closing_year'] <= 2019
beforecovid_count = df_filled['beforecovid'].sum()
print(f"Projects closed before COVID (up to 2019): {beforecovid_count} ({beforecovid_count/len(df_filled)*100:.1f}%)")
print(f"Projects closed during/after COVID (2020+): {(~df_filled['beforecovid']).sum()} ({(~df_filled['beforecovid']).sum()/len(df_filled)*100:.1f}%)")
duration_over_2years = (df_filled['duration_final'] > 2).sum()
print(f"\nProjects with duration > 2 years: {duration_over_2years} ({duration_over_2years/len(df_filled)*100:.1f}%)")

print(f"\nDuration statistics:")
print(df_filled['duration_final'].describe())

# %%
# Find rows with negative duration
negative_duration = df_filled[df_filled['duration_final'] < 0]

print(f"Rows with negative duration: {len(negative_duration)}")

if len(negative_duration) > 0:
    print("\nDetails of rows with negative duration:")
    print(negative_duration[['projectid', 'projectname', 'approvaldate', 
                            'closingdate_final', 'duration_final']].to_string())

# %%
df_filled.loc[df_filled['projectid'] == '31280-013', 'closingdate_initial'] = '2018-03-31'
df_filled.loc[df_filled['projectid'] == '31280-013', 'closingdate_final'] = '2020-02-12'

df_filled.loc[df_filled['projectid'] == '41682-039', 'closingdate_initial'] = '2022-09-30'
df_filled.loc[df_filled['projectid'] == '41682-039', 'closingdate_final'] = '2023-05-10'

df_filled.loc[df_filled['projectid'] == '43141-043', 'closingdate_initial'] = '2017-12-31'
df_filled.loc[df_filled['projectid'] == '43141-043', 'closingdate_final'] = '2022-10-10'

df_filled.loc[df_filled['projectid'] == '43141-044', 'closingdate_initial'] = '2018-12-31'
df_filled.loc[df_filled['projectid'] == '43141-044', 'closingdate_final'] = '2022-04-27'

df_filled['closingdate_initial'] = pd.to_datetime(df_filled['closingdate_initial'])
df_filled['closingdate_final'] = pd.to_datetime(df_filled['closingdate_final'])
df_filled['approvaldate'] = pd.to_datetime(df_filled['approvaldate'])

df_filled['duration_initial'] = ((df_filled['closingdate_initial'] - df_filled['approvaldate']).dt.days / 365.25).round(1)
df_filled['duration_final'] = ((df_filled['closingdate_final'] - df_filled['approvaldate']).dt.days / 365.25).round(1)
df_filled['delay'] = ((df_filled['closingdate_final'] - df_filled['closingdate_initial']).dt.days / 365.25).round(1)
df_filled['delay_mark'] = df_filled['delay'] > 0

print("Updated rows:")
updated_ids = ['31280-013', '41682-039', '43141-044']
print(df_filled[df_filled['projectid'].isin(updated_ids)][
    ['projectid', 'approvaldate', 'closingdate_initial', 'closingdate_final', 
     'duration_initial', 'duration_final', 'delay']
].to_string())

print(f"\nRows with negative duration remaining: {(df_filled['duration_final'] < 0).sum()}")

# %%
print(f"Before filtering: {len(df_filled)} rows")
print(f"Projects with beforecovid=True: {df_filled['beforecovid'].sum()}")
print(f"Projects with duration_final > 2: {(df_filled['duration_final'] > 2).sum()}")

df_filled = df_filled[(df_filled['beforecovid'] == True) & (df_filled['duration_final'] > 2)].copy()

print(f"\nAfter filtering: {len(df_filled)} rows")
print(f"\nRemaining projects statistics:")
print(f"All have beforecovid=True: {df_filled['beforecovid'].all()}")
print(f"All have duration_final > 2: {(df_filled['duration_final'] > 2).all()}")
print(f"\nDuration range: {df_filled['duration_final'].min():.2f} to {df_filled['duration_final'].max():.2f} years")

# %%
df_filled.info()

# %%
df_filled.to_csv('adb_projects_clean.csv')

# %% [markdown]
# # 2. Preprocessing: Using extra 2 datasets from World Bank

# %%
df_project = pd.read_csv('adb_projects_clean.csv')
df_plr = pd.read_csv('WB_PLR.csv')
df_gdp = pd.read_csv('WB_GDPDeflator.csv')

# %%
df_project.info()

# %%
df_project = df_project.drop(['Unnamed: 0.1', 'Unnamed: 0', 'projectid_head', 'beforecovid'], axis=1)
print(f"Remaining columns: {len(df_project.columns)}")
print(f"\nDataFrame info:")
df_project.info()

# %%
import seaborn as sns

sns.heatmap(df_project.isna().transpose(), cmap='viridis')

# %%
print(f"Starting with: {len(df_project)} projects")
plr_countries = set(df_plr['countryname'].unique())
gdp_countries = set(df_gdp['countryname'].unique())
print(f"\nCountries in df_plr: {len(plr_countries)}")
print(f"Countries in df_gdp: {len(gdp_countries)}")
df_project_countries = set(df_project['countryname'].unique())
missing_in_plr = df_project_countries - plr_countries
missing_in_gdp = df_project_countries - gdp_countries
missing_in_either = missing_in_plr | missing_in_gdp
print(f"\nCountries in df_project missing from df_plr: {len(missing_in_plr)}")
if missing_in_plr:
    print(f"  {missing_in_plr}")
print(f"\nCountries in df_project missing from df_gdp: {len(missing_in_gdp)}")
if missing_in_gdp:
    print(f"  {missing_in_gdp}")
print(f"\nCountries missing from either df_plr OR df_gdp: {len(missing_in_either)}")
if missing_in_either:
    print(f"  {missing_in_either}")
df_project = df_project[
    (df_project['countryname'].isin(plr_countries)) & 
    (df_project['countryname'].isin(gdp_countries))
]
print(f"\nAfter dropping countries not in both df_plr and df_gdp: {len(df_project)} projects")
df_project = df_project.reset_index(drop=True)
print(f"Dataframe reset. Final shape: {df_project.shape}")

# %% [markdown]
# ## Cost Conversion (Appling Price Level Ratio & GDP Deflator in sequence)
# - For both initial cost and final cost

# %%
df_project['approvaldate'] = pd.to_datetime(df_project['approvaldate'])
df_project['approval_year'] = df_project['approvaldate'].dt.year
df_project['year_for_plr'] = df_project['approval_year'].astype(str)

df_project['totalcost_initial_adj1_plr'] = None

success_step1 = 0
failure_step1 = 0
failure_reasons = {}

for idx, row in df_project.iterrows():
    country = row['countryname'] 
    year = row['year_for_plr']
    initial_cost = row['totalcost_initial']
    plr_row = df_plr[df_plr['countryname'] == country]
    
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
        failure_reasons[idx] = 'PLR value is NaN'
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

print("\nSample results:")
print(df_project[['countryname', 'year_for_plr', 'totalcost_initial', 'totalcost_initial_adj1_plr']].head(10))

# %%
df_project['totalcost_initial_adj2_2019'] = None
failure_reasons_step2 = {}
success_step2 = 0
failure_step2 = 0

for idx, row in df_project.iterrows():
    if pd.isna(row['totalcost_initial_adj1_plr']):
        failure_reasons_step2[idx] = 'Step 1 failed (NA)'
        failure_step2 += 1
        continue
    
    country = row['countryname']
    year = row['year_for_plr']
    cost_adj1 = row['totalcost_initial_adj1_plr']
    gdp_row = df_gdp[df_gdp['countryname'] == country]
    
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

print(f"Successfully adjusted: {success_step2}")
print(f"Failed adjustments: {failure_step2}")

if failure_step2 > 0:
    print("\nFailure reasons:")
    from collections import Counter
    reason_counts = Counter(failure_reasons_step2.values())
    for reason, count in reason_counts.most_common():
        print(f"  {reason}: {count}")

print("\nSample results:")
print(df_project[['countryname', 'year_for_plr', 'totalcost_initial', 'totalcost_initial_adj1_plr', 'totalcost_initial_adj2_2019']].head(10))

print(f"\nTotal projects: {len(df_project)}")
print(f"Fully adjusted: {df_project['totalcost_initial_adj2_2019'].notna().sum()}")
print(f"Failed: {df_project['totalcost_initial_adj2_2019'].isna().sum()}")

# %%
from collections import Counter

df_project['year_for_closing'] = df_project['closing_year'].astype(int).astype(str)
df_project['totalcost_final_adj1_plr'] = None
failure_reasons_final_step1 = {}
success_step1 = 0
failure_step1 = 0

# PLR conversion
for idx, row in df_project.iterrows():
    country = row['countryname']
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
    
    plr_row = df_plr[df_plr['countryname'] == country]
    
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
        failure_reasons_final_step1[idx] = 'PLR value is NaN'
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

# GDP Deflator conversion
df_project['totalcost_final_adj2_2019'] = None
failure_reasons_final_step2 = {}
success_step2 = 0
failure_step2 = 0

for idx, row in df_project.iterrows():
    if pd.isna(row['totalcost_final_adj1_plr']):
        failure_reasons_final_step2[idx] = 'Step 1 failed (NA)'
        failure_step2 += 1
        continue
    
    country = row['countryname']
    year = row['year_for_closing']
    cost_adj1 = row['totalcost_final_adj1_plr']
    
    gdp_row = df_gdp[df_gdp['countryname'] == country]
    
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

print("\nSample results:")
print(df_project[['countryname', 'year_for_closing', 'totalcost_final', 'totalcost_final_adj1_plr', 'totalcost_final_adj2_2019']].head(10))

print(f"\nTotal projects: {len(df_project)}")
print(f"Fully adjusted final costs: {df_project['totalcost_final_adj2_2019'].notna().sum()}")
print(f"Failed: {df_project['totalcost_final_adj2_2019'].isna().sum()}")

# %%
# any outliers?
initial_adjustment_ratio = df_project['totalcost_initial_adj2_2019'] / df_project['totalcost_initial']
final_adjustment_ratio = df_project['totalcost_final_adj2_2019'] / df_project['totalcost_final']

print("\nAdjustment ratios calculated")
print(f"Valid initial ratios: {initial_adjustment_ratio.notna().sum()}")
print(f"Valid final ratios: {final_adjustment_ratio.notna().sum()}")

print("\nInitial Cost Adjustment Ratio:")
print(initial_adjustment_ratio.describe())

print("\nFinal Cost Adjustment Ratio:")
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

print(f"\nOutlier Detection (z-score threshold: {z_threshold})")

if is_outlier_initial_zscore.sum() > 0:
    print(f"\nInitial cost outliers: {is_outlier_initial_zscore.sum()}")
    outlier_indices = is_outlier_initial_zscore[is_outlier_initial_zscore].index
    outliers_df = df_project.loc[outlier_indices, ['projectid', 'countryname', 'approval_year', 'totalcost_initial', 'totalcost_initial_adj2_2019']].copy()
    outliers_df['initial_adjustment_ratio'] = initial_adjustment_ratio.loc[outlier_indices]
    outliers_df['initial_ratio_zscore'] = initial_ratio_zscore.loc[outlier_indices]
    outliers_df = outliers_df.sort_values('initial_ratio_zscore', ascending=False)
    print(outliers_df.to_string())
else:
    print("\nNo initial cost outliers detected")

if is_outlier_final_zscore.sum() > 0:
    print(f"\nFinal cost outliers: {is_outlier_final_zscore.sum()}")
    outlier_indices = is_outlier_final_zscore[is_outlier_final_zscore].index
    outliers_df = df_project.loc[outlier_indices, ['projectid', 'countryname', 'closing_year', 'totalcost_final', 'totalcost_final_adj2_2019']].copy()
    outliers_df['final_adjustment_ratio'] = final_adjustment_ratio.loc[outlier_indices]
    outliers_df['final_ratio_zscore'] = final_ratio_zscore.loc[outlier_indices]
    outliers_df = outliers_df.sort_values('final_ratio_zscore', ascending=False)
    print(outliers_df.to_string())
else:
    print("\nNo final cost outliers detected")

is_clean_adjustment = ~is_outlier_initial_zscore & ~is_outlier_final_zscore

print(f"\nTotal projects before outlier removal: {len(df_project)}")
print(f"Initial cost outliers: {is_outlier_initial_zscore.sum()}, Final cost outliers: {is_outlier_final_zscore.sum()}")
print(f"Total outliers to remove: {(is_outlier_initial_zscore | is_outlier_final_zscore).sum()}")

# Store original length for percentage calculation
original_length = len(df_project)

df_project = df_project[is_clean_adjustment]
df_project = df_project.reset_index(drop=True)

print(f"After removing outliers: {len(df_project)} projects")
print(f"Clean percentage: {len(df_project) / original_length * 100:.1f}%")

# %%
df_project.info()

# %%
# Check if all projects closed before 2020
all_before_2020 = (df_project['closing_year'] < 2020).all()
projects_before_2020 = (df_project['closing_year'] < 2020).sum()

print("="*80)
print("PROJECT CLOSING YEAR CHECK")
print("="*80)
print(f"Total projects: {len(df_project)}")
print(f"Projects closed before 2020: {projects_before_2020}")
print(f"All projects closed before 2020? {all_before_2020}")

if not all_before_2020:
    print("\nProjects closed in 2020 or later:")
    after_2020 = df_project[df_project['closing_year'] >= 2020]
    print(after_2020[['projectid', 'projectname', 'closing_year', 'closingdate_final']].to_string())
else:
    print("✓ All projects closed before 2020")

print("\n" + "="*80)
print("PROJECT DURATION CHECK")
print("="*80)

# Check if all projects have duration > 2 years
all_duration_over_2 = (df_project['duration_final'] > 2).all()
projects_over_2_years = (df_project['duration_final'] > 2).sum()

print(f"Projects with duration > 2 years: {projects_over_2_years}")
print(f"All projects have duration > 2 years? {all_duration_over_2}")

if not all_duration_over_2:
    print("\nProjects with duration ≤ 2 years:")
    under_2_years = df_project[df_project['duration_final'] <= 2]
    print(under_2_years[['projectid', 'projectname', 'duration_final', 'approvaldate', 'closingdate_final']].to_string())
else:
    print("✓ All projects have duration > 2 years")

print("\n" + "="*80)
print("DURATION STATISTICS")
print("="*80)
print(df_project['duration_final'].describe())
print(f"\nClosing year range: {df_project['closing_year'].min()} to {df_project['closing_year'].max()}")

# %%
df_project['totalcost_initial_adj'] = df_project['totalcost_initial_adj2_2019'].apply(
    lambda x: round(x, 2) if pd.notna(x) else None
)
df_project['totalcost_final_adj'] = df_project['totalcost_final_adj2_2019'].apply(
    lambda x: round(x, 2) if pd.notna(x) else None
)

# %%
def classify_project_size(cost):
    if pd.notna(cost):
        if cost >= 1_000:
            return 'mega'
        elif cost >= 500:
            return 'large'
        elif cost >= 100:
            return 'medium'
        else:
            return 'small'
    return None

df_project['project_size'] = df_project['totalcost_initial_adj'].apply(classify_project_size)

print("Project Size Distribution:")
print(df_project['project_size'].value_counts().sort_index())

print("\nSample of classified projects:")
print(df_project[['projectid', 'projectname', 'totalcost_initial_adj', 'project_size']].head(10))

print("\nCost ranges by size category:")
for size in ['small', 'medium', 'large', 'mega']:
    size_projects = df_project[df_project['project_size'] == size]
    if len(size_projects) > 0:
        print(f"\n{size.upper()}:")
        print(f"  Count: {len(size_projects)}")
        print(f"  Cost range: ${size_projects['totalcost_initial_adj'].min():.2f}M - ${size_projects['totalcost_initial_adj'].max():.2f}M")
        print(f"  Mean cost: ${size_projects['totalcost_initial_adj'].mean():.2f}M")

# %%
print(f"Before dropping small projects: {len(df_project)} projects")
df_project = df_project[df_project['project_size'] != 'small']
df_project = df_project.reset_index(drop=True)
print(f"After dropping small projects: {len(df_project)} projects")
print(f"\nRemaining project size distribution:")
print(df_project['project_size'].value_counts())

# %%
df_project.info()

# %%
negative_duration_initial = (df_project['duration_initial'] < 0).sum()
print(f"Number of rows with duration_initial < 0: {negative_duration_initial}")

# Show the rows if there are any
if negative_duration_initial > 0:
    print("\nRows with negative duration_initial:")
    print(df_project[df_project['duration_initial'] < 0][['projectid', 'approvaldate', 'closingdate_initial', 'duration_initial']])
else:
    print("No rows with negative duration_initial found")

# %%
df_project.info()

# %%
df_project['env_risk'] = df_project['safe_env'].isin(['A', 'B']).astype(int)
df_project['soc_risk'] = (
    (df_project['safe_ind'].isin(['A', 'B'])) | 
    (df_project['safe_res'].isin(['A', 'B']))
).astype(int)
print("Risk distribution:")
print(f"Projects with environmental risk: {df_project['env_risk'].sum()}")
print(f"Projects with social risk: {df_project['soc_risk'].sum()}")

# %%
def categorize_risk(row):
    if row['env_risk'] == 1 and row['soc_risk'] == 1:
        return 'Both'
    elif row['env_risk'] == 1:
        return 'Environmental Only'
    elif row['soc_risk'] == 1:
        return 'Social Only'
    else:
        return 'No Risk'

df_project['risk_category'] = df_project.apply(categorize_risk, axis=1)

print("\nRisk category distribution:")
print(df_project['risk_category'].value_counts())

# %%
df_project.to_csv('adb_projects_clean_final.csv')

# %% [markdown]
# # 3. IDA and EDA

# %%
import os
import pandas as pd
import numpy as np
import matplotlib as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from scipy import stats

# %%
df_project = pd.read_csv('adb_projects_clean_final.csv')

# %%
df_project.info()

# %%
country_total = df_project.groupby('countryname').agg({
    'projectid': 'count',
    'sector1': lambda x: ', '.join(x.value_counts().index[:3])
}).reset_index()
country_total.columns = ['countryname', 'total_projects', 'main_sectors']

country_avg_cost = df_project.groupby('countryname').agg({
    'projectid': 'count',
    'totalcost_initial_adj': 'mean',
    'sector1': lambda x: ', '.join(x.value_counts().index[:3])
}).reset_index()
country_avg_cost.columns = ['countryname', 'total_projects', 'avg_cost', 'main_sectors']

fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Number of Projects per Country', 'Average Project Cost per Country'),
    specs=[[{'type': 'choropleth'}, {'type': 'choropleth'}]],
    horizontal_spacing=0.01
)

fig.add_trace(
    go.Choropleth(
        locations=country_total['countryname'],
        locationmode='country names',
        z=country_total['total_projects'],
        customdata=country_total[['total_projects', 'main_sectors']],
        hovertemplate='<b>%{location}</b><br>Total Projects: %{customdata[0]}<br>Main Sectors: %{customdata[1]}<extra></extra>',
        colorscale='Pinkyl',
        colorbar=dict(x=0.4, y = 0.8, len=0.5, title='Projects'),
        showscale=True
    ),
    row=1, col=1
)

fig.add_trace(
    go.Choropleth(
        locations=country_avg_cost['countryname'],
        locationmode='country names',
        z=country_avg_cost['avg_cost'],
        customdata=country_avg_cost[['total_projects', 'avg_cost', 'main_sectors']],
        hovertemplate='<b>%{location}</b><br>Total Projects: %{customdata[0]}<br>Avg Cost: $%{customdata[1]:.2f}M<br>Main Sectors: %{customdata[2]}<extra></extra>',
        colorscale='Pinkyl',
        colorbar=dict(x=0.95, y = 0.8, len=0.5, title='Avg Cost (M USD)'),
        showscale=True
    ),
    row=1, col=2
)

fig.update_geos(
    scope='asia',
    projection_type='natural earth',
    showland=True,
    landcolor='rgb(243, 243, 243)',
    coastlinecolor='rgb(204, 204, 204)',
    showcountries=True,
    countrycolor='rgb(204, 204, 204)'
)

fig.update_layout(
    title_text='Geographic Distribution of Projects by Country',
    title_x=0.5,
    width=1600,
    height=600,
    font=dict(family='Arial'),
    showlegend=False
)

fig.show()

# print(f"\nCountries with most projects:")
# print(country_total.sort_values('total_projects', ascending=False)[['countryname', 'total_projects']].head(10).to_string(index=False))

# print(f"\nCountries with highest average project cost:")
# print(country_avg_cost.sort_values('avg_cost', ascending=False)[['countryname', 'total_projects', 'avg_cost']].head(10).to_string(index=False))


print(f"\nInsight: India has the greatest number of projects, but China has projects that have higher average cost per project.")

# %%
df_project['sector1'].unique()

# %%
# Check the distribution of sectors by country
sector_by_country = df_project.groupby(['countryname', 'sector1']).size().reset_index(name='count')
print("Sector distribution by country:")
print(sector_by_country.pivot(index='countryname', columns='sector1', values='count').fillna(0))

# Check which countries have Water as the dominant sector
water_dominant = df_project[df_project['sector1'] == 'Water'].groupby('countryname').size()
print("\nCountries with Water projects:")
print(water_dominant)

# Check if any country has Water as the most common sector
for country in df_project['countryname'].unique():
    country_sectors = df_project[df_project['countryname'] == country]['sector1']
    mode_sector = country_sectors.mode()[0] if len(country_sectors.mode()) > 0 else None
    if mode_sector == 'Water':
        print(f"{country}: Water is dominant")

# %%
sector_colors = {'Energy': '#d95f02', 'Transportation': '#57c4ad', 'Water': '#0571b0'}

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
    "Lao People's Democratic Republic": (19.8563, 102.4955),
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
    'Micronesia, Federated States of': (7.4256, 150.5508),
    'Nauru': (-0.5228, 166.9315),
    'Palau': (7.5150, 134.5825),
    'Papua New Guinea': (-6.3150, 143.9555),
    'Samoa': (-13.7590, -172.1046),
    'Solomon Islands': (-9.6457, 160.1562),
    'Tonga': (-21.1789, -175.1982),
    'Tuvalu': (-7.1095, 177.6493),
    'Vanuatu': (-15.3767, 166.9592)
}

country_data = df_project.groupby(['countryname']).agg({
    'projectid': 'count',
    'totalcost_initial_adj': 'sum',
    'sector1': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Mixed'
}).reset_index()
country_data.columns = ['country', 'project_count', 'total_cost', 'dominant_sector']

country_data['lat'] = country_data['country'].map(lambda x: country_coords.get(x, (None, None))[0])
country_data['lon'] = country_data['country'].map(lambda x: country_coords.get(x, (None, None))[1])
country_data = country_data.dropna(subset=['lat', 'lon'])

country_sector_data = df_project.groupby(['countryname', 'sector1']).agg({
    'projectid': 'count',
    'totalcost_initial_adj': 'sum'
}).reset_index()
country_sector_data.columns = ['country', 'sector', 'project_count', 'total_cost']

np.random.seed(114)
country_sector_data['lat'] = country_sector_data['country'].map(lambda x: country_coords.get(x, (None, None))[0])
country_sector_data['lon'] = country_sector_data['country'].map(lambda x: country_coords.get(x, (None, None))[1])
country_sector_data['lat'] = country_sector_data['lat'] + np.random.uniform(-0.3, 0.3, len(country_sector_data))
country_sector_data['lon'] = country_sector_data['lon'] + np.random.uniform(-0.3, 0.3, len(country_sector_data))
country_sector_data = country_sector_data.dropna(subset=['lat', 'lon'])

fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Dominant Sector by Country', 'All Sectors by Country'),
    specs=[[{'type': 'geo'}, {'type': 'geo'}]],
    horizontal_spacing=0.01
)

for sector in ['Energy', 'Transportation', 'Water']:
    sector_data = country_data[country_data['dominant_sector'] == sector]
    if len(sector_data) > 0:
        fig.add_trace(
            go.Scattergeo(
                lon=sector_data['lon'],
                lat=sector_data['lat'],
                mode='markers',
                marker=dict(
                    size=sector_data['project_count'],
                    sizemode='diameter',
                    sizeref=max(country_data['project_count']) / 50,
                    color=sector_colors[sector],
                    line=dict(width=0.5, color='white')
                ),
                name=sector,
                text=sector_data['country'],
                customdata=sector_data[['project_count', 'total_cost', 'dominant_sector']],
                hovertemplate='<b>%{text}</b><br>Projects: %{customdata[0]}<br>Total Cost: $%{customdata[1]:.2f}M<br>Dominant Sector: %{customdata[2]}<extra></extra>',
                showlegend=False,
                legendgroup=sector
            ),
            row=1, col=1
        )

for sector in ['Energy', 'Transportation', 'Water']:
    sector_data = country_sector_data[country_sector_data['sector'] == sector]
    if len(sector_data) > 0:
        fig.add_trace(
            go.Scattergeo(
                lon=sector_data['lon'],
                lat=sector_data['lat'],
                mode='markers',
                marker=dict(
                    size=sector_data['project_count'],
                    sizemode='diameter',
                    sizeref=max(country_sector_data['project_count']) / 40,
                    color=sector_colors[sector],
                    line=dict(width=0.5, color='white')
                ),
                name=sector,
                text=sector_data['country'],
                customdata=sector_data[['sector', 'project_count', 'total_cost']],
                hovertemplate='<b>%{text}</b><br>Sector: %{customdata[0]}<br>Projects: %{customdata[1]}<br>Total Cost: $%{customdata[2]:.2f}M<extra></extra>',
                showlegend=True,
                legendgroup=sector
            ),
            row=1, col=2
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
    title_text='Geographic Distribution of Projects',
    title_x=0.5,
    width=1600,
    height=600,
    font=dict(family='Arial'),
    legend=dict(
        x=0.45,
        y=0.5,
        xanchor='center',
        yanchor='middle',
        itemsizing='constant'  
    )
)

fig.show()

print(f"\nLeft map: {len(country_data)} countries, {country_data['project_count'].sum()} projects")
print(f"Right map: {len(country_sector_data)} bubbles, {country_sector_data['project_count'].sum()} projects")
print(f"\nProjects by sector:")
print(country_sector_data.groupby('sector')['project_count'].sum())

# %%
# Aggregate by country AND sector
country_sector_data = df_project.groupby(['countryname', 'sector1']).agg({
    'projectid': 'count',
    'totalcost_initial_adj': 'sum'
}).reset_index()
country_sector_data.columns = ['country', 'sector', 'project_count', 'total_cost']

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
    "Lao People's Democratic Republic": (19.8563, 102.4955),
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
    'Micronesia, Federated States of': (7.4256, 150.5508),
    'Nauru': (-0.5228, 166.9315),
    'Palau': (7.5150, 134.5825),
    'Papua New Guinea': (-6.3150, 143.9555),
    'Samoa': (-13.7590, -172.1046),
    'Solomon Islands': (-9.6457, 160.1562),
    'Tonga': (-21.1789, -175.1982),
    'Tuvalu': (-7.1095, 177.6493),
    'Vanuatu': (-15.3767, 166.9592)
}

# Add coordinates
np.random.seed(42)
country_sector_data['lat'] = country_sector_data['country'].map(lambda x: country_coords.get(x, (None, None))[0])
country_sector_data['lon'] = country_sector_data['country'].map(lambda x: country_coords.get(x, (None, None))[1])

# Add small random offset to prevent exact overlap
country_sector_data['lat'] = country_sector_data['lat'] + np.random.uniform(-0.3, 0.3, len(country_sector_data))
country_sector_data['lon'] = country_sector_data['lon'] + np.random.uniform(-0.3, 0.3, len(country_sector_data))

# Check for missing coordinates
missing_coords = country_sector_data[country_sector_data['lat'].isna()]
if len(missing_coords) > 0:
    print("Countries missing coordinates:")
    print(missing_coords['country'].unique().tolist())

country_sector_data = country_sector_data.dropna(subset=['lat', 'lon'])

fig = px.scatter_geo(
    country_sector_data,
    lat='lat',
    lon='lon',
    size='project_count',
    color='sector',
    hover_name='country',
    hover_data={
        'sector': True,
        'project_count': True, 
        'total_cost': ':.2f',
        'lat': False, 
        'lon': False
    },
    color_discrete_map=sector_colors,
    title='Geographic Distribution of Projects by Country and Sector',
    size_max=40,
    labels={'project_count': 'Projects', 'total_cost': 'Total Cost (M USD)', 'sector': 'Sector'}
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

print(f"\nTotal bubbles plotted: {len(country_sector_data)}")
print(f"\nProjects by sector:")
print(country_sector_data.groupby('sector')['project_count'].sum())

# %%
approval_distribution = df_project['approval_year'].value_counts().sort_index()
closing_distribution = df_project['closing_year'].value_counts().sort_index()

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
    barmode='overlay',
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
fig = make_subplots(
    rows=1, cols=2, 
    subplot_titles=('Projects by Sector', 'Projects by Region and Sector'), 
    horizontal_spacing=0.1
)

sector_order = ['Energy', 'Transportation', 'Water']
sector_counts = df_project['sector1'].value_counts()
sector_counts = sector_counts.reindex(sector_order, fill_value=0)

sector_colors = {
    'Energy': '#d95f02', 
    'Transportation': '#57c4ad', 
    'Water': '#0571b0'
}

# Add first subplot (Projects by Sector)
fig.add_trace(
    go.Bar(
        x=sector_counts.index,
        y=sector_counts.values,
        marker=dict(
            color=[sector_colors.get(sector, '#95a5a6') for sector in sector_counts.index], 
            line=dict(width=0)
        ),
        text=sector_counts.values,
        textposition='auto',
        textfont=dict(size=14, color='white', family='Arial'),
        showlegend=False
    ),
    row=1, col=1
)

# Add second subplot (Projects by Region and Sector)
region_counts = df_project['region'].value_counts().sort_values(ascending=False)
regions = region_counts.index

for sector in sector_order:
    sector_by_region = df_project[df_project['sector1'] == sector].groupby('region').size()
    sector_by_region = sector_by_region.reindex(regions, fill_value=0)
    
    fig.add_trace(
        go.Bar(
            x=regions,
            y=sector_by_region.values,
            name=sector,
            marker=dict(color=sector_colors[sector], line=dict(width=0)),
            showlegend=True,
            legendgroup='sector'
        ),
        row=1, col=2
    )

# Update axes
fig.update_xaxes(title_text='Sector', tickfont=dict(size=14), row=1, col=1)
fig.update_xaxes(title_text='Region', tickfont=dict(size=14), tickangle=-30, row=1, col=2)
fig.update_yaxes(title_text='Number of Projects', gridcolor='lightgray', row=1, col=1)
fig.update_yaxes(title_text='Number of Projects', gridcolor='lightgray', row=1, col=2)

# Update layout
fig.update_layout(
    title=dict(
        text='Distribution of Projects by Sector and Region',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1400,
    height=500,
    font=dict(family='Arial'),
    barmode='stack',
    legend=dict(
        title=dict(text='Sector'),
        x=1.0,
        y=0.95,
        xanchor='left'
    )
)

fig.show()

# %%
projects_by_year = df_project.groupby(['approval_year', 'sector1']).size().reset_index(name='count')
avg_cost_by_year = df_project.groupby(['approval_year', 'sector1'])['totalcost_initial_adj'].mean().reset_index(name='avg_cost')

fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Number of Projects Over Time by Sector', 'Average Project Cost Over Time by Sector'),
    horizontal_spacing=0.12
)

for sector in ['Energy', 'Transportation', 'Water']:
    sector_data = projects_by_year[projects_by_year['sector1'] == sector]
    fig.add_trace(
        go.Scatter(
            x=sector_data['approval_year'],
            y=sector_data['count'],
            mode='lines+markers',
            name=sector,
            line=dict(width=3, color=sector_colors.get(sector, '#95a5a6')),
            marker=dict(size=8, color=sector_colors.get(sector, '#95a5a6'), line=dict(width=0.5)),
            showlegend=True,
            legendgroup=sector
        ),
        row=1, col=1
    )

for sector in ['Energy', 'Transportation', 'Water']:
    sector_data = avg_cost_by_year[avg_cost_by_year['sector1'] == sector]
    fig.add_trace(
        go.Scatter(
            x=sector_data['approval_year'],
            y=sector_data['avg_cost'],
            mode='lines+markers',
            name=sector,
            line=dict(width=3, color=sector_colors.get(sector, '#95a5a6')),
            marker=dict(size=8, color=sector_colors.get(sector, '#95a5a6'), line=dict(width=0.5)),
            hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Avg Cost: $%{y:.2f}M<extra></extra>',
            showlegend=False,
            legendgroup=sector
        ),
        row=1, col=2
    )

fig.update_xaxes(
    title_text='Approval Year',
    tickmode='linear',
    dtick=2,
    tickfont=dict(family='Arial', size=12),
    row=1, col=1
)
fig.update_xaxes(
    title_text='Approval Year',
    tickmode='linear',
    dtick=2,
    tickfont=dict(family='Arial', size=12),
    row=1, col=2
)

fig.update_yaxes(
    title_text='Number of Projects',
    gridcolor='lightgray',
    gridwidth=0.5,
    tickfont=dict(family='Arial', size=12),
    row=1, col=1
)
fig.update_yaxes(
    title_text='Average Cost (Million USD, 2019)',
    gridcolor='lightgray',
    gridwidth=0.5,
    tickfont=dict(family='Arial', size=12),
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
        y=1.06,
        xanchor='center',
        x=0.5,
        font=dict(family='Arial', size=12)
    ),
    hovermode='x unified'
)
fig.show()

# %%
avg_cost = df_project.groupby('sector1')['totalcost_initial_adj'].mean().sort_values(ascending=False)
avg_duration = df_project.groupby('sector1')['duration_final'].mean().reindex(avg_cost.index)
avg_delay = df_project.groupby('sector1')['delay'].mean().reindex(avg_cost.index)

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
            line=dict(width=0)  # Removed border
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

fig.add_trace(
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

fig.update_xaxes(title_text='Sector', tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=1)
fig.update_xaxes(title_text='Sector', tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=2)
fig.update_xaxes(title_text='Sector', tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=3)

fig.update_yaxes(title_text='Million USD', gridcolor='lightgray', gridwidth=0.5, tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=1)
fig.update_yaxes(title_text='Years', gridcolor='lightgray', gridwidth=0.5, tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=2)
fig.update_yaxes(title_text='Years', gridcolor='lightgray', gridwidth=0.5, tickfont=dict(family='Arial', size=11), title_font=dict(size=12, family='Arial'), row=1, col=3)

fig.update_layout(
    title=dict(
        text='Project Metrics by Sector',
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

print("\nProject metrics by sector:")
for sector in avg_cost.index:
    count = len(df_project[df_project['sector1'] == sector])
    print(f"\n{sector} (n={count}):")
    print(f"  Average Cost: ${avg_cost[sector]:.2f}M")
    print(f"  Average Duration: {avg_duration[sector]:.2f} years")
    print(f"  Average Delay: {avg_delay[sector]:.2f} years")

# %%
df_project.info()

# %%
df_project['risk_category'].unique()

# %%
# Count projects in each risk category
risk_category_counts = df_project['risk_category'].value_counts()

print("Projects by risk category:")
print(risk_category_counts)
print(f"\nTotal projects: {len(df_project)}")

# With percentages
print("\nProjects by risk category (with percentages):")
for category, count in risk_category_counts.items():
    pct = (count / len(df_project) * 100)
    print(f"{category}: {count} ({pct:.1f}%)")

# If you want them in a specific order
category_order = ['No Risk', 'Environmental Only', 'Social Only', 'Both']
print("\nProjects by risk category (ordered):")
for category in category_order:
    count = (df_project['risk_category'] == category).sum()
    pct = (count / len(df_project) * 100)
    print(f"{category}: {count} ({pct:.1f}%)")

# %%
# Create ordinal risk level
def create_risk_level(category):
    if category == 'No Risk':
        return 0
    elif category in ['Environmental Only', 'Social Only']:
        return 1
    elif category == 'Both':
        return 2
    else:
        return None

df_project['risk_level'] = df_project['risk_category'].apply(create_risk_level)

# Verify the results
print("Risk level distribution:")
print(df_project['risk_level'].value_counts().sort_index())

print("\nRisk level with percentages:")
for level in [0, 1, 2]:
    count = (df_project['risk_level'] == level).sum()
    pct = (count / len(df_project) * 100)
    print(f"Level {level}: {count} ({pct:.1f}%)")

# Cross-check with risk_category
print("\nCross-tabulation:")
print(pd.crosstab(df_project['risk_category'], df_project['risk_level']))

# %%
sector_order = ['Energy', 'Transportation', 'Water']
sectors = [s for s in sector_order if s in df_project['sector1'].unique()]

risk_categories = ['env_risk', 'soc_risk', 'both']
risk_labels = {'env_risk': 'Environmental Risk', 'soc_risk': 'Social Risk', 'both': 'Both Risks'}
risk_colors_new = {'env_risk': '#1b9e77', 'soc_risk': '#e6ab02', 'both': '#a6761d'}

fig = go.Figure()

for risk_type in risk_categories:
    risk_data = []
    for sector in sectors:
        sector_data = df_project[df_project['sector1'] == sector]
        
        if risk_type == 'both':
            # Count projects with both risks
            risk_count = ((sector_data['env_risk'] == 1) & (sector_data['soc_risk'] == 1)).sum()
        else:
            # Count projects with this specific risk
            risk_count = sector_data[risk_type].sum()
        
        total_projects = len(sector_data)
        risk_pct = (risk_count / total_projects * 100) if total_projects > 0 else 0
        risk_data.append(risk_pct)
    
    fig.add_trace(go.Bar(
        x=sectors,
        y=risk_data,
        name=risk_labels[risk_type],
        marker=dict(color=risk_colors_new[risk_type], line=dict(width=0)),
        text=[f'{val:.1f}%' if val > 5 else '' for val in risk_data],
        textposition='inside',
        textfont=dict(size=13, color='white', family='Arial'),
        opacity=0.8
    ))

fig.update_layout(
    title=dict(
        text='Risk Profile by Sector',
        font=dict(size=16, family='Arial', color='black'),
        x=0.5,
        y=0.92,
        xanchor='center'
    ),
    xaxis=dict(
        title=dict(text='Sector', font=dict(size=14, family='Arial', color='black')),
        tickfont=dict(family='Arial', size=14)
    ),
    yaxis=dict(
        title=dict(text='Percentage of Projects (%)', font=dict(size=14, family='Arial', color='black')),
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=14)
    ),
    plot_bgcolor='white',
    width=900,
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
    ),
    margin=dict(t=100) 
)

fig.show()

print("\nRisk profile summary:")
for sector in sectors:
    sector_data = df_project[df_project['sector1'] == sector]
    print(f"\n{sector} (n={len(sector_data)}):")
    for risk_type in risk_categories:
        if risk_type == 'both':
            risk_count = ((sector_data['env_risk'] == 1) & (sector_data['soc_risk'] == 1)).sum()
        else:
            risk_count = sector_data[risk_type].sum()
        total_projects = len(sector_data)
        pct = (risk_count / total_projects * 100) if total_projects > 0 else 0
        print(f"  {risk_labels[risk_type]}: {risk_count}/{total_projects} ({pct:.1f}%)")

# %%
risk_levels = [0, 1, 2]
risk_level_labels = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}
sectors = ['Energy', 'Transportation', 'Water']
project_sizes = ['medium', 'large', 'mega']

# Heatmap 1: Risk Level × Sector (Duration)
heatmap_data_sector_duration = []
heatmap_text_sector_duration = []

for risk_level in risk_levels:
    row_data = []
    row_text = []
    for sector in sectors:
        projects = df_project[(df_project['risk_level'] == risk_level) & 
                              (df_project['sector1'] == sector)]
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
        projects = df_project[(df_project['risk_level'] == risk_level) & 
                              (df_project['sector1'] == sector)]
        avg_delay = projects['delay'].mean()
        count = len(projects)
        row_data.append(avg_delay if count > 0 else np.nan)
        row_text.append(f'{avg_delay:.2f}y<br>(n={count})' if count > 0 else 'N/A')
    heatmap_data_sector_delay.append(row_data)
    heatmap_text_sector_delay.append(row_text)

# Create subplots
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Average Duration by Risk Level and Sector',
                    'Average Delay by Risk Level and Sector'),
    horizontal_spacing=0.20,
    specs=[[{'type': 'heatmap'}, {'type': 'heatmap'}]]
)

# Add Duration heatmap
fig.add_trace(
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
fig.add_trace(
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
fig.update_xaxes(title='Sector', tickfont=dict(family='Arial', size=11), row=1, col=1)
fig.update_xaxes(title='Sector', tickfont=dict(family='Arial', size=11), row=1, col=2)
fig.update_yaxes(title='Risk Level', tickfont=dict(family='Arial', size=11), row=1, col=1)
fig.update_yaxes(title='Risk Level', tickfont=dict(family='Arial', size=11), row=1, col=2)

# Update layout
fig.update_layout(
    title=dict(
        text='Project Duration and Delay by Risk Level and Sector',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    width=1500,
    height=600,
    font=dict(family='Arial')
)

fig.show()

print("\nAverage duration by risk level and sector:")
for risk_level in risk_levels:
    print(f"\n{risk_level_labels[risk_level]} (Level {risk_level}):")
    for sector in sectors:
        projects = df_project[(df_project['risk_level'] == risk_level) & 
                              (df_project['sector1'] == sector)]
        if len(projects) > 0:
            print(f"  {sector}: Duration={projects['duration_final'].mean():.2f}y, Delay={projects['delay'].mean():.2f}y (n={len(projects)})")

print("\n" + "="*80)
print("\nOverall averages by risk level:")
for risk_level in risk_levels:
    projects = df_project[df_project['risk_level'] == risk_level]
    if len(projects) > 0:
        print(f"{risk_level_labels[risk_level]}: Duration={projects['duration_final'].mean():.2f}y, Delay={projects['delay'].mean():.2f}y (n={len(projects)})")

# %%
sector_colors = {'Energy': '#d95f02', 'Transportation': '#57c4ad', 'Water': '#0571b0'}
risk_colors = {'No Risk': '#fee5d9','Environmental Only': '#1b9e77','Social Only': '#e6ab02','Both': '#a6761d'}
risk_level_colors = {0: '#fcc5c0', 1: '#fa9fb5',2: '#c51b8a'}
risk_level_labels = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}

fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=('Duration vs Final Duration by Sector',
                    'Duration vs Final Duration by Risk Category',
                    'Duration vs Final Duration by Risk Level'),
    horizontal_spacing=0.10
)

# Subplot 1: By Sector
for sector in ['Energy', 'Transportation', 'Water']:
    sector_data = df_project[df_project['sector1'] == sector]
    fig.add_trace(
        go.Scatter(
            x=sector_data['duration_initial'],
            y=sector_data['duration_final'],
            mode='markers',
            name=sector,
            marker=dict(
                color=sector_colors[sector],
                size=8,
                opacity=0.6,
                line=dict(width=0.5, color='white')
            ),
            legendgroup='sector',
            legendgrouptitle_text='Sector',
            showlegend=True
        ),
        row=1, col=1
    )

# Subplot 2: By Risk Category
for risk_cat in ['No Risk', 'Environmental Only', 'Social Only', 'Both']:
    risk_data = df_project[df_project['risk_category'] == risk_cat]
    fig.add_trace(
        go.Scatter(
            x=risk_data['duration_initial'],
            y=risk_data['duration_final'],
            mode='markers',
            name=risk_cat,
            marker=dict(
                color=risk_colors[risk_cat],
                size=8,
                opacity=0.6,
                line=dict(width=0.5, color='white')
            ),
            legendgroup='risk_cat',
            legendgrouptitle_text='Risk Category',
            showlegend=True
        ),
        row=1, col=2
    )

# Subplot 3: By Risk Level
for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    fig.add_trace(
        go.Scatter(
            x=level_data['duration_initial'],
            y=level_data['duration_final'],
            mode='markers',
            name=risk_level_labels[risk_level],
            marker=dict(
                color=risk_level_colors[risk_level],
                size=8,
                opacity=0.6,
                line=dict(width=0.5, color='white')
            ),
            legendgroup='risk_level',
            legendgrouptitle_text='Risk Level',
            showlegend=True
        ),
        row=1, col=3
    )

# Add diagonal reference lines (y=x) to all subplots
for col in [1, 2, 3]:
    max_val = max(df_project['duration_initial'].max(), df_project['duration_final'].max())
    fig.add_trace(
        go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            line=dict(color='gray', width=1, dash='dash'),
            showlegend=False,
            hoverinfo='skip'
        ),
        row=1, col=col
    )

# Update axes
for col in [1, 2, 3]:
    fig.update_xaxes(
        title='Initial Duration (years)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=10),
        row=1, col=col
    )
    fig.update_yaxes(
        title='Final Duration (years)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=10),
        row=1, col=col
    )

# Update layout
fig.update_layout(
    title=dict(
        text='Initial vs Final Duration Comparison',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1800,
    height=650,
    font=dict(family='Arial'),
    legend=dict(
        orientation='h',  
        yanchor='bottom',
        y=-0.45,
        xanchor='center',
        x=0.5,
        font=dict(family='Arial', size=12),
        tracegroupgap=30  # Space between the three groups
    )
)

fig.show()

# %%
sector_colors = {'Energy': '#d95f02', 'Transportation': '#57c4ad', 'Water': '#0571b0'}
risk_colors = {'No Risk': '#fee5d9','Environmental Only': '#1b9e77','Social Only': '#e6ab02','Both': '#a6761d'}
risk_level_colors = {0: '#fcc5c0', 1: '#fa9fb5',2: '#c51b8a'}
risk_level_labels = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}

fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=('Initial Cost vs Delay by Sector',
                    'Initial Cost vs Delay by Risk Category',
                    'Initial Cost vs Delay by Risk Level'),
    horizontal_spacing=0.10
)

# Subplot 1: By Sector
for sector in ['Energy', 'Transportation', 'Water']:
    sector_data = df_project[df_project['sector1'] == sector]
    fig.add_trace(
        go.Scatter(
            x=sector_data['totalcost_initial_adj'],
            y=sector_data['delay'],
            mode='markers',
            name=sector,
            marker=dict(
                color=sector_colors[sector],
                size=8,
                opacity=0.6,
                line=dict(width=0.5, color='white')
            ),
            legendgroup='sector',
            legendgrouptitle_text='Sector',
            showlegend=True
        ),
        row=1, col=1
    )

# Subplot 2: By Risk Category
for risk_cat in ['No Risk', 'Environmental Only', 'Social Only', 'Both']:
    risk_data = df_project[df_project['risk_category'] == risk_cat]
    fig.add_trace(
        go.Scatter(
            x=risk_data['totalcost_initial_adj'],
            y=risk_data['delay'],
            mode='markers',
            name=risk_cat,
            marker=dict(
                color=risk_colors[risk_cat],
                size=8,
                opacity=0.6,
                line=dict(width=0.5, color='white')
            ),
            legendgroup='risk_cat',
            legendgrouptitle_text='Risk Category',
            showlegend=True
        ),
        row=1, col=2
    )

# Subplot 3: By Risk Level
for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    fig.add_trace(
        go.Scatter(
            x=level_data['totalcost_initial_adj'],
            y=level_data['delay'],
            mode='markers',
            name=risk_level_labels[risk_level],
            marker=dict(
                color=risk_level_colors[risk_level],
                size=8,
                opacity=0.6,
                line=dict(width=0.5, color='white')
            ),
            legendgroup='risk_level',
            legendgrouptitle_text='Risk Level',
            showlegend=True
        ),
        row=1, col=3
    )

# Add horizontal reference line at y=0 (no delay) to all subplots
for col in [1, 2, 3]:
    fig.add_trace(
        go.Scatter(
            x=[df_project['totalcost_initial_adj'].min(), df_project['totalcost_initial_adj'].max()],
            y=[0, 0],
            mode='lines',
            line=dict(color='gray', width=1, dash='dash'),
            showlegend=False,
            hoverinfo='skip'
        ),
        row=1, col=col
    )

# Update axes
for col in [1, 2, 3]:
    fig.update_xaxes(
        title='Initial Cost (Million USD, 2019)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=10),
        row=1, col=col
    )
    fig.update_yaxes(
        title='Delay (years)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=10),
        row=1, col=col
    )

# Update layout
fig.update_layout(
    title=dict(
        text='Initial Cost vs Project Delay Comparison',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1800,
    height=650,
    font=dict(family='Arial'),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=-0.45,
        xanchor='center',
        x=0.5,
        font=dict(family='Arial', size=10),
        tracegroupgap=30
    )
)

fig.show()

# %%
sector_colors = {'Energy': '#d95f02', 'Transportation': '#57c4ad', 'Water': '#0571b0'}
risk_colors = {'No Risk': '#fee5d9','Environmental Only': '#1b9e77','Social Only': '#e6ab02','Both': '#a6761d'}
risk_level_colors = {0: '#fcc5c0', 1: '#fa9fb5', 2: '#c51b8a'}
risk_level_labels = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}

fig = go.Figure()

# Add sector data
for sector in ['Energy', 'Transportation', 'Water']:
    sector_data = df_project[df_project['sector1'] == sector]
    fig.add_trace(
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

# Add risk category data
for risk_cat in ['No Risk', 'Environmental Only', 'Social Only', 'Both']:
    risk_data = df_project[df_project['risk_category'] == risk_cat]
    fig.add_trace(
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
            visible='legendonly'  # Hide by default
        )
    )

# Add risk level data
for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    fig.add_trace(
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
            visible='legendonly'  # Hide by default
        )
    )

# Add horizontal reference line at y=0
fig.add_trace(
    go.Scatter(
        x=[df_project['totalcost_initial_adj'].min(), df_project['totalcost_initial_adj'].max()],
        y=[0, 0],
        mode='lines',
        line=dict(color='gray', width=1, dash='dash'),
        showlegend=False,
        hoverinfo='skip'
    )
)

# Update layout
fig.update_layout(
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
    width=1200,
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

fig.show()

# %%
from scipy.stats import mannwhitneyu

sector_colors = {'Energy': '#d95f02', 'Transportation': '#57c4ad', 'Water': '#0571b0'}

# Summary statistics by sector
print("="*80)
print("SECTOR AND DELAY ANALYSIS")
print("="*80)

print("\nSUMMARY STATISTICS")
print("-" * 80)

for sector in ['Energy', 'Transportation', 'Water']:
    sector_data = df_project[df_project['sector1'] == sector]
    mean_delay = sector_data['delay'].mean()
    median_delay = sector_data['delay'].median()
    std_delay = sector_data['delay'].std()
    count = len(sector_data)
    delayed_projects = (sector_data['delay'] > 0).sum()
    delayed_pct = (delayed_projects / count * 100) if count > 0 else 0
    print(f"\n{sector.upper()} projects (n={count}):")
    print(f"  Mean delay: {mean_delay:.2f} years")
    print(f"  Median delay: {median_delay:.2f} years")
    print(f"  Std deviation: {std_delay:.2f} years")
    print(f"  Projects with delay: {delayed_projects} ({delayed_pct:.1f}%)")

# Kruskal-Wallis test
print("\n\nOVERALL TEST: Kruskal-Wallis")
print("-" * 80)

energy_delay = df_project[df_project['sector1'] == 'Energy']['delay'].dropna()
transport_delay = df_project[df_project['sector1'] == 'Transportation']['delay'].dropna()
water_delay = df_project[df_project['sector1'] == 'Water']['delay'].dropna()

h_stat, p_value = stats.kruskal(energy_delay, transport_delay, water_delay)
print(f"Kruskal-Wallis H-statistic: {h_stat:.3f}")
print(f"P-value: {p_value:.4f}")
if p_value < 0.05:
    print("→ Sectors have statistically significant differences in delay (p < 0.05)")
else:
    print("→ No significant difference in delays across sectors (p ≥ 0.05)")

# Pairwise comparisons
print("\n\nPAIRWISE COMPARISONS: Mann-Whitney U Test")
print("-" * 80)
print("(with Bonferroni correction for multiple comparisons)")

sector_pairs = [('Energy', 'Transportation'), ('Energy', 'Water'), ('Transportation', 'Water')]
alpha = 0.05
bonferroni_alpha = alpha / len(sector_pairs)
print(f"\nNumber of comparisons: {len(sector_pairs)}")
print(f"Adjusted significance level (Bonferroni): α = {bonferroni_alpha:.4f}\n")

for sector1, sector2 in sector_pairs:
    data1 = df_project[df_project['sector1'] == sector1]['delay'].dropna()
    data2 = df_project[df_project['sector1'] == sector2]['delay'].dropna()
    
    if len(data1) > 0 and len(data2) > 0:
        u_stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
        
        print(f"{sector1} vs {sector2}:")
        print(f"  Mann-Whitney U statistic: {u_stat:.3f}")
        print(f"  P-value: {p_value:.4f}")
        
        if p_value < bonferroni_alpha:
            print(f"  → Significant difference (p < {bonferroni_alpha:.4f})")
            if data1.median() > data2.median():
                print(f"     {sector1} has longer delays (median: {data1.median():.2f}y vs {data2.median():.2f}y)")
            else:
                print(f"     {sector2} has longer delays (median: {data2.median():.2f}y vs {data1.median():.2f}y)")
        else:
            print(f"  → No significant difference (p ≥ {bonferroni_alpha:.4f})")
        print()

# Violin plot
print("\n" + "="*80)
print("VISUALIZATION")
print("="*80 + "\n")

fig = go.Figure()

sector_order = ['Energy', 'Transportation', 'Water']

for sector in sector_order:
    sector_data = df_project[df_project['sector1'] == sector]
    fig.add_trace(go.Violin(
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
        line=dict(color=sector_colors[sector], width=2)
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
        tickfont=dict(family='Arial', size=12),
        categoryorder='array',
        categoryarray=sector_order
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
print("="*80)
print("SECTOR vs RISK CATEGORY ANALYSIS")
print("="*80)

# Cross-tabulation: Sector vs Risk Category
crosstab_risk_cat = pd.crosstab(df_project['sector1'], df_project['risk_category'], margins=True)
print("\nCross-tabulation: Sector vs Risk Category")
print(crosstab_risk_cat)

# Chi-square test for independence
contingency_table = pd.crosstab(df_project['sector1'], df_project['risk_category'])
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
print(f"\nCHI-SQUARE TEST: Sector vs Risk Category")
print(f"Chi-square statistic: {chi2:.3f}")
print(f"P-value: {p_value:.4f}")
print(f"Degrees of freedom: {dof}")
if p_value < 0.05:
    print("→ Sector and Risk Category are significantly associated")
else:
    print("→ No significant association between Sector and Risk Category")

# Percentage breakdown
print("\nPercentage breakdown by sector:")
for sector in ['Energy', 'Transportation', 'Water']:
    sector_data = df_project[df_project['sector1'] == sector]
    print(f"\n{sector} (n={len(sector_data)}):")
    for risk_cat in ['No Risk', 'Environmental Only', 'Social Only', 'Both']:
        count = (sector_data['risk_category'] == risk_cat).sum()
        pct = (count / len(sector_data) * 100) if len(sector_data) > 0 else 0
        print(f"  {risk_cat}: {count} ({pct:.1f}%)")

print("\n" + "="*80)
print("SECTOR vs RISK LEVEL ANALYSIS")
print("="*80)

# Cross-tabulation: Sector vs Risk Level
crosstab_risk_level = pd.crosstab(df_project['sector1'], df_project['risk_level'], margins=True)
print("\nCross-tabulation: Sector vs Risk Level")
print(crosstab_risk_level)

# Chi-square test for independence
contingency_table_level = pd.crosstab(df_project['sector1'], df_project['risk_level'])
chi2_level, p_value_level, dof_level, expected_level = stats.chi2_contingency(contingency_table_level)
print(f"\nCHI-SQUARE TEST: Sector vs Risk Level")
print(f"Chi-square statistic: {chi2_level:.3f}")
print(f"P-value: {p_value_level:.4f}")
print(f"Degrees of freedom: {dof_level}")
if p_value_level < 0.05:
    print("→ Sector and Risk Level are significantly associated")
else:
    print("→ No significant association between Sector and Risk Level")

# Percentage breakdown by risk level
print("\nPercentage breakdown by sector:")
for sector in ['Energy', 'Transportation', 'Water']:
    sector_data = df_project[df_project['sector1'] == sector]
    print(f"\n{sector} (n={len(sector_data)}):")
    for risk_level in [0, 1, 2]:
        count = (sector_data['risk_level'] == risk_level).sum()
        pct = (count / len(sector_data) * 100) if len(sector_data) > 0 else 0
        risk_label = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}[risk_level]
        print(f"  Level {risk_level} ({risk_label}): {count} ({pct:.1f}%)")

# Visualization 1: Stacked bar chart - Sector vs Risk Category
fig1 = go.Figure()

for risk_cat in ['No Risk', 'Environmental Only', 'Social Only', 'Both']:
    risk_counts = []
    for sector in ['Energy', 'Transportation', 'Water']:
        sector_data = df_project[df_project['sector1'] == sector]
        count = (sector_data['risk_category'] == risk_cat).sum()
        pct = (count / len(sector_data) * 100) if len(sector_data) > 0 else 0
        risk_counts.append(pct)
    
    fig1.add_trace(go.Bar(
        x=['Energy', 'Transportation', 'Water'],
        y=risk_counts,
        name=risk_cat,
        marker=dict(color=risk_colors[risk_cat], line=dict(width=0)),
        text=[f'{val:.1f}%' if val > 5 else '' for val in risk_counts],
        textposition='inside',
        textfont=dict(size=11, color='white', family='Arial')
    ))

fig1.update_layout(
    title=dict(
        text='Risk Category Distribution by Sector',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title='Sector',
        tickfont=dict(family='Arial', size=12)
    ),
    yaxis=dict(
        title='Percentage (%)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=12)
    ),
    barmode='stack',
    plot_bgcolor='white',
    width=900,
    height=600,
    font=dict(family='Arial'),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5,
        font=dict(family='Arial', size=11)
    )
)

fig1.show()

# Visualization 2: Stacked bar chart - Sector vs Risk Level
risk_level_colors_viz = {0: '#fcc5c0', 1: '#fa9fb5', 2: '#c51b8a'}
risk_level_labels = {0: 'No Risk (0)', 1: 'Single Risk (1)', 2: 'Both Risks (2)'}

fig2 = go.Figure()

for risk_level in [0, 1, 2]:
    risk_counts = []
    for sector in ['Energy', 'Transportation', 'Water']:
        sector_data = df_project[df_project['sector1'] == sector]
        count = (sector_data['risk_level'] == risk_level).sum()
        pct = (count / len(sector_data) * 100) if len(sector_data) > 0 else 0
        risk_counts.append(pct)
    
    fig2.add_trace(go.Bar(
        x=['Energy', 'Transportation', 'Water'],
        y=risk_counts,
        name=risk_level_labels[risk_level],
        marker=dict(color=risk_level_colors_viz[risk_level], line=dict(width=0)),
        text=[f'{val:.1f}%' if val > 5 else '' for val in risk_counts],
        textposition='inside',
        textfont=dict(size=11, color='white', family='Arial')
    ))

fig2.update_layout(
    title=dict(
        text='Risk Level Distribution by Sector',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title='Sector',
        tickfont=dict(family='Arial', size=12)
    ),
    yaxis=dict(
        title='Percentage (%)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=12)
    ),
    barmode='stack',
    plot_bgcolor='white',
    width=900,
    height=600,
    font=dict(family='Arial'),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5,
        font=dict(family='Arial', size=11)
    )
)

fig2.show()

# %%
size_colors = {'medium': '#dfe318', 'large': '#8bd646', 'mega': '#2fb47c'}

for size in ['medium', 'large', 'mega']:
    size_data = df_project[df_project['project_size'] == size]
    mean_delay = size_data['delay'].mean()
    median_delay = size_data['delay'].median()
    std_delay = size_data['delay'].std()
    count = len(size_data)
    delayed_projects = (size_data['delay'] > 0).sum()
    delayed_pct = (delayed_projects / count * 100) if count > 0 else 0
    print(f"\n{size.upper()} projects (n={count}):")
    print(f"  Mean delay: {mean_delay:.2f} years")
    print(f"  Median delay: {median_delay:.2f} years")
    print(f"  Std deviation: {std_delay:.2f} years")
    print(f"  Projects with delay: {delayed_projects} ({delayed_pct:.1f}%)")

# Kruskal-Wallis test (non-parametric alternative to ANOVA)
print("\n\nOVERALL TEST: Kruskal-Wallis")
print("-" * 80)

medium_delay = df_project[df_project['project_size'] == 'medium']['delay'].dropna()
large_delay = df_project[df_project['project_size'] == 'large']['delay'].dropna()
mega_delay = df_project[df_project['project_size'] == 'mega']['delay'].dropna()

h_stat, p_value = stats.kruskal(medium_delay, large_delay, mega_delay)
print(f"Kruskal-Wallis H-statistic: {h_stat:.3f}")
print(f"P-value: {p_value:.4f}")
if p_value < 0.05:
    print("→ Project sizes have statistically significant differences in delay (p < 0.05)")
else:
    print("→ No significant difference in delays across project sizes (p ≥ 0.05)")

# Pairwise comparisons
print("\n\nPAIRWISE COMPARISONS: Mann-Whitney U Test")
print("-" * 80)
print("(with Bonferroni correction for multiple comparisons)")

size_pairs = [('medium', 'large'), ('medium', 'mega'), ('large', 'mega')]
alpha = 0.05
bonferroni_alpha = alpha / len(size_pairs)
print(f"\nNumber of comparisons: {len(size_pairs)}")
print(f"Adjusted significance level (Bonferroni): α = {bonferroni_alpha:.4f}\n")

for size1, size2 in size_pairs:
    data1 = df_project[df_project['project_size'] == size1]['delay'].dropna()
    data2 = df_project[df_project['project_size'] == size2]['delay'].dropna()
    
    if len(data1) > 0 and len(data2) > 0:
        u_stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
        
        print(f"{size1.capitalize()} vs {size2.capitalize()}:")
        print(f"  Mann-Whitney U statistic: {u_stat:.3f}")
        print(f"  P-value: {p_value:.4f}")
        
        if p_value < bonferroni_alpha:
            print(f"  → Significant difference (p < {bonferroni_alpha:.4f})")
            if data1.median() > data2.median():
                print(f"     {size1.capitalize()} has longer delays (median: {data1.median():.2f}y vs {data2.median():.2f}y)")
            else:
                print(f"     {size2.capitalize()} has longer delays (median: {data2.median():.2f}y vs {data1.median():.2f}y)")
        else:
            print(f"  → No significant difference (p ≥ {bonferroni_alpha:.4f})")
        print()

# Spearman correlation (trend analysis)
print("\nTREND ANALYSIS: Spearman Correlation")
print("-" * 80)

size_numeric = []
delay_values = []
size_map = {'medium': 1, 'large': 2, 'mega': 3}

for size in ['medium', 'large', 'mega']:
    size_data = df_project[df_project['project_size'] == size]
    delays = size_data['delay'].dropna()
    size_numeric.extend([size_map[size]] * len(delays))
    delay_values.extend(delays.values)

if len(size_numeric) > 0:
    corr, corr_p = stats.spearmanr(size_numeric, delay_values)
    print(f"Spearman correlation coefficient: {corr:.3f}")
    print(f"P-value: {corr_p:.4f}")
    
    if corr_p < 0.05:
        if corr > 0:
            print(f"→ Significant positive correlation: Larger projects associated with longer delays")
        elif corr < 0:
            print(f"→ Significant negative correlation: Larger projects associated with shorter delays")
    else:
        print(f"→ No significant correlation between project size and delay")

# Violin plot
print("\n" + "="*80)
print("VISUALIZATION")
print("="*80 + "\n")

fig = go.Figure()

size_order = ['medium', 'large', 'mega']
for size in size_order:
    size_data = df_project[df_project['project_size'] == size]
    fig.add_trace(go.Violin(
        y=size_data['delay'],
        x=[size] * len(size_data),
        name=size.capitalize(),
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
        text='Project Delay Distribution by Project Size<br><sub>Medium: $100M-500M | Large: $500M-1B | Mega: ≥$1B</sub>',
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
risk_category_colors = {
    'No Risk': '#fee5d9',
    'Environmental Only': '#1b9e77',
    'Social Only': '#e6ab02',
    'Both': '#a6761d'
}

risk_level_colors = {
    0: '#fcc5c0',
    1: '#fa9fb5',
    2: '#c51b8a'
}

risk_level_labels = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}

# Create subplots
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=['Delay by Risk Category', 'Delay by Risk Level'],
    horizontal_spacing=0.12
)

# Subplot 1: By Risk Category
risk_category_order = ['No Risk', 'Environmental Only', 'Social Only', 'Both']
for risk_cat in risk_category_order:
    risk_data = df_project[df_project['risk_category'] == risk_cat]
    
    fig.add_trace(
        go.Violin(
            y=risk_data['delay'],
            x=[risk_cat] * len(risk_data),
            name=risk_cat,
            box_visible=True,
            meanline_visible=True,
            points='all',
            pointpos=-0.5,
            jitter=0.3,
            marker=dict(color=risk_category_colors[risk_cat]),
            scalemode='width',
            width=0.6,
            side='positive',
            line=dict(color=risk_category_colors[risk_cat], width=2),
            showlegend=False
        ),
        row=1, col=1
    )

# Subplot 2: By Risk Level
for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    
    fig.add_trace(
        go.Violin(
            y=level_data['delay'],
            x=[risk_level_labels[risk_level]] * len(level_data),
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

# Update layout
fig.update_layout(
    title=dict(
        text='Project Delay Distribution by Risk Category and Level',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1400,
    height=600,
    font=dict(family='Arial')
)

# Update x-axes
fig.update_xaxes(
    title_text='Risk Category',
    title_font=dict(size=14, family='Arial'),
    tickfont=dict(family='Arial', size=11),
    tickangle=-30,
    categoryorder='array',
    categoryarray=risk_category_order,
    row=1, col=1
)

fig.update_xaxes(
    title_text='Risk Level',
    title_font=dict(size=14, family='Arial'),
    tickfont=dict(family='Arial', size=11),
    categoryorder='array',
    categoryarray=[risk_level_labels[0], risk_level_labels[1], risk_level_labels[2]],
    row=1, col=2
)

# Update y-axes
fig.update_yaxes(
    title_text='Delay (years)',
    title_font=dict(size=14, family='Arial'),
    gridcolor='lightgray',
    gridwidth=0.5,
    tickfont=dict(family='Arial', size=12),
    row=1, col=1
)

fig.update_yaxes(
    title_text='Delay (years)',
    title_font=dict(size=14, family='Arial'),
    gridcolor='lightgray',
    gridwidth=0.5,
    tickfont=dict(family='Arial', size=12),
    row=1, col=2
)

fig.show()

# Statistical Analysis
print("="*80)
print("STATISTICAL ANALYSIS: Risk and Project Delays")
print("="*80)

# ============================================================================
# PART 1: RISK CATEGORY ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("PART 1: RISK CATEGORY ANALYSIS")
print("="*80)

# Summary statistics
print("\nSUMMARY STATISTICS")
print("-" * 80)

for risk_cat in risk_category_order:
    risk_data = df_project[df_project['risk_category'] == risk_cat]
    delay_data = risk_data['delay'].dropna()
    print(f"\n{risk_cat}:")
    print(f"  n={len(delay_data)}")
    print(f"  mean={delay_data.mean():.2f} years")
    print(f"  median={delay_data.median():.2f} years")
    print(f"  std={delay_data.std():.2f} years")

# Kruskal-Wallis test for risk categories
print("\n\nOVERALL TEST: Kruskal-Wallis")
print("-" * 80)

delay_groups_cat = []
for risk_cat in risk_category_order:
    risk_data = df_project[df_project['risk_category'] == risk_cat]
    delay_groups_cat.append(risk_data['delay'].dropna())

if all(len(group) > 0 for group in delay_groups_cat):
    h_stat, p_value = stats.kruskal(*delay_groups_cat)
    print(f"Kruskal-Wallis H-statistic: {h_stat:.3f}")
    print(f"P-value: {p_value:.4f}")
    if p_value < 0.05:
        print(f"→ Delays are significantly different across risk categories (p < 0.05)")
    else:
        print(f"→ No significant difference in delays across risk categories (p ≥ 0.05)")

# Pairwise comparisons for risk categories
print("\n\nPAIRWISE COMPARISONS: Mann-Whitney U Test")
print("-" * 80)
print("(with Bonferroni correction for multiple comparisons)")

# All possible pairs
cat_pairs = []
for i in range(len(risk_category_order)):
    for j in range(i+1, len(risk_category_order)):
        cat_pairs.append((risk_category_order[i], risk_category_order[j]))

alpha = 0.05
bonferroni_alpha_cat = alpha / len(cat_pairs)
print(f"\nNumber of comparisons: {len(cat_pairs)}")
print(f"Adjusted significance level (Bonferroni): α = {bonferroni_alpha_cat:.4f}\n")

for cat1, cat2 in cat_pairs:
    data1 = df_project[df_project['risk_category'] == cat1]['delay'].dropna()
    data2 = df_project[df_project['risk_category'] == cat2]['delay'].dropna()
    
    if len(data1) > 0 and len(data2) > 0:
        u_stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
        
        print(f"{cat1} vs {cat2}:")
        print(f"  Mann-Whitney U statistic: {u_stat:.3f}")
        print(f"  P-value: {p_value:.4f}")
        
        if p_value < bonferroni_alpha_cat:
            print(f"  → Significant difference (p < {bonferroni_alpha_cat:.4f})")
            if data1.median() > data2.median():
                print(f"     {cat1} has longer delays (median: {data1.median():.2f}y vs {data2.median():.2f}y)")
            else:
                print(f"     {cat2} has longer delays (median: {data2.median():.2f}y vs {data1.median():.2f}y)")
        else:
            print(f"  → No significant difference (p ≥ {bonferroni_alpha_cat:.4f})")
        print()

# ============================================================================
# PART 2: RISK LEVEL ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("PART 2: RISK LEVEL ANALYSIS")
print("="*80)

# Summary statistics
print("\nSUMMARY STATISTICS")
print("-" * 80)

for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    delay_data = level_data['delay'].dropna()
    print(f"\nLevel {risk_level} ({risk_level_labels[risk_level]}):")
    print(f"  n={len(delay_data)}")
    print(f"  mean={delay_data.mean():.2f} years")
    print(f"  median={delay_data.median():.2f} years")
    print(f"  std={delay_data.std():.2f} years")

# Kruskal-Wallis test for risk levels
print("\n\nOVERALL TEST: Kruskal-Wallis")
print("-" * 80)

delay_groups_level = []
for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    delay_groups_level.append(level_data['delay'].dropna())

if all(len(group) > 0 for group in delay_groups_level):
    h_stat_level, p_value_level = stats.kruskal(*delay_groups_level)
    print(f"Kruskal-Wallis H-statistic: {h_stat_level:.3f}")
    print(f"P-value: {p_value_level:.4f}")
    if p_value_level < 0.05:
        print(f"→ Delays are significantly different across risk levels (p < 0.05)")
    else:
        print(f"→ No significant difference in delays across risk levels (p ≥ 0.05)")

# Pairwise comparisons for risk levels
print("\n\nPAIRWISE COMPARISONS: Mann-Whitney U Test")
print("-" * 80)
print("(with Bonferroni correction for multiple comparisons)")

level_pairs = [(0, 1), (0, 2), (1, 2)]
pair_names = [
    (risk_level_labels[0], risk_level_labels[1]),
    (risk_level_labels[0], risk_level_labels[2]),
    (risk_level_labels[1], risk_level_labels[2])
]

bonferroni_alpha_level = alpha / len(level_pairs)
print(f"\nNumber of comparisons: {len(level_pairs)}")
print(f"Adjusted significance level (Bonferroni): α = {bonferroni_alpha_level:.4f}\n")

for (level1, level2), (name1, name2) in zip(level_pairs, pair_names):
    data1 = df_project[df_project['risk_level'] == level1]['delay'].dropna()
    data2 = df_project[df_project['risk_level'] == level2]['delay'].dropna()
    
    if len(data1) > 0 and len(data2) > 0:
        u_stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
        
        print(f"{name1} (Level {level1}) vs {name2} (Level {level2}):")
        print(f"  Mann-Whitney U statistic: {u_stat:.3f}")
        print(f"  P-value: {p_value:.4f}")
        
        if p_value < bonferroni_alpha_level:
            print(f"  → Significant difference (p < {bonferroni_alpha_level:.4f})")
            if data1.median() > data2.median():
                print(f"     {name1} has longer delays (median: {data1.median():.2f}y vs {data2.median():.2f}y)")
            else:
                print(f"     {name2} has longer delays (median: {data2.median():.2f}y vs {data1.median():.2f}y)")
        else:
            print(f"  → No significant difference (p ≥ {bonferroni_alpha_level:.4f})")
        print()

# Spearman correlation (trend analysis for risk levels)
print("\nTREND ANALYSIS: Spearman Correlation")
print("-" * 80)

risk_numeric = []
delay_values = []

for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    delays = level_data['delay'].dropna()
    risk_numeric.extend([risk_level] * len(delays))
    delay_values.extend(delays.values)

if len(risk_numeric) > 0:
    corr, corr_p = stats.spearmanr(risk_numeric, delay_values)
    print(f"Spearman correlation coefficient: {corr:.3f}")
    print(f"P-value: {corr_p:.4f}")
    
    if corr_p < 0.05:
        if corr > 0:
            print(f"→ Significant positive correlation: Higher risk levels associated with longer delays")
        elif corr < 0:
            print(f"→ Significant negative correlation: Higher risk levels associated with shorter delays")
    else:
        print(f"→ No significant correlation between risk level and delay")

# %%
risk_category_colors = {
    'No Risk': '#fee5d9',
    'Environmental Only': '#1b9e77',
    'Social Only': '#e6ab02',
    'Both': '#a6761d'
}

risk_level_colors = {
    0: '#fcc5c0',
    1: '#fa9fb5',
    2: '#c51b8a'
}

risk_level_labels = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}

# Create subplots
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=['Initial Duration by Risk Category', 'Initial Duration by Risk Level'],
    horizontal_spacing=0.12
)

# Subplot 1: By Risk Category
risk_category_order = ['No Risk', 'Environmental Only', 'Social Only', 'Both']
for risk_cat in risk_category_order:
    risk_data = df_project[df_project['risk_category'] == risk_cat]
    
    fig.add_trace(
        go.Violin(
            y=risk_data['duration_initial'],
            x=[risk_cat] * len(risk_data),
            name=risk_cat,
            box_visible=True,
            meanline_visible=True,
            points='all',
            pointpos=-0.5,
            jitter=0.3,
            marker=dict(color=risk_category_colors[risk_cat]),
            scalemode='width',
            width=0.6,
            side='positive',
            line=dict(color=risk_category_colors[risk_cat], width=2),
            showlegend=False
        ),
        row=1, col=1
    )

# Subplot 2: By Risk Level
for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    
    fig.add_trace(
        go.Violin(
            y=level_data['duration_initial'],
            x=[risk_level_labels[risk_level]] * len(level_data),
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

# Update layout
fig.update_layout(
    title=dict(
        text='Project Initial Duration Distribution by Risk Category and Level',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1400,
    height=600,
    font=dict(family='Arial')
)

# Update x-axes
fig.update_xaxes(
    title_text='Risk Category',
    title_font=dict(size=14, family='Arial'),
    tickfont=dict(family='Arial', size=11),
    tickangle=-30,
    categoryorder='array',
    categoryarray=risk_category_order,
    row=1, col=1
)

fig.update_xaxes(
    title_text='Risk Level',
    title_font=dict(size=14, family='Arial'),
    tickfont=dict(family='Arial', size=11),
    categoryorder='array',
    categoryarray=[risk_level_labels[0], risk_level_labels[1], risk_level_labels[2]],
    row=1, col=2
)

# Update y-axes
fig.update_yaxes(
    title_text='Initial Duration (years)',
    title_font=dict(size=14, family='Arial'),
    gridcolor='lightgray',
    gridwidth=0.5,
    tickfont=dict(family='Arial', size=12),
    row=1, col=1
)

fig.update_yaxes(
    title_text='Initial Duration (years)',
    title_font=dict(size=14, family='Arial'),
    gridcolor='lightgray',
    gridwidth=0.5,
    tickfont=dict(family='Arial', size=12),
    row=1, col=2
)

fig.show()

# Statistical Analysis
print("="*80)
print("STATISTICAL ANALYSIS: Risk and Project Initial Duration")
print("="*80)

# ============================================================================
# PART 1: RISK CATEGORY ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("PART 1: RISK CATEGORY ANALYSIS")
print("="*80)

# Summary statistics
print("\nSUMMARY STATISTICS")
print("-" * 80)

for risk_cat in risk_category_order:
    risk_data = df_project[df_project['risk_category'] == risk_cat]
    duration_data = risk_data['duration_initial'].dropna()
    print(f"\n{risk_cat}:")
    print(f"  n={len(duration_data)}")
    print(f"  mean={duration_data.mean():.2f} years")
    print(f"  median={duration_data.median():.2f} years")
    print(f"  std={duration_data.std():.2f} years")

# Kruskal-Wallis test for risk categories
print("\n\nOVERALL TEST: Kruskal-Wallis")
print("-" * 80)

duration_groups_cat = []
for risk_cat in risk_category_order:
    risk_data = df_project[df_project['risk_category'] == risk_cat]
    duration_groups_cat.append(risk_data['duration_initial'].dropna())

if all(len(group) > 0 for group in duration_groups_cat):
    h_stat, p_value = stats.kruskal(*duration_groups_cat)
    print(f"Kruskal-Wallis H-statistic: {h_stat:.3f}")
    print(f"P-value: {p_value:.4f}")
    if p_value < 0.05:
        print(f"→ Initial durations are significantly different across risk categories (p < 0.05)")
    else:
        print(f"→ No significant difference in initial durations across risk categories (p ≥ 0.05)")

# Pairwise comparisons for risk categories
print("\n\nPAIRWISE COMPARISONS: Mann-Whitney U Test")
print("-" * 80)
print("(with Bonferroni correction for multiple comparisons)")

# All possible pairs
cat_pairs = []
for i in range(len(risk_category_order)):
    for j in range(i+1, len(risk_category_order)):
        cat_pairs.append((risk_category_order[i], risk_category_order[j]))

alpha = 0.05
bonferroni_alpha_cat = alpha / len(cat_pairs)
print(f"\nNumber of comparisons: {len(cat_pairs)}")
print(f"Adjusted significance level (Bonferroni): α = {bonferroni_alpha_cat:.4f}\n")

for cat1, cat2 in cat_pairs:
    data1 = df_project[df_project['risk_category'] == cat1]['duration_initial'].dropna()
    data2 = df_project[df_project['risk_category'] == cat2]['duration_initial'].dropna()
    
    if len(data1) > 0 and len(data2) > 0:
        u_stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
        
        print(f"{cat1} vs {cat2}:")
        print(f"  Mann-Whitney U statistic: {u_stat:.3f}")
        print(f"  P-value: {p_value:.4f}")
        
        if p_value < bonferroni_alpha_cat:
            print(f"  → Significant difference (p < {bonferroni_alpha_cat:.4f})")
            if data1.median() > data2.median():
                print(f"     {cat1} has longer initial duration (median: {data1.median():.2f}y vs {data2.median():.2f}y)")
            else:
                print(f"     {cat2} has longer initial duration (median: {data2.median():.2f}y vs {data1.median():.2f}y)")
        else:
            print(f"  → No significant difference (p ≥ {bonferroni_alpha_cat:.4f})")
        print()

# ============================================================================
# PART 2: RISK LEVEL ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("PART 2: RISK LEVEL ANALYSIS")
print("="*80)

# Summary statistics
print("\nSUMMARY STATISTICS")
print("-" * 80)

for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    duration_data = level_data['duration_initial'].dropna()
    print(f"\nLevel {risk_level} ({risk_level_labels[risk_level]}):")
    print(f"  n={len(duration_data)}")
    print(f"  mean={duration_data.mean():.2f} years")
    print(f"  median={duration_data.median():.2f} years")
    print(f"  std={duration_data.std():.2f} years")

# Kruskal-Wallis test for risk levels
print("\n\nOVERALL TEST: Kruskal-Wallis")
print("-" * 80)

duration_groups_level = []
for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    duration_groups_level.append(level_data['duration_initial'].dropna())

if all(len(group) > 0 for group in duration_groups_level):
    h_stat_level, p_value_level = stats.kruskal(*duration_groups_level)
    print(f"Kruskal-Wallis H-statistic: {h_stat_level:.3f}")
    print(f"P-value: {p_value_level:.4f}")
    if p_value_level < 0.05:
        print(f"→ Initial durations are significantly different across risk levels (p < 0.05)")
    else:
        print(f"→ No significant difference in initial durations across risk levels (p ≥ 0.05)")

# Pairwise comparisons for risk levels
print("\n\nPAIRWISE COMPARISONS: Mann-Whitney U Test")
print("-" * 80)
print("(with Bonferroni correction for multiple comparisons)")

level_pairs = [(0, 1), (0, 2), (1, 2)]
pair_names = [
    (risk_level_labels[0], risk_level_labels[1]),
    (risk_level_labels[0], risk_level_labels[2]),
    (risk_level_labels[1], risk_level_labels[2])
]

bonferroni_alpha_level = alpha / len(level_pairs)
print(f"\nNumber of comparisons: {len(level_pairs)}")
print(f"Adjusted significance level (Bonferroni): α = {bonferroni_alpha_level:.4f}\n")

for (level1, level2), (name1, name2) in zip(level_pairs, pair_names):
    data1 = df_project[df_project['risk_level'] == level1]['duration_initial'].dropna()
    data2 = df_project[df_project['risk_level'] == level2]['duration_initial'].dropna()
    
    if len(data1) > 0 and len(data2) > 0:
        u_stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
        
        print(f"{name1} (Level {level1}) vs {name2} (Level {level2}):")
        print(f"  Mann-Whitney U statistic: {u_stat:.3f}")
        print(f"  P-value: {p_value:.4f}")
        
        if p_value < bonferroni_alpha_level:
            print(f"  → Significant difference (p < {bonferroni_alpha_level:.4f})")
            if data1.median() > data2.median():
                print(f"     {name1} has longer initial duration (median: {data1.median():.2f}y vs {data2.median():.2f}y)")
            else:
                print(f"     {name2} has longer initial duration (median: {data2.median():.2f}y vs {data1.median():.2f}y)")
        else:
            print(f"  → No significant difference (p ≥ {bonferroni_alpha_level:.4f})")
        print()

# Spearman correlation (trend analysis for risk levels)
print("\nTREND ANALYSIS: Spearman Correlation")
print("-" * 80)

risk_numeric = []
duration_values = []

for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    durations = level_data['duration_initial'].dropna()
    risk_numeric.extend([risk_level] * len(durations))
    duration_values.extend(durations.values)

if len(risk_numeric) > 0:
    corr, corr_p = stats.spearmanr(risk_numeric, duration_values)
    print(f"Spearman correlation coefficient: {corr:.3f}")
    print(f"P-value: {corr_p:.4f}")
    
    if corr_p < 0.05:
        if corr > 0:
            print(f"→ Significant positive correlation: Higher risk levels associated with longer initial durations")
        elif corr < 0:
            print(f"→ Significant negative correlation: Higher risk levels associated with shorter initial durations")
    else:
        print(f"→ No significant correlation between risk level and initial duration")

# %%
df_project['cost_overrun_pct'] = ((df_project['totalcost_final_adj'] - df_project['totalcost_initial_adj']) / df_project['totalcost_initial_adj']) * 100

# Display some stats about cost overrun percentage
print("Cost Overrun Percentage Statistics:")
print(f"Mean: {df_project['cost_overrun_pct'].mean():.2f}%")
print(f"Median: {df_project['cost_overrun_pct'].median():.2f}%")
print(f"Min: {df_project['cost_overrun_pct'].min():.2f}%")
print(f"Max: {df_project['cost_overrun_pct'].max():.2f}%")
print(f"Projects with cost overrun: {(df_project['cost_overrun_pct'] > 0).sum()} ({(df_project['cost_overrun_pct'] > 0).sum() / len(df_project) * 100:.1f}%)")
print("\n" + "="*80 + "\n")

risk_category_colors = {
    'No Risk': '#fee5d9',
    'Environmental Only': '#1b9e77',
    'Social Only': '#e6ab02',
    'Both': '#a6761d'
}

risk_level_colors = {
    0: '#fcc5c0',
    1: '#fa9fb5',
    2: '#c51b8a'
}

risk_level_labels = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}

# Create subplots
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=['Cost Overrun by Risk Category', 'Cost Overrun by Risk Level'],
    horizontal_spacing=0.12
)

# Subplot 1: By Risk Category
risk_category_order = ['No Risk', 'Environmental Only', 'Social Only', 'Both']
for risk_cat in risk_category_order:
    risk_data = df_project[df_project['risk_category'] == risk_cat]
    
    fig.add_trace(
        go.Violin(
            y=risk_data['cost_overrun_pct'],
            x=[risk_cat] * len(risk_data),
            name=risk_cat,
            box_visible=True,
            meanline_visible=True,
            points='all',
            pointpos=-0.5,
            jitter=0.3,
            marker=dict(color=risk_category_colors[risk_cat]),
            scalemode='width',
            width=0.6,
            side='positive',
            line=dict(color=risk_category_colors[risk_cat], width=2),
            showlegend=False
        ),
        row=1, col=1
    )

# Subplot 2: By Risk Level
for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    
    fig.add_trace(
        go.Violin(
            y=level_data['cost_overrun_pct'],
            x=[risk_level_labels[risk_level]] * len(level_data),
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

# Update layout
fig.update_layout(
    title=dict(
        text='Project Cost Overrun (%) by Risk Category and Level',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1400,
    height=600,
    font=dict(family='Arial')
)

# Update x-axes
fig.update_xaxes(
    title_text='Risk Category',
    title_font=dict(size=14, family='Arial'),
    tickfont=dict(family='Arial', size=11),
    tickangle=-30,
    categoryorder='array',
    categoryarray=risk_category_order,
    row=1, col=1
)

fig.update_xaxes(
    title_text='Risk Level',
    title_font=dict(size=14, family='Arial'),
    tickfont=dict(family='Arial', size=11),
    categoryorder='array',
    categoryarray=[risk_level_labels[0], risk_level_labels[1], risk_level_labels[2]],
    row=1, col=2
)

# Update y-axes
fig.update_yaxes(
    title_text='Cost Overrun (%)',
    title_font=dict(size=14, family='Arial'),
    gridcolor='lightgray',
    gridwidth=0.5,
    tickfont=dict(family='Arial', size=12),
    row=1, col=1
)

fig.update_yaxes(
    title_text='Cost Overrun (%)',
    title_font=dict(size=14, family='Arial'),
    gridcolor='lightgray',
    gridwidth=0.5,
    tickfont=dict(family='Arial', size=12),
    row=1, col=2
)

fig.show()

# Statistical Analysis
print("="*80)
print("STATISTICAL ANALYSIS: Risk and Project Cost Overrun (%)")
print("="*80)

# ============================================================================
# PART 1: RISK CATEGORY ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("PART 1: RISK CATEGORY ANALYSIS")
print("="*80)

# Summary statistics
print("\nSUMMARY STATISTICS")
print("-" * 80)

for risk_cat in risk_category_order:
    risk_data = df_project[df_project['risk_category'] == risk_cat]
    overrun_data = risk_data['cost_overrun_pct'].dropna()
    print(f"\n{risk_cat}:")
    print(f"  n={len(overrun_data)}")
    print(f"  mean={overrun_data.mean():.2f}%")
    print(f"  median={overrun_data.median():.2f}%")
    print(f"  std={overrun_data.std():.2f}%")

# Kruskal-Wallis test for risk categories
print("\n\nOVERALL TEST: Kruskal-Wallis")
print("-" * 80)

overrun_groups_cat = []
for risk_cat in risk_category_order:
    risk_data = df_project[df_project['risk_category'] == risk_cat]
    overrun_groups_cat.append(risk_data['cost_overrun_pct'].dropna())

if all(len(group) > 0 for group in overrun_groups_cat):
    h_stat, p_value = stats.kruskal(*overrun_groups_cat)
    print(f"Kruskal-Wallis H-statistic: {h_stat:.3f}")
    print(f"P-value: {p_value:.4f}")
    if p_value < 0.05:
        print(f"→ Cost overruns are significantly different across risk categories (p < 0.05)")
    else:
        print(f"→ No significant difference in cost overruns across risk categories (p ≥ 0.05)")

# Pairwise comparisons for risk categories
print("\n\nPAIRWISE COMPARISONS: Mann-Whitney U Test")
print("-" * 80)
print("(with Bonferroni correction for multiple comparisons)")

# All possible pairs
cat_pairs = []
for i in range(len(risk_category_order)):
    for j in range(i+1, len(risk_category_order)):
        cat_pairs.append((risk_category_order[i], risk_category_order[j]))

alpha = 0.05
bonferroni_alpha_cat = alpha / len(cat_pairs)
print(f"\nNumber of comparisons: {len(cat_pairs)}")
print(f"Adjusted significance level (Bonferroni): α = {bonferroni_alpha_cat:.4f}\n")

for cat1, cat2 in cat_pairs:
    data1 = df_project[df_project['risk_category'] == cat1]['cost_overrun_pct'].dropna()
    data2 = df_project[df_project['risk_category'] == cat2]['cost_overrun_pct'].dropna()
    
    if len(data1) > 0 and len(data2) > 0:
        u_stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
        
        print(f"{cat1} vs {cat2}:")
        print(f"  Mann-Whitney U statistic: {u_stat:.3f}")
        print(f"  P-value: {p_value:.4f}")
        
        if p_value < bonferroni_alpha_cat:
            print(f"  → Significant difference (p < {bonferroni_alpha_cat:.4f})")
            if data1.median() > data2.median():
                print(f"     {cat1} has higher cost overrun (median: {data1.median():.2f}% vs {data2.median():.2f}%)")
            else:
                print(f"     {cat2} has higher cost overrun (median: {data2.median():.2f}% vs {data1.median():.2f}%)")
        else:
            print(f"  → No significant difference (p ≥ {bonferroni_alpha_cat:.4f})")
        print()

# ============================================================================
# PART 2: RISK LEVEL ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("PART 2: RISK LEVEL ANALYSIS")
print("="*80)

# Summary statistics
print("\nSUMMARY STATISTICS")
print("-" * 80)

for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    overrun_data = level_data['cost_overrun_pct'].dropna()
    print(f"\nLevel {risk_level} ({risk_level_labels[risk_level]}):")
    print(f"  n={len(overrun_data)}")
    print(f"  mean={overrun_data.mean():.2f}%")
    print(f"  median={overrun_data.median():.2f}%")
    print(f"  std={overrun_data.std():.2f}%")

# Kruskal-Wallis test for risk levels
print("\n\nOVERALL TEST: Kruskal-Wallis")
print("-" * 80)

overrun_groups_level = []
for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    overrun_groups_level.append(level_data['cost_overrun_pct'].dropna())

if all(len(group) > 0 for group in overrun_groups_level):
    h_stat_level, p_value_level = stats.kruskal(*overrun_groups_level)
    print(f"Kruskal-Wallis H-statistic: {h_stat_level:.3f}")
    print(f"P-value: {p_value_level:.4f}")
    if p_value_level < 0.05:
        print(f"→ Cost overruns are significantly different across risk levels (p < 0.05)")
    else:
        print(f"→ No significant difference in cost overruns across risk levels (p ≥ 0.05)")

# Pairwise comparisons for risk levels
print("\n\nPAIRWISE COMPARISONS: Mann-Whitney U Test")
print("-" * 80)
print("(with Bonferroni correction for multiple comparisons)")

level_pairs = [(0, 1), (0, 2), (1, 2)]
pair_names = [
    (risk_level_labels[0], risk_level_labels[1]),
    (risk_level_labels[0], risk_level_labels[2]),
    (risk_level_labels[1], risk_level_labels[2])
]

bonferroni_alpha_level = alpha / len(level_pairs)
print(f"\nNumber of comparisons: {len(level_pairs)}")
print(f"Adjusted significance level (Bonferroni): α = {bonferroni_alpha_level:.4f}\n")

for (level1, level2), (name1, name2) in zip(level_pairs, pair_names):
    data1 = df_project[df_project['risk_level'] == level1]['cost_overrun_pct'].dropna()
    data2 = df_project[df_project['risk_level'] == level2]['cost_overrun_pct'].dropna()
    
    if len(data1) > 0 and len(data2) > 0:
        u_stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
        
        print(f"{name1} (Level {level1}) vs {name2} (Level {level2}):")
        print(f"  Mann-Whitney U statistic: {u_stat:.3f}")
        print(f"  P-value: {p_value:.4f}")
        
        if p_value < bonferroni_alpha_level:
            print(f"  → Significant difference (p < {bonferroni_alpha_level:.4f})")
            if data1.median() > data2.median():
                print(f"     {name1} has higher cost overrun (median: {data1.median():.2f}% vs {data2.median():.2f}%)")
            else:
                print(f"     {name2} has higher cost overrun (median: {data2.median():.2f}% vs {data1.median():.2f}%)")
        else:
            print(f"  → No significant difference (p ≥ {bonferroni_alpha_level:.4f})")
        print()

# Spearman correlation (trend analysis for risk levels)
print("\nTREND ANALYSIS: Spearman Correlation")
print("-" * 80)

risk_numeric = []
overrun_values = []

for risk_level in [0, 1, 2]:
    level_data = df_project[df_project['risk_level'] == risk_level]
    overruns = level_data['cost_overrun_pct'].dropna()
    risk_numeric.extend([risk_level] * len(overruns))
    overrun_values.extend(overruns.values)

if len(risk_numeric) > 0:
    corr, corr_p = stats.spearmanr(risk_numeric, overrun_values)
    print(f"Spearman correlation coefficient: {corr:.3f}")
    print(f"P-value: {corr_p:.4f}")
    
    if corr_p < 0.05:
        if corr > 0:
            print(f"→ Significant positive correlation: Higher risk levels associated with higher cost overruns")
        elif corr < 0:
            print(f"→ Significant negative correlation: Higher risk levels associated with lower cost overruns")
    else:
        print(f"→ No significant correlation between risk level and cost overrun")

# %%
df_project['risk_associated'] = (df_project['risk_level'] >= 1).astype(int)
print("Risk Association Mapping:")
print(df_project[['risk_level', 'risk_category', 'risk_associated']].value_counts().sort_index())

print("\n" + "="*80)
print("Risk Associated Distribution:")
print(df_project['risk_associated'].value_counts().sort_index())

print("\nCross-check:")
for risk_assoc in [0, 1]:
    count = (df_project['risk_associated'] == risk_assoc).sum()
    pct = (count / len(df_project) * 100)
    label = "No Risk" if risk_assoc == 0 else "Risk Associated"
    print(f"{label} ({risk_assoc}): {count} projects ({pct:.1f}%)")

# %%
# First, let's check what risk severity columns you have
print("Available risk severity columns:")
risk_severity_cols = [col for col in df_project.columns if 'safe_' in col or 'risk' in col.lower()]
print(risk_severity_cols)

# Assuming you have columns like 'safe_env', 'safe_ind', 'safe_res' with values A, B, C, FI
# Let's check the distribution

print("\n" + "="*80)
print("RISK SEVERITY DISTRIBUTION")
print("="*80)

# Check what columns contain A, B, C values
for col in ['safe_env', 'safe_ind', 'safe_res']:
    if col in df_project.columns:
        print(f"\n{col} distribution:")
        print(df_project[col].value_counts().sort_index())

# Filter out 'FI' (Financially Intermediated) projects if needed
df_project_risk_filtered = df_project[
    ~df_project['safe_env'].isin(['FI']) & 
    ~df_project['safe_ind'].isin(['FI']) & 
    ~df_project['safe_res'].isin(['FI'])
].copy()

print(f"\nProjects after filtering out FI: {len(df_project_risk_filtered)}")
print(f"Projects removed (FI): {len(df_project) - len(df_project_risk_filtered)}")

# %% [markdown]
# ## By risk severity

# %%
from scipy.stats import mannwhitneyu
import numpy as np

# Define risk colors for A, B, C
severity_colors = {'A': '#db4325', 'B': '#dea247', 'C': '#bbd4a6'}
severity_labels = {'A': 'Level A (High)', 'B': 'Level B (Medium)', 'C': 'Level C (Low)'}

# Define risk categories - Environmental vs Social
risk_categories_grouped = {
    'Environmental': 'safe_env',
    'Social': ['safe_ind', 'safe_res']  # Social includes both Indigenous and Resettlement
}

print("="*80)
print("RISK SEVERITY ANALYSIS: DELAY BY ENVIRONMENTAL VS SOCIAL RISK")
print("="*80)

# For Social risk, we need to determine the "worst" (highest) severity across ind and res
# Create a combined social severity column
def get_worst_severity(row):
    """Get the worst (highest) severity between Indigenous and Resettlement risks"""
    severities = []
    if pd.notna(row['safe_ind']):
        severities.append(row['safe_ind'])
    if pd.notna(row['safe_res']):
        severities.append(row['safe_res'])
    
    if not severities:
        return None
    
    # A > B > C (A is worst)
    if 'A' in severities:
        return 'A'
    elif 'B' in severities:
        return 'B'
    else:
        return 'C'

df_project['social_severity'] = df_project.apply(get_worst_severity, axis=1)

print("\nSocial Risk Severity Distribution (worst of Indigenous/Resettlement):")
print(df_project['social_severity'].value_counts().sort_index())

# Create violin plots
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=['Environmental Risk', 'Social Risk'],
    horizontal_spacing=0.15
)

# Environmental Risk subplot
for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['safe_env'] == severity]
    
    fig.add_trace(
        go.Violin(
            y=risk_data['delay'],
            x=[severity_labels[severity]] * len(risk_data),
            name=severity_labels[severity],
            box_visible=True,
            meanline_visible=True,
            points='all',
            pointpos=-0.5,
            jitter=0.3,
            marker=dict(color=severity_colors[severity]),
            scalemode='width',
            width=0.6,
            side='positive',
            line=dict(color=severity_colors[severity], width=2),
            showlegend=False
        ),
        row=1, col=1
    )

# Social Risk subplot
for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['social_severity'] == severity]
    
    fig.add_trace(
        go.Violin(
            y=risk_data['delay'],
            x=[severity_labels[severity]] * len(risk_data),
            name=severity_labels[severity],
            box_visible=True,
            meanline_visible=True,
            points='all',
            pointpos=-0.5,
            jitter=0.3,
            marker=dict(color=severity_colors[severity]),
            scalemode='width',
            width=0.6,
            side='positive',
            line=dict(color=severity_colors[severity], width=2),
            showlegend=False
        ),
        row=1, col=2
    )

# Update layout
fig.update_layout(
    title=dict(
        text='Project Delay by Environmental vs Social Risk Severity',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1200,
    height=600,
    font=dict(family='Arial')
)

# Update axes
for col_idx in range(1, 3):
    fig.update_xaxes(
        title_text='Severity Level',
        title_font=dict(size=14, family='Arial'),
        tickfont=dict(family='Arial', size=11),
        categoryorder='array',
        categoryarray=[severity_labels['C'], severity_labels['B'], severity_labels['A']],
        row=1, col=col_idx
    )
    fig.update_yaxes(
        title_text='Delay (years)',
        title_font=dict(size=14, family='Arial'),
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=11),
        row=1, col=col_idx
    )

fig.show()

# Statistical Analysis
print("\n" + "="*80)
print("STATISTICAL ANALYSIS")
print("="*80)

# Environmental Risk Analysis
print(f"\n{'='*80}")
print("ENVIRONMENTAL RISK")
print(f"{'='*80}")

print("\nSUMMARY STATISTICS")
print("-" * 80)

for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['safe_env'] == severity]
    delay_data = risk_data['delay'].dropna()
    print(f"\nLevel {severity} ({severity_labels[severity]}):")
    print(f"  n={len(delay_data)}")
    print(f"  mean={delay_data.mean():.2f} years")
    print(f"  median={delay_data.median():.2f} years")
    print(f"  std={delay_data.std():.2f} years")

print("\n\nOVERALL TEST: Kruskal-Wallis")
print("-" * 80)

env_delay_groups = []
for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['safe_env'] == severity]
    env_delay_groups.append(risk_data['delay'].dropna())

if all(len(group) > 0 for group in env_delay_groups):
    h_stat, p_value = stats.kruskal(*env_delay_groups)
    print(f"Kruskal-Wallis H-statistic: {h_stat:.3f}")
    print(f"P-value: {p_value:.4f}")
    if p_value < 0.05:
        print(f"→ Delays are significantly different across environmental severity levels (p < 0.05)")
    else:
        print(f"→ No significant difference in delays across environmental severity levels (p ≥ 0.05)")

print("\n\nPAIRWISE COMPARISONS: Mann-Whitney U Test")
print("-" * 80)
print("(with Bonferroni correction for multiple comparisons)")

severity_pairs = [('C', 'B'), ('C', 'A'), ('B', 'A')]
alpha = 0.05
bonferroni_alpha = alpha / len(severity_pairs)
print(f"\nNumber of comparisons: {len(severity_pairs)}")
print(f"Adjusted significance level (Bonferroni): α = {bonferroni_alpha:.4f}\n")

for sev1, sev2 in severity_pairs:
    data1 = df_project[df_project['safe_env'] == sev1]['delay'].dropna()
    data2 = df_project[df_project['safe_env'] == sev2]['delay'].dropna()
    
    if len(data1) > 0 and len(data2) > 0:
        u_stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
        
        print(f"Level {sev1} vs Level {sev2}:")
        print(f"  Mann-Whitney U statistic: {u_stat:.3f}")
        print(f"  P-value: {p_value:.4f}")
        
        if p_value < bonferroni_alpha:
            print(f"  → Significant difference (p < {bonferroni_alpha:.4f})")
            if data1.median() > data2.median():
                print(f"     Level {sev1} has longer delays (median: {data1.median():.2f}y vs {data2.median():.2f}y)")
            else:
                print(f"     Level {sev2} has longer delays (median: {data2.median():.2f}y vs {data1.median():.2f}y)")
        else:
            print(f"  → No significant difference (p ≥ {bonferroni_alpha:.4f})")
        print()

print("\nTREND ANALYSIS: Spearman Correlation")
print("-" * 80)

severity_numeric = []
delay_values = []
severity_map = {'C': 1, 'B': 2, 'A': 3}

for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['safe_env'] == severity]
    delays = risk_data['delay'].dropna()
    severity_numeric.extend([severity_map[severity]] * len(delays))
    delay_values.extend(delays.values)

if len(severity_numeric) > 0:
    corr, corr_p = stats.spearmanr(severity_numeric, delay_values)
    print(f"Spearman correlation coefficient: {corr:.3f}")
    print(f"P-value: {corr_p:.4f}")
    
    if corr_p < 0.05:
        if corr > 0:
            print(f"→ Significant positive correlation: Higher environmental severity associated with longer delays")
        elif corr < 0:
            print(f"→ Significant negative correlation: Higher environmental severity associated with shorter delays")
    else:
        print(f"→ No significant correlation between environmental severity and delay")

# Social Risk Analysis
print(f"\n\n{'='*80}")
print("SOCIAL RISK (Combined Indigenous & Resettlement)")
print(f"{'='*80}")

print("\nSUMMARY STATISTICS")
print("-" * 80)

for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['social_severity'] == severity]
    delay_data = risk_data['delay'].dropna()
    print(f"\nLevel {severity} ({severity_labels[severity]}):")
    print(f"  n={len(delay_data)}")
    print(f"  mean={delay_data.mean():.2f} years")
    print(f"  median={delay_data.median():.2f} years")
    print(f"  std={delay_data.std():.2f} years")

print("\n\nOVERALL TEST: Kruskal-Wallis")
print("-" * 80)

soc_delay_groups = []
for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['social_severity'] == severity]
    soc_delay_groups.append(risk_data['delay'].dropna())

if all(len(group) > 0 for group in soc_delay_groups):
    h_stat, p_value = stats.kruskal(*soc_delay_groups)
    print(f"Kruskal-Wallis H-statistic: {h_stat:.3f}")
    print(f"P-value: {p_value:.4f}")
    if p_value < 0.05:
        print(f"→ Delays are significantly different across social severity levels (p < 0.05)")
    else:
        print(f"→ No significant difference in delays across social severity levels (p ≥ 0.05)")

print("\n\nPAIRWISE COMPARISONS: Mann-Whitney U Test")
print("-" * 80)
print("(with Bonferroni correction for multiple comparisons)")

print(f"\nNumber of comparisons: {len(severity_pairs)}")
print(f"Adjusted significance level (Bonferroni): α = {bonferroni_alpha:.4f}\n")

for sev1, sev2 in severity_pairs:
    data1 = df_project[df_project['social_severity'] == sev1]['delay'].dropna()
    data2 = df_project[df_project['social_severity'] == sev2]['delay'].dropna()
    
    if len(data1) > 0 and len(data2) > 0:
        u_stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
        
        print(f"Level {sev1} vs Level {sev2}:")
        print(f"  Mann-Whitney U statistic: {u_stat:.3f}")
        print(f"  P-value: {p_value:.4f}")
        
        if p_value < bonferroni_alpha:
            print(f"  → Significant difference (p < {bonferroni_alpha:.4f})")
            if data1.median() > data2.median():
                print(f"     Level {sev1} has longer delays (median: {data1.median():.2f}y vs {data2.median():.2f}y)")
            else:
                print(f"     Level {sev2} has longer delays (median: {data2.median():.2f}y vs {data1.median():.2f}y)")
        else:
            print(f"  → No significant difference (p ≥ {bonferroni_alpha:.4f})")
        print()

print("\nTREND ANALYSIS: Spearman Correlation")
print("-" * 80)

severity_numeric = []
delay_values = []

for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['social_severity'] == severity]
    delays = risk_data['delay'].dropna()
    severity_numeric.extend([severity_map[severity]] * len(delays))
    delay_values.extend(delays.values)

if len(severity_numeric) > 0:
    corr, corr_p = stats.spearmanr(severity_numeric, delay_values)
    print(f"Spearman correlation coefficient: {corr:.3f}")
    print(f"P-value: {corr_p:.4f}")
    
    if corr_p < 0.05:
        if corr > 0:
            print(f"→ Significant positive correlation: Higher social severity associated with longer delays")
        elif corr < 0:
            print(f"→ Significant negative correlation: Higher social severity associated with shorter delays")
    else:
        print(f"→ No significant correlation between social severity and delay")

# %%
# Define risk colors for A, B, C
severity_colors = {'A': '#db4325', 'B': '#dea247', 'C': '#bbd4a6'}
severity_labels = {'A': 'Level A (High)', 'B': 'Level B (Medium)', 'C': 'Level C (Low)'}

print("="*80)
print("RISK SEVERITY ANALYSIS: COST OVERRUN (%) BY ENVIRONMENTAL VS SOCIAL RISK")
print("="*80)

# Create social severity if not already created
if 'social_severity' not in df_project.columns:
    def get_worst_severity(row):
        """Get the worst (highest) severity between Indigenous and Resettlement risks"""
        severities = []
        if pd.notna(row['safe_ind']):
            severities.append(row['safe_ind'])
        if pd.notna(row['safe_res']):
            severities.append(row['safe_res'])
        
        if not severities:
            return None
        
        # A > B > C (A is worst)
        if 'A' in severities:
            return 'A'
        elif 'B' in severities:
            return 'B'
        else:
            return 'C'
    
    df_project['social_severity'] = df_project.apply(get_worst_severity, axis=1)

print("\nSocial Risk Severity Distribution (worst of Indigenous/Resettlement):")
print(df_project['social_severity'].value_counts().sort_index())

# Create violin plots
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=['Environmental Risk', 'Social Risk'],
    horizontal_spacing=0.15
)

# Environmental Risk subplot
for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['safe_env'] == severity]
    
    fig.add_trace(
        go.Violin(
            y=risk_data['cost_overrun_pct'],
            x=[severity_labels[severity]] * len(risk_data),
            name=severity_labels[severity],
            box_visible=True,
            meanline_visible=True,
            points='all',
            pointpos=-0.5,
            jitter=0.3,
            marker=dict(color=severity_colors[severity]),
            scalemode='width',
            width=0.6,
            side='positive',
            line=dict(color=severity_colors[severity], width=2),
            showlegend=False
        ),
        row=1, col=1
    )

# Social Risk subplot
for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['social_severity'] == severity]
    
    fig.add_trace(
        go.Violin(
            y=risk_data['cost_overrun_pct'],
            x=[severity_labels[severity]] * len(risk_data),
            name=severity_labels[severity],
            box_visible=True,
            meanline_visible=True,
            points='all',
            pointpos=-0.5,
            jitter=0.3,
            marker=dict(color=severity_colors[severity]),
            scalemode='width',
            width=0.6,
            side='positive',
            line=dict(color=severity_colors[severity], width=2),
            showlegend=False
        ),
        row=1, col=2
    )

# Update layout
fig.update_layout(
    title=dict(
        text='Project Cost Overrun (%) by Environmental vs Social Risk Severity',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1200,
    height=600,
    font=dict(family='Arial')
)

# Update axes
for col_idx in range(1, 3):
    fig.update_xaxes(
        title_text='Severity Level',
        title_font=dict(size=14, family='Arial'),
        tickfont=dict(family='Arial', size=11),
        categoryorder='array',
        categoryarray=[severity_labels['C'], severity_labels['B'], severity_labels['A']],
        row=1, col=col_idx
    )
    fig.update_yaxes(
        title_text='Cost Overrun (%)',
        title_font=dict(size=14, family='Arial'),
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=11),
        row=1, col=col_idx
    )

fig.show()

# Statistical Analysis
print("\n" + "="*80)
print("STATISTICAL ANALYSIS")
print("="*80)

# Environmental Risk Analysis
print(f"\n{'='*80}")
print("ENVIRONMENTAL RISK")
print(f"{'='*80}")

print("\nSUMMARY STATISTICS")
print("-" * 80)

for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['safe_env'] == severity]
    overrun_data = risk_data['cost_overrun_pct'].dropna()
    print(f"\nLevel {severity} ({severity_labels[severity]}):")
    print(f"  n={len(overrun_data)}")
    print(f"  mean={overrun_data.mean():.2f}%")
    print(f"  median={overrun_data.median():.2f}%")
    print(f"  std={overrun_data.std():.2f}%")

print("\n\nOVERALL TEST: Kruskal-Wallis")
print("-" * 80)

env_overrun_groups = []
for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['safe_env'] == severity]
    env_overrun_groups.append(risk_data['cost_overrun_pct'].dropna())

if all(len(group) > 0 for group in env_overrun_groups):
    h_stat, p_value = stats.kruskal(*env_overrun_groups)
    print(f"Kruskal-Wallis H-statistic: {h_stat:.3f}")
    print(f"P-value: {p_value:.4f}")
    if p_value < 0.05:
        print(f"→ Cost overruns are significantly different across environmental severity levels (p < 0.05)")
    else:
        print(f"→ No significant difference in cost overruns across environmental severity levels (p ≥ 0.05)")

print("\n\nPAIRWISE COMPARISONS: Mann-Whitney U Test")
print("-" * 80)
print("(with Bonferroni correction for multiple comparisons)")

severity_pairs = [('C', 'B'), ('C', 'A'), ('B', 'A')]
alpha = 0.05
bonferroni_alpha = alpha / len(severity_pairs)
print(f"\nNumber of comparisons: {len(severity_pairs)}")
print(f"Adjusted significance level (Bonferroni): α = {bonferroni_alpha:.4f}\n")

for sev1, sev2 in severity_pairs:
    data1 = df_project[df_project['safe_env'] == sev1]['cost_overrun_pct'].dropna()
    data2 = df_project[df_project['safe_env'] == sev2]['cost_overrun_pct'].dropna()
    
    if len(data1) > 0 and len(data2) > 0:
        u_stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
        
        print(f"Level {sev1} vs Level {sev2}:")
        print(f"  Mann-Whitney U statistic: {u_stat:.3f}")
        print(f"  P-value: {p_value:.4f}")
        
        if p_value < bonferroni_alpha:
            print(f"  → Significant difference (p < {bonferroni_alpha:.4f})")
            if data1.median() > data2.median():
                print(f"     Level {sev1} has higher cost overrun (median: {data1.median():.2f}% vs {data2.median():.2f}%)")
            else:
                print(f"     Level {sev2} has higher cost overrun (median: {data2.median():.2f}% vs {data1.median():.2f}%)")
        else:
            print(f"  → No significant difference (p ≥ {bonferroni_alpha:.4f})")
        print()

print("\nTREND ANALYSIS: Spearman Correlation")
print("-" * 80)

severity_numeric = []
overrun_values = []
severity_map = {'C': 1, 'B': 2, 'A': 3}

for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['safe_env'] == severity]
    overruns = risk_data['cost_overrun_pct'].dropna()
    severity_numeric.extend([severity_map[severity]] * len(overruns))
    overrun_values.extend(overruns.values)

if len(severity_numeric) > 0:
    corr, corr_p = stats.spearmanr(severity_numeric, overrun_values)
    print(f"Spearman correlation coefficient: {corr:.3f}")
    print(f"P-value: {corr_p:.4f}")
    
    if corr_p < 0.05:
        if corr > 0:
            print(f"→ Significant positive correlation: Higher environmental severity associated with higher cost overruns")
        elif corr < 0:
            print(f"→ Significant negative correlation: Higher environmental severity associated with lower cost overruns")
    else:
        print(f"→ No significant correlation between environmental severity and cost overrun")

# Social Risk Analysis
print(f"\n\n{'='*80}")
print("SOCIAL RISK (Combined Indigenous & Resettlement)")
print(f"{'='*80}")

print("\nSUMMARY STATISTICS")
print("-" * 80)

for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['social_severity'] == severity]
    overrun_data = risk_data['cost_overrun_pct'].dropna()
    print(f"\nLevel {severity} ({severity_labels[severity]}):")
    print(f"  n={len(overrun_data)}")
    print(f"  mean={overrun_data.mean():.2f}%")
    print(f"  median={overrun_data.median():.2f}%")
    print(f"  std={overrun_data.std():.2f}%")

print("\n\nOVERALL TEST: Kruskal-Wallis")
print("-" * 80)

soc_overrun_groups = []
for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['social_severity'] == severity]
    soc_overrun_groups.append(risk_data['cost_overrun_pct'].dropna())

if all(len(group) > 0 for group in soc_overrun_groups):
    h_stat, p_value = stats.kruskal(*soc_overrun_groups)
    print(f"Kruskal-Wallis H-statistic: {h_stat:.3f}")
    print(f"P-value: {p_value:.4f}")
    if p_value < 0.05:
        print(f"→ Cost overruns are significantly different across social severity levels (p < 0.05)")
    else:
        print(f"→ No significant difference in cost overruns across social severity levels (p ≥ 0.05)")

print("\n\nPAIRWISE COMPARISONS: Mann-Whitney U Test")
print("-" * 80)
print("(with Bonferroni correction for multiple comparisons)")

print(f"\nNumber of comparisons: {len(severity_pairs)}")
print(f"Adjusted significance level (Bonferroni): α = {bonferroni_alpha:.4f}\n")

for sev1, sev2 in severity_pairs:
    data1 = df_project[df_project['social_severity'] == sev1]['cost_overrun_pct'].dropna()
    data2 = df_project[df_project['social_severity'] == sev2]['cost_overrun_pct'].dropna()
    
    if len(data1) > 0 and len(data2) > 0:
        u_stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
        
        print(f"Level {sev1} vs Level {sev2}:")
        print(f"  Mann-Whitney U statistic: {u_stat:.3f}")
        print(f"  P-value: {p_value:.4f}")
        
        if p_value < bonferroni_alpha:
            print(f"  → Significant difference (p < {bonferroni_alpha:.4f})")
            if data1.median() > data2.median():
                print(f"     Level {sev1} has higher cost overrun (median: {data1.median():.2f}% vs {data2.median():.2f}%)")
            else:
                print(f"     Level {sev2} has higher cost overrun (median: {data2.median():.2f}% vs {data1.median():.2f}%)")
        else:
            print(f"  → No significant difference (p ≥ {bonferroni_alpha:.4f})")
        print()

print("\nTREND ANALYSIS: Spearman Correlation")
print("-" * 80)

severity_numeric = []
overrun_values = []

for severity in ['C', 'B', 'A']:
    risk_data = df_project[df_project['social_severity'] == severity]
    overruns = risk_data['cost_overrun_pct'].dropna()
    severity_numeric.extend([severity_map[severity]] * len(overruns))
    overrun_values.extend(overruns.values)

if len(severity_numeric) > 0:
    corr, corr_p = stats.spearmanr(severity_numeric, overrun_values)
    print(f"Spearman correlation coefficient: {corr:.3f}")
    print(f"P-value: {corr_p:.4f}")
    
    if corr_p < 0.05:
        if corr > 0:
            print(f"→ Significant positive correlation: Higher social severity associated with higher cost overruns")
        elif corr < 0:
            print(f"→ Significant negative correlation: Higher social severity associated with lower cost overruns")
    else:
        print(f"→ No significant correlation between social severity and cost overrun")

# %%
import numpy as np
from scipy import stats

print("="*80)
print("RELATIONSHIP BETWEEN DELAY AND COST OVERRUN")
print("="*80)

# Summary statistics
print("\nSUMMARY STATISTICS")
print("-" * 80)
print(f"Delay:")
print(f"  Mean: {df_project['delay'].mean():.2f} years")
print(f"  Median: {df_project['delay'].median():.2f} years")
print(f"  Range: {df_project['delay'].min():.2f} to {df_project['delay'].max():.2f} years")

print(f"\nCost Overrun:")
print(f"  Mean: {df_project['cost_overrun_pct'].mean():.2f}%")
print(f"  Median: {df_project['cost_overrun_pct'].median():.2f}%")
print(f"  Range: {df_project['cost_overrun_pct'].min():.2f}% to {df_project['cost_overrun_pct'].max():.2f}%")

# Correlation analysis
print("\n\nCORRELATION ANALYSIS")
print("-" * 80)

# Remove rows with missing values
data_complete = df_project[['delay', 'cost_overrun_pct']].dropna()

# Pearson correlation (linear relationship)
pearson_corr, pearson_p = stats.pearsonr(data_complete['delay'], data_complete['cost_overrun_pct'])
print(f"Pearson correlation coefficient: {pearson_corr:.3f}")
print(f"P-value: {pearson_p:.4f}")
if pearson_p < 0.05:
    if pearson_corr > 0:
        print("→ Significant positive linear correlation: Longer delays associated with higher cost overruns")
    else:
        print("→ Significant negative linear correlation: Longer delays associated with lower cost overruns")
else:
    print("→ No significant linear correlation")

# Spearman correlation (monotonic relationship)
spearman_corr, spearman_p = stats.spearmanr(data_complete['delay'], data_complete['cost_overrun_pct'])
print(f"\nSpearman correlation coefficient: {spearman_corr:.3f}")
print(f"P-value: {spearman_p:.4f}")
if spearman_p < 0.05:
    if spearman_corr > 0:
        print("→ Significant positive monotonic correlation: Longer delays associated with higher cost overruns")
    else:
        print("→ Significant negative monotonic correlation: Longer delays associated with lower cost overruns")
else:
    print("→ No significant monotonic correlation")

# Linear regression
from scipy.stats import linregress
slope, intercept, r_value, p_value, std_err = linregress(data_complete['delay'], data_complete['cost_overrun_pct'])
print(f"\n\nLINEAR REGRESSION")
print("-" * 80)
print(f"Equation: Cost Overrun (%) = {intercept:.2f} + {slope:.2f} × Delay (years)")
print(f"R-squared: {r_value**2:.3f}")
print(f"P-value: {p_value:.4f}")
print(f"Standard error: {std_err:.3f}")

if p_value < 0.05:
    print(f"\n→ For each additional year of delay, cost overrun changes by {slope:.2f}%")
else:
    print("\n→ Delay is not a significant predictor of cost overrun")

# Scatter plot with regression line
fig = go.Figure()

# Add scatter points colored by sector
sector_colors = {'Energy': '#d95f02', 'Transportation': '#57c4ad', 'Water': '#0571b0'}

for sector in ['Energy', 'Transportation', 'Water']:
    sector_data = df_project[df_project['sector1'] == sector]
    fig.add_trace(go.Scatter(
        x=sector_data['delay'],
        y=sector_data['cost_overrun_pct'],
        mode='markers',
        name=sector,
        marker=dict(
            color=sector_colors[sector],
            size=8,
            opacity=0.6,
            line=dict(width=0.5, color='white')
        )
    ))

# Add regression line
x_range = np.array([data_complete['delay'].min(), data_complete['delay'].max()])
y_pred = intercept + slope * x_range

fig.add_trace(go.Scatter(
    x=x_range,
    y=y_pred,
    mode='lines',
    name=f'Regression (R²={r_value**2:.3f})',
    line=dict(color='red', width=2, dash='dash'),
    showlegend=True
))

fig.update_layout(
    title=dict(
        text=f'Delay vs Cost Overrun<br><sub>Pearson r={pearson_corr:.3f}, p={pearson_p:.4f}</sub>',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title='Delay (years)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=12),
        title_font=dict(size=14, family='Arial')
    ),
    yaxis=dict(
        title='Cost Overrun (%)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=12),
        title_font=dict(size=14, family='Arial')
    ),
    plot_bgcolor='white',
    width=1000,
    height=700,
    font=dict(family='Arial'),
    legend=dict(
        orientation='v',
        yanchor='top',
        y=0.99,
        xanchor='right',
        x=0.99,
        font=dict(family='Arial', size=11)
    ),
    hovermode='closest'
)

fig.show()

# Analysis by delay categories
print("\n\n" + "="*80)
print("COST OVERRUN BY DELAY CATEGORY")
print("="*80)

# Create delay categories
df_project['delay_category'] = pd.cut(df_project['delay'], 
                                       bins=[-np.inf, 0, 1, 2, 3, np.inf],
                                       labels=['No delay/Early', '0-1 year', '1-2 years', '2-3 years', '>3 years'])

print("\nSummary by delay category:")
for cat in ['No delay/Early', '0-1 year', '1-2 years', '2-3 years', '>3 years']:
    cat_data = df_project[df_project['delay_category'] == cat]['cost_overrun_pct']
    if len(cat_data) > 0:
        print(f"\n{cat} (n={len(cat_data)}):")
        print(f"  Mean cost overrun: {cat_data.mean():.2f}%")
        print(f"  Median cost overrun: {cat_data.median():.2f}%")
        print(f"  Std: {cat_data.std():.2f}%")

# Kruskal-Wallis test across delay categories
print("\n\nKruskal-Wallis Test: Cost overrun across delay categories")
print("-" * 80)

delay_cat_groups = []
for cat in ['No delay/Early', '0-1 year', '1-2 years', '2-3 years', '>3 years']:
    cat_data = df_project[df_project['delay_category'] == cat]['cost_overrun_pct'].dropna()
    if len(cat_data) > 0:
        delay_cat_groups.append(cat_data)

if len(delay_cat_groups) > 1:
    h_stat, p_value = stats.kruskal(*delay_cat_groups)
    print(f"Kruskal-Wallis H-statistic: {h_stat:.3f}")
    print(f"P-value: {p_value:.4f}")
    if p_value < 0.05:
        print("→ Cost overruns are significantly different across delay categories (p < 0.05)")
    else:
        print("→ No significant difference in cost overruns across delay categories (p ≥ 0.05)")

# %%
print("="*80)
print("INVESTIGATING THE COUNTERINTUITIVE RESULT")
print("="*80)

# Check if cost_overrun_pct is calculated correctly
print("\nCost Overrun Calculation Check:")
print("-" * 80)

# Recalculate to verify
df_project['cost_overrun_pct_check'] = ((df_project['totalcost_final_adj'] - df_project['totalcost_initial_adj']) / df_project['totalcost_initial_adj']) * 100

print(f"Original cost_overrun_pct mean: {df_project['cost_overrun_pct'].mean():.2f}%")
print(f"Recalculated mean: {df_project['cost_overrun_pct_check'].mean():.2f}%")

# Check distribution
print("\n\nCost Overrun Distribution:")
print("-" * 80)
print(f"Negative cost overrun (cost savings): {(df_project['cost_overrun_pct'] < 0).sum()} projects ({(df_project['cost_overrun_pct'] < 0).sum()/len(df_project)*100:.1f}%)")
print(f"Positive cost overrun (cost increase): {(df_project['cost_overrun_pct'] > 0).sum()} projects ({(df_project['cost_overrun_pct'] > 0).sum()/len(df_project)*100:.1f}%)")
print(f"Exactly 0: {(df_project['cost_overrun_pct'] == 0).sum()} projects")

# Check actual cost values
print("\n\nCost Values Check:")
print("-" * 80)
print(f"Initial cost mean: ${df_project['totalcost_initial_adj'].mean():.2f}M")
print(f"Final cost mean: ${df_project['totalcost_final_adj'].mean():.2f}M")
print(f"Difference: ${(df_project['totalcost_final_adj'] - df_project['totalcost_initial_adj']).mean():.2f}M")

# Look at extreme cases
print("\n\nExtreme Cases:")
print("-" * 80)

print("\nProjects with longest delays:")
top_delays = df_project.nlargest(5, 'delay')[['delay', 'cost_overrun_pct', 'totalcost_initial_adj', 'totalcost_final_adj']]
print(top_delays)

print("\n\nProjects with highest cost overruns:")
top_overruns = df_project.nlargest(5, 'cost_overrun_pct')[['delay', 'cost_overrun_pct', 'totalcost_initial_adj', 'totalcost_final_adj']]
print(top_overruns)

print("\n\nProjects with most cost savings (negative overrun):")
top_savings = df_project.nsmallest(5, 'cost_overrun_pct')[['delay', 'cost_overrun_pct', 'totalcost_initial_adj', 'totalcost_final_adj']]
print(top_savings)

# Possible explanation: Are costs in constant dollars?
print("\n\n" + "="*80)
print("HYPOTHESIS: Costs Adjusted for Inflation?")
print("="*80)
print("\nIf costs are inflation-adjusted to constant dollars:")
print("- Initial costs: estimated in approval year dollars")
print("- Final costs: converted back to approval year dollars (removing inflation)")
print("- Longer delays → more years of inflation removed")
print("- Final costs in real terms appear LOWER than initial estimates")
print("- This creates the counterintuitive negative correlation")

print("\n\nCheck: Compare raw vs adjusted costs")
if 'totalcost_initial' in df_project.columns and 'totalcost_final' in df_project.columns:
    print("\nRaw (nominal) costs:")
    df_project['cost_overrun_nominal'] = ((df_project['totalcost_final'] - df_project['totalcost_initial']) / df_project['totalcost_initial']) * 100
    print(f"Mean nominal cost overrun: {df_project['cost_overrun_nominal'].mean():.2f}%")
    
    # Correlation with delay using nominal costs
    data_nominal = df_project[['delay', 'cost_overrun_nominal']].dropna()
    if len(data_nominal) > 0:
        corr_nominal, p_nominal = stats.pearsonr(data_nominal['delay'], data_nominal['cost_overrun_nominal'])
        print(f"Correlation (delay vs nominal overrun): {corr_nominal:.3f} (p={p_nominal:.4f})")
        
        if corr_nominal > 0:
            print("→ Using NOMINAL costs: Longer delays ARE associated with higher cost overruns!")
        
    print("\nAdjusted (real) costs:")
    print(f"Mean adjusted cost overrun: {df_project['cost_overrun_pct'].mean():.2f}%")
else:
    print("\nRaw cost columns not available for comparison")
    print("Column names in dataset:", [col for col in df_project.columns if 'cost' in col.lower()])

# Alternative: Use absolute cost change instead of percentage
print("\n\n" + "="*80)
print("ALTERNATIVE ANALYSIS: Absolute Cost Change")
print("="*80)

df_project['cost_change_abs'] = df_project['totalcost_final_adj'] - df_project['totalcost_initial_adj']

print(f"Mean absolute cost change: ${df_project['cost_change_abs'].mean():.2f}M")
print(f"Median absolute cost change: ${df_project['cost_change_abs'].median():.2f}M")

data_abs = df_project[['delay', 'cost_change_abs']].dropna()
corr_abs, p_abs = stats.pearsonr(data_abs['delay'], data_abs['cost_change_abs'])
print(f"\nCorrelation (delay vs absolute cost change): {corr_abs:.3f} (p={p_abs:.4f})")

if p_abs < 0.05:
    if corr_abs > 0:
        print("→ Longer delays associated with higher absolute cost increases")
    else:
        print("→ Longer delays associated with lower absolute costs")
else:
    print("→ No significant relationship")

# Check by delay categories
print("\n\n" + "="*80)
print("COST OVERRUN BY DELAY QUARTILES")
print("="*80)

df_project['delay_quartile'] = pd.qcut(df_project['delay'], q=4, labels=['Q1 (Shortest)', 'Q2', 'Q3', 'Q4 (Longest)'], duplicates='drop')

for q in df_project['delay_quartile'].unique():
    q_data = df_project[df_project['delay_quartile'] == q]
    print(f"\n{q}:")
    print(f"  Delay range: {q_data['delay'].min():.2f} to {q_data['delay'].max():.2f} years")
    print(f"  Mean cost overrun: {q_data['cost_overrun_pct'].mean():.2f}%")
    print(f"  n={len(q_data)}")

# %%
from scipy import stats

# Create binary size category: non-mega vs mega
df_project['size_binary'] = df_project['project_size'].map({
    'medium': 'Non-Mega (<$1B)',
    'large': 'Non-Mega (<$1B)',
    'mega': 'Mega (≥$1B)'
})

print("="*80)
print("INTERACTION EFFECTS: PROJECT SIZE (Non-Mega vs Mega) × RISK LEVEL")
print("="*80)

# Summary table
print("\nSUMMARY TABLE: Mean Delay (years)")
print("-" * 80)
print(f"{'Size':<20} {'Risk 0':<20} {'Risk 1':<20} {'Risk 2':<20}")
print("-" * 80)

for size in ['Non-Mega (<$1B)', 'Mega (≥$1B)']:
    row = f"{size:<20}"
    for risk_level in [0, 1, 2]:
        data = df_project[(df_project['size_binary'] == size) & 
                          (df_project['risk_level'] == risk_level)]
        if len(data) > 0:
            row += f"{data['delay'].mean():.2f}y (n={len(data):<3})    "
        else:
            row += f"{'N/A':<20}"
    print(row)

# Detailed statistics
print("\n\nDETAILED STATISTICS BY SIZE AND RISK LEVEL")
print("="*80)

for size in ['Non-Mega (<$1B)', 'Mega (≥$1B)']:
    print(f"\n{size.upper()} PROJECTS:")
    print("-" * 80)
    
    for risk_level in [0, 1, 2]:
        data = df_project[(df_project['size_binary'] == size) & 
                          (df_project['risk_level'] == risk_level)]
        if len(data) > 0:
            risk_label = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}[risk_level]
            print(f"\n  {risk_label} (Level {risk_level}):")
            print(f"    n = {len(data)}")
            print(f"    Mean delay: {data['delay'].mean():.2f} years")
            print(f"    Median delay: {data['delay'].median():.2f} years")
            print(f"    Std: {data['delay'].std():.2f} years")

# Statistical test: Is there an interaction effect?
print("\n\n" + "="*80)
print("STATISTICAL TEST: Two-Way Analysis (Size × Risk Level)")
print("="*80)

# For each size, test if risk levels differ
print("\nWithin each size category:")
for size in ['Non-Mega (<$1B)', 'Mega (≥$1B)']:
    size_data = df_project[df_project['size_binary'] == size]
    groups = []
    for risk_level in [0, 1, 2]:
        group_data = size_data[size_data['risk_level'] == risk_level]['delay'].dropna()
        if len(group_data) > 0:
            groups.append(group_data)
    
    if len(groups) > 1:
        h_stat, p_value = stats.kruskal(*groups)
        print(f"\n{size}: H={h_stat:.3f}, p={p_value:.4f}")
        if p_value < 0.05:
            print(f"  → Risk level significantly affects delay in {size} projects")
        else:
            print(f"  → Risk level does NOT significantly affect delay in {size} projects")

# Test if size effect differs by risk level
print("\n\nWithin each risk level:")
for risk_level in [0, 1, 2]:
    risk_label = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}[risk_level]
    
    nonmega_data = df_project[(df_project['size_binary'] == 'Non-Mega (<$1B)') & 
                               (df_project['risk_level'] == risk_level)]['delay'].dropna()
    mega_data = df_project[(df_project['size_binary'] == 'Mega (≥$1B)') & 
                            (df_project['risk_level'] == risk_level)]['delay'].dropna()
    
    if len(nonmega_data) > 0 and len(mega_data) > 0:
        u_stat, p_value = stats.mannwhitneyu(nonmega_data, mega_data, alternative='two-sided')
        print(f"\n{risk_label} (Level {risk_level}): U={u_stat:.3f}, p={p_value:.4f}")
        if p_value < 0.05:
            if nonmega_data.median() > mega_data.median():
                print(f"  → Non-Mega projects have longer delays (median: {nonmega_data.median():.2f}y vs {mega_data.median():.2f}y)")
            else:
                print(f"  → Mega projects have longer delays (median: {mega_data.median():.2f}y vs {nonmega_data.median():.2f}y)")
        else:
            print(f"  → No significant size difference in delays")

# Visualization: Grouped bar chart
print("\n\nVISUALIZATION")
print("="*80 + "\n")

fig = go.Figure()

risk_level_colors = {0: '#fcc5c0', 1: '#fa9fb5', 2: '#c51b8a'}
risk_level_labels = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}

for risk_level in [0, 1, 2]:
    delays_by_size = []
    for size in ['Non-Mega (<$1B)', 'Mega (≥$1B)']:
        data = df_project[(df_project['size_binary'] == size) & 
                          (df_project['risk_level'] == risk_level)]
        delays_by_size.append(data['delay'].mean() if len(data) > 0 else 0)
    
    fig.add_trace(go.Bar(
        x=['Non-Mega (<$1B)', 'Mega (≥$1B)'],
        y=delays_by_size,
        name=risk_level_labels[risk_level],
        marker=dict(color=risk_level_colors[risk_level], line=dict(width=0)),
        text=[f'{val:.2f}y' if val > 0 else 'N/A' for val in delays_by_size],
        textposition='auto',
        textfont=dict(size=11, color='white', family='Arial')
    ))

fig.update_layout(
    title=dict(
        text='Mean Delay by Project Size and Risk Level',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title='Project Size',
        tickfont=dict(family='Arial', size=12),
        title_font=dict(size=14, family='Arial')
    ),
    yaxis=dict(
        title='Mean Delay (years)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=12),
        title_font=dict(size=14, family='Arial')
    ),
    barmode='group',
    plot_bgcolor='white',
    width=900,
    height=600,
    font=dict(family='Arial'),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5,
        font=dict(family='Arial', size=11)
    )
)

fig.show()

# %%
print("\n\n" + "="*80)
print("REGIONAL ANALYSIS: DELAY BY REGION")
print("="*80)

# Check if region column exists
if 'region' in df_project.columns:
    print("\nREGION SUMMARY STATISTICS")
    print("-" * 80)
    
    # Get unique regions
    regions = df_project['region'].unique()
    print(f"\nNumber of regions: {len(regions)}")
    print(f"Regions: {sorted(regions)}\n")
    
    # Summary by region
    for region in sorted(df_project['region'].unique()):
        region_data = df_project[df_project['region'] == region]
        print(f"\n{region} (n={len(region_data)}):")
        print(f"  Mean delay: {region_data['delay'].mean():.2f} years")
        print(f"  Median delay: {region_data['delay'].median():.2f} years")
        print(f"  Std: {region_data['delay'].std():.2f} years")
        
        # Risk distribution in this region
        print(f"  Risk distribution:")
        for risk_level in [0, 1, 2]:
            count = (region_data['risk_level'] == risk_level).sum()
            pct = (count / len(region_data) * 100) if len(region_data) > 0 else 0
            print(f"    Level {risk_level}: {count} ({pct:.1f}%)")
    
    # Statistical test: Do regions differ?
    print("\n\nKRUSKAL-WALLIS TEST: Delays across regions")
    print("-" * 80)
    
    region_groups = []
    region_names = []
    for region in df_project['region'].unique():
        region_data = df_project[df_project['region'] == region]['delay'].dropna()
        if len(region_data) > 5:  # Only include regions with sufficient data
            region_groups.append(region_data)
            region_names.append(region)
    
    if len(region_groups) > 1:
        h_stat, p_value = stats.kruskal(*region_groups)
        print(f"Kruskal-Wallis H-statistic: {h_stat:.3f}")
        print(f"P-value: {p_value:.4f}")
        if p_value < 0.05:
            print("→ Delays are significantly different across regions (p < 0.05)")
        else:
            print("→ No significant difference in delays across regions (p ≥ 0.05)")
    
    # Visualization: Box plot by region
    print("\n\nVISUALIZATION")
    print("="*80 + "\n")
    
    fig = go.Figure()
    
    for region in sorted(df_project['region'].unique()):
        region_data = df_project[df_project['region'] == region]
        
        fig.add_trace(go.Box(
            y=region_data['delay'],
            name=region,
            boxmean='sd',
            marker=dict(opacity=0.7),
            line=dict(width=2)
        ))
    
    fig.update_layout(
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
        width=1200,
        height=600,
        font=dict(family='Arial'),
        showlegend=False
    )
    
    fig.show()
    
else:
    print("\nRegion column not found in dataset.")
    print("Available columns:", df_project.columns.tolist())

# %%
print("="*80)
print("MEGA PROJECTS: SINGLE RISK TYPE ANALYSIS")
print("="*80)

# Filter to mega projects with single risk (Level 1)
mega_single_risk = df_project[(df_project['size_binary'] == 'Mega (≥$1B)') & 
                               (df_project['risk_level'] == 1)]

print(f"\nTotal Mega projects with single risk: {len(mega_single_risk)}")

# Break down by risk category
print("\nBreakdown by risk type:")
print("-" * 80)

for risk_cat in ['Environmental Only', 'Social Only']:
    cat_data = mega_single_risk[mega_single_risk['risk_category'] == risk_cat]
    if len(cat_data) > 0:
        print(f"\n{risk_cat}:")
        print(f"  n = {len(cat_data)}")
        print(f"  Mean delay: {cat_data['delay'].mean():.2f} years")
        print(f"  Median delay: {cat_data['delay'].median():.2f} years")
        print(f"  Std: {cat_data['delay'].std():.2f} years")

# Statistical test
env_only = mega_single_risk[mega_single_risk['risk_category'] == 'Environmental Only']['delay'].dropna()
soc_only = mega_single_risk[mega_single_risk['risk_category'] == 'Social Only']['delay'].dropna()

if len(env_only) > 0 and len(soc_only) > 0:
    u_stat, p_value = stats.mannwhitneyu(env_only, soc_only, alternative='two-sided')
    print(f"\n\nMann-Whitney U Test:")
    print(f"U-statistic: {u_stat:.3f}")
    print(f"P-value: {p_value:.4f}")
    if p_value < 0.05:
        if env_only.median() > soc_only.median():
            print(f"→ Environmental Only risks cause significantly longer delays")
            print(f"   (median: {env_only.median():.2f}y vs {soc_only.median():.2f}y)")
        else:
            print(f"→ Social Only risks cause significantly longer delays")
            print(f"   (median: {soc_only.median():.2f}y vs {env_only.median():.2f}y)")
    else:
        print(f"→ No significant difference between Environmental Only and Social Only")

# Compare to Non-Mega single risk
print("\n\n" + "="*80)
print("COMPARISON: Mega vs Non-Mega Single Risk Projects")
print("="*80)

nonmega_single_risk = df_project[(df_project['size_binary'] == 'Non-Mega (<$1B)') & 
                                  (df_project['risk_level'] == 1)]

print("\nNon-Mega projects with single risk:")
print(f"Total: {len(nonmega_single_risk)}")

for risk_cat in ['Environmental Only', 'Social Only']:
    cat_data = nonmega_single_risk[nonmega_single_risk['risk_category'] == risk_cat]
    if len(cat_data) > 0:
        print(f"\n{risk_cat}:")
        print(f"  n = {len(cat_data)}")
        print(f"  Mean delay: {cat_data['delay'].mean():.2f} years")
        print(f"  Median delay: {cat_data['delay'].median():.2f} years")

# Visualization
print("\n\nVISUALIZATION")
print("="*80 + "\n")

fig = go.Figure()

risk_cat_colors = {'Environmental Only': '#1b9e77', 'Social Only': '#e6ab02'}

for risk_cat in ['Environmental Only', 'Social Only']:
    delays = []
    for size in ['Non-Mega (<$1B)', 'Mega (≥$1B)']:
        data = df_project[(df_project['size_binary'] == size) & 
                          (df_project['risk_category'] == risk_cat)]
        delays.append(data['delay'].mean() if len(data) > 0 else 0)
    
    fig.add_trace(go.Bar(
        x=['Non-Mega (<$1B)', 'Mega (≥$1B)'],
        y=delays,
        name=risk_cat,
        marker=dict(color=risk_cat_colors[risk_cat], line=dict(width=0)),
        text=[f'{val:.2f}y' if val > 0 else 'N/A' for val in delays],
        textposition='auto',
        textfont=dict(size=11, color='white', family='Arial')
    ))

fig.update_layout(
    title=dict(
        text='Mean Delay: Single Risk Types by Project Size',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title='Project Size',
        tickfont=dict(family='Arial', size=12),
        title_font=dict(size=14, family='Arial')
    ),
    yaxis=dict(
        title='Mean Delay (years)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=12),
        title_font=dict(size=14, family='Arial')
    ),
    barmode='group',
    plot_bgcolor='white',
    width=900,
    height=600,
    font=dict(family='Arial'),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5,
        font=dict(family='Arial', size=11)
    )
)

fig.show()

# %%
print("\n\n" + "="*80)
print("SECTOR ANALYSIS: Size × Risk Level Interaction by Sector")
print("="*80)

sector_colors = {'Energy': '#d95f02', 'Transportation': '#57c4ad', 'Water': '#0571b0'}

for sector in ['Energy', 'Transportation', 'Water']:
    print(f"\n{'='*80}")
    print(f"{sector.upper()} SECTOR")
    print(f"{'='*80}")
    
    sector_data = df_project[df_project['sector1'] == sector]
    
    # Summary table
    print(f"\nMean Delay (years) - {sector}")
    print("-" * 80)
    print(f"{'Size':<20} {'Risk 0':<15} {'Risk 1':<15} {'Risk 2':<15}")
    print("-" * 80)
    
    for size in ['Non-Mega (<$1B)', 'Mega (≥$1B)']:
        row = f"{size:<20}"
        for risk_level in [0, 1, 2]:
            data = sector_data[(sector_data['size_binary'] == size) & 
                              (sector_data['risk_level'] == risk_level)]
            if len(data) > 0:
                row += f"{data['delay'].mean():.2f}y (n={len(data):<2}) "
            else:
                row += f"{'N/A':<15}"
        print(row)
    
    # Test within mega projects of this sector
    mega_sector = sector_data[sector_data['size_binary'] == 'Mega (≥$1B)']
    
    if len(mega_sector) > 10:  # Only test if sufficient data
        groups = []
        for risk_level in [0, 1, 2]:
            group_data = mega_sector[mega_sector['risk_level'] == risk_level]['delay'].dropna()
            if len(group_data) > 0:
                groups.append(group_data)
        
        if len(groups) > 1:
            h_stat, p_value = stats.kruskal(*groups)
            print(f"\nKruskal-Wallis test for Mega {sector} projects:")
            print(f"H-statistic: {h_stat:.3f}, p-value: {p_value:.4f}")
            if p_value < 0.05:
                print(f"→ Risk level significantly affects delay in Mega {sector} projects")
            else:
                print(f"→ Risk level does NOT significantly affect delay in Mega {sector} projects")

# Visualization: Heatmap showing mean delays
print("\n\n" + "="*80)
print("COMPREHENSIVE VISUALIZATION")
print("="*80 + "\n")

# Create data for heatmap
sectors = ['Energy', 'Transportation', 'Water']
sizes = ['Non-Mega (<$1B)', 'Mega (≥$1B)']
risk_levels = [0, 1, 2]

fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=['Energy', 'Transportation', 'Water'],
    horizontal_spacing=0.12
)

for col_idx, sector in enumerate(sectors, start=1):
    sector_data = df_project[df_project['sector1'] == sector]
    
    # Create matrix for heatmap
    z_data = []
    text_data = []
    
    for size in sizes:
        row_data = []
        row_text = []
        for risk_level in risk_levels:
            data = sector_data[(sector_data['size_binary'] == size) & 
                              (sector_data['risk_level'] == risk_level)]
            if len(data) > 0:
                mean_delay = data['delay'].mean()
                row_data.append(mean_delay)
                row_text.append(f'{mean_delay:.2f}y<br>(n={len(data)})')
            else:
                row_data.append(None)
                row_text.append('N/A')
        z_data.append(row_data)
        text_data.append(row_text)
    
    fig.add_trace(
        go.Heatmap(
            z=z_data,
            x=['Risk 0', 'Risk 1', 'Risk 2'],
            y=['Non-Mega', 'Mega'],
            text=text_data,
            texttemplate='%{text}',
            textfont=dict(size=10, family='Arial'),
            colorscale='Reds',
            showscale=(col_idx == 3),
            colorbar=dict(title='Delay<br>(years)', x=1.02) if col_idx == 3 else None
        ),
        row=1, col=col_idx
    )

fig.update_layout(
    title=dict(
        text='Mean Delay by Sector, Size, and Risk Level',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    width=1400,
    height=500,
    font=dict(family='Arial')
)

# Update axes
for col_idx in range(1, 4):
    fig.update_xaxes(title_text='Risk Level', title_font=dict(size=12), row=1, col=col_idx)
    fig.update_yaxes(title_text='Size', title_font=dict(size=12), row=1, col=col_idx)

fig.show()

# %% [markdown]
# # Proceeding with Mega vs. Non-mega

# %%
print("="*80)
print("COMPREHENSIVE ANALYSIS: MEGA vs NON-MEGA PROJECTS")
print("="*80)

# Create binary size category if not already done
df_project['size_binary'] = df_project['project_size'].map({
    'medium': 'Non-Mega (<$1B)',
    'large': 'Non-Mega (<$1B)',
    'mega': 'Mega (≥$1B)'
})

# ============================================================================
# 1. OVERALL COMPARISON
# ============================================================================
print("\n" + "="*80)
print("1. OVERALL COMPARISON")
print("="*80)

print("\nProject Distribution:")
print("-" * 80)
for size in ['Non-Mega (<$1B)', 'Mega (≥$1B)']:
    count = (df_project['size_binary'] == size).sum()
    pct = (count / len(df_project) * 100)
    print(f"{size}: {count} projects ({pct:.1f}%)")

print("\n\nDelay Statistics:")
print("-" * 80)
for size in ['Non-Mega (<$1B)', 'Mega (≥$1B)']:
    size_data = df_project[df_project['size_binary'] == size]
    print(f"\n{size}:")
    print(f"  n = {len(size_data)}")
    print(f"  Mean delay: {size_data['delay'].mean():.2f} years")
    print(f"  Median delay: {size_data['delay'].median():.2f} years")
    print(f"  Std: {size_data['delay'].std():.2f} years")
    print(f"  Min-Max: {size_data['delay'].min():.2f} to {size_data['delay'].max():.2f} years")

# Statistical test
nonmega_delay = df_project[df_project['size_binary'] == 'Non-Mega (<$1B)']['delay'].dropna()
mega_delay = df_project[df_project['size_binary'] == 'Mega (≥$1B)']['delay'].dropna()

u_stat, p_value = stats.mannwhitneyu(nonmega_delay, mega_delay, alternative='two-sided')
print("\n\nMann-Whitney U Test:")
print(f"U-statistic: {u_stat:.3f}")
print(f"P-value: {p_value:.4f}")
if p_value < 0.05:
    if nonmega_delay.median() > mega_delay.median():
        print(f"→ Non-Mega projects have significantly longer delays")
    else:
        print(f"→ Mega projects have significantly longer delays")
else:
    print(f"→ No significant difference in delays between size categories")

# ============================================================================
# 2. BY SECTOR
# ============================================================================
print("\n\n" + "="*80)
print("2. DELAY BY SECTOR AND SIZE")
print("="*80)

print("\nSummary Table:")
print("-" * 80)
print(f"{'Sector':<15} {'Non-Mega (n)':<20} {'Non-Mega Mean':<20} {'Mega (n)':<15} {'Mega Mean':<15}")
print("-" * 80)

for sector in ['Energy', 'Transportation', 'Water']:
    nonmega = df_project[(df_project['sector1'] == sector) & 
                         (df_project['size_binary'] == 'Non-Mega (<$1B)')]
    mega = df_project[(df_project['sector1'] == sector) & 
                      (df_project['size_binary'] == 'Mega (≥$1B)')]
    
    print(f"{sector:<15} n={len(nonmega):<17} {nonmega['delay'].mean():.2f}y{'':<15} n={len(mega):<12} {mega['delay'].mean():.2f}y")

# Test within each sector
print("\n\nStatistical Tests by Sector:")
print("-" * 80)
for sector in ['Energy', 'Transportation', 'Water']:
    nonmega = df_project[(df_project['sector1'] == sector) & 
                         (df_project['size_binary'] == 'Non-Mega (<$1B)')]['delay'].dropna()
    mega = df_project[(df_project['sector1'] == sector) & 
                      (df_project['size_binary'] == 'Mega (≥$1B)')]['delay'].dropna()
    
    if len(nonmega) > 0 and len(mega) > 0:
        u_stat, p_value = stats.mannwhitneyu(nonmega, mega, alternative='two-sided')
        print(f"\n{sector}: U={u_stat:.3f}, p={p_value:.4f}")
        if p_value < 0.05:
            if nonmega.median() > mega.median():
                print(f"  → Non-Mega have longer delays (median: {nonmega.median():.2f}y vs {mega.median():.2f}y)")
            else:
                print(f"  → Mega have longer delays (median: {mega.median():.2f}y vs {nonmega.median():.2f}y)")
        else:
            print(f"  → No significant difference")

# ============================================================================
# 3. BY RISK LEVEL
# ============================================================================
print("\n\n" + "="*80)
print("3. DELAY BY RISK LEVEL AND SIZE")
print("="*80)

risk_level_labels = {0: 'No Risk', 1: 'Single Risk', 2: 'Both Risks'}

print("\nSummary Table:")
print("-" * 80)
print(f"{'Risk Level':<15} {'Non-Mega (n)':<20} {'Non-Mega Mean':<20} {'Mega (n)':<15} {'Mega Mean':<15}")
print("-" * 80)

for risk_level in [0, 1, 2]:
    nonmega = df_project[(df_project['risk_level'] == risk_level) & 
                         (df_project['size_binary'] == 'Non-Mega (<$1B)')]
    mega = df_project[(df_project['risk_level'] == risk_level) & 
                      (df_project['size_binary'] == 'Mega (≥$1B)')]
    
    risk_label = risk_level_labels[risk_level]
    print(f"{risk_label:<15} n={len(nonmega):<17} {nonmega['delay'].mean():.2f}y{'':<15} n={len(mega):<12} {mega['delay'].mean():.2f}y")

# Test within each risk level
print("\n\nStatistical Tests by Risk Level:")
print("-" * 80)
for risk_level in [0, 1, 2]:
    nonmega = df_project[(df_project['risk_level'] == risk_level) & 
                         (df_project['size_binary'] == 'Non-Mega (<$1B)')]['delay'].dropna()
    mega = df_project[(df_project['risk_level'] == risk_level) & 
                      (df_project['size_binary'] == 'Mega (≥$1B)')]['delay'].dropna()
    
    risk_label = risk_level_labels[risk_level]
    if len(nonmega) > 0 and len(mega) > 0:
        u_stat, p_value = stats.mannwhitneyu(nonmega, mega, alternative='two-sided')
        print(f"\n{risk_label} (Level {risk_level}): U={u_stat:.3f}, p={p_value:.4f}")
        if p_value < 0.05:
            if nonmega.median() > mega.median():
                print(f"  → Non-Mega have longer delays (median: {nonmega.median():.2f}y vs {mega.median():.2f}y)")
            else:
                print(f"  → Mega have longer delays (median: {mega.median():.2f}y vs {nonmega.median():.2f}y)")
        else:
            print(f"  → No significant difference")

# ============================================================================
# 4. BY RISK CATEGORY
# ============================================================================
print("\n\n" + "="*80)
print("4. DELAY BY RISK CATEGORY AND SIZE")
print("="*80)

print("\nSummary Table:")
print("-" * 80)
print(f"{'Risk Category':<20} {'Non-Mega (n)':<20} {'Non-Mega Mean':<20} {'Mega (n)':<15} {'Mega Mean':<15}")
print("-" * 80)

for risk_cat in ['No Risk', 'Environmental Only', 'Social Only', 'Both']:
    nonmega = df_project[(df_project['risk_category'] == risk_cat) & 
                         (df_project['size_binary'] == 'Non-Mega (<$1B)')]
    mega = df_project[(df_project['risk_category'] == risk_cat) & 
                      (df_project['size_binary'] == 'Mega (≥$1B)')]
    
    if len(nonmega) > 0 and len(mega) > 0:
        print(f"{risk_cat:<20} n={len(nonmega):<17} {nonmega['delay'].mean():.2f}y{'':<15} n={len(mega):<12} {mega['delay'].mean():.2f}y")

# ============================================================================
# 5. BY RISK SEVERITY (A, B, C)
# ============================================================================
print("\n\n" + "="*80)
print("5. DELAY BY RISK SEVERITY AND SIZE")
print("="*80)

severity_labels = {'A': 'High', 'B': 'Medium', 'C': 'Low'}

for risk_type, col_name in [('Environmental', 'safe_env'), ('Social', 'social_severity')]:
    print(f"\n{risk_type} Risk Severity:")
    print("-" * 80)
    print(f"{'Severity':<15} {'Non-Mega (n)':<20} {'Non-Mega Mean':<20} {'Mega (n)':<15} {'Mega Mean':<15}")
    print("-" * 80)
    
    for severity in ['C', 'B', 'A']:
        nonmega = df_project[(df_project[col_name] == severity) & 
                             (df_project['size_binary'] == 'Non-Mega (<$1B)')]
        mega = df_project[(df_project[col_name] == severity) & 
                          (df_project['size_binary'] == 'Mega (≥$1B)')]
        
        if len(nonmega) > 0 and len(mega) > 0:
            sev_label = f"{severity} ({severity_labels[severity]})"
            print(f"{sev_label:<15} n={len(nonmega):<17} {nonmega['delay'].mean():.2f}y{'':<15} n={len(mega):<12} {mega['delay'].mean():.2f}y")

# ============================================================================
# 6. VISUALIZATIONS
# ============================================================================
print("\n\n" + "="*80)
print("6. VISUALIZATIONS")
print("="*80 + "\n")

# Violin plot: Overall comparison
fig1 = go.Figure()

for size in ['Non-Mega (<$1B)', 'Mega (≥$1B)']:
    size_data = df_project[df_project['size_binary'] == size]
    
    fig1.add_trace(go.Violin(
        y=size_data['delay'],
        x=[size] * len(size_data),
        name=size,
        box_visible=True,
        meanline_visible=True,
        points='all',
        pointpos=-0.5,
        jitter=0.3,
        marker=dict(opacity=0.6),
        scalemode='width',
        width=0.6,
        side='positive',
        line=dict(width=2)
    ))

fig1.update_layout(
    title=dict(
        text='Project Delay Distribution: Mega vs Non-Mega',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title='Project Size',
        tickfont=dict(family='Arial', size=12),
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
    width=800,
    height=600,
    font=dict(family='Arial'),
    showlegend=False
)

fig1.show()

# Grouped bar chart: By Risk Level
fig2 = go.Figure()

risk_level_colors = {0: '#fcc5c0', 1: '#fa9fb5', 2: '#c51b8a'}

for risk_level in [0, 1, 2]:
    delays = []
    for size in ['Non-Mega (<$1B)', 'Mega (≥$1B)']:
        data = df_project[(df_project['size_binary'] == size) & 
                          (df_project['risk_level'] == risk_level)]
        delays.append(data['delay'].mean() if len(data) > 0 else 0)
    
    fig2.add_trace(go.Bar(
        x=['Non-Mega', 'Mega'],
        y=delays,
        name=risk_level_labels[risk_level],
        marker=dict(color=risk_level_colors[risk_level], line=dict(width=0)),
        text=[f'{val:.2f}y' for val in delays],
        textposition='auto',
        textfont=dict(size=11, color='white', family='Arial')
    ))

fig2.update_layout(
    title=dict(
        text='Mean Delay by Project Size and Risk Level',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title='Project Size',
        tickfont=dict(family='Arial', size=12),
        title_font=dict(size=14, family='Arial')
    ),
    yaxis=dict(
        title='Mean Delay (years)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=12),
        title_font=dict(size=14, family='Arial')
    ),
    barmode='group',
    plot_bgcolor='white',
    width=900,
    height=600,
    font=dict(family='Arial'),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5
    )
)

fig2.show()

# %%
# Deep dive into the Single Risk / Mega combination
print("="*80)
print("DEEP DIVE: MEGA PROJECTS WITH SINGLE RISK")
print("="*80)

mega_single = df_project[(df_project['size_binary'] == 'Mega (≥$1B)') & 
                         (df_project['risk_level'] == 1)]

print(f"\nTotal: {len(mega_single)} projects")
print(f"Mean delay: {mega_single['delay'].mean():.2f} years")

# By sector
print("\nBy Sector:")
for sector in ['Energy', 'Transportation', 'Water']:
    data = mega_single[mega_single['sector1'] == sector]
    if len(data) > 0:
        print(f"  {sector}: n={len(data)}, mean={data['delay'].mean():.2f}y")

# Environmental vs Social only
print("\nEnvironmental Only vs Social Only:")
env_only = mega_single[mega_single['risk_category'] == 'Environmental Only']
soc_only = mega_single[mega_single['risk_category'] == 'Social Only']
print(f"  Environmental Only: n={len(env_only)}, mean={env_only['delay'].mean():.2f}y")
print(f"  Social Only: n={len(soc_only)}, mean={soc_only['delay'].mean():.2f}y" if len(soc_only) > 0 else "  Social Only: No projects")

# %%
print("="*80)
print("COMPREHENSIVE ANALYSIS: BY RISK TYPE (ENVIRONMENTAL vs SOCIAL)")
print("="*80)

# ============================================================================
# 1. OVERALL COMPARISON BY RISK TYPE
# ============================================================================
print("\n" + "="*80)
print("1. OVERALL DELAY BY RISK TYPE")
print("="*80)

print("\nProject Distribution:")
print("-" * 80)
print(f"Environmental Risk (env_risk=1): {df_project['env_risk'].sum()} projects ({df_project['env_risk'].sum()/len(df_project)*100:.1f}%)")
print(f"Social Risk (soc_risk=1): {df_project['soc_risk'].sum()} projects ({df_project['soc_risk'].sum()/len(df_project)*100:.1f}%)")
print(f"Both Risks: {((df_project['env_risk']==1) & (df_project['soc_risk']==1)).sum()} projects")
print(f"No Risks: {((df_project['env_risk']==0) & (df_project['soc_risk']==0)).sum()} projects")

print("\n\nDelay Statistics:")
print("-" * 80)

# Environmental Risk
env_yes = df_project[df_project['env_risk'] == 1]
env_no = df_project[df_project['env_risk'] == 0]

print("\nENVIRONMENTAL RISK:")
print(f"  With Env Risk (n={len(env_yes)}): mean={env_yes['delay'].mean():.2f}y, median={env_yes['delay'].median():.2f}y")
print(f"  No Env Risk (n={len(env_no)}): mean={env_no['delay'].mean():.2f}y, median={env_no['delay'].median():.2f}y")

u_stat, p_value = stats.mannwhitneyu(env_yes['delay'].dropna(), env_no['delay'].dropna(), alternative='two-sided')
print(f"  Mann-Whitney U: {u_stat:.3f}, p={p_value:.4f}")
if p_value < 0.05:
    print(f"  → Environmental risk significantly affects delay")
else:
    print(f"  → No significant effect of environmental risk on delay")

# Social Risk
soc_yes = df_project[df_project['soc_risk'] == 1]
soc_no = df_project[df_project['soc_risk'] == 0]

print("\nSOCIAL RISK:")
print(f"  With Soc Risk (n={len(soc_yes)}): mean={soc_yes['delay'].mean():.2f}y, median={soc_yes['delay'].median():.2f}y")
print(f"  No Soc Risk (n={len(soc_no)}): mean={soc_no['delay'].mean():.2f}y, median={soc_no['delay'].median():.2f}y")

u_stat, p_value = stats.mannwhitneyu(soc_yes['delay'].dropna(), soc_no['delay'].dropna(), alternative='two-sided')
print(f"  Mann-Whitney U: {u_stat:.3f}, p={p_value:.4f}")
if p_value < 0.05:
    print(f"  → Social risk significantly affects delay")
else:
    print(f"  → No significant effect of social risk on delay")

# ============================================================================
# 2. BY PROJECT SIZE (MEGA vs NON-MEGA)
# ============================================================================
print("\n\n" + "="*80)
print("2. RISK TYPE BY PROJECT SIZE")
print("="*80)

print("\nENVIRONMENTAL RISK:")
print("-" * 80)
print(f"{'Size':<20} {'With Env Risk':<25} {'Without Env Risk':<25} {'p-value':<10}")
print("-" * 80)

for size in ['Non-Mega (<$1B)', 'Mega (≥$1B)']:
    with_env = df_project[(df_project['size_binary'] == size) & (df_project['env_risk'] == 1)]
    without_env = df_project[(df_project['size_binary'] == size) & (df_project['env_risk'] == 0)]
    
    if len(with_env) > 0 and len(without_env) > 0:
        u_stat, p_value = stats.mannwhitneyu(with_env['delay'].dropna(), without_env['delay'].dropna(), alternative='two-sided')
        print(f"{size:<20} {with_env['delay'].mean():.2f}y (n={len(with_env):<3})       {without_env['delay'].mean():.2f}y (n={len(without_env):<3})       {p_value:.4f}")

print("\n\nSOCIAL RISK:")
print("-" * 80)
print(f"{'Size':<20} {'With Soc Risk':<25} {'Without Soc Risk':<25} {'p-value':<10}")
print("-" * 80)

for size in ['Non-Mega (<$1B)', 'Mega (≥$1B)']:
    with_soc = df_project[(df_project['size_binary'] == size) & (df_project['soc_risk'] == 1)]
    without_soc = df_project[(df_project['size_binary'] == size) & (df_project['soc_risk'] == 0)]
    
    if len(with_soc) > 0 and len(without_soc) > 0:
        u_stat, p_value = stats.mannwhitneyu(with_soc['delay'].dropna(), without_soc['delay'].dropna(), alternative='two-sided')
        print(f"{size:<20} {with_soc['delay'].mean():.2f}y (n={len(with_soc):<3})       {without_soc['delay'].mean():.2f}y (n={len(without_soc):<3})       {p_value:.4f}")

# ============================================================================
# 3. BY SECTOR
# ============================================================================
print("\n\n" + "="*80)
print("3. RISK TYPE BY SECTOR")
print("="*80)

for risk_type, risk_col in [('ENVIRONMENTAL', 'env_risk'), ('SOCIAL', 'soc_risk')]:
    print(f"\n{risk_type} RISK:")
    print("-" * 80)
    print(f"{'Sector':<15} {'With Risk':<25} {'Without Risk':<25} {'p-value':<10}")
    print("-" * 80)
    
    for sector in ['Energy', 'Transportation', 'Water']:
        with_risk = df_project[(df_project['sector1'] == sector) & (df_project[risk_col] == 1)]
        without_risk = df_project[(df_project['sector1'] == sector) & (df_project[risk_col] == 0)]
        
        if len(with_risk) > 0 and len(without_risk) > 0:
            u_stat, p_value = stats.mannwhitneyu(with_risk['delay'].dropna(), without_risk['delay'].dropna(), alternative='two-sided')
            print(f"{sector:<15} {with_risk['delay'].mean():.2f}y (n={len(with_risk):<3})       {without_risk['delay'].mean():.2f}y (n={len(without_risk):<3})       {p_value:.4f}")

# ============================================================================
# 4. INTERACTION: SIZE × RISK TYPE
# ============================================================================
print("\n\n" + "="*80)
print("4. INTERACTION: PROJECT SIZE × RISK TYPE")
print("="*80)

print("\nSummary Table - Mean Delay (years):")
print("-" * 80)
print(f"{'Risk Type':<25} {'Non-Mega':<20} {'Mega':<20} {'Difference':<15}")
print("-" * 80)

# Environmental Risk
nonmega_env = df_project[(df_project['size_binary'] == 'Non-Mega (<$1B)') & (df_project['env_risk'] == 1)]
mega_env = df_project[(df_project['size_binary'] == 'Mega (≥$1B)') & (df_project['env_risk'] == 1)]
diff_env = mega_env['delay'].mean() - nonmega_env['delay'].mean()
print(f"{'Environmental Risk':<25} {nonmega_env['delay'].mean():.2f}y (n={len(nonmega_env):<3})   {mega_env['delay'].mean():.2f}y (n={len(mega_env):<3})   {diff_env:+.2f}y")

# Social Risk
nonmega_soc = df_project[(df_project['size_binary'] == 'Non-Mega (<$1B)') & (df_project['soc_risk'] == 1)]
mega_soc = df_project[(df_project['size_binary'] == 'Mega (≥$1B)') & (df_project['soc_risk'] == 1)]
diff_soc = mega_soc['delay'].mean() - nonmega_soc['delay'].mean()
print(f"{'Social Risk':<25} {nonmega_soc['delay'].mean():.2f}y (n={len(nonmega_soc):<3})   {mega_soc['delay'].mean():.2f}y (n={len(mega_soc):<3})   {diff_soc:+.2f}y")

# No Risk
nonmega_norisk = df_project[(df_project['size_binary'] == 'Non-Mega (<$1B)') & (df_project['env_risk'] == 0) & (df_project['soc_risk'] == 0)]
mega_norisk = df_project[(df_project['size_binary'] == 'Mega (≥$1B)') & (df_project['env_risk'] == 0) & (df_project['soc_risk'] == 0)]
if len(nonmega_norisk) > 0 and len(mega_norisk) > 0:
    diff_norisk = mega_norisk['delay'].mean() - nonmega_norisk['delay'].mean()
    print(f"{'No Risk':<25} {nonmega_norisk['delay'].mean():.2f}y (n={len(nonmega_norisk):<3})   {mega_norisk['delay'].mean():.2f}y (n={len(mega_norisk):<3})   {diff_norisk:+.2f}y")

# Statistical tests
print("\n\nStatistical Tests:")
print("-" * 80)

print("\nEnvironmental Risk:")
if len(nonmega_env) > 0 and len(mega_env) > 0:
    u_stat, p_value = stats.mannwhitneyu(nonmega_env['delay'].dropna(), mega_env['delay'].dropna(), alternative='two-sided')
    print(f"  Non-Mega vs Mega: U={u_stat:.3f}, p={p_value:.4f}")
    if p_value < 0.05:
        print(f"  → Significant difference in delays")
    else:
        print(f"  → No significant difference")

print("\nSocial Risk:")
if len(nonmega_soc) > 0 and len(mega_soc) > 0:
    u_stat, p_value = stats.mannwhitneyu(nonmega_soc['delay'].dropna(), mega_soc['delay'].dropna(), alternative='two-sided')
    print(f"  Non-Mega vs Mega: U={u_stat:.3f}, p={p_value:.4f}")
    if p_value < 0.05:
        print(f"  → Significant difference in delays")
    else:
        print(f"  → No significant difference")

# ============================================================================
# 5. VISUALIZATIONS
# ============================================================================
print("\n\n" + "="*80)
print("5. VISUALIZATIONS")
print("="*80 + "\n")

# Visualization 1: Violin plots by risk type
fig1 = make_subplots(
    rows=1, cols=2,
    subplot_titles=['Environmental Risk', 'Social Risk'],
    horizontal_spacing=0.15
)

# Environmental Risk
for has_risk in [0, 1]:
    data = df_project[df_project['env_risk'] == has_risk]
    label = 'With Env Risk' if has_risk == 1 else 'No Env Risk'
    
    fig1.add_trace(
        go.Violin(
            y=data['delay'],
            x=[label] * len(data),
            name=label,
            box_visible=True,
            meanline_visible=True,
            points='all',
            pointpos=-0.5,
            jitter=0.3,
            marker=dict(color='#1b9e77' if has_risk == 1 else '#fee5d9'),
            scalemode='width',
            width=0.6,
            side='positive',
            line=dict(width=2),
            showlegend=False
        ),
        row=1, col=1
    )

# Social Risk
for has_risk in [0, 1]:
    data = df_project[df_project['soc_risk'] == has_risk]
    label = 'With Soc Risk' if has_risk == 1 else 'No Soc Risk'
    
    fig1.add_trace(
        go.Violin(
            y=data['delay'],
            x=[label] * len(data),
            name=label,
            box_visible=True,
            meanline_visible=True,
            points='all',
            pointpos=-0.5,
            jitter=0.3,
            marker=dict(color='#e6ab02' if has_risk == 1 else '#fee5d9'),
            scalemode='width',
            width=0.6,
            side='positive',
            line=dict(width=2),
            showlegend=False
        ),
        row=1, col=2
    )

fig1.update_layout(
    title=dict(
        text='Project Delay by Risk Type',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='white',
    width=1200,
    height=600,
    font=dict(family='Arial')
)

for col_idx in range(1, 3):
    fig1.update_xaxes(tickfont=dict(family='Arial', size=11), row=1, col=col_idx)
    fig1.update_yaxes(
        title='Delay (years)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=11),
        row=1, col=col_idx
    )

fig1.show()

# Visualization 2: Grouped bar chart - Size × Risk Type
fig2 = go.Figure()

risk_data = [
    ('Env Risk', '#1b9e77'),
    ('Soc Risk', '#e6ab02'),
    ('No Risk', '#fee5d9')
]

for risk_label, color in risk_data:
    delays = []
    for size in ['Non-Mega (<$1B)', 'Mega (≥$1B)']:
        if risk_label == 'Env Risk':
            data = df_project[(df_project['size_binary'] == size) & (df_project['env_risk'] == 1)]
        elif risk_label == 'Soc Risk':
            data = df_project[(df_project['size_binary'] == size) & (df_project['soc_risk'] == 1)]
        else:  # No Risk
            data = df_project[(df_project['size_binary'] == size) & 
                             (df_project['env_risk'] == 0) & (df_project['soc_risk'] == 0)]
        delays.append(data['delay'].mean() if len(data) > 0 else 0)
    
    fig2.add_trace(go.Bar(
        x=['Non-Mega', 'Mega'],
        y=delays,
        name=risk_label,
        marker=dict(color=color, line=dict(width=0)),
        text=[f'{val:.2f}y' for val in delays],
        textposition='auto',
        textfont=dict(size=11, color='white', family='Arial')
    ))

fig2.update_layout(
    title=dict(
        text='Mean Delay by Project Size and Risk Type',
        font=dict(size=18, family='Arial', color='black'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title='Project Size',
        tickfont=dict(family='Arial', size=12),
        title_font=dict(size=14, family='Arial')
    ),
    yaxis=dict(
        title='Mean Delay (years)',
        gridcolor='lightgray',
        gridwidth=0.5,
        tickfont=dict(family='Arial', size=12),
        title_font=dict(size=14, family='Arial')
    ),
    barmode='group',
    plot_bgcolor='white',
    width=900,
    height=600,
    font=dict(family='Arial'),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5
    )
)

fig2.show()

# %% [markdown]
# # Draft for streamlit app

# %%
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import numpy as np

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
    # CHANGE THIS to your actual file path
    df = pd.read_csv('adb_clean_416.csv')
    
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
    
    return df

df = load_data()

# Sidebar
st.sidebar.title("🏗️ Infrastructure Project Risk Analysis")
st.sidebar.markdown("---")
st.sidebar.info(
    """
    Analysis of Asian Development Bank infrastructure projects examining
    how project size and risk interact to affect delays.
    
    **Key Focus**: Mega vs Non-Mega projects
    """
)

# Color schemes (consistent across all charts)
sector_colors = {'Energy': '#d95f02', 'Transportation': '#57c4ad', 'Water': '#0571b0'}
risk_level_colors = {0: '#fcc5c0', 1: '#fa9fb5', 2: '#c51b8a'}
size_colors = {'medium': '#dfe318', 'large': '#8bd646', 'mega': '#2fb47c'}

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🏭 Sector Analysis",
    "📏 Size & Risk",
    "🔍 Key Findings",
    "📋 Data"
])

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================
with tab1:
    st.title("📊 Project Overview")
    
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
    st.subheader("🗺️ Geographic Distribution")
    
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
    st.subheader("🌏 Projects by Country and Sector")
    
    # Aggregate by country AND sector
    country_sector_data = df.groupby(['countryname', 'sector1']).agg({
        'projectid': 'count',
        'totalcost_initial_adj': 'sum'
    }).reset_index()
    country_sector_data.columns = ['country', 'sector', 'project_count', 'total_cost']
    
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
        "Lao People's Democratic Republic": (19.8563, 102.4955),
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
        'Micronesia, Federated States of': (7.4256, 150.5508),
        'Nauru': (-0.5228, 166.9315),
        'Palau': (7.5150, 134.5825),
        'Papua New Guinea': (-6.3150, 143.9555),
        'Samoa': (-13.7590, -172.1046),
        'Solomon Islands': (-9.6457, 160.1562),
        'Tonga': (-21.1789, -175.1982),
        'Tuvalu': (-7.1095, 177.6493),
        'Vanuatu': (-15.3767, 166.9592)
    }
    
    # Add coordinates
    np.random.seed(42)
    country_sector_data['lat'] = country_sector_data['country'].map(lambda x: country_coords.get(x, (None, None))[0])
    country_sector_data['lon'] = country_sector_data['country'].map(lambda x: country_coords.get(x, (None, None))[1])
    
    # Add small random offset to prevent exact overlap
    country_sector_data['lat'] = country_sector_data['lat'] + np.random.uniform(-0.3, 0.3, len(country_sector_data))
    country_sector_data['lon'] = country_sector_data['lon'] + np.random.uniform(-0.3, 0.3, len(country_sector_data))
    
    country_sector_data = country_sector_data.dropna(subset=['lat', 'lon'])
    
    fig_bubble = px.scatter_geo(
        country_sector_data,
        lat='lat',
        lon='lon',
        size='project_count',
        color='sector',
        hover_name='country',
        hover_data={
            'sector': True,
            'project_count': True, 
            'total_cost': ':.2f',
            'lat': False, 
            'lon': False
        },
        color_discrete_map=sector_colors,
        title='Geographic Distribution of Projects by Country and Sector',
        size_max=40,
        labels={'project_count': 'Projects', 'total_cost': 'Total Cost (M USD)', 'sector': 'Sector'}
    )
    
    fig_bubble.update_geos(
        scope='asia',
        projection_type='natural earth',
        showland=True,
        landcolor='rgb(243, 243, 243)',
        coastlinecolor='rgb(204, 204, 204)',
        showcountries=True,
        countrycolor='rgb(204, 204, 204)',
        center=dict(lat=15, lon=100)
    )
    
    fig_bubble.update_layout(
        height=700,
        font=dict(family='Arial')
    )
    
    st.plotly_chart(fig_bubble, use_container_width=True)
    
    st.markdown("---")
    
    # Distribution charts
    st.subheader("📊 Project Distribution")
    
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
            x=sector_counts.index,
            y=sector_counts.values,
            marker=dict(
                color=[sector_colors.get(sector, '#95a5a6') for sector in sector_counts.index], 
                line=dict(width=0)
            ),
            text=sector_counts.values,
            textposition='auto',
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
                x=regions,
                y=sector_by_region.values,
                name=sector,
                marker=dict(color=sector_colors[sector], line=dict(width=0)),
                showlegend=True,
                legendgroup='sector'
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
            x=0.5,
            xanchor='center'
        ),
        plot_bgcolor='white',
        height=500,
        font=dict(family='Arial'),
        barmode='stack',
        legend=dict(
            title=dict(text='Sector'),
            x=1.0,
            y=0.95,
            xanchor='left'
        )
    )
    
    st.plotly_chart(fig_dist, use_container_width=True)

# ============================================================================
# TAB 2: SECTOR ANALYSIS
# ============================================================================
with tab2:
    st.title("🏭 Sector Analysis")
    
    st.markdown("""
    ### How do delays vary across sectors?
    """)
    
    # Summary statistics
    st.subheader("📊 Summary Statistics by Sector")
    
    summary_data = []
    for sector in ['Energy', 'Transportation', 'Water']:
        sector_data = df[df['sector1'] == sector]
        summary_data.append({
            'Sector': sector,
            'Projects': len(sector_data),
            'Mean Delay (years)': sector_data['delay'].mean(),
            'Median Delay (years)': sector_data['delay'].median(),
            'Std Dev': sector_data['delay'].std()
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df.style.format({
        'Mean Delay (years)': '{:.2f}',
        'Median Delay (years)': '{:.2f}',
        'Std Dev': '{:.2f}'
    }), use_container_width=True)
    
    st.markdown("---")
    
    # Violin plot
    st.subheader("📈 Delay Distribution by Sector")
    
    fig = go.Figure()
    
    for sector in ['Energy', 'Transportation', 'Water']:
        sector_data = df[df['sector1'] == sector]
        
        fig.add_trace(go.Violin(
            y=sector_data['delay'],
            x=[sector] * len(sector_data),
            name=sector,
            box_visible=True,
            meanline_visible=True,
            marker=dict(color=sector_colors[sector]),
            line=dict(color=sector_colors[sector], width=2),
            fillcolor=sector_colors[sector],
            opacity=0.6
        ))
    
    fig.update_layout(
        title='Project Delay Distribution by Sector',
        xaxis_title='Sector',
        yaxis_title='Delay (years)',
        height=600,
        showlegend=False,
        plot_bgcolor='white',
        font=dict(family='Arial')
    )
    
    fig.update_yaxes(gridcolor='lightgray')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistical test result
    st.info("""
    📊 **Statistical Test**: Kruskal-Wallis test shows borderline significance (p=0.05)
    
    Energy projects show a trend toward longer delays compared to Transportation projects.
    """)

# ============================================================================
# PLACEHOLDER for remaining tabs - We'll build these next
# ============================================================================
with tab3:
    st.title("📏 Size & Risk Analysis")
    st.info("🚧 Coming next - this will be your KEY FINDINGS tab!")

with tab4:
    st.title("🔍 Key Findings Summary")
    st.info("🚧 Coming next - highlights of all findings!")

with tab5:
    st.title("📋 Raw Data")
    st.dataframe(df.head(100), use_container_width=True)
    
    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Full Dataset",
        data=csv,
        file_name='project_data.csv',
        mime='text/csv',
    )

# Footer
st.markdown("---")
st.caption("Infrastructure Project Risk Analysis | Data: Asian Development Bank")


