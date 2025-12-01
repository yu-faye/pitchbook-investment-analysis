import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

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
    "142343-92",   # Playermaker
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
    "142343-92": "Playermaker",
    "50982-94": "Fitbit",
    "100191-79": "Zepp Health",
    "61931-08": "Peloton"
}

print("="*100)
print("ENTRY MECHANISM vs PERFORMANCE CORRELATION ANALYSIS")
print("="*100)

# Load entry mechanism data
print("\n1. Loading entry mechanism data...")
entry_data = pd.read_csv('entry_data_by_company.csv')
entry_data['company_id'] = entry_data['company_id'].astype(str)
print(f"   Loaded entry data for {len(entry_data)} companies")

# Load deal data to calculate total funding
print("\n2. Loading deal data to calculate total funding...")
chunk_size = 100000
deals_list = []

for chunk in pd.read_csv('../Deal.csv', chunksize=chunk_size, low_memory=False):
    filtered = chunk[chunk['CompanyID'].isin(company_ids)]
    if len(filtered) > 0:
        deals_list.append(filtered)

deals = pd.concat(deals_list, ignore_index=True)
deals['DealDate'] = pd.to_datetime(deals['DealDate'], errors='coerce')
deals['year'] = deals['DealDate'].dt.year
print(f"   Loaded {len(deals)} deals")

# Calculate total funding per company
print("\n3. Calculating total funding per company...")
# Handle DealSize - it may already be in millions, but let's check
# DealSize is typically in millions, so we'll use it as-is
total_funding = deals.groupby('CompanyID').agg({
    'DealSize': lambda x: x[x.notna()].sum(),
    'DealID': 'count'
}).reset_index()
total_funding.columns = ['company_id', 'total_funding', 'total_deals']
total_funding['company_id'] = total_funding['company_id'].astype(str)
# DealSize is already in millions based on the data format
# If it's not, we'll adjust based on the actual values

# Load valuation data
print("\n4. Loading valuation data...")
valuation_data = pd.read_csv('../analysis_valuation_trends/data/valuation_summary_by_company.csv')
valuation_data['CompanyID'] = valuation_data['CompanyID'].astype(str)
valuation_data = valuation_data[['CompanyID', 'LatestValuation', 'ValuationGrowthPct', 'TotalValuationPoints']].copy()
valuation_data.columns = ['company_id', 'latest_valuation', 'valuation_growth_pct', 'valuation_points']
print(f"   Loaded valuation data for {len(valuation_data)} companies")

# Merge all data
print("\n5. Merging data...")
performance_data = entry_data.merge(
    total_funding, 
    on='company_id', 
    how='left'
).merge(
    valuation_data,
    on='company_id',
    how='left'
)

# Add company names
performance_data['company_name'] = performance_data['company_id'].map(company_names)

print(f"\n   Final dataset: {len(performance_data)} companies")
print(f"   Companies with funding data: {performance_data['total_funding'].notna().sum()}")
print(f"   Companies with valuation data: {performance_data['latest_valuation'].notna().sum()}")

# Display summary statistics
print("\n" + "="*100)
print("PERFORMANCE METRICS SUMMARY BY ENTRY MECHANISM")
print("="*100)

# Group by entry mechanism and calculate statistics
mechanism_stats = performance_data.groupby('entry_mechanism').agg({
    'total_rounds': ['mean', 'median', 'count'],
    'total_funding': ['mean', 'median', 'sum'],
    'latest_valuation': ['mean', 'median'],
    'valuation_growth_pct': ['mean', 'median'],
    'first_deal_size': ['mean', 'median']
}).round(2)

print("\n📊 AVERAGE PERFORMANCE BY ENTRY MECHANISM:")
print("-" * 100)
print(f"{'Entry Mechanism':<35} {'Count':<8} {'Avg Rounds':<12} {'Avg Funding ($M)':<18} {'Avg Valuation ($M)':<20}")
print("-" * 100)

