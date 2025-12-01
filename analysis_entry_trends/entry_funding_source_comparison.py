#!/usr/bin/env python3
"""
Entry Funding Source Trends Comparison: Wearable Industry vs Broader Industry
Analyzes investor types in first deals (entry funding sources) for wearable companies
compared to industry benchmarks.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (20, 14)

def identify_wearable_companies(chunk, wearable_keywords=None):
    """Identify wearable tech companies based on industry keywords"""
    if wearable_keywords is None:
        wearable_keywords = ['wearable', 'fitness tracker', 'smartwatch', 'activity monitor', 
                            'health monitoring', 'biometric', 'fitness band', 'sports technology']
    
    mask = pd.Series([False] * len(chunk), index=chunk.index)
    
    # Check various industry fields
    industry_fields = ['PrimaryIndustrySector', 'PrimaryIndustryGroup', 'AllIndustries', 
                      'Verticals', 'Description', 'DescriptionShort', 'Keywords']
    
    for field in industry_fields:
        if field in chunk.columns:
            field_data = chunk[field].astype(str).str.lower()
            for keyword in wearable_keywords:
                mask |= field_data.str.contains(keyword, na=False, case=False)
    
    return mask

print("="*100)
print("ENTRY FUNDING SOURCE TRENDS: WEARABLE INDUSTRY vs BROADER INDUSTRY")
print("="*100)

chunk_size = 100000

# Parse company IDs from list.txt
def parse_company_ids(list_file):
    """Parse company IDs from list.txt"""
    company_data = []
    with open(list_file, 'r') as f:
        lines = f.readlines()
    
    for i in range(0, len(lines)-1, 2):
        name = lines[i].strip()
        company_id = lines[i+1].strip().strip('"')
        if name and company_id and name != 'Total Valuation Sum: $20.01B':
            company_data.append({'name': name, 'id': company_id})
    
    return company_data

# Load focus companies from list.txt
print("\nLoading focus companies from list.txt...")
company_data = parse_company_ids('../list.txt')
company_ids = [c['id'] for c in company_data]
company_names = {c['id']: c['name'] for c in company_data}
print(f"Found {len(company_ids)} focus companies from list.txt:")
for comp in company_data:
    print(f"  - {comp['name']} ({comp['id']})")

if len(company_ids) == 0:
    print("ERROR: No companies found in list.txt. Exiting.")
    exit(1)

# Load Deal data for wearable companies
print("\nLoading Deal data for wearable companies...")
deals_list = []
for chunk in pd.read_csv('../Deal.csv', chunksize=chunk_size, low_memory=False):
    filtered = chunk[chunk['CompanyID'].isin(company_ids)]
    if len(filtered) > 0:
        deals_list.append(filtered)
wearable_deals = pd.concat(deals_list, ignore_index=True)
wearable_deals['DealDate'] = pd.to_datetime(wearable_deals['DealDate'], errors='coerce')
wearable_deals['year'] = wearable_deals['DealDate'].dt.year
# Get company name from CompanyName in Deal.csv, or fall back to company_names dict
wearable_deals['company_name'] = wearable_deals.apply(
    lambda row: row.get('CompanyName', company_names.get(row['CompanyID'], 'Unknown')), axis=1
)
wearable_deals = wearable_deals.sort_values('DealDate')

print(f"Found {len(wearable_deals)} deals for wearable companies")

# Get first deals (entry deals) for wearable companies
print("\nIdentifying entry deals for wearable companies...")
first_deals_wearable = wearable_deals.groupby('CompanyID').first().reset_index()
first_deals_wearable = first_deals_wearable[first_deals_wearable['DealDate'].notna()].copy()
print(f"Found {len(first_deals_wearable)} entry deals")

# Extract investor IDs from entry deals
def extract_investor_ids(investors_str):
    """Extract investor IDs from Investors column"""
    if pd.isna(investors_str):
        return []
    investor_str = str(investors_str)
    # Try different separators
    for sep in [',', ';', '|']:
        if sep in investor_str:
            return [inv.strip() for inv in investor_str.split(sep) if inv.strip()]
    return [investor_str.strip()] if investor_str.strip() else []

print("\nExtracting entry funding sources from entry deals...")
# Use DealType as entry funding source (entry mechanism)
entry_funding_sources = []
for idx, row in first_deals_wearable.iterrows():
    deal_type = str(row.get('DealType', 'Unknown')) if pd.notna(row.get('DealType')) else 'Unknown'
    entry_funding_sources.append({
        'CompanyID': row['CompanyID'],
        'CompanyName': row['company_name'],
        'EntryYear': row['year'],
        'EntryDate': row['DealDate'],
        'EntryFundingSource': deal_type,
        'DealSize': row.get('DealSize', None),
        'VCRound': row.get('VCRound', None)
    })

entry_funding_df = pd.DataFrame(entry_funding_sources)
print(f"Found {len(entry_funding_df)} entry funding source records")

# Load comparison sample from broader industry
print("\nLoading industry comparison sample...")
print("(Analyzing first deals for all companies as industry benchmark)")

# Sample size limit for performance
SAMPLE_SIZE = 50000  # Limit to 50k companies for performance

all_companies_first_deals = []
company_ids_seen = set()
chunk_count = 0

for chunk in pd.read_csv('../Deal.csv', chunksize=chunk_size, low_memory=False):
    chunk['DealDate'] = pd.to_datetime(chunk['DealDate'], errors='coerce')
    chunk = chunk[chunk['DealDate'].notna()].copy()
    chunk = chunk.sort_values(['CompanyID', 'DealDate'])
    
    # Get first deal for each company in this chunk
    first_deals_chunk = chunk.groupby('CompanyID').first().reset_index()
    
    # Filter out wearable companies from comparison
    first_deals_chunk = first_deals_chunk[~first_deals_chunk['CompanyID'].isin(company_ids)]
    
    # Add only new companies
    for _, row in first_deals_chunk.iterrows():
        if row['CompanyID'] not in company_ids_seen:
            company_ids_seen.add(row['CompanyID'])
            all_companies_first_deals.append({
                'CompanyID': row['CompanyID'],
                'CompanyName': row.get('CompanyName', 'Unknown'),
                'DealDate': row['DealDate'],
                'Year': row['DealDate'].year if pd.notna(row['DealDate']) else None,
                'Investors': row.get('Investors', ''),
                'DealType': row.get('DealType', 'Unknown'),
                'DealSize': row.get('DealSize', None)
            })
            
            if len(company_ids_seen) >= SAMPLE_SIZE:
                break
    
    if len(company_ids_seen) >= SAMPLE_SIZE:
        break
    chunk_count += 1
    if chunk_count % 10 == 0:
        print(f"  Processed {chunk_count} chunks, found {len(company_ids_seen)} companies...")

industry_first_deals = pd.DataFrame(all_companies_first_deals)
print(f"Loaded {len(industry_first_deals)} industry entry deals for comparison")

# Extract entry funding sources from industry entry deals
print("\nExtracting entry funding sources from industry entry deals...")
industry_funding_sources = []
for idx, row in industry_first_deals.iterrows():
    deal_type = str(row.get('DealType', 'Unknown')) if pd.notna(row.get('DealType')) else 'Unknown'
    industry_funding_sources.append({
        'CompanyID': row['CompanyID'],
        'EntryYear': row['Year'],
        'EntryFundingSource': deal_type
    })

industry_funding_df = pd.DataFrame(industry_funding_sources)
print(f"Found {len(industry_funding_df)} industry entry funding source records")

# Analyze entry funding source trends
print("\n" + "="*100)
print("ANALYZING ENTRY FUNDING SOURCE TRENDS")
print("="*100)

# Filter to only include entries after 2000
print("\nFiltering data to focus on entries after 2000...")
entry_funding_df_filtered = entry_funding_df[entry_funding_df['EntryYear'] >= 2000].copy()
industry_funding_df_filtered = industry_funding_df[industry_funding_df['EntryYear'] >= 2000].copy()

print(f"Wearable entries after 2000: {len(entry_funding_df_filtered)}")
print(f"Industry entries after 2000: {len(industry_funding_df_filtered)}")

# Wearable: Entry funding sources by year
wearable_entry_by_year = entry_funding_df_filtered.groupby(['EntryYear', 'EntryFundingSource']).size().reset_index(name='Count')
wearable_entry_by_year = wearable_entry_by_year.pivot(index='EntryYear', columns='EntryFundingSource', values='Count').fillna(0)

# Industry: Entry funding sources by year
industry_entry_by_year = industry_funding_df_filtered.groupby(['EntryYear', 'EntryFundingSource']).size().reset_index(name='Count')
industry_entry_by_year = industry_entry_by_year.pivot(index='EntryYear', columns='EntryFundingSource', values='Count').fillna(0)

# Overall distribution (using filtered data)
wearable_entry_dist = entry_funding_df_filtered['EntryFundingSource'].value_counts().reset_index()
wearable_entry_dist.columns = ['FundingSource', 'Count']
wearable_entry_dist['Percentage'] = (wearable_entry_dist['Count'] / wearable_entry_dist['Count'].sum() * 100).round(1)

industry_entry_dist = industry_funding_df_filtered['EntryFundingSource'].value_counts().reset_index()
industry_entry_dist.columns = ['FundingSource', 'Count']
industry_entry_dist['Percentage'] = (industry_entry_dist['Count'] / industry_entry_dist['Count'].sum() * 100).round(1)

print("\n📊 WEARABLE INDUSTRY - ENTRY FUNDING SOURCE DISTRIBUTION:")
print("-" * 100)
print(f"{'Funding Source':<35} {'Count':<10} {'Percentage':<10}")
print("-" * 100)
for _, row in wearable_entry_dist.iterrows():
    print(f"{row['FundingSource']:<35} {int(row['Count']):<10} {row['Percentage']:.1f}%")

print("\n📊 BROADER INDUSTRY - ENTRY FUNDING SOURCE DISTRIBUTION:")
print("-" * 100)
print(f"{'Funding Source':<35} {'Count':<10} {'Percentage':<10}")
print("-" * 100)
for _, row in industry_entry_dist.head(15).iterrows():
    print(f"{row['FundingSource']:<35} {int(row['Count']):<10} {row['Percentage']:.1f}%")

# Create comparison visualization
print("\n" + "="*100)
print("GENERATING VISUALIZATIONS...")
print("="*100)

# Create consistent color mapping for funding sources
# Get all unique funding sources across both datasets
all_funding_sources = set(wearable_entry_dist['FundingSource'].tolist()) | set(industry_entry_dist['FundingSource'].tolist())
all_funding_sources = sorted(list(all_funding_sources))

# Use a colormap to assign consistent colors
color_map = {}
n_colors = len(all_funding_sources)
cmap = plt.cm.get_cmap('tab20', n_colors)
for i, source in enumerate(all_funding_sources):
    color_map[source] = cmap(i)

# ============================================================================
# 1. DISTRIBUTION COMPARISON - Pie Charts
# ============================================================================
print("\nCreating distribution pie charts...")
fig1 = plt.figure(figsize=(18, 8))
gs1 = fig1.add_gridspec(1, 2, hspace=0.3, wspace=0.3)

# 1a. Wearable Industry Pie Chart
ax1 = fig1.add_subplot(gs1[0, 0])
wearable_top_pct = wearable_entry_dist.head(8)
# Use consistent colors from color_map
pie_colors_wearable = [color_map.get(source, '#3498db') for source in wearable_top_pct['FundingSource']]
wedges, texts, autotexts = ax1.pie(wearable_top_pct['Count'], labels=wearable_top_pct['FundingSource'], 
                                    autopct='%1.1f%%', colors=pie_colors_wearable, startangle=90)
for text in texts:
    text.set_fontsize(8)
for autotext in autotexts:
    autotext.set_color('black')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(9)
ax1.set_title('Wearable Industry\nEntry Funding Sources', fontsize=12, fontweight='bold')

# 1b. Broader Industry Pie Chart
ax2 = fig1.add_subplot(gs1[0, 1])
industry_top_pct = industry_entry_dist.head(8)
# Use consistent colors from color_map
pie_colors_industry = [color_map.get(source, '#3498db') for source in industry_top_pct['FundingSource']]
wedges, texts, autotexts = ax2.pie(industry_top_pct['Count'], labels=industry_top_pct['FundingSource'], 
                                     autopct='%1.1f%%', colors=pie_colors_industry, startangle=90)
for text in texts:
    text.set_fontsize(8)
for autotext in autotexts:
    autotext.set_color('black')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(9)
ax2.set_title('Broader Industry\nEntry Funding Sources', fontsize=12, fontweight='bold')

plt.suptitle('Entry Funding Source Distribution: Wearable vs Broader Industry (Post-2000)', 
             fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('visualizations/distribution/entry_funding_source_distribution.png', dpi=300, bbox_inches='tight')
plt.close(fig1)
print("✓ Distribution pie charts saved to 'visualizations/distribution/entry_funding_source_distribution.png'")

# ============================================================================
# 2. TIME SERIES - Area Charts (Wearable and Industry)
# ============================================================================
print("\nCreating time series area charts...")
fig2 = plt.figure(figsize=(20, 10))
gs2 = fig2.add_gridspec(1, 2, hspace=0.3, wspace=0.3)

# 2a. Entry Funding Sources Over Time - Wearable
ax2 = fig2.add_subplot(gs2[0, 0])
if not wearable_entry_by_year.empty:
    # Use consistent colors for each column
    colors_list = [color_map.get(col, '#3498db') for col in wearable_entry_by_year.columns]
    wearable_entry_by_year.plot(kind='area', ax=ax2, stacked=True, alpha=0.7, color=colors_list)
    ax2.set_xlabel('Entry Year', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Number of Entry Investments', fontsize=11, fontweight='bold')
    ax2.set_title('Wearable Industry: Entry Funding Sources Over Time (Post-2000)', fontsize=12, fontweight='bold')
    ax2.set_xlim(left=2000)
    ax2.legend(title='Funding Source', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=7)
    ax2.grid(alpha=0.3)

# 2b. Entry Funding Sources Over Time - Industry
ax3 = fig2.add_subplot(gs2[0, 1])
if not industry_entry_by_year.empty:
    # Select top investor types for clarity
    top_types = industry_entry_by_year.sum().nlargest(8).index
    # Use consistent colors for each column (same as wearable)
    colors_list = [color_map.get(col, '#3498db') for col in top_types]
    industry_entry_by_year[top_types].plot(kind='area', ax=ax3, stacked=True, alpha=0.7, color=colors_list)
    ax3.set_xlabel('Entry Year', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Number of Entry Investments', fontsize=11, fontweight='bold')
    ax3.set_title('Broader Industry: Entry Funding Sources Over Time\n(Top 8 Types, Post-2000)', fontsize=12, fontweight='bold')
    ax3.set_xlim(left=2000)
    ax3.legend(title='Funding Source', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=7)
    ax3.grid(alpha=0.3)

plt.suptitle('Entry Funding Sources Over Time: Wearable vs Broader Industry (Post-2000)', 
             fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('visualizations/time_series/entry_funding_sources_over_time.png', dpi=300, bbox_inches='tight')
plt.close(fig2)
print("✓ Time series area charts saved to 'visualizations/time_series/entry_funding_sources_over_time.png'")

# ============================================================================
# 3. TIME SERIES - Line Chart (Top Funding Sources Comparison)
# ============================================================================
print("\nCreating time series line chart...")
fig3 = plt.figure(figsize=(18, 8))
ax4 = fig3.add_subplot(111)

# Get top 5 funding sources from wearable
top_wearable_types = wearable_entry_dist.head(5)['FundingSource'].tolist()

# Create normalized percentages over time (using filtered data)
for funding_type in top_wearable_types:
    wearable_data = entry_funding_df_filtered[entry_funding_df_filtered['EntryFundingSource'] == funding_type]
    wearable_yearly = wearable_data.groupby('EntryYear').size()
    
    industry_data = industry_funding_df_filtered[industry_funding_df_filtered['EntryFundingSource'] == funding_type]
    industry_yearly = industry_data.groupby('EntryYear').size()
    
    # Normalize by total entries in that year
    wearable_total_yearly = entry_funding_df_filtered.groupby('EntryYear').size()
    industry_total_yearly = industry_funding_df_filtered.groupby('EntryYear').size()
    
    wearable_pct = (wearable_yearly / wearable_total_yearly * 100).fillna(0)
    industry_pct = (industry_yearly / industry_total_yearly * 100).fillna(0)
    
    # Use consistent color for this funding source
    source_color = color_map.get(funding_type, '#3498db')
    
    ax4.plot(wearable_pct.index, wearable_pct.values, marker='o', linewidth=2, 
             label=f'Wearable: {funding_type}', linestyle='-', markersize=6, color=source_color)
    ax4.plot(industry_pct.index, industry_pct.values, marker='s', linewidth=2, 
             label=f'Industry: {funding_type}', linestyle='--', markersize=4, alpha=0.7, color=source_color)

ax4.set_xlabel('Entry Year', fontsize=11, fontweight='bold')
ax4.set_ylabel('Percentage of Entry Investments (%)', fontsize=11, fontweight='bold')
ax4.set_title('Top Funding Sources: Entry Funding Source Trends Over Time (Post-2000)', fontsize=12, fontweight='bold')
ax4.set_xlim(left=2000)
ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8, ncol=2)
ax4.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('visualizations/time_series/top_funding_sources_trends.png', dpi=300, bbox_inches='tight')
plt.close(fig3)
print("✓ Time series line chart saved to 'visualizations/time_series/top_funding_sources_trends.png'")

print("\n✓ All visualizations saved successfully!")

# Save data
entry_funding_df.to_csv('entry_funding_sources_wearable.csv', index=False)
industry_funding_df.head(10000).to_csv('entry_funding_sources_industry_sample.csv', index=False)
print("✓ Data saved to CSV files")

print("\n" + "="*100)
print("ANALYSIS COMPLETE")
print("="*100)

print("\n💡 KEY INSIGHTS:")
print("-" * 100)
print(f"• Wearable companies analyzed (post-2000): {len(entry_funding_df_filtered)}")
print(f"• Industry comparison sample (post-2000): {len(industry_funding_df_filtered)} companies")
print(f"• Unique funding sources (wearable): {wearable_entry_dist['FundingSource'].nunique()}")
print(f"• Unique funding sources (industry): {industry_entry_dist['FundingSource'].nunique()}")
if len(wearable_entry_dist) > 0:
    print(f"• Top entry funding source (wearable): {wearable_entry_dist.iloc[0]['FundingSource']} ({wearable_entry_dist.iloc[0]['Percentage']:.1f}%)")
if len(industry_entry_dist) > 0:
    print(f"• Top entry funding source (industry): {industry_entry_dist.iloc[0]['FundingSource']} ({industry_entry_dist.iloc[0]['Percentage']:.1f}%)")
print()

