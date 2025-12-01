#!/usr/bin/env python3
"""
Create a table of latest valuations for companies in list.txt
"""

import pandas as pd
import os

# Paths
BASE_DIR = '/Users/yufei/SchoolWork/fin/stata'
ANALYSIS_DIR = os.path.join(BASE_DIR, 'analysis_valuation_trends')
DATA_DIR = os.path.join(ANALYSIS_DIR, 'data')

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

print(f"Found {len(companies)} companies")

# Load valuation summary data
valuation_file = os.path.join(DATA_DIR, 'valuation_summary_by_company.csv')
if os.path.exists(valuation_file):
    valuation_df = pd.read_csv(valuation_file)
    print(f"\nLoaded valuation data for {len(valuation_df)} companies")
else:
    print("\nWarning: valuation_summary_by_company.csv not found!")
    valuation_df = pd.DataFrame()

# Create a mapping from CompanyID to LatestValuation and LatestValuationDate
valuation_map = {}
if not valuation_df.empty:
    for _, row in valuation_df.iterrows():
        valuation_map[row['CompanyID']] = {
            'LatestValuation': row['LatestValuation'],
            'LatestValuationDate': row['LatestValuationDate']
        }

# Build the table
table_data = []
for comp in companies:
    comp_id = comp['id']
    comp_name = comp['name']
    
    if comp_id in valuation_map:
        latest_val = valuation_map[comp_id]['LatestValuation']
        latest_date = valuation_map[comp_id]['LatestValuationDate']
        # Format valuation with proper units (B for billions, M for millions)
        if pd.notna(latest_val) and latest_val > 0:
            if latest_val >= 1000:  # >= $1B
                valuation_formatted = f"${latest_val/1000:.2f}B"
            else:
                valuation_formatted = f"${latest_val:.2f}M"
        else:
            valuation_formatted = "N/A"
            latest_date = "N/A"
    else:
        valuation_formatted = "N/A"
        latest_date = "N/A"
    
    table_data.append({
        'Company Name': comp_name,
        'Company ID': comp_id,
        'Latest Valuation': valuation_formatted,
        'Latest Valuation Date': latest_date
    })

# Create DataFrame
table_df = pd.DataFrame(table_data)

# Sort by valuation (companies with valuations first, then by value descending)
def sort_key(row):
    val_str = row['Latest Valuation']
    if val_str == "N/A":
        return (1, 0)  # Sort N/A to the end
    else:
        # Extract numeric value for sorting (handle both B and M)
        val_clean = val_str.replace('$', '').replace(',', '')
        if 'B' in val_clean:
            val_num = float(val_clean.replace('B', '')) * 1000  # Convert billions to millions
        elif 'M' in val_clean:
            val_num = float(val_clean.replace('M', ''))
        else:
            val_num = 0
        return (0, -val_num)  # Negative for descending order

table_df['_sort_key'] = table_df.apply(sort_key, axis=1)
table_df = table_df.sort_values('_sort_key').drop('_sort_key', axis=1)

# Save to CSV
output_file = os.path.join(DATA_DIR, 'latest_valuation_table.csv')
table_df.to_csv(output_file, index=False)
print(f"\nSaved table to: {output_file}")

# Print the table
print("\n" + "="*80)
print("LATEST VALUATION TABLE")
print("="*80)
print(table_df.to_string(index=False))
print("="*80)

# Also print summary statistics
companies_with_val = table_df[table_df['Latest Valuation'] != 'N/A']
print(f"\nSummary:")
print(f"  Total companies: {len(table_df)}")
print(f"  Companies with disclosed valuations: {len(companies_with_val)}")
print(f"  Companies without disclosed valuations: {len(table_df) - len(companies_with_val)}")

