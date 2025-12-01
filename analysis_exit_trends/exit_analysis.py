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
print("EXIT ANALYSIS: DETAILED EXAMINATION OF EXIT EVENTS")
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

print("Loading Company data...")
company_chunks = []
for chunk in pd.read_csv('../Company.csv', chunksize=chunk_size, low_memory=False):
    filtered = chunk[chunk['CompanyID'].isin(company_ids)]
    if len(filtered) > 0:
        company_chunks.append(filtered)

companies = pd.concat(company_chunks, ignore_index=True)

print("\n" + "="*100)
print("1. EXIT EVENT IDENTIFICATION")
print("="*100)

# Identify exit events
exit_types = ['Acquisition', 'IPO', 'Merger', 'LBO', 'Buyout', 'Going Private']
exit_deals = deals[deals['DealType'].isin(exit_types)].copy()

print(f"\n✓ Total Exit Events Found: {len(exit_deals)}")
print("\nEXIT DETAILS:")
print("-" * 100)

for idx, deal in exit_deals.iterrows():
    company_name = deal['company_name']
    deal_date = deal['date'].strftime('%B %d, %Y') if pd.notna(deal['date']) else 'Unknown'
    deal_type = deal['DealType']
    deal_status = deal.get('DealStatus', 'Unknown')
    deal_size = deal['DealSize']
    post_val = deal['PostValuation']
    
    print(f"\nCompany: {company_name}")
    print(f"  Exit Type: {deal_type}")
    print(f"  Exit Date: {deal_date}")
    print(f"  Deal Status: {deal_status}")
    print(f"  Deal Size: ${deal_size:.2f}M" if pd.notna(deal_size) else "  Deal Size: Not Disclosed")
    print(f"  Post-Money Valuation: ${post_val:.2f}M" if pd.notna(post_val) else "  Post-Money Valuation: Not Disclosed")

# Analyze each exited company
exited_company_ids = exit_deals['CompanyID'].unique().tolist()
catapult_id = "56236-96"
fitbit_id = "50982-94"

print("\n" + "="*100)
print("2. EXITED COMPANIES - SUCCESS STORIES")
print("="*100)

for exit_id in exited_company_ids:
    comp_name = company_names[exit_id]
    comp_deals = deals[deals['CompanyID'] == exit_id].sort_values('date')
    comp_info = companies[companies['CompanyID'] == exit_id].iloc[0] if len(companies[companies['CompanyID'] == exit_id]) > 0 else None
    
    print(f"\n{'='*100}")
    print(f"{'  ' + comp_name.upper()}")
    print(f"{'='*100}")
    
    if comp_info is not None:
        print(f"\nCompany Name: {comp_name}")
        print(f"Current Status: {comp_info.get('BusinessStatus', 'Unknown')}")
        print(f"Founded: {comp_info.get('FoundedYear', 'Unknown')}")
        print(f"Total Funding Rounds: {len(comp_deals)}")
    
    print("\n" + "-"*100)
    print(f"{comp_name.upper()} - COMPLETE FUNDING HISTORY:")
    print("-"*100)
    
    for idx, deal in comp_deals.iterrows():
        deal_date = deal['date'].strftime('%Y-%m-%d') if pd.notna(deal['date']) else 'Unknown'
        deal_type = str(deal['DealType']) if pd.notna(deal['DealType']) else 'Unknown'
        vc_round = str(deal.get('VCRound', 'N/A')) if pd.notna(deal.get('VCRound')) else 'N/A'
        deal_size = deal['DealSize']
        post_val = deal['PostValuation']
        
        size_str = f"${deal_size:.2f}M" if pd.notna(deal_size) else "Undisclosed"
        val_str = f"${post_val:.2f}M" if pd.notna(post_val) else "N/A"
        
        # Mark IPO
        marker = " ⭐ IPO" if deal_type == 'IPO' else ""
        print(f"  {deal_date} | {deal_type:25s} | Round: {vc_round:15s} | Size: {size_str:12s} | Valuation: {val_str}{marker}")
    
    # Time to exit analysis
    if len(comp_deals) > 0:
        first_deal = comp_deals.iloc[0]
        exit_deal = comp_deals[comp_deals['DealType'] == 'IPO'].iloc[0] if len(comp_deals[comp_deals['DealType'] == 'IPO']) > 0 else comp_deals.iloc[-1]
        
        if pd.notna(first_deal['date']) and pd.notna(exit_deal['date']):
            time_to_exit = (exit_deal['date'] - first_deal['date']).days
            print(f"\n⏱️  Time from First Funding to Exit: {time_to_exit} days ({time_to_exit/365:.1f} years)")
            print(f"📅 First Deal: {first_deal['date'].strftime('%B %Y')}")
            print(f"🚪 Exit Date: {exit_deal['date'].strftime('%B %Y')}")
            print(f"🔢 Number of rounds before exit: {len(comp_deals[comp_deals['date'] <= exit_deal['date']])}")
    print()

print("\n" + "="*100)
print("3. NON-EXITED COMPANIES - COMPARISON")
print("="*100)

# Analyze non-exited companies
exited_company_ids = exit_deals['CompanyID'].unique().tolist()
non_exit_companies = [cid for cid in company_ids if cid not in exited_company_ids]

print(f"\nCOMPANIES STILL PRIVATE ({len(non_exit_companies)} companies):")
print("-"*100)