for mechanism in performance_data['entry_mechanism'].unique():
    mechanism_data = performance_data[performance_data['entry_mechanism'] == mechanism]
    count = len(mechanism_data)
    avg_rounds = mechanism_data['total_rounds'].mean()
    avg_funding = mechanism_data['total_funding'].mean()
    avg_valuation = mechanism_data['latest_valuation'].mean()
    
    funding_str = f"${avg_funding:.1f}" if pd.notna(avg_funding) else "N/A"
    valuation_str = f"${avg_valuation:.1f}" if pd.notna(avg_valuation) else "N/A"
    
    print(f"{mechanism:<35} {count:<8} {avg_rounds:<12.1f} {funding_str:<18} {valuation_str:<20}")

# Detailed correlation analysis
print("\n" + "="*100)
print("CORRELATION ANALYSIS")
print("="*100)

# Create mechanism categories for better analysis
mechanism_categories = {
    'Traditional VC': ['Early Stage VC', 'Later Stage VC', 'First Stage Capital'],
    'Seed/Angel': ['Seed Round', 'Angel (individual)', 'Angel'],
    'Institutional': ['Accelerator/Incubator'],
    'Corporate/Academic': ['Corporate', 'University Spin-Out', 'Joint Venture'],
    'Public/Other': ['IPO', 'Merger/Acquisition', 'Grant', 'Debt - General', 
                     'Product Crowdfunding', 'Equity Crowdfunding']
}

performance_data['mechanism_category'] = performance_data['entry_mechanism'].apply(
    lambda x: next((cat for cat, mechs in mechanism_categories.items() if x in mechs), 'Other')
)

print("\n📈 PERFORMANCE BY MECHANISM CATEGORY:")
print("-" * 100)

category_stats = performance_data.groupby('mechanism_category').agg({
    'total_rounds': ['mean', 'median', 'count'],
    'total_funding': ['mean', 'median'],
    'latest_valuation': ['mean', 'median'],
    'valuation_growth_pct': ['mean', 'median']
}).round(2)

print(f"\n{'Category':<25} {'Count':<8} {'Avg Rounds':<12} {'Avg Funding ($M)':<18} {'Avg Valuation ($M)':<20} {'Avg Growth %':<15}")
print("-" * 100)

for category in category_stats.index:
    count = int(category_stats.loc[category, ('total_rounds', 'count')])
    avg_rounds = category_stats.loc[category, ('total_rounds', 'mean')]
    avg_funding = category_stats.loc[category, ('total_funding', 'mean')]
    avg_valuation = category_stats.loc[category, ('latest_valuation', 'mean')]
    avg_growth = category_stats.loc[category, ('valuation_growth_pct', 'mean')]
    
    funding_str = f"${avg_funding:.1f}" if pd.notna(avg_funding) else "N/A"
    valuation_str = f"${avg_valuation:.1f}" if pd.notna(avg_valuation) else "N/A"
    growth_str = f"{avg_growth:.0f}%" if pd.notna(avg_growth) else "N/A"
    
    print(f"{category:<25} {count:<8} {avg_rounds:<12.1f} {funding_str:<18} {valuation_str:<20} {growth_str:<15}")

# Statistical tests
print("\n" + "="*100)
print("STATISTICAL SIGNIFICANCE TESTS")
print("="*100)

# Test if different entry mechanisms lead to different performance
print("\n🔬 Kruskal-Wallis Test (Non-parametric ANOVA):")
print("   Tests if different entry mechanisms have significantly different performance metrics")
print("-" * 100)

metrics_to_test = ['total_rounds', 'total_funding', 'latest_valuation', 'valuation_growth_pct']

for metric in metrics_to_test:
    if performance_data[metric].notna().sum() < 3:
        continue
    
    # Get data grouped by mechanism
    groups = []
    group_names = []
    for mechanism in performance_data['entry_mechanism'].unique():
        mechanism_values = performance_data[performance_data['entry_mechanism'] == mechanism][metric].dropna()
        if len(mechanism_values) > 0:
            groups.append(mechanism_values.values)
            group_names.append(mechanism)
    
    if len(groups) >= 2:
        try:
            stat, p_value = stats.kruskal(*groups)
            significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"
            print(f"   {metric:<25} H-statistic: {stat:.3f}, p-value: {p_value:.4f} {significance}")
        except:
            pass

