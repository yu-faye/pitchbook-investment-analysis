#!/usr/bin/env python3
"""
Valuation Trends Analysis
Extracts and visualizes valuation data over time for companies in list.txt
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
import os
from matplotlib.ticker import MaxNLocator

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 10

# Paths
BASE_DIR = '/Users/yufei/SchoolWork/fin/stata'
ANALYSIS_DIR = os.path.join(BASE_DIR, 'analysis_valuation_trends')
OUTPUT_DIR = ANALYSIS_DIR
DATA_DIR = os.path.join(ANALYSIS_DIR, 'data')
VIS_DIR = os.path.join(ANALYSIS_DIR, 'visualizations')

print("Loading company list...")
# Parse list.txt - alternating lines of company name and ID
with open(os.path.join(BASE_DIR, 'list.txt'), 'r') as f:
    lines = [line.strip().strip('"') for line in f.readlines() if line.strip()]

# Create list of companies
companies = []
for i in range(0, len(lines), 2):
    if i+1 < len(lines):
        companies.append({
            'name': lines[i],
            'id': lines[i+1]
        })

print(f"Found {len(companies)} companies to analyze:")
for comp in companies:
    print(f"  - {comp['name']} ({comp['id']})")

# Extract company IDs
company_ids = [comp['id'] for comp in companies]
company_names_map = {comp['id']: comp['name'] for comp in companies}

print("\nLoading Deal data (this may take a while)...")
# Read Deal.csv in chunks to handle large file
deal_chunks = []
chunk_size = 100000

for chunk in pd.read_csv(os.path.join(BASE_DIR, 'Deal.csv'), 
                         chunksize=chunk_size,
                         low_memory=False):
    # Filter for our companies
    company_deals = chunk[chunk['CompanyID'].isin(company_ids)]
    if len(company_deals) > 0:
        deal_chunks.append(company_deals)
    print(f"  Processed {len(chunk)} rows, found {len(company_deals)} relevant deals...")

if deal_chunks:
    deals_df = pd.concat(deal_chunks, ignore_index=True)
    print(f"\nTotal deals found: {len(deals_df)}")
else:
    print("\nNo deals found for these companies!")
    deals_df = pd.DataFrame()

# Process valuation data
print("\nProcessing valuation data...")

# Convert date to datetime
deals_df['DealDate'] = pd.to_datetime(deals_df['DealDate'], errors='coerce')

# Filter deals with valuation data
valuation_cols = ['CompanyID', 'CompanyName', 'DealDate', 'DealID', 
                 'PremoneyValuation', 'PostValuation', 'PostValuationStatus',
                 'DealType', 'DealType2', 'DealSize', 'VCRound']

deals_with_valuation = deals_df[valuation_cols].copy()

# Create a combined valuation column (prefer PostValuation, fallback to PremoneyValuation)
deals_with_valuation['Valuation'] = deals_with_valuation['PostValuation'].fillna(
    deals_with_valuation['PremoneyValuation']
)
deals_with_valuation['ValuationType'] = deals_with_valuation.apply(
    lambda x: 'Post-Money' if pd.notna(x['PostValuation']) else 'Pre-Money', axis=1
)

# Filter out rows without valuation
deals_with_valuation = deals_with_valuation[
    pd.notna(deals_with_valuation['Valuation']) & 
    (deals_with_valuation['Valuation'] > 0)
].copy()

# Add company name from our map
deals_with_valuation['CompanyNameFromList'] = deals_with_valuation['CompanyID'].map(company_names_map)

print(f"Found {len(deals_with_valuation)} deals with valuation data")

# Sort by date
deals_with_valuation = deals_with_valuation.sort_values('DealDate')

# Save detailed data
output_file = os.path.join(DATA_DIR, 'valuation_data_detailed.csv')
deals_with_valuation.to_csv(output_file, index=False)
print(f"\nSaved detailed valuation data to: {output_file}")

# Create summary by company
print("\nCreating company valuation summary...")
company_summary = []

for comp_id in company_ids:
    comp_name = company_names_map[comp_id]
    comp_deals = deals_with_valuation[deals_with_valuation['CompanyID'] == comp_id]
    
    if len(comp_deals) > 0:
        latest_valuation = comp_deals.iloc[-1]
        first_valuation = comp_deals.iloc[0]
        
        summary = {
            'CompanyID': comp_id,
            'CompanyName': comp_name,
            'TotalValuationPoints': len(comp_deals),
            'FirstValuationDate': first_valuation['DealDate'],
            'FirstValuation': first_valuation['Valuation'],
            'LatestValuationDate': latest_valuation['DealDate'],
            'LatestValuation': latest_valuation['Valuation'],
            'PeakValuation': comp_deals['Valuation'].max(),
            'ValuationGrowth': latest_valuation['Valuation'] - first_valuation['Valuation'],
            'ValuationGrowthPct': ((latest_valuation['Valuation'] - first_valuation['Valuation']) / 
                                  first_valuation['Valuation'] * 100) if first_valuation['Valuation'] > 0 else 0
        }
        company_summary.append(summary)

summary_df = pd.DataFrame(company_summary)
summary_file = os.path.join(DATA_DIR, 'valuation_summary_by_company.csv')
summary_df.to_csv(summary_file, index=False)
print(f"Saved company summary to: {summary_file}")

# Visualization 1: Valuation over time for all companies
print("\nCreating visualizations...")

fig, ax = plt.subplots(figsize=(16, 10))

for comp_id in company_ids:
    comp_name = company_names_map[comp_id]
    comp_deals = deals_with_valuation[deals_with_valuation['CompanyID'] == comp_id]
    
    if len(comp_deals) > 0:
        ax.plot(comp_deals['DealDate'], comp_deals['Valuation'], 
               marker='o', linewidth=2, markersize=8, label=comp_name, alpha=0.7)

ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Valuation', fontsize=12, fontweight='bold')
ax.set_title('Company Valuations Over Time', fontsize=16, fontweight='bold', pad=20)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3)

# Format y-axis - values are already in millions
def format_valuation_main(x, p):
    if x < 0.001:
        return '$0'
    elif x >= 1000:  # >= 1000M = billions
        return f'${x/1000:.1f}B'
    elif x >= 1:  # >= 1M = millions
        return f'${x:.0f}M'
    elif x >= 0.001:  # >= 0.001M = thousands
        return f'${x*1000:.0f}K'
    else:
        return f'${x*1e6:.0f}'

ax.yaxis.set_major_formatter(plt.FuncFormatter(format_valuation_main))

plt.xticks(rotation=45, ha='right')
plt.tight_layout()

plot1_file = os.path.join(VIS_DIR, 'valuation_trends_all_companies.png')
plt.savefig(plot1_file, dpi=300, bbox_inches='tight')
print(f"Saved plot: {plot1_file}")
plt.close()

# Visualization 2: Individual company charts
print("\nCreating individual company charts...")

companies_with_data = [comp_id for comp_id in company_ids 
                       if len(deals_with_valuation[deals_with_valuation['CompanyID'] == comp_id]) > 0]

if companies_with_data:
    # Determine grid size
    n_companies = len(companies_with_data)
    n_cols = 3
    n_rows = (n_companies + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 5*n_rows))
    
    if n_companies == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    for idx, comp_id in enumerate(companies_with_data):
        comp_name = company_names_map[comp_id]
        comp_deals = deals_with_valuation[deals_with_valuation['CompanyID'] == comp_id].copy()
        
        ax = axes[idx]
        ax.plot(comp_deals['DealDate'], comp_deals['Valuation'], 
               marker='o', linewidth=2, markersize=8, color='#2E86AB', alpha=0.7)
        
        # Add markers for different valuation types
        for val_type, marker, color in [('Post-Money', 'o', '#2E86AB'), 
                                        ('Pre-Money', 's', '#A23B72')]:
            type_deals = comp_deals[comp_deals['ValuationType'] == val_type]
            if len(type_deals) > 0:
                ax.scatter(type_deals['DealDate'], type_deals['Valuation'],
                         marker=marker, s=100, label=val_type, color=color, alpha=0.7, zorder=5)
        
        ax.set_xlabel('Date', fontsize=10, fontweight='bold')
        
        # Determine appropriate unit label based on company's valuation range
        # Note: Values are already in millions
        max_val = comp_deals['Valuation'].max()
        if max_val >= 1000:  # >= 1000M = billions range
            ylabel = 'Valuation (USD Billions)'
        elif max_val >= 1:  # >= 1M = millions range
            ylabel = 'Valuation (USD Millions)'
        else:  # < 1M = thousands range
            ylabel = 'Valuation (USD Thousands)'
        
        ax.set_ylabel(ylabel, fontsize=10, fontweight='bold')
        ax.set_title(f'{comp_name} ({comp_id})', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        
        # Format y-axis and set appropriate limits
        min_val = comp_deals['Valuation'].min()
        max_val = comp_deals['Valuation'].max()
        val_range = max_val - min_val
        
        # For single data points or very small ranges, use a percentage-based range
        if val_range < max_val * 0.01:  # Less than 1% range
            # Use 40% of the value as the range (20% above and below)
            padding = max_val * 0.2
            y_min = max(0, min_val - padding)
            y_max = max_val + padding
        else:
            # Add padding: 10% above and below, but at least 5% of max value
            padding = max(val_range * 0.1, max_val * 0.05)
            y_min = max(0, min_val - padding)
            y_max = max_val + padding
        
        # Set y-axis limits
        ax.set_ylim(y_min, y_max)
        
        # Use MaxNLocator to ensure reasonable number of ticks (4-6 ticks)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=False))
        
        # Format y-axis labels - values are already in millions
        def format_valuation(x, p):
            if x < 0.001:  # Handle near-zero values
                return '$0'
            elif x >= 1000:  # >= 1000M = billions
                return f'${x/1000:.1f}B'
            elif x >= 1:  # >= 1M = millions
                return f'${x:.1f}M'
            elif x >= 0.001:  # >= 0.001M = thousands
                return f'${x*1000:.0f}K'
            else:
                return f'${x*1e6:.0f}'
        
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_valuation))
        
        # Ensure y-axis labels are readable
        plt.setp(ax.yaxis.get_majorticklabels(), fontsize=9)
        
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Hide empty subplots
    for idx in range(len(companies_with_data), len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    plot2_file = os.path.join(VIS_DIR, 'valuation_trends_individual.png')
    plt.savefig(plot2_file, dpi=300, bbox_inches='tight')
    print(f"Saved plot: {plot2_file}")
    plt.close()

# Visualization 3: Latest valuation comparison
if len(summary_df) > 0:
    fig, ax = plt.subplots(figsize=(14, 8))
    
    summary_sorted = summary_df.sort_values('LatestValuation', ascending=True)
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(summary_sorted)))
    bars = ax.barh(summary_sorted['CompanyName'], summary_sorted['LatestValuation'], color=colors)
    
    # Determine appropriate unit label based on data range
    # Note: Values are already in millions
    max_val = summary_sorted['LatestValuation'].max()
    if max_val >= 1000:  # >= 1000M = billions
        xlabel = 'Latest Valuation (USD Billions)'
    elif max_val >= 1:  # >= 1M = millions
        xlabel = 'Latest Valuation (USD Millions)'
    else:  # < 1M = thousands
        xlabel = 'Latest Valuation (USD Thousands)'
    
    ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
    ax.set_ylabel('Company', fontsize=12, fontweight='bold')
    ax.set_title('Latest Valuation by Company', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, axis='x')
    
    # Format x-axis with proper units - values are already in millions
    def format_valuation_bar(x, p):
        if x < 0.001:
            return '$0'
        elif x >= 1000:
            return f'${x/1000:.1f}B'
        elif x >= 1:
            return f'${x:.0f}M'
        elif x >= 0.001:
            return f'${x*1000:.0f}K'
        else:
            return f'${x*1e6:.0f}'
    
    ax.xaxis.set_major_formatter(plt.FuncFormatter(format_valuation_bar))
    
    # Prepare company labels with dates
    company_labels = []
    for idx, row in summary_sorted.iterrows():
        date_str = row['LatestValuationDate']
        
        # Format date cleanly
        try:
            # Handle different date formats
            if pd.isna(date_str) or date_str == '':
                date_display = ''
            else:
                # Convert to datetime, handling various formats
                date_obj = pd.to_datetime(str(date_str))
                # Format as "MMM YYYY" (e.g., "Sep 2019")
                date_display = date_obj.strftime('%b %Y')
        except:
            # Fallback: try to extract just date part if it has timestamp
            date_str_clean = str(date_str).split()[0] if ' ' in str(date_str) else str(date_str)
            try:
                date_obj = pd.to_datetime(date_str_clean)
                date_display = date_obj.strftime('%b %Y')
            except:
                date_display = date_str_clean[:7] if len(date_str_clean) >= 7 else date_str_clean
        
        comp_name = row['CompanyName']
        if date_display:
            company_labels.append(f"{comp_name}\n({date_display})")
        else:
            company_labels.append(comp_name)
    
    # Update y-axis labels
    ax.set_yticks(range(len(summary_sorted)))
    ax.set_yticklabels(company_labels, fontsize=10)
    
    # Add value labels on bars
    for i, (idx, row) in enumerate(summary_sorted.iterrows()):
        val = row['LatestValuation']
        
        # Format valuation amount with proper units - values are already in millions
        if val >= 1000:  # >= 1000M = billions
            val_label = f'${val/1000:.2f}B'
        elif val >= 1:  # >= 1M = millions
            val_label = f'${val:.1f}M'
        elif val >= 0.001:  # >= 0.001M = thousands
            val_label = f'${val*1000:.1f}K'
        else:
            val_label = f'${val*1e6:.1f}'
        
        # Add valuation amount label at the end of the bar
        ax.text(val, i, f'  {val_label}', va='center', fontsize=10, 
               fontweight='bold', ha='left')
    
    plt.tight_layout()
    plot3_file = os.path.join(VIS_DIR, 'latest_valuation_comparison.png')
    plt.savefig(plot3_file, dpi=300, bbox_inches='tight')
    print(f"Saved plot: {plot3_file}")
    plt.close()

# Visualization 4: Valuation growth
if len(summary_df) > 0:
    summary_with_growth = summary_df[summary_df['ValuationGrowth'] != 0].copy()
    
    if len(summary_with_growth) > 0:
        fig, ax = plt.subplots(figsize=(14, 8))
        
        summary_sorted = summary_with_growth.sort_values('ValuationGrowthPct', ascending=True)
        
        colors = ['green' if x > 0 else 'red' for x in summary_sorted['ValuationGrowthPct']]
        bars = ax.barh(summary_sorted['CompanyName'], summary_sorted['ValuationGrowthPct'], color=colors, alpha=0.7)
        
        ax.set_xlabel('Valuation Growth (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Company', fontsize=12, fontweight='bold')
        ax.set_title('Valuation Growth Rate (First to Latest)', fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='x')
        ax.axvline(x=0, color='black', linewidth=1, linestyle='--')
        
        # Add value labels
        for i, (idx, row) in enumerate(summary_sorted.iterrows()):
            val = row['ValuationGrowthPct']
            ax.text(val, i, f'  {val:.1f}%', va='center', fontsize=9, 
                   ha='left' if val > 0 else 'right')
        
        plt.tight_layout()
        plot4_file = os.path.join(VIS_DIR, 'valuation_growth_rate.png')
        plt.savefig(plot4_file, dpi=300, bbox_inches='tight')
        print(f"Saved plot: {plot4_file}")
        plt.close()

print("\n" + "="*80)
print("VALUATION ANALYSIS COMPLETE")
print("="*80)
print(f"\nOutput directory: {OUTPUT_DIR}")
print(f"\nFiles created:")
print(f"  - valuation_data_detailed.csv (all deals with valuation data)")
print(f"  - valuation_summary_by_company.csv (summary statistics by company)")
print(f"  - valuation_trends_all_companies.png (all companies on one chart)")
print(f"  - valuation_trends_individual.png (individual company charts)")
print(f"  - latest_valuation_comparison.png (bar chart of latest valuations)")
print(f"  - valuation_growth_rate.png (growth rate comparison)")

if len(summary_df) > 0:
    print(f"\nSummary Statistics:")
    print(f"  Companies with valuation data: {len(summary_df)}")
    print(f"  Total valuation data points: {summary_df['TotalValuationPoints'].sum()}")
    print(f"\nTop 3 Companies by Latest Valuation:")
    top3 = summary_df.nlargest(3, 'LatestValuation')[['CompanyName', 'LatestValuation', 'LatestValuationDate']]
    for idx, row in top3.iterrows():
        val = row['LatestValuation']
        # Values are already in millions
        val_str = f'${val/1000:.2f}B' if val >= 1000 else f'${val:.1f}M'
        print(f"    {row['CompanyName']}: {val_str} (as of {row['LatestValuationDate'].strftime('%Y-%m-%d')})")