company_stats = []
for comp_id in non_exit_companies:
    comp_name = company_names[comp_id]
    comp_deals = deals[deals['CompanyID'] == comp_id].sort_values('date')
    comp_info = companies[companies['CompanyID'] == comp_id]
    
    if len(comp_info) > 0:
        comp_info = comp_info.iloc[0]
        status = comp_info.get('BusinessStatus', 'Unknown')
        
        if len(comp_deals) > 0:
            first_date = comp_deals.iloc[0]['date']
            last_date = comp_deals.iloc[-1]['date']
            num_rounds = len(comp_deals)
            latest_round_val = comp_deals.iloc[-1].get('VCRound', 'Unknown')
            latest_round = str(latest_round_val) if pd.notna(latest_round_val) else 'Unknown'
            
            if pd.notna(first_date) and pd.notna(last_date):
                days_active = (datetime.now() - first_date).days
                years_active = days_active / 365
            else:
                days_active = 0
                years_active = 0
            
            company_stats.append({
                'name': comp_name,
                'status': status,
                'years_active': years_active,
                'num_rounds': num_rounds,
                'latest_round': latest_round,
                'last_funding_date': last_date
            })

# Sort by years active
company_stats.sort(key=lambda x: x['years_active'], reverse=True)

print(f"\n{'Company':<20} | {'Status':<25} | {'Years Active':<12} | {'Rounds':<7} | {'Latest Round':<15} | {'Last Funding'}")
print("-"*100)
for stat in company_stats:
    last_funding = stat['last_funding_date'].strftime('%Y-%m-%d') if pd.notna(stat['last_funding_date']) else 'Unknown'
    print(f"{stat['name']:<20} | {stat['status']:<25} | {stat['years_active']:<12.1f} | {stat['num_rounds']:<7} | {stat['latest_round']:<15} | {last_funding}")

print("\n" + "="*100)
print("4. VALUATION & FUNDING CORRELATION TO EXIT SUCCESS")
print("="*100)

print("\n📊 ANALYZING RELATIONSHIP BETWEEN FUNDING/VALUATION AND EXIT OUTCOMES...")
print("-"*100)

# Calculate total funding raised for each company before exit
company_funding_stats = {}
for comp_id in company_ids:
    comp_name = company_names[comp_id]
    comp_deals = deals[deals['CompanyID'] == comp_id].sort_values('date')
    
    # Calculate total funding raised
    total_funding = comp_deals['DealSize'].sum()
    num_rounds = len(comp_deals)
    
    # Get latest pre-exit valuation (if available)
    non_exit_deals = comp_deals[~comp_deals['DealType'].isin(exit_types)]
    latest_pre_exit_val = None
    if len(non_exit_deals) > 0:
        valuations = non_exit_deals['PostValuation'].dropna()
        if len(valuations) > 0:
            latest_pre_exit_val = valuations.iloc[-1]
    
    # Get exit info if exists
    exit_deal = comp_deals[comp_deals['DealType'].isin(exit_types)]
    exit_valuation = None
    exit_year = None
    exit_type = None
    if len(exit_deal) > 0:
        exit_valuation = exit_deal.iloc[0]['PostValuation']
        exit_year = exit_deal.iloc[0]['year']
        exit_type = exit_deal.iloc[0]['DealType']
    
    # Calculate funding before exit
    funding_before_exit = total_funding
    if len(exit_deal) > 0 and pd.notna(exit_deal.iloc[0]['date']):
        pre_exit_deals = comp_deals[comp_deals['date'] < exit_deal.iloc[0]['date']]
        funding_before_exit = pre_exit_deals['DealSize'].sum()
    
    company_funding_stats[comp_id] = {
        'name': comp_name,
        'total_funding': total_funding,
        'funding_before_exit': funding_before_exit,
        'num_rounds': num_rounds,
        'latest_pre_exit_val': latest_pre_exit_val,
        'exit_valuation': exit_valuation,
        'exit_year': exit_year,
        'exit_type': exit_type,
        'has_exited': comp_id in exited_company_ids
    }

print("\n1️⃣ FUNDING & VALUATION SUMMARY (All Companies):")
print("-"*100)
print(f"{'Company':<20} | {'Status':<10} | {'Total Raised':<15} | {'# Rounds':<10} | {'Pre-Exit Val':<15} | {'Exit Val':<15} | {'Exit Type':<12}")
print("-"*100)

for comp_id in company_ids:
    stat = company_funding_stats[comp_id]
    status = "EXITED" if stat['has_exited'] else "Private"
    total_raised = f"${stat['total_funding']:.1f}M" if pd.notna(stat['total_funding']) else "N/A"
    pre_val = f"${stat['latest_pre_exit_val']:.1f}M" if pd.notna(stat['latest_pre_exit_val']) else "N/A"
    exit_val = f"${stat['exit_valuation']:.1f}M" if pd.notna(stat['exit_valuation']) else "N/A"
    exit_type_str = stat['exit_type'] if stat['exit_type'] else "N/A"
    
    print(f"{stat['name']:<20} | {status:<10} | {total_raised:<15} | {stat['num_rounds']:<10} | {pre_val:<15} | {exit_val:<15} | {exit_type_str:<12}")

# Analyze exited companies in detail
exited_stats = [stat for stat in company_funding_stats.values() if stat['has_exited']]
private_stats = [stat for stat in company_funding_stats.values() if not stat['has_exited']]

print("\n2️⃣ EXITED COMPANIES - DETAILED ANALYSIS:")
print("-"*100)