# Correlation coefficients
print("\n" + "="*100)
print("INDIVIDUAL COMPANY PERFORMANCE")
print("="*100)

print(f"\n{'Company':<25} {'Entry Mechanism':<30} {'Rounds':<8} {'Total Funding ($M)':<20} {'Latest Valuation ($M)':<25} {'Growth %':<15}")
print("-" * 120)

for _, row in performance_data.sort_values('total_funding', ascending=False, na_position='last').iterrows():
    rounds = int(row['total_rounds']) if pd.notna(row['total_rounds']) else 0
    funding = f"${row['total_funding']:.1f}" if pd.notna(row['total_funding']) else "N/A"
    valuation = f"${row['latest_valuation']:.1f}" if pd.notna(row['latest_valuation']) else "N/A"
    growth = f"{row['valuation_growth_pct']:.0f}%" if pd.notna(row['valuation_growth_pct']) else "N/A"
    
    print(f"{row['company_name']:<25} {row['entry_mechanism']:<30} {rounds:<8} {funding:<20} {valuation:<25} {growth:<15}")

# Create visualizations
print("\n" + "="*100)
print("GENERATING VISUALIZATIONS...")
print("="*100)

fig = plt.figure(figsize=(20, 14))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)

# 1. Entry Mechanism vs Total Rounds
ax1 = fig.add_subplot(gs[0, 0])
mechanism_rounds = performance_data.groupby('entry_mechanism')['total_rounds'].mean().sort_values(ascending=True)
ax1.barh(range(len(mechanism_rounds)), mechanism_rounds.values, color='steelblue', alpha=0.7, edgecolor='black')
ax1.set_yticks(range(len(mechanism_rounds)))
ax1.set_yticklabels(mechanism_rounds.index, fontsize=9)
ax1.set_xlabel('Average Total Rounds', fontweight='bold')
ax1.set_title('Entry Mechanism vs Funding Rounds', fontweight='bold', fontsize=12)
ax1.grid(axis='x', alpha=0.3)

# 2. Entry Mechanism vs Total Funding
ax2 = fig.add_subplot(gs[0, 1])
mechanism_funding = performance_data.groupby('entry_mechanism')['total_funding'].mean().sort_values(ascending=True)
ax2.barh(range(len(mechanism_funding)), mechanism_funding.values, color='forestgreen', alpha=0.7, edgecolor='black')
ax2.set_yticks(range(len(mechanism_funding)))
ax2.set_yticklabels(mechanism_funding.index, fontsize=9)
ax2.set_xlabel('Average Total Funding ($M)', fontweight='bold')
ax2.set_title('Entry Mechanism vs Total Funding', fontweight='bold', fontsize=12)
ax2.grid(axis='x', alpha=0.3)

# 3. Entry Mechanism vs Latest Valuation
ax3 = fig.add_subplot(gs[0, 2])
mechanism_val = performance_data.groupby('entry_mechanism')['latest_valuation'].mean().sort_values(ascending=True)
ax3.barh(range(len(mechanism_val)), mechanism_val.values, color='coral', alpha=0.7, edgecolor='black')
ax3.set_yticks(range(len(mechanism_val)))
ax3.set_yticklabels(mechanism_val.index, fontsize=9)
ax3.set_xlabel('Average Latest Valuation ($M)', fontweight='bold')
ax3.set_title('Entry Mechanism vs Valuation', fontweight='bold', fontsize=12)
ax3.grid(axis='x', alpha=0.3)

# 4. Mechanism Category Comparison - Rounds
ax4 = fig.add_subplot(gs[1, 0])
category_rounds = performance_data.groupby('mechanism_category')['total_rounds'].mean().sort_values(ascending=True)
colors = plt.cm.Set3(range(len(category_rounds)))
ax4.barh(range(len(category_rounds)), category_rounds.values, color=colors, alpha=0.7, edgecolor='black')
ax4.set_yticks(range(len(category_rounds)))
ax4.set_yticklabels(category_rounds.index, fontsize=10)
ax4.set_xlabel('Average Total Rounds', fontweight='bold')
ax4.set_title('Mechanism Category vs Rounds', fontweight='bold', fontsize=12)
ax4.grid(axis='x', alpha=0.3)

