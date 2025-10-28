import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

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

print("Loading Deal data...")
# Load deals in chunks to handle large file
chunk_size = 100000
deals_list = []

for chunk in pd.read_csv('../Deal.csv', chunksize=chunk_size, low_memory=False):
    # Filter for our companies
    filtered = chunk[chunk['CompanyID'].isin(company_ids)]
    if len(filtered) > 0:
        deals_list.append(filtered)

deals = pd.concat(deals_list, ignore_index=True)
print(f"Found {len(deals)} deals for the 14 companies")

# Load company data
print("Loading Company data...")
company_chunks = []
for chunk in pd.read_csv('../Company.csv', chunksize=chunk_size, low_memory=False):
    filtered = chunk[chunk['CompanyID'].isin(company_ids)]
    if len(filtered) > 0:
        company_chunks.append(filtered)

companies = pd.concat(company_chunks, ignore_index=True)
print(f"Found {len(companies)} companies")

# Convert date columns
deals['DealDate'] = pd.to_datetime(deals['DealDate'], errors='coerce')
deals['AnnouncedDate'] = pd.to_datetime(deals['AnnouncedDate'], errors='coerce')

# Use DealDate as primary date
deals['date'] = deals['DealDate']

# Add company names
deals['company_name'] = deals['CompanyID'].map(company_names)

# Sort by date
deals = deals.sort_values('date')

print("\n" + "="*80)
print("INVESTMENT TRENDS ANALYSIS FOR 14 WEARABLE TECH COMPANIES")
print("="*80)

# 1. ENTRY TRENDS - Initial Funding & Early Stages
print("\n1. ENTRY TRENDS (First Investments & Early Stages)")
print("-" * 80)

# First deal for each company
first_deals = deals.groupby('CompanyID').first().reset_index()
first_deals['company_name'] = first_deals['CompanyID'].map(company_names)
first_deals = first_deals.sort_values('date')

print("\nFirst Investment Date by Company:")
for idx, row in first_deals.iterrows():
    date_str = row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else 'Unknown'
    deal_type = row.get('DealType', 'Unknown')
    round_type = row.get('VCRound', 'Unknown')
    print(f"  {row['company_name']:20s} | {date_str} | {deal_type:20s} | Round: {round_type}")

# Early stage investments by year
deals['year'] = deals['date'].dt.year
early_stage_types = ['Seed Round', 'Angel (individual)', 'Early Stage VC', 'First Stage Capital', 'Later Stage VC', 'Series A', 'Series B']
early_deals = deals[deals['VCRound'].isin(early_stage_types)]

print(f"\nEarly Stage Deals (Seed, Angel, Series A/B): {len(early_deals)} deals")
print("\nEarly Stage Investment Activity by Year:")
early_by_year = early_deals.groupby('year').agg({
    'CompanyID': 'count',
    'DealSize': 'sum'
}).rename(columns={'CompanyID': 'num_deals'})
for year, row in early_by_year.iterrows():
    if pd.notna(year):
        amount = row['DealSize'] / 1e6 if pd.notna(row['DealSize']) else 0
        print(f"  {int(year)}: {int(row['num_deals'])} deals, ${amount:.1f}M raised")

# 2. EXIT TRENDS - Acquisitions, IPOs, etc.
print("\n\n2. EXIT TRENDS (Acquisitions, IPOs, Shutdowns)")
print("-" * 80)

# Check company status
print("\nCurrent Company Status:")
for idx, company in companies.iterrows():
    status = company.get('BusinessStatus', 'Unknown')
    name = company_names.get(company['CompanyID'], company['CompanyID'])
    print(f"  {name:20s} | Status: {status}")

# Exit events
exit_types = ['Acquisition', 'IPO', 'Merger', 'LBO', 'Buyout']
exit_deals = deals[deals['DealType'].isin(exit_types)]

if len(exit_deals) > 0:
    print(f"\nExit Events Found: {len(exit_deals)}")
    for idx, deal in exit_deals.iterrows():
        date_str = deal['date'].strftime('%Y-%m-%d') if pd.notna(deal['date']) else 'Unknown'
        print(f"  {deal['company_name']:20s} | {date_str} | {deal['DealType']}")
else:
    print("\nNo exit events (IPO/Acquisition) found in deal data")
    print("All companies appear to be still operating privately")

# 3. INVESTMENT TRENDS - Overall Patterns
print("\n\n3. INVESTMENT TRENDS (Overall Patterns)")
print("-" * 80)

