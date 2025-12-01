#!/usr/bin/env python3
"""
Valuation Trends Analysis v2
Includes both disclosed and undisclosed valuations for better context
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

print("\nLoading ALL Deal data (this may take a while)...")
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

# Process ALL deals
print("\nProcessing all deal data...")

# Convert date to datetime
deals_df['DealDate'] = pd.to_datetime(deals_df['DealDate'], errors='coerce')

# Select relevant columns
all_deals_cols = ['CompanyID', 'CompanyName', 'DealDate', 'DealID', 'DealNo',
                 'PremoneyValuation', 'PostValuation', 'PostValuationStatus',
                 'DealType', 'DealType2', 'DealSize', 'VCRound']

all_deals = deals_df[all_deals_cols].copy()

# Create a combined valuation column
all_deals['Valuation'] = all_deals['PostValuation'].fillna(all_deals['PremoneyValuation'])
all_deals['HasValuation'] = all_deals['Valuation'].notna() & (all_deals['Valuation'] > 0)
all_deals['ValuationType'] = all_deals.apply(
    lambda x: 'Post-Money' if pd.notna(x['PostValuation']) else ('Pre-Money' if pd.notna(x['PremoneyValuation']) else 'Not Disclosed'), 
    axis=1
)

# Add company name from our map
all_deals['CompanyNameFromList'] = all_deals['CompanyID'].map(company_names_map)

# Sort by date
all_deals = all_deals.sort_values('DealDate')

# Save complete data
output_file = os.path.join(DATA_DIR, 'all_deals_complete.csv')
all_deals.to_csv(output_file, index=False)
print(f"\nSaved complete deal data to: {output_file}")

# Separate deals with and without valuations
deals_with_val = all_deals[all_deals['HasValuation']].copy()
deals_without_val = all_deals[~all_deals['HasValuation']].copy()

print(f"\nDeals with disclosed valuations: {len(deals_with_val)}")
print(f"Deals without disclosed valuations: {len(deals_without_val)}")

# Create company summary with both disclosed and undisclosed deals
print("\nCreating comprehensive company summary...")
company_summary = []

for comp_id in company_ids:
    comp_name = company_names_map[comp_id]
    comp_all_deals = all_deals[all_deals['CompanyID'] == comp_id]
    comp_deals_with_val = deals_with_val[deals_with_val['CompanyID'] == comp_id]
    comp_deals_without_val = deals_without_val[deals_without_val['CompanyID'] == comp_id]
    
    if len(comp_all_deals) > 0:
        summary = {
            'CompanyID': comp_id,
            'CompanyName': comp_name,
            'TotalDeals': len(comp_all_deals),
            'DealsWithValuation': len(comp_deals_with_val),
            'DealsWithoutValuation': len(comp_deals_without_val),
        }
        
        if len(comp_deals_with_val) > 0:
            latest_valuation = comp_deals_with_val.iloc[-1]
            first_valuation = comp_deals_with_val.iloc[0]
            
            summary.update({
                'FirstValuationDate': first_valuation['DealDate'],
                'FirstValuation': first_valuation['Valuation'],
                'LatestValuationDate': latest_valuation['DealDate'],
                'LatestValuation': latest_valuation['Valuation'],
                'PeakValuation': comp_deals_with_val['Valuation'].max(),
                'ValuationGrowth': latest_valuation['Valuation'] - first_valuation['Valuation'],
                'ValuationGrowthPct': ((latest_valuation['Valuation'] - first_valuation['Valuation']) / 
                                      first_valuation['Valuation'] * 100) if first_valuation['Valuation'] > 0 else 0
            })
        else:
            summary.update({
                'FirstValuationDate': None,
                'FirstValuation': None,
                'LatestValuationDate': None,
                'LatestValuation': None,
                'PeakValuation': None,
                'ValuationGrowth': None,
                'ValuationGrowthPct': None
            })
        
        company_summary.append(summary)

summary_df = pd.DataFrame(company_summary)
summary_file = os.path.join(DATA_DIR, 'company_summary_complete.csv')
summary_df.to_csv(summary_file, index=False)
print(f"Saved comprehensive company summary to: {summary_file}")

# Visualization 1: All companies with disclosed and undisclosed deals
print("\nCreating enhanced visualizations...")

fig, ax = plt.subplots(figsize=(18, 10))

for comp_id in company_ids:
    comp_name = company_names_map[comp_id]
    comp_deals_with_val = deals_with_val[deals_with_val['CompanyID'] == comp_id]
    comp_deals_without_val = deals_without_val[deals_without_val['CompanyID'] == comp_id]
    
    # Plot line for disclosed valuations
    if len(comp_deals_with_val) > 0:
        ax.plot(comp_deals_with_val['DealDate'], comp_deals_with_val['Valuation'], 
               marker='o', linewidth=2.5, markersize=10, label=comp_name, alpha=0.7, zorder=5)
        
        # Plot markers for undisclosed valuations at the same height as previous valuation
        if len(comp_deals_without_val) > 0:
            for idx, undisclosed_deal in comp_deals_without_val.iterrows():
                # Find the last known valuation before this deal
                prior_vals = comp_deals_with_val[comp_deals_with_val['DealDate'] < undisclosed_deal['DealDate']]
                if len(prior_vals) > 0:
                    last_val = prior_vals.iloc[-1]['Valuation']
                    # Plot as hollow marker
                    ax.scatter(undisclosed_deal['DealDate'], last_val, 
                             marker='o', s=150, facecolors='none', 
                             edgecolors=ax.lines[-1].get_color(), linewidths=2.5, 
                             alpha=0.5, zorder=4)

# Add custom legend entry for undisclosed deals
from matplotlib.lines import Line2D
legend_elements = ax.get_legend_handles_labels()[0]
legend_labels = ax.get_legend_handles_labels()[1]
legend_elements.append(Line2D([0], [0], marker='o', color='gray', linestyle='None',
                             markersize=10, markerfacecolor='none', markeredgewidth=2.5,
                             label='Deal without disclosed valuation'))
legend_labels.append('Deal without disclosed valuation')

ax.set_xlabel('Date', fontsize=14, fontweight='bold')
# Determine appropriate unit label based on data range
if len(deals_with_val) > 0:
    max_val = deals_with_val['Valuation'].max()
    if max_val >= 1e9:
        ylabel = 'Valuation (USD Billions)'
    elif max_val >= 1e6:
        ylabel = 'Valuation (USD Millions)'
    else:
        ylabel = 'Valuation (USD Thousands)'
else:
    ylabel = 'Valuation (USD)'
ax.set_ylabel(ylabel, fontsize=14, fontweight='bold')
ax.set_title('Company Valuations Over Time\n(Hollow circles = deals without disclosed valuations)', 
            fontsize=18, fontweight='bold', pad=20)
ax.legend(legend_elements, legend_labels, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3)

# Format y-axis as millions/billions
ax.yaxis.set_major_formatter(plt.FuncFormatter(
    lambda x, p: f'${x/1e9:.1f}B' if x >= 1e9 else (f'${x/1e6:.0f}M' if x >= 1e6 else f'${x/1e3:.0f}K')
))

plt.xticks(rotation=45, ha='right')
plt.tight_layout()

plot1_file = os.path.join(VIS_DIR, 'valuation_trends_with_undisclosed.png')
plt.savefig(plot1_file, dpi=300, bbox_inches='tight')
print(f"Saved plot: {plot1_file}")
plt.close()

# Visualization 2: Individual company charts with deal counts
print("\nCreating individual company charts with deal context...")

companies_with_data = [comp_id for comp_id in company_ids 
                       if len(all_deals[all_deals['CompanyID'] == comp_id]) > 0]

if companies_with_data:
    n_companies = len(companies_with_data)
    n_cols = 3
    n_rows = (n_companies + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 6*n_rows))
    
    if n_companies == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    for idx, comp_id in enumerate(companies_with_data):
        comp_name = company_names_map[comp_id]
        comp_deals_with_val = deals_with_val[deals_with_val['CompanyID'] == comp_id].copy()
        comp_deals_without_val = deals_without_val[deals_without_val['CompanyID'] == comp_id].copy()
        
        ax = axes[idx]
        
        # Plot line for disclosed valuations
        if len(comp_deals_with_val) > 0:
            ax.plot(comp_deals_with_val['DealDate'], comp_deals_with_val['Valuation'], 
                   marker='o', linewidth=2.5, markersize=10, color='#2E86AB', 
                   alpha=0.8, zorder=5, label='Disclosed valuation')
            
            # Mark different valuation types
            for val_type, marker, color in [('Post-Money', 'o', '#2E86AB'), 
                                            ('Pre-Money', 's', '#A23B72')]:
                type_deals = comp_deals_with_val[comp_deals_with_val['ValuationType'] == val_type]
                if len(type_deals) > 0:
                    ax.scatter(type_deals['DealDate'], type_deals['Valuation'],
                             marker=marker, s=120, label=val_type, color=color, 
                             alpha=0.8, zorder=6, edgecolors='white', linewidths=1.5)
            
            # Plot undisclosed deals as hollow markers
            if len(comp_deals_without_val) > 0:
                for _, undisclosed_deal in comp_deals_without_val.iterrows():
                    prior_vals = comp_deals_with_val[comp_deals_with_val['DealDate'] < undisclosed_deal['DealDate']]
                    if len(prior_vals) > 0:
                        last_val = prior_vals.iloc[-1]['Valuation']
                        ax.scatter(undisclosed_deal['DealDate'], last_val, 
                                 marker='o', s=150, facecolors='none', 
                                 edgecolors='#E63946', linewidths=2.5, 
                                 alpha=0.6, zorder=4)
                
                # Add hollow marker to legend (only once)
                ax.scatter([], [], marker='o', s=150, facecolors='none', 
                         edgecolors='#E63946', linewidths=2.5, 
                         label='Undisclosed valuation', alpha=0.6)
        
        # If only undisclosed deals, show them on timeline
        elif len(comp_deals_without_val) > 0:
            # Plot undisclosed deals as markers on x-axis
            # Use a small offset so they're visible but don't show misleading y-axis values
            for _, deal in comp_deals_without_val.iterrows():
                ax.scatter(deal['DealDate'], 0, 
                         marker='o', s=150, facecolors='none', 
                         edgecolors='#E63946', linewidths=2.5, alpha=0.6)
            ax.scatter([], [], marker='o', s=150, facecolors='none', 
                     edgecolors='#E63946', linewidths=2.5, 
                     label='Undisclosed valuation', alpha=0.6)
            # Set y-axis to show "No disclosed valuations" message
            ax.set_ylim(-0.1, 0.1)
            ax.set_yticks([0])
            ax.set_yticklabels(['No disclosed\nvaluations'], fontsize=9, style='italic')
        
        # Add title with deal counts
        n_disclosed = len(comp_deals_with_val)
        n_undisclosed = len(comp_deals_without_val)
        title = f'{comp_name} ({comp_id})\n{n_disclosed} disclosed, {n_undisclosed} undisclosed'
        
        ax.set_xlabel('Date', fontsize=11, fontweight='bold')
        
        # Determine appropriate unit label based on company's valuation range
        if len(comp_deals_with_val) > 0:
            max_val = comp_deals_with_val['Valuation'].max()
            if max_val >= 1e9:
                ylabel = 'Valuation (USD Billions)'
            elif max_val >= 1e6:
                ylabel = 'Valuation (USD Millions)'
            else:
                ylabel = 'Valuation (USD Thousands)'
        else:
            ylabel = 'Valuation'
        
        ax.set_ylabel(ylabel, fontsize=11, fontweight='bold')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, loc='best')
        
        # Format y-axis and set appropriate limits
        if len(comp_deals_with_val) > 0:
            min_val = comp_deals_with_val['Valuation'].min()
            max_val = comp_deals_with_val['Valuation'].max()
            val_range = max_val - min_val
            
            # Add padding: 10% above and below, but at least 5% of range
            padding = max(val_range * 0.1, max_val * 0.05)
            y_min = max(0, min_val - padding)
            y_max = max_val + padding
            
            # Set y-axis limits
            ax.set_ylim(y_min, y_max)
            
            # Use MaxNLocator to ensure reasonable number of ticks (4-6 ticks)
            ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=False))
            
            # Format y-axis labels
            ax.yaxis.set_major_formatter(plt.FuncFormatter(
                lambda x, p: f'${x/1e9:.1f}B' if x >= 1e9 else (f'${x/1e6:.0f}M' if x >= 1e6 else f'${x/1e3:.0f}K')
            ))
            
            # Ensure y-axis labels are readable
            plt.setp(ax.yaxis.get_majorticklabels(), fontsize=9)
        
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Hide empty subplots
    for idx in range(len(companies_with_data), len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    plot2_file = os.path.join(VIS_DIR, 'valuation_trends_individual_enhanced.png')
    plt.savefig(plot2_file, dpi=300, bbox_inches='tight')
    print(f"Saved plot: {plot2_file}")
    plt.close()

# Visualization 3: Deal disclosure rate by company
print("\nCreating deal disclosure visualization...")

if len(summary_df) > 0:
    fig, ax = plt.subplots(figsize=(14, 10))
    
    summary_sorted = summary_df.sort_values('TotalDeals', ascending=True)
    
    y_pos = np.arange(len(summary_sorted))
    
    # Stacked horizontal bar
    ax.barh(y_pos, summary_sorted['DealsWithValuation'], 
           color='#06A77D', alpha=0.8, label='Disclosed valuation')
    ax.barh(y_pos, summary_sorted['DealsWithoutValuation'], 
           left=summary_sorted['DealsWithValuation'],
           color='#E63946', alpha=0.6, label='Undisclosed valuation')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(summary_sorted['CompanyName'])
    ax.set_xlabel('Number of Deals', fontsize=12, fontweight='bold')
    ax.set_ylabel('Company', fontsize=12, fontweight='bold')
    ax.set_title('Deal Count by Company: Disclosed vs Undisclosed Valuations', 
                fontsize=16, fontweight='bold', pad=20)
    ax.legend(fontsize=11, loc='lower right')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, (idx, row) in enumerate(summary_sorted.iterrows()):
        # Disclosed count
        if row['DealsWithValuation'] > 0:
            ax.text(row['DealsWithValuation']/2, i, 
                   f"{int(row['DealsWithValuation'])}", 
                   va='center', ha='center', fontsize=10, fontweight='bold', color='white')
        # Undisclosed count
        if row['DealsWithoutValuation'] > 0:
            ax.text(row['DealsWithValuation'] + row['DealsWithoutValuation']/2, i, 
                   f"{int(row['DealsWithoutValuation'])}", 
                   va='center', ha='center', fontsize=10, fontweight='bold', color='white')
        # Total
        ax.text(row['TotalDeals'] + 0.3, i, 
               f"Total: {int(row['TotalDeals'])}", 
               va='center', ha='left', fontsize=9)
    
    plt.tight_layout()
    plot3_file = os.path.join(VIS_DIR, 'deal_disclosure_by_company.png')
    plt.savefig(plot3_file, dpi=300, bbox_inches='tight')
    print(f"Saved plot: {plot3_file}")
    plt.close()

print("\n" + "="*80)
print("ENHANCED VALUATION ANALYSIS COMPLETE")
print("="*80)
print(f"\nOutput directory: {OUTPUT_DIR}")
print(f"\nNew files created:")
print(f"  - all_deals_complete.csv (all deals including undisclosed)")
print(f"  - company_summary_complete.csv (summary with disclosed/undisclosed counts)")
print(f"  - valuation_trends_with_undisclosed.png (timeline with all deals)")
print(f"  - valuation_trends_individual_enhanced.png (individual charts with context)")
print(f"  - deal_disclosure_by_company.png (disclosure rate comparison)")

if len(summary_df) > 0:
    print(f"\nSummary Statistics:")
    print(f"  Total companies: {len(summary_df)}")
    print(f"  Total deals: {summary_df['TotalDeals'].sum()}")
    print(f"  Deals with disclosed valuations: {summary_df['DealsWithValuation'].sum()}")
    print(f"  Deals with undisclosed valuations: {summary_df['DealsWithoutValuation'].sum()}")
    print(f"  Disclosure rate: {summary_df['DealsWithValuation'].sum() / summary_df['TotalDeals'].sum() * 100:.1f}%")