# 5. Mechanism Category Comparison - Funding
ax5 = fig.add_subplot(gs[1, 1])
category_funding = performance_data.groupby('mechanism_category')['total_funding'].mean().sort_values(ascending=True)
colors = plt.cm.Set2(range(len(category_funding)))
ax5.barh(range(len(category_funding)), category_funding.values, color=colors, alpha=0.7, edgecolor='black')
ax5.set_yticks(range(len(category_funding)))
ax5.set_yticklabels(category_funding.index, fontsize=10)
ax5.set_xlabel('Average Total Funding ($M)', fontweight='bold')
ax5.set_title('Mechanism Category vs Funding', fontweight='bold', fontsize=12)
ax5.grid(axis='x', alpha=0.3)

# 6. Mechanism Category Comparison - Valuation
ax6 = fig.add_subplot(gs[1, 2])
category_val = performance_data.groupby('mechanism_category')['latest_valuation'].mean().sort_values(ascending=True)
colors = plt.cm.Pastel1(range(len(category_val)))
ax6.barh(range(len(category_val)), category_val.values, color=colors, alpha=0.7, edgecolor='black')
ax6.set_yticks(range(len(category_val)))
ax6.set_yticklabels(category_val.index, fontsize=10)
ax6.set_xlabel('Average Latest Valuation ($M)', fontweight='bold')
ax6.set_title('Mechanism Category vs Valuation', fontweight='bold', fontsize=12)
ax6.grid(axis='x', alpha=0.3)

# 7. Scatter: First Deal Size vs Total Funding
ax7 = fig.add_subplot(gs[2, 0])
scatter_data = performance_data[performance_data[['first_deal_size', 'total_funding']].notna().all(axis=1)]
if len(scatter_data) > 0:
    colors_scatter = plt.cm.viridis(np.linspace(0, 1, len(scatter_data)))
    for idx, row in scatter_data.iterrows():
        ax7.scatter(row['first_deal_size'], row['total_funding'], 
                   s=200, alpha=0.6, c=[colors_scatter[scatter_data.index.get_loc(idx)]], 
                   edgecolors='black', linewidth=1.5)
        ax7.text(row['first_deal_size'], row['total_funding'], 
                f"  {row['company_name']}", fontsize=8, va='center')
    
    # Add correlation line
    if len(scatter_data) > 1:
        z = np.polyfit(scatter_data['first_deal_size'], scatter_data['total_funding'], 1)
        p = np.poly1d(z)
        ax7.plot(scatter_data['first_deal_size'].sort_values(), 
                p(scatter_data['first_deal_size'].sort_values()), 
                "r--", alpha=0.5, linewidth=2, label='Trend')
        ax7.legend()
    
    ax7.set_xlabel('First Deal Size ($M)', fontweight='bold')
    ax7.set_ylabel('Total Funding ($M)', fontweight='bold')
    ax7.set_title('First Deal Size vs Total Funding', fontweight='bold', fontsize=12)
    ax7.grid(alpha=0.3)

# 8. Scatter: Total Rounds vs Latest Valuation
ax8 = fig.add_subplot(gs[2, 1])
scatter_data2 = performance_data[performance_data[['total_rounds', 'latest_valuation']].notna().all(axis=1)]
if len(scatter_data2) > 0:
    colors_scatter2 = plt.cm.plasma(np.linspace(0, 1, len(scatter_data2)))
    for idx, row in scatter_data2.iterrows():
        ax8.scatter(row['total_rounds'], row['latest_valuation'], 
                   s=200, alpha=0.6, c=[colors_scatter2[scatter_data2.index.get_loc(idx)]], 
                   edgecolors='black', linewidth=1.5)
        ax8.text(row['total_rounds'], row['latest_valuation'], 
                f"  {row['company_name']}", fontsize=8, va='center')
    
    # Add correlation line
    if len(scatter_data2) > 1:
        z = np.polyfit(scatter_data2['total_rounds'], scatter_data2['latest_valuation'], 1)
        p = np.poly1d(z)
        ax8.plot(scatter_data2['total_rounds'].sort_values(), 
                p(scatter_data2['total_rounds'].sort_values()), 
                "r--", alpha=0.5, linewidth=2, label='Trend')
        ax8.legend()
    
    ax8.set_xlabel('Total Rounds', fontweight='bold')
    ax8.set_ylabel('Latest Valuation ($M)', fontweight='bold')
    ax8.set_title('Total Rounds vs Latest Valuation', fontweight='bold', fontsize=12)
    ax8.grid(alpha=0.3)

