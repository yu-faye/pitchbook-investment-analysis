#!/usr/bin/env python3
"""
Capital Efficiency Analysis for Oura, Whoop, and Pulsetto
Compares total funding raised vs. latest valuation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")

# Target companies
target_companies = {
    "110783-26": "Oura",
    "64325-80": "Whoop",
    "495718-39": "Pulsetto"
}

company_ids = list(target_companies.keys())

print("="*80)
print("CAPITAL EFFICIENCY ANALYSIS")
print("Companies: Oura, Whoop, Pulsetto")
print("="*80)

# Load Deal data
print("\nLoading Deal data...")
chunk_size = 100000
deals_list = []

for chunk in pd.read_csv('../Deal.csv', chunksize=chunk_size, low_memory=False):
    filtered = chunk[chunk['CompanyID'].isin(company_ids)]
    if len(filtered) > 0:
        deals_list.append(filtered)

deals = pd.concat(deals_list, ignore_index=True)
deals['company_name'] = deals['CompanyID'].map(target_companies)
print(f"Found {len(deals)} deals")

# Calculate total funding per company
print("\n" + "="*80)
print("TOTAL FUNDING RAISED")
print("="*80)

funding_data = {}

for comp_id, comp_name in target_companies.items():
    comp_deals = deals[deals['CompanyID'] == comp_id]
    comp_deals_with_funding = comp_deals[comp_deals['DealSize'].notna() & (comp_deals['DealSize'] > 0)]
    
    total_funding = comp_deals_with_funding['DealSize'].sum()
    funding_data[comp_name] = {
        'total_funding': total_funding,
        'num_deals': len(comp_deals),
        'num_disclosed': len(comp_deals_with_funding)
    }
    
    print(f"\n{comp_name}:")
    print(f"  Total deals: {len(comp_deals)}")
    print(f"  Deals with disclosed funding: {len(comp_deals_with_funding)}")
    print(f"  Total funding raised: ${total_funding:.2f}M")

# Get latest valuations
print("\n" + "="*80)
print("LATEST VALUATIONS")
print("="*80)

# Filter deals with valuation data
deals['PostValuation_clean'] = pd.to_numeric(deals['PostValuation'], errors='coerce')
deals['PremoneyValuation_clean'] = pd.to_numeric(deals['PremoneyValuation'], errors='coerce')
deals['Valuation'] = deals['PostValuation_clean'].fillna(deals['PremoneyValuation_clean'])
deals['DealDate'] = pd.to_datetime(deals['DealDate'], errors='coerce')

valuation_data = {}

for comp_id, comp_name in target_companies.items():
    comp_deals = deals[deals['CompanyID'] == comp_id]
    comp_deals_with_val = comp_deals[comp_deals['Valuation'].notna() & (comp_deals['Valuation'] > 0)]
    
    if len(comp_deals_with_val) > 0:
        comp_deals_with_val = comp_deals_with_val.sort_values('DealDate')
        latest_val_deal = comp_deals_with_val.iloc[-1]
        latest_valuation = latest_val_deal['Valuation']
        latest_date = latest_val_deal['DealDate']
        
        valuation_data[comp_name] = {
            'latest_valuation': latest_valuation,
            'latest_date': latest_date,
            'num_valuation_points': len(comp_deals_with_val)
        }
        
        print(f"\n{comp_name}:")
        print(f"  Latest valuation: ${latest_valuation:.2f}M")
        print(f"  Valuation date: {latest_date.strftime('%Y-%m-%d') if pd.notna(latest_date) else 'Unknown'}")
        print(f"  Total valuation data points: {len(comp_deals_with_val)}")
    else:
        valuation_data[comp_name] = {
            'latest_valuation': None,
            'latest_date': None,
            'num_valuation_points': 0
        }
        print(f"\n{comp_name}:")
        print(f"  No valuation data available")

# Calculate capital efficiency
print("\n" + "="*80)
print("CAPITAL EFFICIENCY ANALYSIS")
print("="*80)
print("\nMetric Definitions:")
print("  • Capital Efficiency Ratio = Latest Valuation / Total Funding")
print("    (Higher is better - shows value created per dollar invested)")
print("  • Funding to Valuation = Total Funding / Latest Valuation")
print("    (Lower is better - shows efficiency of capital deployment)")
print("\n" + "-"*80)

efficiency_data = {}

for comp_name in target_companies.values():
    funding = funding_data[comp_name]['total_funding']
    valuation = valuation_data[comp_name]['latest_valuation']
    
    if valuation and valuation > 0 and funding > 0:
        efficiency_ratio = valuation / funding
        funding_to_val = funding / valuation
        
        efficiency_data[comp_name] = {
            'funding': funding,
            'valuation': valuation,
            'efficiency_ratio': efficiency_ratio,
            'funding_to_val_pct': funding_to_val * 100,
            'value_created': valuation - funding
        }
        
        print(f"\n{comp_name}:")
        print(f"  Total Funding Raised:    ${funding:.2f}M")
        print(f"  Latest Valuation:        ${valuation:.2f}M")
        print(f"  Value Created:           ${valuation - funding:.2f}M")
        print(f"  Capital Efficiency:      {efficiency_ratio:.2f}x")
        print(f"    → ${efficiency_ratio:.2f} of value per $1 invested")
        print(f"  Funding/Valuation:       {funding_to_val * 100:.1f}%")
        print(f"    → Raised {funding_to_val * 100:.1f}% of current valuation")
    else:
        efficiency_data[comp_name] = None
        print(f"\n{comp_name}:")
        print(f"  Total Funding Raised:    ${funding:.2f}M")
        print(f"  Latest Valuation:        Not Available")
        print(f"  Capital Efficiency:      Cannot calculate")

# Summary comparison
print("\n" + "="*80)
print("COMPARATIVE RANKING")
print("="*80)

valid_companies = [(name, data) for name, data in efficiency_data.items() if data is not None]

if valid_companies:
    print("\nBy Capital Efficiency (Valuation/Funding) - Higher is Better:")
    sorted_by_efficiency = sorted(valid_companies, key=lambda x: x[1]['efficiency_ratio'], reverse=True)
    for rank, (name, data) in enumerate(sorted_by_efficiency, 1):
        print(f"  {rank}. {name:15s} {data['efficiency_ratio']:>6.2f}x  (${data['valuation']:.2f}M / ${data['funding']:.2f}M)")
    
    print("\nBy Funding Efficiency (Funding/Valuation %) - Lower is Better:")
    sorted_by_funding = sorted(valid_companies, key=lambda x: x[1]['funding_to_val_pct'])
    for rank, (name, data) in enumerate(sorted_by_funding, 1):
        print(f"  {rank}. {name:15s} {data['funding_to_val_pct']:>5.1f}%  (Raised ${data['funding']:.2f}M for ${data['valuation']:.2f}M valuation)")

# CREATE VISUALIZATIONS
print("\n" + "="*80)
print("GENERATING VISUALIZATIONS")
print("="*80)

# Create comprehensive visualization
fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# 1. Funding vs Valuation Comparison
ax1 = fig.add_subplot(gs[0, :])

companies_with_data = [name for name in target_companies.values() if efficiency_data.get(name)]
x_pos = np.arange(len(companies_with_data))
width = 0.35

funding_values = [efficiency_data[name]['funding'] for name in companies_with_data]
valuation_values = [efficiency_data[name]['valuation'] for name in companies_with_data]

bars1 = ax1.bar(x_pos - width/2, funding_values, width, label='Total Funding Raised', 
               color='#E63946', alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax1.bar(x_pos + width/2, valuation_values, width, label='Latest Valuation',
               color='#06A77D', alpha=0.8, edgecolor='black', linewidth=1.5)

# Add value labels
for i, v in enumerate(funding_values):
    ax1.text(i - width/2, v + max(valuation_values)*0.02, f'${v:.0f}M',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

for i, v in enumerate(valuation_values):
    ax1.text(i + width/2, v + max(valuation_values)*0.02, f'${v:.0f}M',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax1.set_xticks(x_pos)
ax1.set_xticklabels(companies_with_data, fontsize=13, fontweight='bold')
ax1.set_ylabel('Amount (USD Millions)', fontsize=12, fontweight='bold')
ax1.set_title('Total Funding vs Latest Valuation', fontsize=16, fontweight='bold', pad=15)
ax1.legend(fontsize=12, loc='upper right', framealpha=0.95, edgecolor='black')
ax1.grid(axis='y', alpha=0.3)

# 2. Capital Efficiency Ratio
ax2 = fig.add_subplot(gs[1, 0])

efficiency_ratios = [efficiency_data[name]['efficiency_ratio'] for name in companies_with_data]
colors_eff = ['#2E86AB', '#A23B72', '#F18F01'][:len(companies_with_data)]

bars = ax2.bar(x_pos, efficiency_ratios, color=colors_eff, alpha=0.8, 
              edgecolor='black', linewidth=1.5)

# Add value labels and benchmark line
for i, v in enumerate(efficiency_ratios):
    ax2.text(i, v + max(efficiency_ratios)*0.02, f'{v:.2f}x',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

# Add 1x benchmark line
ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Break-even (1.0x)')

ax2.set_xticks(x_pos)
ax2.set_xticklabels(companies_with_data, fontsize=12, fontweight='bold')
ax2.set_ylabel('Efficiency Ratio (x)', fontsize=11, fontweight='bold')
ax2.set_title('Capital Efficiency Ratio\n(Valuation / Funding)\nHigher is Better', 
             fontsize=14, fontweight='bold', pad=15)
ax2.legend(fontsize=10, loc='upper left', framealpha=0.95, edgecolor='black')
ax2.grid(axis='y', alpha=0.3)

# 3. Funding as % of Valuation
ax3 = fig.add_subplot(gs[1, 1])

funding_pct = [efficiency_data[name]['funding_to_val_pct'] for name in companies_with_data]
colors_pct = ['#06A77D' if x < 20 else '#F18F01' if x < 40 else '#E63946' for x in funding_pct]

bars = ax3.bar(x_pos, funding_pct, color=colors_pct, alpha=0.8, 
              edgecolor='black', linewidth=1.5)

# Add value labels
for i, v in enumerate(funding_pct):
    ax3.text(i, v + max(funding_pct)*0.02, f'{v:.1f}%',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

ax3.set_xticks(x_pos)
ax3.set_xticklabels(companies_with_data, fontsize=12, fontweight='bold')
ax3.set_ylabel('Percentage (%)', fontsize=11, fontweight='bold')
ax3.set_title('Funding as % of Valuation\n(Funding / Valuation)\nLower is Better', 
             fontsize=14, fontweight='bold', pad=15)
ax3.grid(axis='y', alpha=0.3)

# Add color legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#06A77D', label='Excellent (<20%)', edgecolor='black'),
    Patch(facecolor='#F18F01', label='Good (20-40%)', edgecolor='black'),
    Patch(facecolor='#E63946', label='High (>40%)', edgecolor='black')
]
ax3.legend(handles=legend_elements, loc='upper left', fontsize=9, framealpha=0.95, edgecolor='black')

# 4. Value Created
ax4 = fig.add_subplot(gs[2, 0])

value_created = [efficiency_data[name]['value_created'] for name in companies_with_data]
colors_val = ['#1f77b4', '#ff7f0e', '#2ca02c'][:len(companies_with_data)]

bars = ax4.bar(x_pos, value_created, color=colors_val, alpha=0.8, 
              edgecolor='black', linewidth=1.5)

# Add value labels
for i, v in enumerate(value_created):
    ax4.text(i, v + max(value_created)*0.02, f'${v:.0f}M',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

ax4.set_xticks(x_pos)
ax4.set_xticklabels(companies_with_data, fontsize=12, fontweight='bold')
ax4.set_ylabel('Value Created (USD Millions)', fontsize=11, fontweight='bold')
ax4.set_title('Total Value Created\n(Valuation - Funding)', fontsize=14, fontweight='bold', pad=15)
ax4.grid(axis='y', alpha=0.3)

# 5. Summary Table
ax5 = fig.add_subplot(gs[2, 1])
ax5.axis('off')

# Create summary table
table_data = []
for name in companies_with_data:
    data = efficiency_data[name]
    table_data.append([
        name,
        f"${data['funding']:.1f}M",
        f"${data['valuation']:.1f}M",
        f"{data['efficiency_ratio']:.2f}x",
        f"{data['funding_to_val_pct']:.1f}%"
    ])

table = ax5.table(cellText=table_data,
                 colLabels=['Company', 'Funding', 'Valuation', 'Efficiency', 'Fund/Val %'],
                 cellLoc='center',
                 loc='center',
                 bbox=[0, 0.3, 1, 0.6])

table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 2.5)

# Style header
for i in range(5):
    table[(0, i)].set_facecolor('#2E86AB')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Style data rows
colors_row = ['#E8F4F8', '#FFFFFF']
for i in range(len(table_data)):
    for j in range(5):
        table[(i+1, j)].set_facecolor(colors_row[i % 2])
        table[(i+1, j)].set_text_props(weight='bold')

ax5.text(0.5, 0.15, 'Capital Efficiency Summary', 
        ha='center', fontsize=14, fontweight='bold',
        transform=ax5.transAxes)

# Add main title
fig.suptitle('CAPITAL EFFICIENCY ANALYSIS\nOura | Whoop | Pulsetto',
            fontsize=18, fontweight='bold', y=0.98)

# Save
output_file1 = 'capital_efficiency_analysis.png'
plt.savefig(output_file1, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✓ Comprehensive visualization saved as '{output_file1}'")

# Create simple comparison chart
fig2, ax = plt.subplots(figsize=(14, 8))

# Create grouped bar chart
x = np.arange(len(companies_with_data))
width = 0.25

funding_bars = ax.bar(x - width, funding_values, width, label='Funding Raised', 
                     color='#E63946', alpha=0.8, edgecolor='black', linewidth=1)
valuation_bars = ax.bar(x, valuation_values, width, label='Latest Valuation',
                       color='#06A77D', alpha=0.8, edgecolor='black', linewidth=1)
value_created_vals = [v - f for v, f in zip(valuation_values, funding_values)]
created_bars = ax.bar(x + width, value_created_vals, width, label='Value Created',
                     color='#2E86AB', alpha=0.8, edgecolor='black', linewidth=1)

# Add value labels
for i, (f, v, c) in enumerate(zip(funding_values, valuation_values, value_created_vals)):
    ax.text(i - width, f + max(valuation_values)*0.01, f'${f:.0f}M',
           ha='center', va='bottom', fontsize=10, fontweight='bold', rotation=0)
    ax.text(i, v + max(valuation_values)*0.01, f'${v:.0f}M',
           ha='center', va='bottom', fontsize=10, fontweight='bold', rotation=0)
    ax.text(i + width, c + max(valuation_values)*0.01, f'${c:.0f}M',
           ha='center', va='bottom', fontsize=10, fontweight='bold', rotation=0)

ax.set_xticks(x)
ax.set_xticklabels(companies_with_data, fontsize=14, fontweight='bold')
ax.set_ylabel('Amount (USD Millions)', fontsize=13, fontweight='bold')
ax.set_title('Capital Efficiency Comparison\nFunding vs Valuation vs Value Created',
            fontsize=16, fontweight='bold', pad=20)
ax.legend(fontsize=12, loc='upper right', framealpha=0.95, edgecolor='black')
ax.grid(axis='y', alpha=0.3)
# Set y-axis limit to accommodate efficiency text boxes
ax.set_ylim(0, max(valuation_values)*1.3)

# Add efficiency ratios as text at the top
for i, name in enumerate(companies_with_data):
    ratio = efficiency_data[name]['efficiency_ratio']
    pct = efficiency_data[name]['funding_to_val_pct']
    ax.text(i, max(valuation_values)*1.15, 
           f'Efficiency: {ratio:.2f}x\n({pct:.1f}% funded)',
           ha='center', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9, edgecolor='black', linewidth=1))

plt.tight_layout()

output_file2 = 'capital_efficiency_simple.png'
plt.savefig(output_file2, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✓ Simple comparison saved as '{output_file2}'")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print(f"\nGenerated files:")
print(f"  1. {output_file1} - Comprehensive 5-panel analysis")
print(f"  2. {output_file2} - Simple comparison chart")
print("="*80)

