#!/usr/bin/env python3
"""
Add the sum of all valuations to list.txt
"""

import pandas as pd
import os

# Paths
BASE_DIR = '/Users/yufei/SchoolWork/fin/stata'
ANALYSIS_DIR = os.path.join(BASE_DIR, 'analysis_valuation_trends')
DATA_DIR = os.path.join(ANALYSIS_DIR, 'data')
LIST_FILE = os.path.join(BASE_DIR, 'list.txt')

print("Loading valuation data...")
# Load valuation summary data
valuation_file = os.path.join(DATA_DIR, 'valuation_summary_by_company.csv')
if not os.path.exists(valuation_file):
    print(f"Error: {valuation_file} not found!")
    exit(1)

valuation_df = pd.read_csv(valuation_file)
print(f"Loaded valuation data for {len(valuation_df)} companies")

# Calculate sum of all latest valuations (in millions USD)
# Filter out any NaN or invalid values
valid_valuations = valuation_df['LatestValuation'].dropna()
total_valuation_millions = valid_valuations.sum()

print(f"\nTotal valuation sum: ${total_valuation_millions:,.2f}M")
print(f"Total valuation sum: ${total_valuation_millions/1000:,.2f}B")

# Format the sum nicely
if total_valuation_millions >= 1000:
    valuation_sum_formatted = f"${total_valuation_millions/1000:.2f}B"
else:
    valuation_sum_formatted = f"${total_valuation_millions:.2f}M"

print(f"\nFormatted sum: {valuation_sum_formatted}")

# Read current list.txt
print(f"\nReading {LIST_FILE}...")
with open(LIST_FILE, 'r') as f:
    lines = f.readlines()

# Check if sum already exists in the file
sum_line = f"Total Valuation Sum: {valuation_sum_formatted}\n"
has_sum = any("Total Valuation Sum:" in line for line in lines)

if has_sum:
    print("Found existing valuation sum in list.txt, updating...")
    # Update existing sum line
    updated_lines = []
    for line in lines:
        if "Total Valuation Sum:" in line:
            updated_lines.append(sum_line)
        else:
            updated_lines.append(line)
    lines = updated_lines
else:
    print("Adding valuation sum to list.txt...")
    # Add sum at the end
    lines.append("\n")
    lines.append(sum_line)

# Write back to list.txt
with open(LIST_FILE, 'w') as f:
    f.writelines(lines)

print(f"\n✓ Successfully updated {LIST_FILE}")
print(f"  Added/Updated: {sum_line.strip()}")

