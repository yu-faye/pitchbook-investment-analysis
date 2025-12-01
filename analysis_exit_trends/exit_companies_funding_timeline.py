import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (20, 12)

# Company IDs for exited companies
exited_companies = {
    "56236-96": "Catapult Sports",
    "50982-94": "Fitbit",
    "100191-79": "Zepp Health",
    "61931-08": "Peloton"
}

company_ids = list(exited_companies.keys())

print("="*100)
print("LOADING DATA FOR EXITED COMPANIES - FUNDING TIMELINE ANALYSIS")
print("="*100)

# Load Deal data
print("\nLoading Deal data...")
chunk_size = 100000
deals_list = []

for chunk in pd.read_csv('../Deal.csv', chunksize=chunk_size, low_memory=False):
    filtered = chunk[chunk['CompanyID'].isin(company_ids)]
    if len(filtered) > 0:
        deals_list.append(filtered)

deals = pd.concat(deals_list, ignore_index=True)
deals['DealDate'] = pd.to_datetime(deals['DealDate'], errors='coerce')
deals['date'] = deals['DealDate']
deals['company_name'] = deals['CompanyID'].map(exited_companies)
deals['year'] = deals['date'].dt.year

# Sort deals by date
deals = deals.sort_values(['CompanyID', 'date'])

print(f"✓ Loaded {len(deals)} deals for {len(company_ids)} exited companies")

# Create figure with 4 subplots (2x2)
fig, axes = plt.subplots(2, 2, figsize=(24, 16))
axes = axes.flatten()

# Exit types to identify
exit_types = ['Acquisition', 'IPO', 'Merger', 'LBO', 'Buyout']

# Color scheme for different deal types
deal_type_colors = {
    'Angel (individual)': '#ff9999',
    'Seed Round': '#ffcc99',
    'Early Stage VC': '#99ccff',
    'Later Stage VC': '#9999ff',
    'IPO': '#ffd700',
    'PIPE': '#cccccc',
    'Product Crowdfunding': '#ffb3e6',
    'Joint Venture': '#c2f0c2',
    'Secondary Transaction - Open Market': '#e6e6e6',
    'Secondary Transaction - Private': '#d9d9d9',
    'Public Investment 2nd Offering': '#b3b3b3',
    'Merger/Acquisition': '#ff6666',
    'General Corporate Purpose': '#ccccff',
    'Debt Refinancing': '#ffcccc'
}