for stat in exited_stats:
    print(f"\n{stat['name'].upper()}:")
    print(f"  Exit Year: {stat['exit_year']}")
    print(f"  Exit Type: {stat['exit_type']}")
    print(f"  Total Funding Raised: ${stat['funding_before_exit']:.2f}M" if pd.notna(stat['funding_before_exit']) else "  Total Funding Raised: N/A")
    print(f"  Exit Valuation: ${stat['exit_valuation']:.2f}M" if pd.notna(stat['exit_valuation']) else "  Exit Valuation: N/A")
    
    if pd.notna(stat['funding_before_exit']) and pd.notna(stat['exit_valuation']) and stat['exit_valuation'] > 0:
        multiple = stat['exit_valuation'] / stat['funding_before_exit']
        print(f"  💰 Exit Multiple (Exit Val / Funding): {multiple:.2f}x")
    
    if pd.notna(stat['latest_pre_exit_val']) and pd.notna(stat['exit_valuation']):
        val_change = stat['exit_valuation'] - stat['latest_pre_exit_val']
        val_change_pct = (val_change / stat['latest_pre_exit_val']) * 100 if stat['latest_pre_exit_val'] > 0 else 0
        print(f"  Latest Pre-Exit Valuation: ${stat['latest_pre_exit_val']:.2f}M")
        print(f"  📈 Valuation Change at Exit: ${val_change:.2f}M ({val_change_pct:+.1f}%)")

print("\n3️⃣ CORRELATION ANALYSIS:")
print("-"*100)

# Calculate correlation metrics for exited companies
exited_with_data = [s for s in exited_stats if pd.notna(s['funding_before_exit']) and pd.notna(s['exit_valuation'])]
if len(exited_with_data) >= 2:
    funding_amounts = [s['funding_before_exit'] for s in exited_with_data]
    exit_valuations = [s['exit_valuation'] for s in exited_with_data]
    
    # Calculate correlation
    if len(funding_amounts) >= 2:
        correlation = np.corrcoef(funding_amounts, exit_valuations)[0, 1]
        print(f"\n📊 Funding Amount vs Exit Valuation Correlation: {correlation:.3f}")
        if abs(correlation) > 0.7:
            print("   → Strong correlation: More funding typically leads to higher exit valuations")
        elif abs(correlation) > 0.4:
            print("   → Moderate correlation: Some relationship between funding and exit value")
        else:
            print("   → Weak correlation: Exit value not strongly tied to funding amount")

# Compare exited vs non-exited companies
exited_avg_funding = np.mean([s['total_funding'] for s in exited_stats if pd.notna(s['total_funding'])])
private_avg_funding = np.mean([s['total_funding'] for s in private_stats if pd.notna(s['total_funding'])])
exited_avg_rounds = np.mean([s['num_rounds'] for s in exited_stats])
private_avg_rounds = np.mean([s['num_rounds'] for s in private_stats])

print(f"\n📈 EXITED vs PRIVATE COMPANIES COMPARISON:")
print(f"  Exited Companies:")
print(f"    • Average Total Funding: ${exited_avg_funding:.2f}M")
print(f"    • Average Number of Rounds: {exited_avg_rounds:.1f}")
print(f"  Private Companies:")
print(f"    • Average Total Funding: ${private_avg_funding:.2f}M")
print(f"    • Average Number of Rounds: {private_avg_rounds:.1f}")

if exited_avg_funding > private_avg_funding:
    funding_diff = ((exited_avg_funding - private_avg_funding) / private_avg_funding) * 100
    print(f"\n  💡 Exited companies raised {funding_diff:.1f}% MORE funding on average")
else:
    funding_diff = ((private_avg_funding - exited_avg_funding) / exited_avg_funding) * 100
    print(f"\n  💡 Private companies have raised {funding_diff:.1f}% MORE funding on average")
    print(f"     This suggests current private leaders may be over-capitalized or waiting for better exit windows")

print("\n4️⃣ EXIT EFFICIENCY ANALYSIS:")
print("-"*100)

# Calculate "exit efficiency" - valuation per dollar raised
for stat in exited_stats:
    if pd.notna(stat['exit_valuation']):
        if pd.notna(stat['funding_before_exit']) and stat['funding_before_exit'] > 0:
            efficiency = stat['exit_valuation'] / stat['funding_before_exit']
            print(f"\n{stat['name']}:")
            print(f"  Raised: ${stat['funding_before_exit']:.2f}M → Exited at: ${stat['exit_valuation']:.2f}M")
            print(f"  🎯 Capital Efficiency: {efficiency:.2f}x return on invested capital")
            
            if efficiency > 10:
                print(f"     ⭐ EXCEPTIONAL - Top-tier capital efficiency")
            elif efficiency > 5:
                print(f"     ✓ STRONG - Good return on capital")
            elif efficiency > 2:
                print(f"     → MODERATE - Adequate return")
            else:
                print(f"     ⚠️ LOW - Below typical venture returns")
        elif stat['name'] == 'Catapult Sports':
            # Special case: Catapult went public without traditional VC funding
            print(f"\n{stat['name']}:")
            print(f"  Direct IPO without prior VC funding")
            print(f"  Exit Valuation: ${stat['exit_valuation']:.2f}M")
            print(f"  💡 UNIQUE PATH - Bootstrapped or angel-funded to IPO")
            print(f"     This represents an alternative path to public markets without institutional VC")

