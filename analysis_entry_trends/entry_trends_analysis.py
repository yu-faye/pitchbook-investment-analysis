import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (18, 12)

# Company IDs from the list
company_ids = [
    "64325-80",    # Whoop
    "110783-26",   # Oura
    "458417-44",   # Ultrahuman
    "495718-39",   # Pulsetto
    "697387-24",   # ThingX
    "183205-63",   # Flow Neuroscience
    "56236-96",    # Catapult Sports - IPO 2014
    "65652-22",    # GOQii
    "107433-19",   # Empatica
    "142343-92",   # Playermaker
    "50982-94",    # Fitbit - IPO 2015
    "100191-79",   # Zepp Health - IPO 2018
    "61931-08"     # Peloton - IPO 2019
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
print("ENTRY TRENDS ANALYSIS: HOW & WHEN COMPANIES ENTERED THE WEARABLE TECH MARKET")
print("="*100)

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
deals['company_name'] = deals['CompanyID'].map(company_names)
deals['year'] = deals['date'].dt.year
deals = deals.sort_values('date')

print("Loading Company data...")
company_chunks = []
for chunk in pd.read_csv('../Company.csv', chunksize=chunk_size, low_memory=False):
    filtered = chunk[chunk['CompanyID'].isin(company_ids)]
    if len(filtered) > 0:
        company_chunks.append(filtered)

companies = pd.concat(company_chunks, ignore_index=True)

print(f"\nFound {len(deals)} deals for {len(companies)} companies")

print("\n" + "="*100)
print("1. ENTRY TIMING ANALYSIS")
print("="*100)

# Get first deal for each company
first_deals = deals.groupby('CompanyID').first().reset_index()
first_deals['company_name'] = first_deals['CompanyID'].map(company_names)
first_deals = first_deals.sort_values('date')

print("\n📅 FIRST INVESTMENT DATE BY COMPANY (Chronological Order):")
print("-" * 100)
print(f"{'Company':<25} {'First Investment':<20} {'Entry Mechanism':<30} {'Round':<15} {'Year':<6}")
print("-" * 100)

entry_data = []
for idx, row in first_deals.iterrows():
    if pd.notna(row['date']):
        date_str = row['date'].strftime('%B %d, %Y')
        year = row['date'].year
    else:
        date_str = 'Unknown'
        year = None
    
    deal_type = str(row.get('DealType', 'Unknown')) if pd.notna(row.get('DealType')) else 'Unknown'
    vc_round = str(row.get('VCRound', 'Unknown')) if pd.notna(row.get('VCRound')) else 'Unknown'
    deal_size = row.get('DealSize', None)
    
    print(f"{row['company_name']:<25} {date_str:<20} {deal_type:<30} {vc_round:<15} {year if year else 'N/A':<6}")
    
    entry_data.append({
        'company': row['company_name'],
        'company_id': row['CompanyID'],
        'entry_date': row['date'],
        'entry_year': year,
        'entry_mechanism': deal_type,
        'first_round': vc_round,
        'first_deal_size': deal_size
    })

entry_df = pd.DataFrame(entry_data)

# Analyze entry waves
print("\n" + "="*100)
print("2. ENTRY WAVES & MARKET TIMING")
print("="*100)

print("\n🌊 ENTRY COHORTS:")
print("-" * 100)

# Define entry waves
waves = {
    'Pioneer Era (2007-2010)': (2007, 2010),
    'First Wave (2011-2015)': (2011, 2015),
    'Second Wave (2016-2019)': (2016, 2019),
    'Third Wave (2020-2022)': (2020, 2022),
    'Fourth Wave (2023-2025)': (2023, 2025)
}

for wave_name, (start_year, end_year) in waves.items():
    wave_companies = entry_df[(entry_df['entry_year'] >= start_year) & (entry_df['entry_year'] <= end_year)]
    print(f"\n{wave_name}: {len(wave_companies)} companies")
    if len(wave_companies) > 0:
        for _, comp in wave_companies.iterrows():
            year_str = f"{int(comp['entry_year'])}" if pd.notna(comp['entry_year']) else "Unknown"
            print(f"  • {comp['company']:<25} ({year_str}) - {comp['entry_mechanism']}")

print("\n" + "="*100)
print("3. ENTRY MECHANISMS ANALYSIS")
print("="*100)

print("\n🚀 ENTRY MECHANISM DISTRIBUTION:")
print("-" * 100)

# Count entry mechanisms
mechanism_counts = entry_df['entry_mechanism'].value_counts()
print(f"\n{'Entry Mechanism':<35} {'Count':<8} {'Percentage'}")
print("-" * 70)
for mechanism, count in mechanism_counts.items():
    pct = (count / len(entry_df)) * 100
    print(f"{mechanism:<35} {count:<8} {pct:>6.1f}%")

print("\n📊 ENTRY MECHANISM DETAILS BY COMPANY:")
print("-" * 100)

mechanism_categories = {
    'Traditional VC': ['Seed Round', 'Early Stage VC', 'Later Stage VC', 'First Stage Capital'],
    'Angel/Individual': ['Angel (individual)', 'Angel'],
    'Institutional': ['Accelerator/Incubator'],
    'Corporate': ['Corporate'],
    'Academic': ['University Spin-Out'],
    'Public': ['IPO']
}

for category, mechanisms in mechanism_categories.items():
    category_companies = entry_df[entry_df['entry_mechanism'].isin(mechanisms)]
    if len(category_companies) > 0:
        print(f"\n{category}:")
        for _, comp in category_companies.iterrows():
            print(f"  • {comp['company']:<25} - {comp['entry_mechanism']}")

print("\n" + "="*100)
print("4. FIRST ROUND CHARACTERISTICS")
print("="*100)

# Analyze first round sizes
print("\n💰 FIRST ROUND DEAL SIZES:")
print("-" * 100)

sized_entries = entry_df[entry_df['first_deal_size'].notna()].copy()
if len(sized_entries) > 0:
    sized_entries = sized_entries.sort_values('first_deal_size', ascending=False)
    
    print(f"\n{'Company':<25} {'First Deal Size':<20} {'Entry Year':<12} {'Mechanism'}")
    print("-" * 100)
    for _, row in sized_entries.iterrows():
        size_str = f"${row['first_deal_size']:.2f}M"
        year_str = f"{int(row['entry_year'])}" if pd.notna(row['entry_year']) else "Unknown"
        print(f"{row['company']:<25} {size_str:<20} {year_str:<12} {row['entry_mechanism']}")
    
    avg_size = sized_entries['first_deal_size'].mean()
    median_size = sized_entries['first_deal_size'].median()
    print(f"\nAverage first round size: ${avg_size:.2f}M")
    print(f"Median first round size: ${median_size:.2f}M")
else:
    print("\nNo first round deal size data available")

print("\n" + "="*100)
print("5. ENTRY SUCCESS ANALYSIS")
print("="*100)

print("\n📈 ENTRY MECHANISM vs CURRENT STATUS:")
print("-" * 100)

# Get current status for each company
entry_df_status = entry_df.copy()
for idx, row in entry_df_status.iterrows():
    comp_info = companies[companies['CompanyID'] == row['company_id']]
    if len(comp_info) > 0:
        status = comp_info.iloc[0].get('BusinessStatus', 'Unknown')
        entry_df_status.at[idx, 'current_status'] = status
        
        # Count total rounds
        total_rounds = len(deals[deals['CompanyID'] == row['company_id']])
        entry_df_status.at[idx, 'total_rounds'] = total_rounds

print(f"\n{'Company':<25} {'Entry Mechanism':<30} {'Total Rounds':<15} {'Current Status'}")
print("-" * 100)
for _, row in entry_df_status.sort_values('total_rounds', ascending=False).iterrows():
    rounds = int(row.get('total_rounds', 0)) if pd.notna(row.get('total_rounds')) else 0
    status = row.get('current_status', 'Unknown')
    print(f"{row['company']:<25} {row['entry_mechanism']:<30} {rounds:<15} {status}")

# Success by mechanism
print("\n🎯 SUCCESS METRICS BY ENTRY MECHANISM:")
print("-" * 100)

mechanism_success = entry_df_status.groupby('entry_mechanism').agg({
    'total_rounds': 'mean',
    'company': 'count'
}).rename(columns={'company': 'count', 'total_rounds': 'avg_rounds'})
mechanism_success = mechanism_success.sort_values('avg_rounds', ascending=False)

print(f"\n{'Entry Mechanism':<35} {'Count':<8} {'Avg Rounds'}")
print("-" * 70)
for mechanism, row in mechanism_success.iterrows():
    print(f"{mechanism:<35} {int(row['count']):<8} {row['avg_rounds']:.1f}")

print("\n" + "="*100)
print("6. ENTRY TIMING vs PERFORMANCE")
print("="*100)

# Group by entry year and analyze performance
print("\n📅 PERFORMANCE BY ENTRY YEAR:")
print("-" * 100)

year_performance = entry_df_status.groupby('entry_year').agg({
    'total_rounds': 'mean',
    'company': 'count'
}).rename(columns={'company': 'count', 'total_rounds': 'avg_rounds'})
year_performance = year_performance.sort_index()

print(f"\n{'Entry Year':<12} {'Companies':<12} {'Avg Rounds':<15} {'Performance'}")
print("-" * 70)
for year, row in year_performance.iterrows():
    if pd.notna(year):
        year_int = int(year)
        count = int(row['count'])
        avg = row['avg_rounds']
        
        # Categorize performance
        if avg >= 10:
            perf = "Excellent"
        elif avg >= 7:
            perf = "Strong"
        elif avg >= 5:
            perf = "Good"
        elif avg >= 3:
            perf = "Moderate"
        else:
            perf = "Early Stage"
        
        print(f"{year_int:<12} {count:<12} {avg:<15.1f} {perf}")

print("\n" + "="*100)
print("GENERATING VISUALIZATIONS...")
print("="*100)

# Create comprehensive visualization
fig = plt.figure(figsize=(20, 14))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# 1. Entry Timeline
ax1 = fig.add_subplot(gs[0, :])
entry_df_plot = entry_df.dropna(subset=['entry_date']).sort_values('entry_date')
colors_timeline = plt.cm.tab20(np.linspace(0, 1, len(entry_df_plot)))

for idx, (i, row) in enumerate(entry_df_plot.iterrows()):
    ax1.scatter(row['entry_date'], idx, s=300, alpha=0.7, c=[colors_timeline[idx]], 
                edgecolors='black', linewidth=2, zorder=3)
    ax1.text(row['entry_date'], idx, f"  {row['company']}", 
             fontsize=10, va='center', ha='left', fontweight='bold')

ax1.set_yticks([])
ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_title('Market Entry Timeline: All 13 Companies', fontweight='bold', fontsize=14)
ax1.grid(alpha=0.3, axis='x')
ax1.set_ylim(-1, len(entry_df_plot))

# Add wave regions
wave_colors = ['#e6f3ff', '#e8f4f8', '#fff4e6', '#f0f8e8', '#fef0f0']
wave_labels = ['Pioneer\n2007-2010', 'Wave 1\n2011-2015', 'Wave 2\n2016-2019', 'Wave 3\n2020-2022', 'Wave 4\n2023-2025']
wave_ranges = [(2007, 2010), (2011, 2015), (2016, 2019), (2020, 2022), (2023, 2025)]

for i, ((start, end), color, label) in enumerate(zip(wave_ranges, wave_colors, wave_labels)):
    ax1.axvspan(pd.Timestamp(f'{start}-01-01'), pd.Timestamp(f'{end}-12-31'), 
                alpha=0.3, color=color, zorder=1)
    # Stagger labels to avoid overlap
    y_pos = len(entry_df_plot) - 1 - (i % 2) * 1.5
    ax1.text(pd.Timestamp(f'{start+1}-06-01'), y_pos, 
            label, fontsize=9, ha='center', va='top', 
            bbox=dict(boxstyle='round', facecolor=color, alpha=0.7, edgecolor='gray', linewidth=1))

# 2. Entry Mechanism Distribution
ax2 = fig.add_subplot(gs[1, 0:2])
mechanism_counts_plot = mechanism_counts.head(8)
colors_mech = plt.cm.Set3(range(len(mechanism_counts_plot)))
wedges, texts, autotexts = ax2.pie(mechanism_counts_plot.values, labels=mechanism_counts_plot.index, 
                                     autopct='%1.0f%%', colors=colors_mech, startangle=90)
for text in texts:
    text.set_fontsize(9)
for autotext in autotexts:
    autotext.set_color('black')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(10)
ax2.set_title('Entry Mechanism Distribution', fontweight='bold', fontsize=12)

# 3. Entry Mechanism vs Success (Avg Rounds)
ax4 = fig.add_subplot(gs[1, 2])
mech_success_plot = mechanism_success.head(8).sort_values('avg_rounds', ascending=True)
colors_success = ['#2ecc71' if x >= 7 else '#f39c12' if x >= 5 else '#e74c3c' 
                  for x in mech_success_plot['avg_rounds']]
ax4.barh(range(len(mech_success_plot)), mech_success_plot['avg_rounds'].values, 
         color=colors_success, alpha=0.7, edgecolor='black', linewidth=1.5)
ax4.set_yticks(range(len(mech_success_plot)))
ax4.set_yticklabels(mech_success_plot.index, fontsize=9)
ax4.set_xlabel('Average Funding Rounds', fontsize=11, fontweight='bold')
ax4.set_title('Entry Mechanism Success\n(by Avg Rounds Raised)', fontweight='bold', fontsize=12)
ax4.grid(axis='x', alpha=0.3)

# 5. Entry Year vs Performance
ax5 = fig.add_subplot(gs[2, 0])
year_perf_plot = year_performance.dropna()
colors_year = ['#2ecc71' if x >= 10 else '#3498db' if x >= 7 else '#f39c12' if x >= 5 else '#e74c3c' 
               for x in year_perf_plot['avg_rounds']]
ax5.scatter(year_perf_plot.index, year_perf_plot['avg_rounds'], 
            s=year_perf_plot['count']*200, c=colors_year, alpha=0.6, 
            edgecolors='black', linewidth=2)
for year, row in year_perf_plot.iterrows():
    ax5.annotate(f"{int(row['count'])}", (year, row['avg_rounds']), 
                ha='center', va='center', fontweight='bold', fontsize=10)
ax5.set_xlabel('Entry Year', fontsize=11, fontweight='bold')
ax5.set_ylabel('Avg Funding Rounds', fontsize=11, fontweight='bold')
ax5.set_title('Entry Timing vs Performance\n(Bubble size = # companies)', fontweight='bold', fontsize=12)
ax5.grid(alpha=0.3)

# 6. First Deal Size Distribution
ax6 = fig.add_subplot(gs[2, 1])
if len(sized_entries) > 0:
    sized_sorted = sized_entries.sort_values('first_deal_size', ascending=True)
    colors_size = plt.cm.YlOrRd(np.linspace(0.3, 0.9, len(sized_sorted)))
    ax6.barh(range(len(sized_sorted)), sized_sorted['first_deal_size'].values,
             color=colors_size, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax6.set_yticks(range(len(sized_sorted)))
    ax6.set_yticklabels(sized_sorted['company'].values, fontsize=9)
    ax6.set_xlabel('First Deal Size ($M)', fontsize=11, fontweight='bold')
    ax6.set_title('First Round Funding Size', fontweight='bold', fontsize=12)
    ax6.grid(axis='x', alpha=0.3)
    ax6.axvline(avg_size, color='red', linestyle='--', linewidth=2, label=f'Average: ${avg_size:.1f}M')
    ax6.legend()
else:
    ax6.text(0.5, 0.5, 'No Deal Size Data Available', ha='center', va='center', fontsize=12)
    ax6.set_xlim(0, 1)
    ax6.set_ylim(0, 1)

# 7. Entry Wave Comparison
ax7 = fig.add_subplot(gs[2, 2])
wave_data = []
wave_names = []
for wave_name, (start_year, end_year) in waves.items():
    wave_companies_perf = entry_df_status[(entry_df_status['entry_year'] >= start_year) & 
                                           (entry_df_status['entry_year'] <= end_year)]
    if len(wave_companies_perf) > 0:
        wave_names.append(wave_name.split('(')[0].strip())
        wave_data.append(wave_companies_perf['total_rounds'].mean())

colors_wave = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c'][:len(wave_data)]
bars = ax7.bar(range(len(wave_data)), wave_data, color=colors_wave, alpha=0.7, 
               edgecolor='black', linewidth=1.5)
ax7.set_xticks(range(len(wave_data)))
ax7.set_xticklabels(wave_names, fontsize=10, rotation=15, ha='right')
ax7.set_ylabel('Avg Funding Rounds', fontsize=11, fontweight='bold')
ax7.set_title('Performance by Entry Wave', fontweight='bold', fontsize=12)
ax7.grid(axis='y', alpha=0.3)

# Add value labels on bars
for i, (bar, val) in enumerate(zip(bars, wave_data)):
    ax7.text(bar.get_x() + bar.get_width()/2, val + 0.3, f'{val:.1f}', 
            ha='center', va='bottom', fontweight='bold', fontsize=10)

plt.suptitle('ENTRY TRENDS ANALYSIS: Wearable Tech Market Entry Patterns', 
             fontsize=16, fontweight='bold', y=0.995)

plt.savefig('entry_trends_analysis.png', dpi=300, bbox_inches='tight')
print("\n✓ Visualization saved as 'entry_trends_analysis.png'")

# Save entry data to CSV
entry_df_status.to_csv('entry_data_by_company.csv', index=False)
print("✓ Entry data saved as 'entry_data_by_company.csv'")

print("\n" + "="*100)
print("ANALYSIS COMPLETE")
print("="*100)

print("\n💡 KEY INSIGHTS:")
print("-" * 100)
print(f"• Total companies analyzed: {len(entry_df)}")
print(f"• Entry period: {int(entry_df['entry_year'].min())} - {int(entry_df['entry_year'].max())}")
print(f"• Most common entry mechanism: {mechanism_counts.index[0]} ({mechanism_counts.values[0]} companies)")
print(f"• Best performing entry mechanism: {mechanism_success.index[0]} (avg {mechanism_success.iloc[0]['avg_rounds']:.1f} rounds)")
if len(sized_entries) > 0:
    print(f"• Average first round size: ${avg_size:.2f}M")
print(f"• Companies still generating revenue: {len(entry_df_status[entry_df_status['current_status'].str.contains('Revenue', na=False)])}/{len(entry_df_status)}")
print()


