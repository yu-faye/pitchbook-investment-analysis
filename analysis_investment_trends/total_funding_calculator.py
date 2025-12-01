#!/usr/bin/env python3
"""
Total Funding Calculator for 14 Wearable Tech Companies
Aggregates funding from all available sources
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Company IDs from the list
company_ids = [
    "64325-80",    # Whoop
    "110783-26",   # Oura
    "458417-44",   # Ultrahuman
    "495718-39",   # Pulsetto
    "697387-24",   # ThingX
    "183205-63",   # Flow Neuroscience
    "56236-96",    # Catapult Sports
    "65652-22",    # GOQii
    "107433-19",   # Empatica
    "171678-43",   # Sensifai
    "494786-80",   # Playmaker
    "50982-94",    # Fitbit
    "100191-79",   # Zepp Health
    "61931-08"     # Peloton
]

company_names = {
    "64325-80": "Whoop",
    "110783-26": "Oura",
    "458417-44": "Ultrahuman",
    "495718-39": "Pulsetto",
    "697387-24": "ThingX",
    "183205-63": "Flow Neuroscience",
    "56236-96": "Catapult Sports",
    "65652-22": "GOQii",
    "107433-19": "Empatica",
    "171678-43": "Sensifai",
    "494786-80": "Playmaker",
    "50982-94": "Fitbit",
    "100191-79": "Zepp Health",
    "61931-08": "Peloton"
}

print("="*80)
print("TOTAL FUNDING CALCULATOR - 14 WEARABLE TECH COMPANIES")
print("="*80)

print("\nLoading Deal data...")
# Load deals in chunks
chunk_size = 100000
deals_list = []

for chunk in pd.read_csv('../Deal.csv', chunksize=chunk_size, low_memory=False):
    filtered = chunk[chunk['CompanyID'].isin(company_ids)]
    if len(filtered) > 0:
        deals_list.append(filtered)

deals = pd.concat(deals_list, ignore_index=True)
print(f"Found {len(deals)} deals for the 14 companies")

# Add company names
deals['company_name'] = deals['CompanyID'].map(company_names)

# Calculate funding from multiple sources
print("\nCalculating total funding from available data...")

# Method 1: DealSize (most direct)
deals_with_size = deals[deals['DealSize'].notna() & (deals['DealSize'] > 0)].copy()
print(f"\n1. Deals with DealSize field: {len(deals_with_size)} out of {len(deals)}")

# Method 2: IPO amounts
ipo_deals = deals[deals['DealType'] == 'IPO'].copy()
print(f"2. IPO deals found: {len(ipo_deals)}")

# Method 3: Acquisition amounts
acq_deals = deals[deals['DealType'].str.contains('Acquisition|Merger', case=False, na=False)].copy()
print(f"3. Acquisition/Merger deals found: {len(acq_deals)}")

print("\n" + "="*80)
print("FUNDING BREAKDOWN BY COMPANY")
print("="*80)

total_funding = 0
company_funding = {}

for comp_id in company_ids:
    comp_name = company_names[comp_id]
    comp_deals = deals[deals['CompanyID'] == comp_id]
    
    # Get deals with funding amounts
    comp_deals_with_funding = comp_deals[comp_deals['DealSize'].notna() & (comp_deals['DealSize'] > 0)]
    
    company_total = comp_deals_with_funding['DealSize'].sum()
    company_funding[comp_name] = company_total
    
    num_deals = len(comp_deals)
    num_funded = len(comp_deals_with_funding)
    
    print(f"\n{comp_name}:")
    print(f"  Total deals: {num_deals}")
    print(f"  Deals with disclosed funding: {num_funded}")
    # DealSize is already in millions
    if company_total >= 1000:
        print(f"  Total disclosed funding: ${company_total/1000:.2f}B (${company_total:.2f}M)")
    else:
        print(f"  Total disclosed funding: ${company_total:.2f}M")
    
    if company_total > 0:
        total_funding += company_total
        
        # Show top 3 largest rounds
        if num_funded > 0:
            top_rounds = comp_deals_with_funding.nlargest(min(3, num_funded), 'DealSize')
            print(f"  Top funding rounds:")
            for idx, deal in top_rounds.iterrows():
                deal_date = pd.to_datetime(deal['DealDate']).strftime('%Y-%m-%d') if pd.notna(deal['DealDate']) else 'Unknown'
                deal_type = deal.get('DealType', 'Unknown')
                vc_round = deal.get('VCRound', 'Unknown')
                # DealSize is already in millions
                print(f"    - {deal_date}: ${deal['DealSize']:.2f}M ({deal_type}, {vc_round})")

print("\n" + "="*80)
print("TOTAL FUNDING SUMMARY")
print("="*80)

# Sort companies by funding
sorted_companies = sorted(company_funding.items(), key=lambda x: x[1], reverse=True)

print(f"\nRanking by Total Disclosed Funding:")
print(f"\n{'Rank':<6}{'Company':<25}{'Total Funding':<20}{'% of Total'}")
print("-" * 70)

for rank, (company, funding) in enumerate(sorted_companies, 1):
    if funding > 0:
        pct = (funding / total_funding * 100) if total_funding > 0 else 0
        # DealSize is already in millions
        if funding >= 1000:
            funding_str = f"${funding/1000:.2f}B"
        else:
            funding_str = f"${funding:.2f}M"
        print(f"{rank:<6}{company:<25}{funding_str:<20}{pct:.1f}%")

print("\n" + "="*80)
# DealSize is already in millions
print(f"GRAND TOTAL DISCLOSED FUNDING: ${total_funding/1000:.2f} BILLION")
print(f"                                (${total_funding:.2f} Million)")
print("="*80)

# Additional statistics
print(f"\nAdditional Statistics:")
print(f"  Total number of deals: {len(deals)}")
print(f"  Deals with disclosed funding: {len(deals_with_size)}")
print(f"  Disclosure rate: {len(deals_with_size)/len(deals)*100:.1f}%")
# DealSize is already in millions
print(f"  Average funding per disclosed deal: ${(total_funding/len(deals_with_size)):.2f}M")
print(f"  Average funding per company: ${(total_funding/len(company_ids)):.2f}M")

# Companies with no disclosed funding
companies_no_funding = [name for name, funding in company_funding.items() if funding == 0]
if companies_no_funding:
    print(f"\n  Companies with no disclosed funding data:")
    for company in companies_no_funding:
        num_deals = len(deals[deals['company_name'] == company])
        print(f"    - {company}: {num_deals} deals (funding amounts not disclosed)")

print("\n" + "="*80)
print("Note: This total reflects only deals with disclosed funding amounts.")
print("Actual total funding may be higher due to undisclosed deal amounts.")
print("="*80)

# CREATE VISUALIZATIONS
print("\n" + "="*80)
print("GENERATING VISUALIZATIONS")
print("="*80)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (20, 12)

# Create figure with subplots
fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# 1. Total Funding by Company (Horizontal Bar Chart)
ax1 = fig.add_subplot(gs[0:2, 0])
sorted_companies_list = [(name, funding) for name, funding in sorted_companies if funding > 0]
companies_names = [item[0] for item in sorted_companies_list]
companies_values = [item[1] for item in sorted_companies_list]

# Create color gradient
colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(companies_names)))

bars = ax1.barh(range(len(companies_names)), companies_values, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)

# Add value labels on bars
for i, (name, val) in enumerate(sorted_companies_list):
    if val >= 1000:
        label = f'${val/1000:.2f}B'
    else:
        label = f'${val:.1f}M'
    
    # Position label inside or outside bar depending on value
    if val > max(companies_values) * 0.1:
        ax1.text(val - max(companies_values)*0.02, i, label, 
                va='center', ha='right', fontsize=11, fontweight='bold', color='white')
    else:
        ax1.text(val + max(companies_values)*0.01, i, label, 
                va='center', ha='left', fontsize=11, fontweight='bold')

ax1.set_yticks(range(len(companies_names)))
ax1.set_yticklabels(companies_names, fontsize=12, fontweight='bold')
ax1.set_xlabel('Total Funding (USD Millions)', fontsize=13, fontweight='bold')
ax1.set_title('Total Disclosed Funding by Company', fontsize=16, fontweight='bold', pad=20)
ax1.grid(axis='x', alpha=0.3)

# Add grand total annotation
ax1.text(0.98, 0.98, f'Grand Total:\n${total_funding/1000:.2f}B', 
         transform=ax1.transAxes, fontsize=14, fontweight='bold',
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# 2. Top 5 Companies Pie Chart
ax2 = fig.add_subplot(gs[0, 1])
top5 = sorted_companies_list[:5]
top5_names = [item[0] for item in top5]
top5_values = [item[1] for item in top5]
others_value = sum([item[1] for item in sorted_companies_list[5:]])

if others_value > 0:
    top5_names.append('Others (9 companies)')
    top5_values.append(others_value)

colors_pie = plt.cm.Set3(np.linspace(0, 1, len(top5_names)))
wedges, texts, autotexts = ax2.pie(top5_values, labels=top5_names, autopct='%1.1f%%',
                                     colors=colors_pie, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(12)

ax2.set_title('Funding Distribution\n(Top 5 + Others)', fontsize=14, fontweight='bold', pad=20)

# 3. Funding by Company Category
ax3 = fig.add_subplot(gs[1, 1])
# Categorize companies
categories = {
    'Market Leaders (>$3B)': sum([val for name, val in sorted_companies_list if val >= 3000]),
    'Established ($500M-$3B)': sum([val for name, val in sorted_companies_list if 500 <= val < 3000]),
    'Growth Stage ($50M-$500M)': sum([val for name, val in sorted_companies_list if 50 <= val < 500]),
    'Early Stage (<$50M)': sum([val for name, val in sorted_companies_list if val < 50])
}

cat_names = list(categories.keys())
cat_values = list(categories.values())

colors_cat = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
bars_cat = ax3.bar(range(len(cat_names)), cat_values, color=colors_cat, alpha=0.8, edgecolor='black', linewidth=1.5)

# Add value labels
for i, val in enumerate(cat_values):
    if val >= 1000:
        label = f'${val/1000:.2f}B'
    else:
        label = f'${val:.0f}M'
    ax3.text(i, val + max(cat_values)*0.02, label, ha='center', fontsize=12, fontweight='bold')

ax3.set_xticks(range(len(cat_names)))
ax3.set_xticklabels(cat_names, fontsize=10, fontweight='bold', rotation=15, ha='right')
ax3.set_ylabel('Total Funding (USD Millions)', fontsize=12, fontweight='bold')
ax3.set_title('Funding by Company Stage', fontsize=14, fontweight='bold', pad=20)
ax3.grid(axis='y', alpha=0.3)

# 4. Deal Statistics
ax4 = fig.add_subplot(gs[2, :])

# Create data for deal statistics
stats_data = {
    'Total\nDeals': len(deals),
    'Disclosed\nDeals': len(deals_with_size),
    'Undisclosed\nDeals': len(deals) - len(deals_with_size),
    'Total\nCompanies': len(company_ids),
    'Companies with\n>$500M': len([v for v in company_funding.values() if v >= 500]),
    'IPO/M&A\nExits': len(ipo_deals) + len(acq_deals)
}

stat_names = list(stats_data.keys())
stat_values = list(stats_data.values())

colors_stats = ['#06A77D' if i % 2 == 0 else '#E63946' for i in range(len(stat_names))]
bars_stats = ax4.bar(range(len(stat_names)), stat_values, color=colors_stats, alpha=0.7, edgecolor='black', linewidth=1.5)

# Add value labels
for i, val in enumerate(stat_values):
    ax4.text(i, val + max(stat_values)*0.02, str(int(val)), ha='center', fontsize=14, fontweight='bold')

ax4.set_xticks(range(len(stat_names)))
ax4.set_xticklabels(stat_names, fontsize=12, fontweight='bold')
ax4.set_ylabel('Count', fontsize=12, fontweight='bold')
ax4.set_title('Investment Statistics Summary', fontsize=14, fontweight='bold', pad=20)
ax4.grid(axis='y', alpha=0.3)

# Add main title
fig.suptitle('14 WEARABLE TECH COMPANIES - TOTAL FUNDING ANALYSIS\nGrand Total: $11.29 Billion',
             fontsize=20, fontweight='bold', y=0.98)

plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save the figure
output_file = 'total_funding_visualization.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✓ Visualization saved as '{output_file}'")

# Create a second, simpler chart for quick reference
fig2, ax = plt.subplots(figsize=(16, 10))

# Simple bar chart with all companies
sorted_all = [(name, funding) for name, funding in sorted_companies if funding > 0]
names_all = [item[0] for item in sorted_all]
values_all = [item[1] for item in sorted_all]

# Color code by size
colors_all = []
for val in values_all:
    if val >= 3000:
        colors_all.append('#1f77b4')  # Blue for >$3B
    elif val >= 500:
        colors_all.append('#ff7f0e')  # Orange for $500M-$3B
    elif val >= 50:
        colors_all.append('#2ca02c')  # Green for $50M-$500M
    else:
        colors_all.append('#d62728')  # Red for <$50M

bars = ax.barh(range(len(names_all)), values_all, color=colors_all, alpha=0.8, edgecolor='black', linewidth=0.8)

# Add value labels
for i, (name, val) in enumerate(sorted_all):
    if val >= 1000:
        label = f'${val/1000:.2f}B'
    else:
        label = f'${val:.1f}M'
    
    # Determine label position
    if val > max(values_all) * 0.05:
        ax.text(val - max(values_all)*0.01, i, label, 
               va='center', ha='right', fontsize=12, fontweight='bold', color='white')
    else:
        ax.text(val + max(values_all)*0.01, i, label, 
               va='center', ha='left', fontsize=12, fontweight='bold')

ax.set_yticks(range(len(names_all)))
ax.set_yticklabels(names_all, fontsize=13, fontweight='bold')
ax.set_xlabel('Total Disclosed Funding', fontsize=14, fontweight='bold')
ax.set_title('Total Funding by Company - 14 Wearable Tech Companies\nGrand Total: $11.29 Billion',
            fontsize=18, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

# Add legend for color coding
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#1f77b4', edgecolor='black', label='Market Leaders (>$3B)'),
    Patch(facecolor='#ff7f0e', edgecolor='black', label='Established ($500M-$3B)'),
    Patch(facecolor='#2ca02c', edgecolor='black', label='Growth Stage ($50M-$500M)'),
    Patch(facecolor='#d62728', edgecolor='black', label='Early Stage (<$50M)')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=11, framealpha=0.9)

plt.tight_layout()

output_file2 = 'total_funding_simple.png'
plt.savefig(output_file2, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✓ Simple visualization saved as '{output_file2}'")

print("\n" + "="*80)
print("ANALYSIS AND VISUALIZATIONS COMPLETE")
print("="*80)
print(f"\nGenerated files:")
print(f"  1. {output_file} - Comprehensive 4-panel analysis")
print(f"  2. {output_file2} - Simple bar chart for quick reference")
print(f"\nGrand Total: ${total_funding/1000:.2f} Billion (${total_funding:.2f} Million)")
print("="*80)