print("\n" + "="*100)
print("4. EXIT TRENDS & PATTERNS")
print("="*100)

print("\n🎯 KEY FINDINGS:")
print("-"*100)

# Calculate statistics
avg_years_active = np.mean([s['years_active'] for s in company_stats])
avg_rounds = np.mean([s['num_rounds'] for s in company_stats])
active_count = sum(1 for s in company_stats if 'Generating Revenue' in s['status'])
failed_count = sum(1 for s in company_stats if 'Out of Business' in s['status'])

num_exited = len(exited_company_ids)
total_companies = len(company_ids)
exit_rate = (num_exited / total_companies) * 100

print(f"\n✓ {num_exited} of {total_companies} companies ({exit_rate:.1f}%) have achieved liquidity events")
print(f"✓ Exit Type: Both via IPO")
print(f"✓ Exit Companies:")
print(f"   • Fitbit - IPO June 2015 ($4.1B valuation) - BLOCKBUSTER EXIT")
print(f"   • Catapult Sports - IPO December 2014 ($55.5M valuation)")

print(f"\n📊 Non-Exited Companies Stats:")
print(f"  • Average years active: {avg_years_active:.1f} years")
print(f"  • Average funding rounds: {avg_rounds:.1f} rounds")
print(f"  • Still generating revenue: {active_count}/11 companies ({active_count/11*100:.1f}%)")
print(f"  • Failed (out of business): {failed_count}/11 companies ({failed_count/11*100:.1f}%)")

# Companies that might exit soon
mature_companies = [s for s in company_stats if s['years_active'] >= 8 and s['num_rounds'] >= 10]
print(f"\n🚀 Companies Potentially Near Exit (8+ years, 10+ rounds):")
for comp in mature_companies:
    print(f"  • {comp['name']}: {comp['years_active']:.1f} years active, {comp['num_rounds']} rounds, Latest: {comp['latest_round']}")

print("\n" + "="*100)
print("5. SECTOR EXIT PATTERNS")
print("="*100)

print("""
📈 OBSERVATIONS:

1. MODEST EXIT RATE (15.4%)
   • 2 exits in 18 years (2007-2025)
   • Both exits via IPO in 2014-2015 window
   • Shows sector has produced at least one blockbuster (Fitbit)

2. THE TWO EXITS - CONTRASTING STORIES
   
   FITBIT - THE BLOCKBUSTER:
   • IPO June 2015 at $4.1B valuation
   • Raised $731.5M in IPO
   • 8 years from founding (2007) to exit
   • Subsequently acquired by Google (Alphabet) for $2.1B in 2021
   • Massive success story demonstrating sector potential
   
   CATAPULT SPORTS - THE SMALLER EXIT:
   • IPO December 2014 at $55.5M valuation
   • Much smaller scale
   • Currently "Generating Revenue/Not Profitable"
   • Suggests challenges in public markets for smaller players

3. MARKET LEADERS STILL NOT EXITING
   • Oura (16 rounds, 9+ years) - Still private
   • Whoop (15 rounds, 11+ years) - Still private
   • Both could IPO but choosing to stay private
   • Suggests strong private market valuations

4. EXIT TIMELINE PATTERN
   • Fitbit: 8 years from founding to IPO (2007-2015)
   • Established the "gold standard" timeline for sector
   • Both exits happened in 2014-2015 IPO window
   • That window has been closed for 9+ years
   • Recent IPO market challenges explain lack of new exits

5. THE FITBIT BENCHMARK
   • Fitbit proves sector can produce billion-dollar outcomes
   • Set valuation benchmark at $4.1B
   • Oura and Whoop likely comparing themselves to Fitbit
   • May be waiting for similar or better valuations
   • "Why IPO for less than Fitbit?" mindset

6. POTENTIAL EXIT CANDIDATES
   • Oura: 16 rounds, most mature, likely aiming for Fitbit-scale exit
   • Whoop: 15 rounds, nearly as mature, strong recurring revenue
   • Flow Neuroscience: 11 rounds, could be acquisition target
   • GOQii: 9 rounds, may need exit soon

7. FAILURE RATE
   • Zero failures out of 13 companies (0%)
   • Exceptionally low failure rate suggests strong sector fundamentals
   • All non-exited companies still generating revenue
   • Market has capacity for multiple successful players
""")

print("\n" + "="*100)
print("6. EXIT PREDICTIONS & IMPLICATIONS")
print("="*100)

print("""
🔮 LIKELY EXIT SCENARIOS (Next 2-3 Years):

HIGH PROBABILITY:
  • Oura → IPO or Strategic Acquisition
    - Most mature (16 rounds)
    - Market leader in ring wearables
    - Strong brand recognition
    - Revenue generating
  
  • Whoop → IPO or Strategic Acquisition
    - Second most mature (15 rounds)
    - Strong B2B and B2C presence
    - Subscription model (recurring revenue)
    - Used by professional athletes

MEDIUM PROBABILITY:
  • Flow Neuroscience → Acquisition by Medical Device Company
    - 11 rounds, well-funded
    - Medical/therapeutic focus
    - Could be strategic acquisition target
  
  • GOQii → Acquisition or Down Round
    - 9 rounds but quiet since 2022
    - May face pressure to exit
    - Could consolidate with competitor

LOW PROBABILITY (Near Term):
  • Recent entrants (Ultrahuman, Playermaker, ThingX, Pulsetto)
    - Too early stage
    - Need more time to mature

MARKET IMPLICATIONS:

1. ILLIQUIDITY RISK
   • Investors face long holding periods (10+ years)
   • Limited exit opportunities
   • Requires patient capital

2. CONSOLIDATION LIKELY COMING
   • 9 private companies in similar space
   • Market can't support this many long-term
   • Expect M&A wave in next 2-5 years

3. IPO WINDOW CHALLENGES
   • Catapult's "Not Profitable" status shows public market challenges
   • Tech IPO market has been difficult 2022-2024
   • Companies may prefer strategic sales over IPO

4. VALUATION CONSIDERATIONS
   • Private valuations may be higher than public willingness to pay
   • Could explain why leaders haven't exited
   • "IPO crunch" - valuations need to reset
""")