# Total funding by company
print("\nTotal Funding Raised by Company:")
funding_by_company = deals.groupby('company_name')['DealSize'].sum().sort_values(ascending=False)
for company, amount in funding_by_company.items():
    if pd.notna(amount):
        print(f"  {company:20s} | ${amount/1e6:>8.1f}M")

# Investment rounds by company
print("\nNumber of Funding Rounds by Company:")
rounds_by_company = deals.groupby('company_name').size().sort_values(ascending=False)
for company, count in rounds_by_company.items():
    print(f"  {company:20s} | {count} rounds")

# Investment activity over time
print("\nInvestment Activity by Year:")
investment_by_year = deals.groupby('year').agg({
    'CompanyID': 'count',
    'DealSize': 'sum'
}).rename(columns={'CompanyID': 'num_deals'})

for year, row in investment_by_year.iterrows():
    if pd.notna(year):
        amount = row['DealSize'] / 1e6 if pd.notna(row['DealSize']) else 0
        print(f"  {int(year)}: {int(row['num_deals'])} deals, ${amount:.1f}M total")

# Funding stages distribution
print("\nFunding Stages Distribution:")
stage_dist = deals['VCRound'].value_counts()
for stage, count in stage_dist.head(10).items():
    print(f"  {stage:30s} | {count} deals")

# Average deal size by stage
print("\nAverage Deal Size by Stage:")
avg_by_stage = deals.groupby('VCRound')['DealSize'].mean().sort_values(ascending=False)
for stage, avg in avg_by_stage.head(10).items():
    if pd.notna(avg):
        print(f"  {stage:30s} | ${avg/1e6:.1f}M")

# Latest funding round for each company
print("\n\nLatest Funding Round by Company (Current Stage):")
latest_deals = deals.sort_values('date').groupby('CompanyID').last().reset_index()
latest_deals['company_name'] = latest_deals['CompanyID'].map(company_names)
latest_deals = latest_deals.sort_values('date', ascending=False)

for idx, row in latest_deals.iterrows():
    date_str = row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else 'Unknown'
    series = row.get('VCRound', 'Unknown')
    amount = row['DealSize'] / 1e6 if pd.notna(row['DealSize']) else 0
    print(f"  {row['company_name']:20s} | {date_str} | {series:20s} | ${amount:.1f}M")

# Create visualizations
print("\n\nGenerating visualizations...")

fig, axes = plt.subplots(2, 3, figsize=(20, 12))

# 1. First Investment Timeline
ax1 = axes[0, 0]
first_deals_sorted = first_deals.dropna(subset=['date']).sort_values('date')
ax1.barh(range(len(first_deals_sorted)), 
         [(d - first_deals_sorted['date'].min()).days for d in first_deals_sorted['date']],
         color='skyblue')
ax1.set_yticks(range(len(first_deals_sorted)))
ax1.set_yticklabels(first_deals_sorted['company_name'])
ax1.set_xlabel('Days Since First Company Founded')
ax1.set_title('Entry Timeline: First Investment Date', fontweight='bold', fontsize=12)
ax1.grid(axis='x', alpha=0.3)

# 2. Total Funding by Company
ax2 = axes[0, 1]
funding_df = funding_by_company.dropna()
ax2.barh(range(len(funding_df)), funding_df.values / 1e6, color='green', alpha=0.7)
ax2.set_yticks(range(len(funding_df)))
ax2.set_yticklabels(funding_df.index)
ax2.set_xlabel('Total Funding ($ Millions)')
ax2.set_title('Total Funding Raised by Company', fontweight='bold', fontsize=12)
ax2.grid(axis='x', alpha=0.3)

# 3. Number of Rounds by Company
ax3 = axes[0, 2]
ax3.barh(range(len(rounds_by_company)), rounds_by_company.values, color='coral', alpha=0.7)
ax3.set_yticks(range(len(rounds_by_company)))
ax3.set_yticklabels(rounds_by_company.index)
ax3.set_xlabel('Number of Funding Rounds')
ax3.set_title('Funding Rounds by Company', fontweight='bold', fontsize=12)
ax3.grid(axis='x', alpha=0.3)