# 9. Box plot: Mechanism Category vs Valuation Growth
ax9 = fig.add_subplot(gs[2, 2])
box_data = []
box_labels = []
for category in performance_data['mechanism_category'].unique():
    category_data = performance_data[performance_data['mechanism_category'] == category]['valuation_growth_pct'].dropna()
    if len(category_data) > 0:
        box_data.append(category_data.values)
        box_labels.append(category)

if len(box_data) > 0:
    bp = ax9.boxplot(box_data, labels=box_labels, patch_artist=True, vert=True)
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
        patch.set_alpha(0.7)
    ax9.set_ylabel('Valuation Growth (%)', fontweight='bold')
    ax9.set_title('Valuation Growth by Mechanism Category', fontweight='bold', fontsize=12)
    ax9.tick_params(axis='x', rotation=15)
    ax9.grid(axis='y', alpha=0.3)

plt.suptitle('ENTRY MECHANISM vs PERFORMANCE CORRELATION ANALYSIS', 
             fontsize=16, fontweight='bold', y=0.995)

plt.savefig('entry_performance_correlation.png', dpi=300, bbox_inches='tight')
print("\n✓ Visualization saved as 'entry_performance_correlation.png'")

# Save detailed data
performance_data.to_csv('entry_performance_correlation_data.csv', index=False)
print("✓ Detailed data saved as 'entry_performance_correlation_data.csv'")

# Calculate and display correlation coefficients
print("\n" + "="*100)
print("CORRELATION COEFFICIENTS")
print("="*100)

print("\n📊 Pearson Correlation Coefficients:")
print("-" * 100)

# Calculate correlations for numeric metrics
numeric_cols = ['total_rounds', 'total_funding', 'latest_valuation', 'valuation_growth_pct', 
                'first_deal_size', 'total_deals']

corr_matrix = performance_data[numeric_cols].corr()

print("\nCorrelation Matrix:")
print(corr_matrix.round(3))

# Key correlations
print("\n🔗 Key Correlations:")
print("-" * 100)
print(f"Total Rounds vs Total Funding: {performance_data['total_rounds'].corr(performance_data['total_funding']):.3f}")
print(f"Total Rounds vs Latest Valuation: {performance_data['total_rounds'].corr(performance_data['latest_valuation']):.3f}")
print(f"Total Funding vs Latest Valuation: {performance_data['total_funding'].corr(performance_data['latest_valuation']):.3f}")
print(f"First Deal Size vs Total Funding: {performance_data['first_deal_size'].corr(performance_data['total_funding']):.3f}")

print("\n" + "="*100)
print("ANALYSIS COMPLETE")
print("="*100)

print("\n💡 KEY INSIGHTS:")
print("-" * 100)
best_rounds = mechanism_rounds.idxmax()
best_funding = mechanism_funding.idxmax()
best_valuation = mechanism_val.idxmax()

print(f"• Entry mechanism with most rounds: {best_rounds} ({mechanism_rounds[best_rounds]:.1f} rounds)")
print(f"• Entry mechanism with most funding: {best_funding} (${mechanism_funding[best_funding]:.1f}M avg)")
print(f"• Entry mechanism with highest valuation: {best_valuation} (${mechanism_val[best_valuation]:.1f}M avg)")

# Best performing companies by mechanism
print(f"\n• Companies analyzed: {len(performance_data)}")
print(f"• Companies with funding data: {performance_data['total_funding'].notna().sum()}")
print(f"• Companies with valuation data: {performance_data['latest_valuation'].notna().sum()}")

print()