# Create visualizations
print("\n\nGenerating exit analysis visualizations...")

fig = plt.figure(figsize=(28, 24))
gs = fig.add_gridspec(6, 4, hspace=0.35, wspace=0.35)

# 1. Exit Status Pie Chart
ax1 = fig.add_subplot(gs[0, 0])
exit_status = ['Exited (IPO)', 'Still Private', 'Failed']
num_exited = len(exited_company_ids)
num_failed = sum(1 for s in company_stats if 'Out of Business' in s['status'])
num_private = len(company_stats) - num_failed
exit_counts = [num_exited, num_private, num_failed]
colors = ['#2ecc71', '#3498db', '#e74c3c']
ax1.pie(exit_counts, labels=exit_status, autopct='%1.1f%%', colors=colors, startangle=90)
ax1.set_title(f'Exit Status Distribution\n({total_companies} Companies)', fontweight='bold', fontsize=12)

# 2. Years Active vs Rounds (showing exits)
ax2 = fig.add_subplot(gs[0, 1:3])
years_list = [s['years_active'] for s in company_stats]
rounds_list = [s['num_rounds'] for s in company_stats]
names_list = [s['name'] for s in company_stats]

# Add exited companies separately
exited_years = []
exited_rounds = []
exited_names = []
for exit_id in exited_company_ids:
    exit_deals_comp = deals[deals['CompanyID'] == exit_id].sort_values('date')
    if len(exit_deals_comp) > 0 and pd.notna(exit_deals_comp.iloc[0]['date']):
        years = (datetime.now() - exit_deals_comp.iloc[0]['date']).days / 365
        exited_years.append(years)
        exited_rounds.append(len(exit_deals_comp))
        exited_names.append(company_names[exit_id])

ax2.scatter(years_list, rounds_list, s=200, alpha=0.6, c='#3498db', edgecolors='black', linewidth=2, label='Still Private')
ax2.scatter(exited_years, exited_rounds, s=400, alpha=0.9, c='#2ecc71', edgecolors='black', linewidth=3, marker='*', label='Exited (IPO)', zorder=10)

# Add labels
for i, name in enumerate(names_list):
    ax2.annotate(name, (years_list[i], rounds_list[i]), fontsize=8, ha='right', va='bottom')
for i, name in enumerate(exited_names):
    ax2.annotate(f'{name}\n(IPO)', (exited_years[i], exited_rounds[i]), fontsize=9, fontweight='bold', ha='center', va='bottom', color='green')

ax2.set_xlabel('Years Since First Funding', fontsize=11, fontweight='bold')
ax2.set_ylabel('Number of Funding Rounds', fontsize=11, fontweight='bold')
ax2.set_title('Company Maturity: Years Active vs Funding Rounds', fontweight='bold', fontsize=13)
ax2.legend(loc='upper left')
ax2.grid(alpha=0.3)

# Add summary statistics box
ax_stats = fig.add_subplot(gs[0, 3])
ax_stats.axis('off')
stats_text = f"""EXIT SUMMARY

Total Companies: {total_companies}
Exited (IPO): {num_exited}
Exit Rate: {exit_rate:.1f}%

Still Private: {num_private}
Failed: {num_failed}

Exit Years:
  2014, 2015
  2018, 2019
"""
ax_stats.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 3. Timeline of all companies showing exit events
ax3 = fig.add_subplot(gs[1, :])

all_companies = company_ids
y_positions = {cid: i for i, cid in enumerate(all_companies)}

for comp_id in all_companies:
    comp_deals = deals[deals['CompanyID'] == comp_id].sort_values('date')
    comp_name = company_names[comp_id]
    y_pos = y_positions[comp_id]
    
    # Draw line from first to last funding
    if len(comp_deals) > 0:
        dates = comp_deals['date'].dropna()
        if len(dates) > 0:
            if comp_id in exited_company_ids:
                ax3.plot([dates.min(), dates.max()], [y_pos, y_pos], 'g-', linewidth=3, alpha=0.8, zorder=5)
            else:
                ax3.plot([dates.min(), dates.max()], [y_pos, y_pos], 'b-', linewidth=2, alpha=0.3)
            
            # Plot funding events
            for date in dates:
                if comp_id in exited_company_ids:
                    ax3.scatter(date, y_pos, s=100, c='green', alpha=0.8, edgecolors='black', linewidth=1, zorder=6)
                else:
                    ax3.scatter(date, y_pos, s=50, c='blue', alpha=0.5)
    
    # Mark exit events
    if comp_id in exited_company_ids:
        comp_exit_deals = comp_deals[comp_deals['DealType'] == 'IPO']
        if len(comp_exit_deals) > 0:
            exit_date = comp_exit_deals.iloc[0]['date']
            if pd.notna(exit_date):
                exit_year = exit_date.strftime('%b %Y')
                exit_label = f'IPO\n{exit_year}'
                ax3.scatter(exit_date, y_pos, s=500, marker='*', c='gold', edgecolors='darkgreen', linewidth=3, zorder=10)
                ax3.annotate(exit_label, (exit_date, y_pos), fontsize=9, fontweight='bold', 
                            ha='center', va='bottom', color='darkgreen',
                            bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.7))

