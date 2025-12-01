#!/usr/bin/env python3
"""Debug DealSize values"""

import pandas as pd
import numpy as np

company_ids = [
    "64325-80", "110783-26", "458417-44", "495718-39", "697387-24",
    "183205-63", "56236-96", "65652-22", "107433-19", "171678-43",
    "494786-80", "50982-94", "100191-79", "61931-08"
]

print("Loading deals...")
chunk_size = 100000
deals_list = []

for chunk in pd.read_csv('../Deal.csv', chunksize=chunk_size, low_memory=False):
    filtered = chunk[chunk['CompanyID'].isin(company_ids)]
    if len(filtered) > 0:
        deals_list.append(filtered)

deals = pd.concat(deals_list, ignore_index=True)

print(f"\nTotal deals: {len(deals)}")
print(f"\nDealSize column info:")
print(f"  Type: {deals['DealSize'].dtype}")
print(f"  Non-null count: {deals['DealSize'].notna().sum()}")
print(f"  Non-zero count: {(deals['DealSize'] > 0).sum()}")

print(f"\nSample DealSize values (first 20 non-null):")
sample = deals[deals['DealSize'].notna()]['DealSize'].head(20)
for idx, val in enumerate(sample, 1):
    print(f"  {idx}. {val} (type: {type(val).__name__})")

print(f"\nStatistics on DealSize:")
print(f"  Min: {deals['DealSize'].min()}")
print(f"  Max: {deals['DealSize'].max()}")
print(f"  Mean: {deals['DealSize'].mean()}")
print(f"  Median: {deals['DealSize'].median()}")
print(f"  Sum: {deals['DealSize'].sum()}")

print(f"\nChecking specific columns for funding amounts...")
print(f"\nAvailable columns containing 'deal' or 'size' or 'amount':")
relevant_cols = [col for col in deals.columns if any(word in col.lower() for word in ['deal', 'size', 'amount', 'valuation'])]
for col in relevant_cols:
    non_null = deals[col].notna().sum()
    if non_null > 0:
        print(f"  {col}: {non_null} non-null values")

# Check specific companies with known funding
print(f"\nChecking Peloton deals (known to have funding):")
peloton = deals[deals['CompanyID'] == '61931-08']
print(f"Total Peloton deals: {len(peloton)}")
print(f"\nPeloton DealSize values:")
for idx, row in peloton[['DealDate', 'DealType', 'VCRound', 'DealSize']].iterrows():
    print(f"  {row['DealDate']} | {row['DealType']} | {row['VCRound']} | DealSize: {row['DealSize']}")




