import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

# Read the company list
company_list = []
with open('/Users/yufei/SchoolWork/fin/stata/list.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if line and not line.startswith('"') and line not in ['', 'Total Valuation Sum: $20.01B']:
            company_list.append(line)

print(f"Companies to analyze: {company_list}")

# Read Company.csv to get company IDs
print("Loading Company.csv...")
company_df = pd.read_csv('/Users/yufei/SchoolWork/fin/stata/Company.csv', low_memory=False)

# Filter for companies in our list
companies = company_df[company_df['CompanyName'].isin(company_list)].copy()
print(f"Found {len(companies)} companies in dataset")
print(companies[['CompanyName', 'CompanyID']].to_string())

# Read Deal.csv
print("\nLoading Deal.csv...")
deal_df = pd.read_csv('/Users/yufei/SchoolWork/fin/stata/Deal.csv', low_memory=False)

# Print column names to understand structure
print("\nDeal columns:", deal_df.columns.tolist())

# Filter deals for our companies
company_ids = companies['CompanyID'].tolist()
company_deals = deal_df[deal_df['CompanyID'].isin(company_ids)].copy()

print(f"\nFound {len(company_deals)} deals for these companies")

# Check for valuation columns
valuation_cols = [col for col in deal_df.columns if 'valuation' in col.lower() or 'money' in col.lower()]
print(f"Valuation-related columns: {valuation_cols}")

# Convert deal date to datetime
company_deals['DealDate'] = pd.to_datetime(company_deals['DealDate'], errors='coerce')

# Filter for deals with both pre-money and post-money valuations
# Look for PremoneyValuation and PostValuation columns
premoney_col = None
postmoney_col = None

for col in deal_df.columns:
    if 'premoney' in col.lower() and 'valuation' in col.lower():
        premoney_col = col
    elif 'post' in col.lower() and 'valuation' in col.lower() and 'status' not in col.lower():
        postmoney_col = col

print(f"\nPre-money column: {premoney_col}")
print(f"Post-money column: {postmoney_col}")

if premoney_col and postmoney_col:
    # Filter for deals with both valuations
    company_deals_with_valuations = company_deals[
        (company_deals[premoney_col].notna()) & 
        (company_deals[postmoney_col].notna()) &
        (company_deals[premoney_col] > 0) &
        (company_deals[postmoney_col] > 0)
    ].copy()
    
    print(f"\nDeals with both pre and post-money valuations: {len(company_deals_with_valuations)}")
    
    # Sort by date and get first deal for each company
    company_deals_with_valuations = company_deals_with_valuations.sort_values('DealDate')
    first_deals = company_deals_with_valuations.groupby('CompanyID').first().reset_index()
    
    # Calculate equity taken
    # Equity taken = (Post-money - Pre-money) / Post-money
    first_deals['Equity Taken (%)'] = (
        (first_deals[postmoney_col] - first_deals[premoney_col]) / first_deals[postmoney_col] * 100
    )
    
    # CompanyName should already be in first_deals from the groupby
    # Let's check if it exists, otherwise we need to merge
    if 'CompanyName' not in first_deals.columns:
        first_deals = first_deals.merge(
            companies[['CompanyID', 'CompanyName']], 
            on='CompanyID', 
            how='left'
        )
    
    # Select relevant columns
    result_df = first_deals[[
        'CompanyName', 
        'DealDate',
        premoney_col, 
        postmoney_col, 
        'Equity Taken (%)',
        'DealSize',
        'DealType'
    ]].copy()
    
    # Sort by company name
    result_df = result_df.sort_values('CompanyName')
    
    print("\n" + "="*80)
    print("FIRST DEALS WITH PRE-MONEY AND POST-MONEY VALUATIONS")
    print("="*80)
    print(result_df.to_string(index=False))
    
    # Calculate average equity taken
    avg_equity = result_df['Equity Taken (%)'].mean()
    median_equity = result_df['Equity Taken (%)'].median()
    
    print("\n" + "="*80)
    print(f"Average Equity Taken: {avg_equity:.2f}%")
    print(f"Median Equity Taken: {median_equity:.2f}%")
    print("="*80)
    
    # Save to CSV
    result_df.to_csv('/Users/yufei/SchoolWork/fin/stata/analysis_entry_trends/first_deal_equity_data.csv', index=False)
    print("\nData saved to: analysis_entry_trends/first_deal_equity_data.csv")
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    
    # Plot 1: Equity taken by company (bar chart)
    companies_sorted = result_df.sort_values('Equity Taken (%)', ascending=True)
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(companies_sorted)))
    
    bars = ax1.barh(range(len(companies_sorted)), companies_sorted['Equity Taken (%)'], color=colors)
    ax1.set_yticks(range(len(companies_sorted)))
    ax1.set_yticklabels(companies_sorted['CompanyName'], fontsize=10)
    ax1.set_xlabel('Equity Taken (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Equity Taken in First Deal (with Pre/Post-Money Valuations)', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.axvline(avg_equity, color='red', linestyle='--', linewidth=2, label=f'Average: {avg_equity:.2f}%')
    ax1.legend(fontsize=10)
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, companies_sorted['Equity Taken (%)'])):
        ax1.text(value + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{value:.2f}%', 
                va='center', fontsize=9)
    
    # Plot 2: Summary statistics
    ax2.axis('off')
    
    summary_text = f"""
    SUMMARY STATISTICS
    {'='*60}
    
    Number of Companies with Data: {len(result_df)}
    Companies Analyzed: {', '.join(result_df['CompanyName'].tolist())}
    
    Equity Taken Statistics:
    • Average: {avg_equity:.2f}%
    • Median: {median_equity:.2f}%
    • Minimum: {result_df['Equity Taken (%)'].min():.2f}% ({result_df.loc[result_df['Equity Taken (%)'].idxmin(), 'CompanyName']})
    • Maximum: {result_df['Equity Taken (%)'].max():.2f}% ({result_df.loc[result_df['Equity Taken (%)'].idxmax(), 'CompanyName']})
    • Std Dev: {result_df['Equity Taken (%)'].std():.2f}%
    
    Note: Equity taken is calculated as (Post-Money - Pre-Money) / Post-Money × 100
    Only companies with both pre-money and post-money valuations in their first deal are included.
    """
    
    ax2.text(0.1, 0.9, summary_text, fontsize=11, verticalalignment='top', 
             family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig('/Users/yufei/SchoolWork/fin/stata/analysis_entry_trends/first_deal_equity_analysis.png', 
                dpi=300, bbox_inches='tight')
    print("Visualization saved to: analysis_entry_trends/first_deal_equity_analysis.png")
    plt.close()
    
    # Create a detailed report
    report = f"""# First Deal Equity Analysis

## Overview
This analysis examines the equity taken in the first financing deal for wearable technology companies that have both pre-money and post-money valuation data available.

## Methodology
- **Equity Calculation**: (Post-Money Valuation - Pre-Money Valuation) / Post-Money Valuation × 100
- **Data Source**: First deal for each company with both pre-money and post-money valuations
- **Companies Analyzed**: {len(result_df)} out of {len(company_list)} companies in the list

## Results

### Companies Included
{', '.join(result_df['CompanyName'].tolist())}

### Equity Taken by Company

| Company | Deal Date | Pre-Money (USD) | Post-Money (USD) | Deal Amount (USD) | Equity Taken (%) |
|---------|-----------|-----------------|------------------|-------------------|------------------|
"""
    
    for _, row in result_df.iterrows():
        deal_date = row['DealDate'].strftime('%Y-%m-%d') if pd.notna(row['DealDate']) else 'N/A'
        premoney = f"${row[premoney_col]:,.0f}" if pd.notna(row[premoney_col]) else 'N/A'
        postmoney = f"${row[postmoney_col]:,.0f}" if pd.notna(row[postmoney_col]) else 'N/A'
        deal_amount = f"${row['DealSize']:,.0f}" if pd.notna(row['DealSize']) else 'N/A'
        equity = f"{row['Equity Taken (%)']:.2f}%" if pd.notna(row['Equity Taken (%)']) else 'N/A'
        report += f"| {row['CompanyName']} | {deal_date} | {premoney} | {postmoney} | {deal_amount} | {equity} |\n"
    
    report += f"""
### Summary Statistics

- **Average Equity Taken**: {avg_equity:.2f}%
- **Median Equity Taken**: {median_equity:.2f}%
- **Minimum Equity Taken**: {result_df['Equity Taken (%)'].min():.2f}% ({result_df.loc[result_df['Equity Taken (%)'].idxmin(), 'CompanyName']})
- **Maximum Equity Taken**: {result_df['Equity Taken (%)'].max():.2f}% ({result_df.loc[result_df['Equity Taken (%)'].idxmax(), 'CompanyName']})
- **Standard Deviation**: {result_df['Equity Taken (%)'].std():.2f}%

## Key Findings

1. **Average Dilution**: On average, companies gave up {avg_equity:.2f}% equity in their first financing round with documented pre/post-money valuations.

2. **Range of Dilution**: Equity taken ranged from {result_df['Equity Taken (%)'].min():.2f}% to {result_df['Equity Taken (%)'].max():.2f}%, showing significant variation in first-round dilution.

3. **Data Availability**: Only {len(result_df)} out of {len(company_list)} companies had complete pre-money and post-money valuation data for their first deal.

## Notes

- Companies without both pre-money and post-money valuations in their first deal are excluded from this analysis
- The equity percentage represents the ownership stake given to investors in exchange for funding
- This analysis focuses on the first deal only, not subsequent financing rounds
"""
    
    with open('/Users/yufei/SchoolWork/fin/stata/analysis_entry_trends/FIRST_DEAL_EQUITY_REPORT.md', 'w') as f:
        f.write(report)
    
    print("\nReport saved to: analysis_entry_trends/FIRST_DEAL_EQUITY_REPORT.md")
    
else:
    print("\nError: Could not find pre-money and post-money valuation columns in the dataset")
    print("Available columns:", deal_df.columns.tolist())