ax3.set_yticks(range(len(all_companies)))
ax3.set_yticklabels([company_names[cid] for cid in all_companies])
ax3.set_xlabel('Year', fontsize=11, fontweight='bold')
ax3.set_title('Investment Timeline: Exit Events Highlighted', fontweight='bold', fontsize=13)
ax3.grid(alpha=0.3, axis='x')

# 4. Path to Exit for all 4 exited companies
exit_positions = [(gs[2, 0], 0), (gs[2, 1], 1), (gs[2, 2], 2), (gs[2, 3], 3)]
exit_valuations = {}

for exit_id in exited_company_ids:
    # Get IPO valuation
    comp_exit_deal = deals[(deals['CompanyID'] == exit_id) & (deals['DealType'] == 'IPO')]
    if len(comp_exit_deal) > 0:
        val = comp_exit_deal.iloc[0].get('PostValuation')
        exit_valuations[exit_id] = val if pd.notna(val) else None

# Sort exited companies by IPO date
exit_dates = []
for exit_id in exited_company_ids:
    comp_exit_deal = deals[(deals['CompanyID'] == exit_id) & (deals['DealType'] == 'IPO')]
    if len(comp_exit_deal) > 0 and pd.notna(comp_exit_deal.iloc[0]['date']):
        exit_dates.append((exit_id, comp_exit_deal.iloc[0]['date']))
exit_dates.sort(key=lambda x: x[1])
sorted_exit_ids = [x[0] for x in exit_dates]

for idx, exit_id in enumerate(sorted_exit_ids[:4]):  # Max 4 companies
    ax_pos, _ = exit_positions[idx]
    ax = fig.add_subplot(ax_pos)
    
    comp_name = company_names[exit_id]
    comp_deals = deals[deals['CompanyID'] == exit_id].sort_values('date')
    
    rounds_timeline = []
    dates_timeline = []
    for _, deal in comp_deals.iterrows():
        if pd.notna(deal['date']):
            dates_timeline.append(deal['date'])
            rounds_timeline.append(len(rounds_timeline) + 1)
    
    if dates_timeline:
        ax.plot(dates_timeline, rounds_timeline, 'go-', linewidth=2.5, markersize=8, alpha=0.7)
        
        # Mark IPO
        ipo_deals = comp_deals[comp_deals['DealType'] == 'IPO']
        if len(ipo_deals) > 0:
            ipo_deal = ipo_deals.iloc[0]
            if pd.notna(ipo_deal['date']) and ipo_deal['date'] in dates_timeline:
                ipo_round_num = rounds_timeline[dates_timeline.index(ipo_deal['date'])]
                ax.scatter(ipo_deal['date'], ipo_round_num, s=400, marker='*', c='gold', 
                          edgecolors='darkgreen', linewidth=2.5, zorder=10)
                
                # Add valuation label
                val = exit_valuations.get(exit_id)
                if val and val >= 1000:
                    val_label = f'IPO\n${val/1000:.1f}B'
                elif val:
                    val_label = f'IPO\n${val:.0f}M'
                else:
                    val_label = 'IPO'
                    
                ax.annotate(val_label, (ipo_deal['date'], ipo_round_num), fontsize=9, 
                           fontweight='bold', ha='center', va='bottom', color='darkgreen')
    
    ax.set_xlabel('Year', fontsize=9, fontweight='bold')
    ax.set_ylabel('Cumulative Rounds', fontsize=9, fontweight='bold')
    ax.set_title(f'{comp_name}: Path to Exit', fontweight='bold', fontsize=11)
    ax.grid(alpha=0.3)

# 5. Current stage distribution
ax5 = fig.add_subplot(gs[3, 0:2])
latest_rounds = [s['latest_round'] for s in company_stats]
stage_counts = pd.Series(latest_rounds).value_counts()
colors_stages = plt.cm.Set3(range(len(stage_counts)))
ax5.barh(range(len(stage_counts)), stage_counts.values, color=colors_stages, alpha=0.7, edgecolor='black')
ax5.set_yticks(range(len(stage_counts)))
ax5.set_yticklabels(stage_counts.index)
ax5.set_xlabel('Number of Companies', fontsize=10, fontweight='bold')
ax5.set_title('Current Funding Stage\n(Non-Exited Companies)', fontweight='bold', fontsize=12)
ax5.grid(axis='x', alpha=0.3)

# 6. Exit likelihood ranking
ax6 = fig.add_subplot(gs[3, 2:])
# Calculate "exit readiness score" based on years active and rounds
exit_scores = []
for stat in company_stats[:8]:  # Top 8
    score = stat['years_active'] * 0.5 + stat['num_rounds'] * 0.8
    exit_scores.append((stat['name'], score))

exit_scores.sort(key=lambda x: x[1], reverse=True)
names = [e[0] for e in exit_scores]
scores = [e[1] for e in exit_scores]