# Process each company
for idx, (comp_id, comp_name) in enumerate(exited_companies.items()):
    ax = axes[idx]
    comp_deals = deals[deals['CompanyID'] == comp_id].copy()
    
    print(f"\nProcessing {comp_name}...")
    print(f"  Total deals: {len(comp_deals)}")
    
    # Filter deals with valid dates and deal sizes
    comp_deals_with_size = comp_deals[pd.notna(comp_deals['DealSize']) & pd.notna(comp_deals['date'])].copy()
    
    # Separate pre-exit and post-exit deals
    exit_deal = comp_deals[comp_deals['DealType'].isin(exit_types)]
    
    if len(exit_deal) > 0:
        exit_date = exit_deal.iloc[0]['date']
        exit_val = exit_deal.iloc[0].get('PostValuation', None)
        exit_size = exit_deal.iloc[0].get('DealSize', None)
        
        pre_exit_deals = comp_deals_with_size[comp_deals_with_size['date'] < exit_date]
        post_exit_deals = comp_deals_with_size[comp_deals_with_size['date'] >= exit_date]
        
        print(f"  Exit date: {exit_date.strftime('%Y-%m-%d')}")
        print(f"  Pre-exit deals with size: {len(pre_exit_deals)}")
        print(f"  Post-exit deals: {len(post_exit_deals)}")
    else:
        exit_date = None
        exit_val = None
        exit_size = None
        pre_exit_deals = comp_deals_with_size
        post_exit_deals = pd.DataFrame()
    
    # Plot pre-exit deals
    if len(pre_exit_deals) > 0:
        for i, deal in pre_exit_deals.iterrows():
            deal_type = deal['DealType']
            color = deal_type_colors.get(deal_type, '#999999')
            
            ax.bar(deal['date'], deal['DealSize'], width=100, 
                   color=color, alpha=0.7, edgecolor='black', linewidth=1.5,
                   label=deal_type if deal_type not in [d.get_label() for d in ax.containers] else '')
    
    # Plot exit deal with special marker
    if exit_date and pd.notna(exit_size):
        ax.bar(exit_date, exit_size, width=100, 
               color='gold', alpha=0.9, edgecolor='darkgreen', linewidth=3,
               label='IPO')
        
        # Add exit annotation
        ax.annotate(f'IPO EXIT\n{exit_date.strftime("%b %Y")}\n${exit_size:.0f}M',
                   xy=(exit_date, exit_size),
                   xytext=(exit_date, exit_size * 1.2),
                   ha='center', va='bottom',
                   fontsize=10, fontweight='bold', color='darkgreen',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8),
                   arrowprops=dict(arrowstyle='->', color='darkgreen', lw=2))
    
    # Plot post-exit deals (lighter color)
    if len(post_exit_deals) > 0:
        for i, deal in post_exit_deals.iterrows():
            deal_type = deal['DealType']
            ax.bar(deal['date'], deal['DealSize'], width=100,
                   color='lightgray', alpha=0.5, edgecolor='gray', linewidth=1,
                   label='Post-Exit Deals' if i == post_exit_deals.index[0] else '')
    
    # Add cumulative funding line (pre-exit only)
    if len(pre_exit_deals) > 0:
        cumulative = pre_exit_deals['DealSize'].cumsum()
        ax2 = ax.twinx()
        ax2.plot(pre_exit_deals['date'], cumulative, 'r-', linewidth=3, 
                marker='o', markersize=6, alpha=0.7, label='Cumulative Funding')
        ax2.set_ylabel('Cumulative Funding ($M)', fontsize=12, fontweight='bold', color='red')
        ax2.tick_params(axis='y', labelcolor='red')
        
        # Add final cumulative amount
        final_cumulative = cumulative.iloc[-1]
        ax2.text(0.98, 0.95, f'Total Pre-Exit: ${final_cumulative:.1f}M',
                transform=ax.transAxes, fontsize=11, fontweight='bold',
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Formatting
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Deal Size ($M)', fontsize=12, fontweight='bold')
    ax.set_title(f'{comp_name} - Funding Timeline to Exit', fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3, axis='y')
    
    # Add legend (only unique entries)
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    if len(by_label) > 0:
        ax.legend(by_label.values(), by_label.keys(), 
                 loc='upper left', fontsize=8, ncol=1)
    
    # Add exit valuation if available
    if exit_val and pd.notna(exit_val):
        ax.text(0.02, 0.95, f'Exit Valuation: ${exit_val:.0f}M',
               transform=ax.transAxes, fontsize=11, fontweight='bold',
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    # Rotate x-axis labels
    ax.tick_params(axis='x', rotation=45)

plt.suptitle('EXIT COMPANIES: Individual Funding Timelines & Deal Amounts', 
             fontsize=18, fontweight='bold', y=0.995)
plt.tight_layout()

output_file = 'exit_companies_funding_timeline.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\n✓ Visualization saved as '{output_file}'")

print("\n" + "="*100)
print("SUMMARY STATISTICS")
print("="*100)

for comp_id, comp_name in exited_companies.items():
    comp_deals = deals[deals['CompanyID'] == comp_id].copy()
    exit_deal = comp_deals[comp_deals['DealType'].isin(exit_types)]
    
    if len(exit_deal) > 0:
        exit_date = exit_deal.iloc[0]['date']
        pre_exit = comp_deals[(comp_deals['date'] < exit_date) & pd.notna(comp_deals['DealSize'])]
    else:
        pre_exit = comp_deals[pd.notna(comp_deals['DealSize'])]
    
    total_raised = pre_exit['DealSize'].sum()
    num_rounds = len(pre_exit)
    avg_round_size = pre_exit['DealSize'].mean() if num_rounds > 0 else 0
    
    print(f"\n{comp_name}:")
    print(f"  Total Raised (Pre-Exit): ${total_raised:.2f}M")
    print(f"  Number of Rounds: {num_rounds}")
    print(f"  Average Round Size: ${avg_round_size:.2f}M")
    if len(exit_deal) > 0:
        exit_val = exit_deal.iloc[0].get('PostValuation')
        if pd.notna(exit_val) and total_raised > 0:
            multiple = exit_val / total_raised
            print(f"  Exit Multiple: {multiple:.2f}x")

print("\n" + "="*100)
print("ANALYSIS COMPLETE")
print("="*100)




