#!/usr/bin/env python3
"""
Analyze investor types for individual startups
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

def parse_company_ids(list_file):
    """Parse company IDs from list.txt"""
    company_data = []
    with open(list_file, 'r') as f:
        lines = f.readlines()
    
    # Parse pairs of lines (company name, company ID)
    for i in range(0, len(lines)-1, 2):
        name = lines[i].strip()
        company_id = lines[i+1].strip().strip('"')
        if name and company_id:
            company_data.append({'name': name, 'id': company_id})
    
    return company_data[:10]  # Return first 10 companies

def load_investor_data(chunk_size=50000):
    """Load investor data to get investor types"""
    print("Loading investor data...")
    investor_df = pd.read_csv('Investor.csv', 
                               usecols=['InvestorID', 'InvestorName', 'PrimaryInvestorType'],
                               chunksize=chunk_size, 
                               low_memory=False)
    
    # Combine all chunks
    investor_data = pd.concat(investor_df, ignore_index=True)
    print(f"Loaded {len(investor_data)} investors")
    
    return investor_data

def load_deals_for_companies(company_ids, chunk_size=50000):
    """Load deal data for specified companies"""
    print("Loading deal data...")
    company_ids_set = set(company_ids)
    
    deal_df = None
    for chunk in pd.read_csv('Deal.csv', 
                             usecols=['CompanyID', 'CompanyName', 'DealID', 'DealDate', 
                                     'DealType', 'DealSize', 'Investors'],
                             chunksize=chunk_size, 
                             low_memory=False):
        chunk_filtered = chunk[chunk['CompanyID'].isin(company_ids_set)]
        if deal_df is None:
            deal_df = chunk_filtered
        else:
            deal_df = pd.concat([deal_df, chunk_filtered])
    
    print(f"Found {len(deal_df)} deals")
    return deal_df

def extract_investor_ids_from_deals(deal_df):
    """Extract investor IDs from the Investors column in deals"""
    print("Extracting investor IDs from deals...")
    
    # Parse the Investors column which may contain comma-separated investor IDs
    investor_company_links = []
    
    for idx, row in deal_df.iterrows():
        if pd.notna(row['Investors']):
            # Split by common separators (comma, semicolon, pipe)
            investor_str = str(row['Investors'])
            # Try different separators
            for sep in [',', ';', '|']:
                if sep in investor_str:
                    investor_ids = [inv.strip() for inv in investor_str.split(sep)]
                    break
            else:
                investor_ids = [investor_str.strip()]
            
            for inv_id in investor_ids:
                if inv_id:  # Skip empty strings
                    investor_company_links.append({
                        'CompanyID': row['CompanyID'],
                        'CompanyName': row['CompanyName'],
                        'InvestorID': inv_id,
                        'DealDate': row['DealDate'],
                        'DealType': row['DealType']
                    })
    
    links_df = pd.DataFrame(investor_company_links)
    print(f"Found {len(links_df)} company-investor links")
    
    return links_df

def analyze_investor_types_per_company(links_df, investor_df):
    """Analyze what types of investors each company has"""
    print("Analyzing investor types per company...")
    
    # Merge with investor data to get investor types
    merged = links_df.merge(investor_df, on='InvestorID', how='left')
    
    # For each company, count investor types
    company_investor_types = merged.groupby(['CompanyID', 'CompanyName', 'PrimaryInvestorType']).size().reset_index(name='Count')
    
    # Pivot to create a matrix: companies x investor types
    pivot_table = company_investor_types.pivot_table(
        index=['CompanyID', 'CompanyName'],
        columns='PrimaryInvestorType',
        values='Count',
        fill_value=0
    ).reset_index()
    
    # Calculate totals
    investor_type_cols = [col for col in pivot_table.columns if col not in ['CompanyID', 'CompanyName']]
    pivot_table['Total_Investors'] = pivot_table[investor_type_cols].sum(axis=1)
    
    return company_investor_types, pivot_table, merged

def create_visualizations(company_investor_types, pivot_table, merged_data):
    """Create comprehensive visualizations"""
    
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)
    
    # Chart 1: Stacked bar chart - Investor types by company
    ax1 = fig.add_subplot(gs[0, :])
    
    if not pivot_table.empty:
        investor_type_cols = [col for col in pivot_table.columns 
                             if col not in ['CompanyID', 'CompanyName', 'Total_Investors']]
        investor_type_cols = [col for col in investor_type_cols if pivot_table[col].sum() > 0]
        
        # Create stacked bar chart
        plot_data = pivot_table.set_index('CompanyName')[investor_type_cols]
        plot_data.plot(kind='barh', stacked=True, ax=ax1, 
                      colormap='tab20', edgecolor='black', linewidth=0.5)
        
        ax1.set_xlabel('Number of Investors', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Company', fontsize=12, fontweight='bold')
        ax1.set_title('Investor Types by Company (Stacked)', fontsize=14, fontweight='bold')
        ax1.legend(title='Investor Type', bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
        ax1.grid(True, alpha=0.3, axis='x')
    
    # Chart 2: Distribution of investor types across all companies
    ax2 = fig.add_subplot(gs[1, 0])
    
    if not company_investor_types.empty and 'PrimaryInvestorType' in company_investor_types.columns:
        investor_type_totals = company_investor_types.groupby('PrimaryInvestorType')['Count'].sum().sort_values(ascending=True)
        
        colors = sns.color_palette("husl", len(investor_type_totals))
        bars = ax2.barh(range(len(investor_type_totals)), investor_type_totals.values, color=colors)
        ax2.set_yticks(range(len(investor_type_totals)))
        ax2.set_yticklabels(investor_type_totals.index, fontsize=10)
        ax2.set_xlabel('Total Investment Count', fontsize=12, fontweight='bold')
        ax2.set_title('Overall Distribution of Investor Types', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, investor_type_totals.values)):
            ax2.text(value, i, f' {int(value)}', va='center', fontsize=9, fontweight='bold')
    
    # Chart 3: Pie chart of investor type distribution
    ax3 = fig.add_subplot(gs[1, 1])
    
    if not company_investor_types.empty and 'PrimaryInvestorType' in company_investor_types.columns:
        investor_type_totals = company_investor_types.groupby('PrimaryInvestorType')['Count'].sum()
        
        colors = sns.color_palette("Set3", len(investor_type_totals))
        wedges, texts, autotexts = ax3.pie(investor_type_totals.values, 
                                            labels=investor_type_totals.index,
                                            autopct='%1.1f%%',
                                            colors=colors,
                                            startangle=90)
        
        for text in texts:
            text.set_fontsize(9)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax3.set_title('Investor Type Distribution (%)', fontsize=14, fontweight='bold')
    
    # Chart 4: Detailed table showing each company's investor breakdown
    ax4 = fig.add_subplot(gs[2, :])
    ax4.axis('tight')
    ax4.axis('off')
    
    if not pivot_table.empty:
        # Prepare table data
        table_data = []
        investor_type_cols = [col for col in pivot_table.columns 
                             if col not in ['CompanyID', 'CompanyName', 'Total_Investors']]
        investor_type_cols = [col for col in investor_type_cols if pivot_table[col].sum() > 0]
        
        # Add header
        header = ['Company'] + investor_type_cols + ['Total']
        table_data.append(header)
        
        # Add data rows
        for idx, row in pivot_table.iterrows():
            row_data = [row['CompanyName'][:30]]  # Truncate long names
            for col in investor_type_cols:
                val = int(row[col]) if row[col] > 0 else ''
                row_data.append(str(val) if val else '-')
            row_data.append(str(int(row['Total_Investors'])))
            table_data.append(row_data)
        
        # Create table
        table = ax4.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.25] + [0.1] * len(investor_type_cols) + [0.08])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2)
        
        # Style header row
        for i in range(len(header)):
            table[(0, i)].set_facecolor('#2E86AB')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Alternate row colors
        for i in range(1, len(table_data)):
            for j in range(len(header)):
                table[(i, j)].set_facecolor(['#f1f1f2', 'white'][i % 2])
        
        ax4.set_title('Detailed Investor Type Breakdown by Company', 
                     fontsize=14, fontweight='bold', pad=20)
    
    plt.savefig('investor_types_analysis.png', dpi=300, bbox_inches='tight')
    print("\nChart saved as 'investor_types_analysis.png'")
    plt.close()

def print_summary(company_investor_types, pivot_table, company_data):
    """Print detailed summary"""
    print("\n" + "="*80)
    print("INVESTOR TYPES IN INDIVIDUAL STARTUPS - ANALYSIS SUMMARY")
    print("="*80)
    
    print(f"\nCompanies analyzed: {len(company_data)}")
    for i, company in enumerate(company_data, 1):
        print(f"  {i}. {company['name']} (ID: {company['id']})")
    
    print("\n" + "-"*80)
    print("INVESTOR TYPE BREAKDOWN BY COMPANY")
    print("-"*80)
    
    if not pivot_table.empty:
        for idx, row in pivot_table.iterrows():
            print(f"\n{row['CompanyName']}:")
            investor_type_cols = [col for col in pivot_table.columns 
                                 if col not in ['CompanyID', 'CompanyName', 'Total_Investors']]
            
            for col in investor_type_cols:
                if row[col] > 0:
                    print(f"  - {col}: {int(row[col])}")
            print(f"  Total Investors: {int(row['Total_Investors'])}")
    
    print("\n" + "-"*80)
    print("OVERALL INVESTOR TYPE DISTRIBUTION")
    print("-"*80)
    
    if not company_investor_types.empty and 'PrimaryInvestorType' in company_investor_types.columns:
        investor_type_totals = company_investor_types.groupby('PrimaryInvestorType')['Count'].sum().sort_values(ascending=False)
        total = investor_type_totals.sum()
        
        for inv_type, count in investor_type_totals.items():
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {inv_type}: {int(count)} ({pct:.1f}%)")
    
    print("\n" + "="*80)

def main():
    # Parse company IDs
    print("Parsing company IDs from list.txt...")
    company_data = parse_company_ids('list.txt')
    company_ids = [c['id'] for c in company_data]
    
    print(f"\nAnalyzing investor types for {len(company_data)} companies:")
    for i, company in enumerate(company_data, 1):
        print(f"  {i}. {company['name']} (ID: {company['id']})")
    
    # Load data
    investor_df = load_investor_data()
    deal_df = load_deals_for_companies(company_ids)
    
    # Extract investor-company links
    links_df = extract_investor_ids_from_deals(deal_df)
    
    # Analyze investor types
    company_investor_types, pivot_table, merged_data = analyze_investor_types_per_company(links_df, investor_df)
    
    # Create visualizations
    print("\nCreating visualizations...")
    create_visualizations(company_investor_types, pivot_table, merged_data)
    
    # Print summary
    print_summary(company_investor_types, pivot_table, company_data)
    
    # Save detailed results to CSV
    if not pivot_table.empty:
        pivot_table.to_csv('investor_types_by_company.csv', index=False)
        print("\nDetailed results saved to 'investor_types_by_company.csv'")
    
    if not company_investor_types.empty:
        company_investor_types.to_csv('company_investor_type_details.csv', index=False)
        print("Detailed investor type records saved to 'company_investor_type_details.csv'")

if __name__ == "__main__":
    main()