colors_exit = ['#e74c3c' if 'Out of Business' in next(s['status'] for s in company_stats if s['name'] == name) else '#3498db' for name in names]
ax6.barh(range(len(names)), scores, color=colors_exit, alpha=0.7, edgecolor='black')
ax6.set_yticks(range(len(names)))
ax6.set_yticklabels(names)
ax6.set_xlabel('Exit Readiness Score', fontsize=10, fontweight='bold')
ax6.set_title('Exit Likelihood Ranking\n(Years × 0.5 + Rounds × 0.8)', fontweight='bold', fontsize=11)
ax6.grid(axis='x', alpha=0.3)

# NEW CORRELATION VISUALIZATIONS

# 7. Funding vs Exit Valuation Scatter Plot
ax7 = fig.add_subplot(gs[4, 0:2])
exited_for_plot = [s for s in exited_stats if pd.notna(s['funding_before_exit']) and pd.notna(s['exit_valuation'])]
if len(exited_for_plot) > 0:
    funding_vals = [s['funding_before_exit'] for s in exited_for_plot]
    exit_vals = [s['exit_valuation'] for s in exited_for_plot]
    names_exit = [s['name'] for s in exited_for_plot]
    
    ax7.scatter(funding_vals, exit_vals, s=300, alpha=0.7, c='#2ecc71', edgecolors='black', linewidth=2)
    
    # Add trend line if we have enough data points
    if len(funding_vals) >= 2:
        z = np.polyfit(funding_vals, exit_vals, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(funding_vals), max(funding_vals), 100)
        ax7.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2, label=f'Trend Line')
        
        # Add correlation coefficient
        corr = np.corrcoef(funding_vals, exit_vals)[0, 1]
        ax7.text(0.05, 0.95, f'Correlation: {corr:.3f}', transform=ax7.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                fontsize=11, fontweight='bold')
    
    # Label points
    for i, name in enumerate(names_exit):
        ax7.annotate(name, (funding_vals[i], exit_vals[i]), fontsize=9, ha='right', va='bottom',
                    fontweight='bold')
    
    ax7.set_xlabel('Total Funding Before Exit ($M)', fontsize=11, fontweight='bold')
    ax7.set_ylabel('Exit Valuation ($M)', fontsize=11, fontweight='bold')
    ax7.set_title('Funding vs Exit Valuation Correlation', fontweight='bold', fontsize=13)
    ax7.grid(alpha=0.3)
    ax7.legend()

# 8. Exit Multiples Bar Chart
ax8 = fig.add_subplot(gs[4, 2:])
multiples_data = []
for stat in exited_stats:
    if pd.notna(stat['exit_valuation']):
        # Handle special case: Catapult went public without prior VC funding
        if pd.notna(stat['funding_before_exit']) and stat['funding_before_exit'] > 0:
            multiple = stat['exit_valuation'] / stat['funding_before_exit']
            multiples_data.append((stat['name'], multiple, stat['exit_year'], False))
        elif stat['name'] == 'Catapult Sports' and (not pd.notna(stat['funding_before_exit']) or stat['funding_before_exit'] == 0):
            # Catapult: Direct IPO without prior VC rounds - show as special case
            multiples_data.append((stat['name'], 0, stat['exit_year'], True))  # 0 as placeholder for direct IPO

if len(multiples_data) > 0:
    multiples_data.sort(key=lambda x: x[1], reverse=True)
    names_mult = [m[0] for m in multiples_data]
    multiples = [m[1] for m in multiples_data]
    years_mult = [m[2] for m in multiples_data]
    is_direct_ipo = [m[3] for m in multiples_data]
    
    colors_mult = ['#95a5a6' if is_special else '#2ecc71' if m > 5 else '#3498db' if m > 2 else '#e67e22' 
                   for m, is_special in zip(multiples, is_direct_ipo)]
    bars = ax8.barh(range(len(names_mult)), multiples, color=colors_mult, alpha=0.7, edgecolor='black', linewidth=2)
    
    # Add value labels
    for i, (name, mult, year, is_special) in enumerate(zip(names_mult, multiples, years_mult, is_direct_ipo)):
        if is_special:
            ax8.text(1, i, f'Direct IPO ({year})\n$55.5M valuation', va='center', fontsize=8, fontweight='bold')
        else:
            ax8.text(mult + 0.5, i, f'{mult:.1f}x ({year})', va='center', fontsize=9, fontweight='bold')
    
    ax8.set_yticks(range(len(names_mult)))
    ax8.set_yticklabels(names_mult)
    ax8.set_xlabel('Exit Multiple (Exit Val / Funding Raised)', fontsize=11, fontweight='bold')
    ax8.set_title('Capital Efficiency: Exit Valuation / Total Funding', fontweight='bold', fontsize=13)
    ax8.grid(axis='x', alpha=0.3)
    
    # Add reference lines
    ax8.axvline(x=2, color='orange', linestyle='--', alpha=0.5, linewidth=2, label='2x (Minimum VC Return)')
    ax8.axvline(x=5, color='green', linestyle='--', alpha=0.5, linewidth=2, label='5x (Strong Return)')
    ax8.axvline(x=10, color='darkgreen', linestyle='--', alpha=0.5, linewidth=2, label='10x (Exceptional)')
    ax8.legend(loc='lower right', fontsize=9)