# 4. Investment Activity Over Time
ax4 = axes[1, 0]
investment_by_year_clean = investment_by_year.dropna()
years = investment_by_year_clean.index.astype(int)
ax4.plot(years, investment_by_year_clean['num_deals'], marker='o', linewidth=2, markersize=8, color='blue')
ax4.set_xlabel('Year')
ax4.set_ylabel('Number of Deals')
ax4.set_title('Investment Activity Over Time', fontweight='bold', fontsize=12)
ax4.grid(alpha=0.3)

# 5. Funding Amount Over Time
ax5 = axes[1, 1]
amounts = investment_by_year_clean['DealSize'] / 1e6
ax5.bar(years, amounts, color='purple', alpha=0.7)
ax5.set_xlabel('Year')
ax5.set_ylabel('Total Funding ($ Millions)')
ax5.set_title('Funding Amount Over Time', fontweight='bold', fontsize=12)
ax5.grid(axis='y', alpha=0.3)

# 6. Funding Stage Distribution
ax6 = axes[1, 2]
top_stages = stage_dist.head(8)
colors = plt.cm.Set3(range(len(top_stages)))
ax6.pie(top_stages.values, labels=top_stages.index, autopct='%1.1f%%', colors=colors, startangle=90)
ax6.set_title('Funding Stage Distribution', fontweight='bold', fontsize=12)

plt.tight_layout()
plt.savefig('investment_trends_analysis.png', dpi=300, bbox_inches='tight')
print(f"Visualization saved as 'investment_trends_analysis.png'")

# Create timeline visualization
fig2, ax = plt.subplots(figsize=(16, 10))

# Plot all deals over time for each company
companies_list = list(company_names.keys())
colors_map = plt.cm.tab20(np.linspace(0, 1, len(companies_list)))
company_colors = {cid: colors_map[i] for i, cid in enumerate(companies_list)}

for company_id in companies_list:
    company_deals = deals[deals['CompanyID'] == company_id].dropna(subset=['date'])
    if len(company_deals) > 0:
        company_deals = company_deals.sort_values('date')
        y_pos = companies_list.index(company_id)
        
        # Plot each deal as a point
        for idx, deal in company_deals.iterrows():
            marker_size = 100
            if pd.notna(deal['DealSize']) and deal['DealSize'] > 0:
                marker_size = min(1000, max(50, deal['DealSize'] / 1e6 * 10))
            
            ax.scatter(deal['date'], y_pos, s=marker_size, 
                      color=company_colors[company_id], alpha=0.6, 
                      edgecolors='black', linewidths=0.5)

ax.set_yticks(range(len(companies_list)))
ax.set_yticklabels([company_names[cid] for cid in companies_list])
ax.set_xlabel('Year', fontsize=12)
ax.set_title('Investment Timeline for 14 Companies\n(Bubble size represents funding amount)', 
             fontweight='bold', fontsize=14)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('investment_timeline.png', dpi=300, bbox_inches='tight')
print(f"Timeline visualization saved as 'investment_timeline.png'")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)

# Summary statistics
print("\n\nKEY INSIGHTS:")
print("-" * 80)

# Calculate average time between rounds
time_between_rounds = []
for company_id in company_ids:
    company_deals = deals[deals['CompanyID'] == company_id].dropna(subset=['date']).sort_values('date')
    if len(company_deals) > 1:
        dates = company_deals['date'].tolist()
        for i in range(1, len(dates)):
            days = (dates[i] - dates[i-1]).days
            if days > 0:
                time_between_rounds.append(days)

if time_between_rounds:
    avg_days = np.mean(time_between_rounds)
    print(f"• Average time between funding rounds: {avg_days:.0f} days ({avg_days/365:.1f} years)")

# Active vs inactive
active_count = len([c for c in companies['BusinessStatus'] if c in ['Active', 'Operating']])
print(f"• Currently active companies: {active_count}/{len(companies)}")

# Total investment
total_funding = deals['DealSize'].sum()
if pd.notna(total_funding):
    print(f"• Total funding across all companies: ${total_funding/1e9:.2f} billion")

# Year with most activity
if len(investment_by_year_clean) > 0:
    peak_year = investment_by_year_clean['num_deals'].idxmax()
    peak_deals = investment_by_year_clean.loc[peak_year, 'num_deals']
    print(f"• Peak investment year: {int(peak_year)} with {int(peak_deals)} deals")

# Average funding per company
avg_per_company = total_funding / len(company_ids) if pd.notna(total_funding) else 0
print(f"• Average funding per company: ${avg_per_company/1e6:.1f} million")

print("\n")

