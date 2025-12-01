#!/usr/bin/env python3
"""
Create a bar chart showing each company's latest valuation
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# Paths
BASE_DIR = '/Users/yufei/SchoolWork/fin/stata'
ANALYSIS_DIR = os.path.join(BASE_DIR, 'analysis_valuation_trends')
DATA_DIR = os.path.join(ANALYSIS_DIR, 'data')
VIS_DIR = os.path.join(ANALYSIS_DIR, 'visualizations')

# Ensure visualization directory exists
os.makedirs(VIS_DIR, exist_ok=True)

print("Loading valuation data...")
# Load latest valuation table
valuation_file = os.path.join(DATA_DIR, 'latest_valuation_table.csv')
if not os.path.exists(valuation_file):
    print(f"Error: {valuation_file} not found!")
    exit(1)

df = pd.read_csv(valuation_file)
print(f"Loaded valuation data for {len(df)} companies")

# Parse valuation strings to numeric values (in millions)
def parse_valuation(val_str):
    """Convert valuation string like '$8.10B' or '$125.49M' to millions"""
    if pd.isna(val_str) or val_str == 'N/A':
        return 0
    
    val_str = str(val_str).replace('$', '').replace(',', '').strip()
    
    if 'B' in val_str:
        return float(val_str.replace('B', '')) * 1000  # Convert billions to millions
    elif 'M' in val_str:
        return float(val_str.replace('M', ''))
    else:
        return 0

# Add numeric valuation column
df['ValuationMillions'] = df['Latest Valuation'].apply(parse_valuation)

# Filter to companies with valuations
df_with_vals = df[df['ValuationMillions'] > 0].copy()

# Sort by valuation (descending)
df_with_vals = df_with_vals.sort_values('ValuationMillions', ascending=False)

print(f"\nCompanies with valuations: {len(df_with_vals)}")
print(f"Total valuation sum: ${df_with_vals['ValuationMillions'].sum():,.2f}M (${df_with_vals['ValuationMillions'].sum()/1000:.2f}B)")

# Create the visualization
fig, ax = plt.subplots(figsize=(14, 8))

# Create color palette
colors = sns.color_palette("husl", len(df_with_vals))

# Create horizontal bar chart
bars = ax.barh(range(len(df_with_vals)), 
               df_with_vals['ValuationMillions'],
               color=colors)

# Customize the chart
ax.set_yticks(range(len(df_with_vals)))
ax.set_yticklabels(df_with_vals['Company Name'])
ax.set_xlabel('Valuation (Millions USD)', fontsize=12, fontweight='bold')
ax.set_title('Company Valuations Summary', fontsize=16, fontweight='bold', pad=20)

# Format x-axis to show values in millions
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.1f}B' if x >= 1000 else f'${x:.0f}M'))

# Add value labels on bars
for i, (idx, row) in enumerate(df_with_vals.iterrows()):
    val = row['ValuationMillions']
    if val >= 1000:
        label = f'${val/1000:.2f}B'
    else:
        label = f'${val:.2f}M'
    
    # Position label at the end of the bar
    ax.text(val, i, f'  {label}', 
            va='center', ha='left', fontweight='bold', fontsize=10)

# Add grid
ax.grid(axis='x', alpha=0.3, linestyle='--')

# Invert y-axis so highest value is at top
ax.invert_yaxis()

# Adjust layout
plt.tight_layout()

# Save the figure
output_file = os.path.join(VIS_DIR, 'company_valuation_summary.png')
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization to: {output_file}")

# Also create a vertical bar chart version
fig2, ax2 = plt.subplots(figsize=(12, 8))

bars2 = ax2.bar(range(len(df_with_vals)), 
                df_with_vals['ValuationMillions'],
                color=colors)

ax2.set_xticks(range(len(df_with_vals)))
ax2.set_xticklabels(df_with_vals['Company Name'], rotation=45, ha='right')
ax2.set_ylabel('Valuation (Millions USD)', fontsize=12, fontweight='bold')
ax2.set_title('Company Valuations Summary (Vertical)', fontsize=16, fontweight='bold', pad=20)

# Format y-axis
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.1f}B' if x >= 1000 else f'${x:.0f}M'))

# Add value labels on top of bars
for i, (idx, row) in enumerate(df_with_vals.iterrows()):
    val = row['ValuationMillions']
    if val >= 1000:
        label = f'${val/1000:.2f}B'
    else:
        label = f'${val:.2f}M'
    
    ax2.text(i, val, label, 
            va='bottom', ha='center', fontweight='bold', fontsize=9, rotation=0)

ax2.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()

output_file2 = os.path.join(VIS_DIR, 'company_valuation_summary_vertical.png')
plt.savefig(output_file2, dpi=300, bbox_inches='tight')
print(f"✓ Saved vertical visualization to: {output_file2}")

# Print summary table
print("\n" + "="*80)
print("VALUATION SUMMARY TABLE")
print("="*80)
summary_df = df_with_vals[['Company Name', 'Latest Valuation', 'Latest Valuation Date']].copy()
print(summary_df.to_string(index=False))
print("="*80)

print("\n✓ Visualization complete!")