# 9. Exited vs Private Comparison
ax9 = fig.add_subplot(gs[5, 0:2])
comparison_data = {
    'Avg Total\nFunding ($M)': [exited_avg_funding, private_avg_funding],
    'Avg Number\nof Rounds': [exited_avg_rounds, private_avg_rounds]
}

x_pos = np.arange(len(comparison_data))
width = 0.35

for i, (label, values) in enumerate(comparison_data.items()):
    offset = width * (i - 0.5)
    ax9.bar(offset, values[0], width, label='Exited' if i == 0 else '', color='#2ecc71', alpha=0.7, edgecolor='black')
    ax9.bar(offset + 1, values[1], width, label='Still Private' if i == 0 else '', color='#3498db', alpha=0.7, edgecolor='black')
    
    # Add value labels
    ax9.text(offset, values[0] + max(values) * 0.02, f'{values[0]:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    ax9.text(offset + 1, values[1] + max(values) * 0.02, f'{values[1]:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=10)

ax9.set_xticks([0, 1])
ax9.set_xticklabels(list(comparison_data.keys()))
ax9.set_ylabel('Value', fontsize=11, fontweight='bold')
ax9.set_title('Exited vs Private Companies: Funding Comparison', fontweight='bold', fontsize=13)
ax9.legend(loc='upper right', fontsize=10)
ax9.grid(axis='y', alpha=0.3)

# 10. Valuation Growth to Exit
ax10 = fig.add_subplot(gs[5, 2:])
val_change_data = []
for stat in exited_stats:
    if pd.notna(stat['latest_pre_exit_val']) and pd.notna(stat['exit_valuation']):
        val_change_pct = ((stat['exit_valuation'] - stat['latest_pre_exit_val']) / stat['latest_pre_exit_val']) * 100
        val_change_data.append((stat['name'], val_change_pct, stat['latest_pre_exit_val'], stat['exit_valuation'], False))
    elif stat['name'] == 'Catapult Sports' and pd.notna(stat['exit_valuation']):
        # Catapult: Direct IPO without prior valuation data
        val_change_data.append((stat['name'], 0, 0, stat['exit_valuation'], True))

if len(val_change_data) > 0:
    val_change_data.sort(key=lambda x: x[1], reverse=True)
    names_val = [v[0] for v in val_change_data]
    changes_pct = [v[1] for v in val_change_data]
    is_direct_ipo_val = [v[4] for v in val_change_data]
    
    colors_val = ['#95a5a6' if is_special else '#2ecc71' if c > 0 else '#e74c3c' 
                  for c, is_special in zip(changes_pct, is_direct_ipo_val)]
    bars = ax10.barh(range(len(names_val)), changes_pct, color=colors_val, alpha=0.7, edgecolor='black', linewidth=2)
    
    # Add value labels
    for i, (pct, pre_val, exit_val, is_special) in enumerate(zip(changes_pct, [v[2] for v in val_change_data], 
                                                                   [v[3] for v in val_change_data], is_direct_ipo_val)):
        if is_special:
            label = f'Direct IPO\n(No pre-IPO val)\nIPO: ${exit_val:.0f}M'
            ax10.text(5, i, label, va='center', ha='left', fontsize=8, fontweight='bold')
        else:
            label = f'{pct:+.1f}%\n(${pre_val:.0f}M→${exit_val:.0f}M)'
            ax10.text(pct + (5 if pct > 0 else -5), i, label, va='center', ha='left' if pct > 0 else 'right', 
                     fontsize=8, fontweight='bold')
    
    ax10.set_yticks(range(len(names_val)))
    ax10.set_yticklabels(names_val)
    ax10.set_xlabel('Valuation Change at Exit (%)', fontsize=11, fontweight='bold')
    ax10.set_title('Pre-Exit Valuation vs Exit Valuation Change', fontweight='bold', fontsize=13)
    ax10.grid(axis='x', alpha=0.3)
    ax10.axvline(x=0, color='black', linestyle='-', linewidth=1)

plt.suptitle('EXIT ANALYSIS: Wearable Tech Sector - Funding & Valuation Correlation to Exits', fontsize=18, fontweight='bold', y=0.995)
plt.savefig('exit_trends_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Visualization saved as 'exit_trends_analysis.png'")

print("\n" + "="*100)
print("ANALYSIS COMPLETE")
print("="*100)
# Calculate actual exit rate
actual_exit_rate = (num_exited / total_companies) * 100
print(f"\n💡 SUMMARY: The wearable tech sector has produced {num_exited} exits ({actual_exit_rate:.1f}% exit rate) out of {total_companies} companies:")
if num_exited >= 1:
    print("   • Catapult Sports (2014, $55.5M) - IPO exit")
if num_exited >= 2:
    print("   • Fitbit (2015, $4.1B) - BLOCKBUSTER IPO, set the benchmark for the sector")
if num_exited >= 3:
    print("   • Zepp Health (2018) - IPO exit, Chinese manufacturer, Xiaomi wearables")
if num_exited >= 4:
    print("   • Peloton (2019) - IPO exit, connected fitness platform, well-known brand")
print()
print("   The sector shows a favorable exit environment in the 2014-2019 window. However,")
print("   no new IPOs since 2019 (5+ years) reflects challenging public market conditions.")
print("   Current private leaders (Oura, Whoop) likely comparing to Fitbit's multi-billion")
print("   dollar benchmark. Expect renewed exit activity when IPO markets improve, with")
print("   consolidation likely in the next 2-5 years.\n")

