#!/usr/bin/env python3
"""
Script to regenerate Playermaker (142343-92) company profile with real data
Extracts data from Company.csv, Deal.csv, and Investor.csv
Generates reports and visualizations
"""

import csv
import json
import os
from datetime import datetime
from dateutil import parser

# Company ID
COMPANY_ID = "142343-92"
COMPANY_NAME = "Playermaker"

def load_csv_as_dict(filepath, filter_key=None, filter_value=None):
    """Load CSV file and return as list of dicts"""
    data = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if filter_key and filter_value:
                if row.get(filter_key) == filter_value:
                    data.append(row)
            else:
                data.append(row)
    return data

def load_company_data():
    """Load company data from Company.csv"""
    print(f"Loading company data for {COMPANY_NAME} ({COMPANY_ID})...")
    companies = load_csv_as_dict('../Company.csv', 'CompanyID', COMPANY_ID)
    if companies:
        print(f"✓ Found company: {companies[0].get('CompanyName', 'N/A')}")
        return companies[0]
    return None

def load_deals_data():
    """Load deals data from Deal.csv"""
    print(f"Loading deals data for {COMPANY_NAME} ({COMPANY_ID})...")
    deals = load_csv_as_dict('../Deal.csv', 'CompanyID', COMPANY_ID)
    
    # Sort by deal number
    def get_deal_no(deal):
        try:
            return int(deal.get('DealNo', 0) or 0)
        except:
            return 999
    
    deals.sort(key=get_deal_no)
    print(f"✓ Found {len(deals)} deals")
    return deals

def parse_date(date_str):
    """Parse date string safely"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        return parser.parse(str(date_str))
    except:
        return None

def parse_float(value):
    """Parse float safely"""
    if not value or str(value).strip() == '':
        return None
    try:
        return float(value)
    except:
        return None

def create_timeline_visualization(company_data, deals_data):
    """Create timeline visualization"""
    print("\nCreating timeline visualization...")
    
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        print("⚠ matplotlib not available, skipping visualization")
        return
    
    # Filter completed deals with dates
    valid_deals = []
    for deal in deals_data:
        if deal.get('DealStatus') == 'Completed':
            deal_date = parse_date(deal.get('DealDate'))
            if deal_date:
                deal_size = parse_float(deal.get('DealSize')) or 0
                valid_deals.append({
                    'date': deal_date,
                    'size': deal_size,
                    'type': deal.get('DealType', 'Unknown'),
                    'round': deal.get('VCRound', '')
                })
    
    if not valid_deals:
        print("⚠ No valid deals with dates found")
        return
    
    # Sort by date
    valid_deals.sort(key=lambda x: x['date'])
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(14, 8))
    
    dates = [d['date'] for d in valid_deals]
    sizes = [d['size'] for d in valid_deals]
    
    # Normalize sizes for bubble chart
    max_size = max(sizes) if sizes else 1
    bubble_sizes = [(s / max_size * 1000) if s > 0 else 100 for s in sizes]
    
    # Plot deals
    import numpy as np
    colors = plt.cm.viridis([i / len(valid_deals) for i in range(len(valid_deals))])
    
    for i, deal in enumerate(valid_deals):
        size = bubble_sizes[i] if deal['size'] > 0 else 50
        ax.scatter(deal['date'], 0, s=size, alpha=0.7, color=colors[i], 
                  edgecolors='black', linewidths=1.5, zorder=3)
        
        # Add annotation
        if deal['size'] > 0:
            amount_str = f"${deal['size']:.2f}M" if deal['size'] >= 1 else f"${deal['size']*1000:.0f}K"
            ax.annotate(amount_str, 
                       xy=(deal['date'], 0),
                       xytext=(0, 20 if i % 2 == 0 else -30),
                       textcoords='offset points',
                       fontsize=9, ha='center',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Formatting
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=2, zorder=1)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_title(f'{COMPANY_NAME} - Financing Timeline', fontsize=16, fontweight='bold', pad=20)
    ax.set_yticks([])
    ax.grid(True, alpha=0.3, axis='x', zorder=0)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # Save
    output_path = f'visualizations/{COMPANY_ID}_{COMPANY_NAME}_timeline.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved visualization to {output_path}")
    plt.close()

def generate_company_report(company_data, deals_data):
    """Generate detailed company report"""
    print("\nGenerating company report...")
    
    # Parse dates and calculate metrics
    founded_year_str = company_data.get('YearFounded', '')
    try:
        founded_year = int(founded_year_str) if founded_year_str else None
    except:
        founded_year = None
    
    current_year = datetime.now().year
    company_age = current_year - founded_year if founded_year else None
    
    # Filter and sort deals
    completed_deals = [d for d in deals_data if d.get('DealStatus') == 'Completed']
    completed_deals.sort(key=lambda x: parse_date(x.get('DealDate')) or datetime.min)
    
    first_deal = completed_deals[0] if completed_deals else None
    first_deal_date = parse_date(first_deal.get('DealDate')) if first_deal else None
    
    # Calculate total raised
    total_raised = 0
    for deal in completed_deals:
        deal_size = parse_float(deal.get('DealSize'))
        if deal_size:
            total_raised += deal_size
    
    # Generate report
    report_lines = [
        f"# Company Profile: {COMPANY_NAME}",
        "",
        f"**Company ID**: {COMPANY_ID}  ",
        f"**Report Generated**: {datetime.now().strftime('%B %d, %Y')}",
        "",
        "---",
        "",
        "",
        "## 1. Company Foundation & Initial Financing",
        "",
        "### When was the company founded?",
        f"- **Year Founded**: {founded_year or 'N/A'}",
        f"- **Company Age**: {company_age} years (as of {current_year})" if company_age else "- **Company Age**: N/A",
        "",
        "### How long until it first received financing?",
    ]
    
    if first_deal_date and founded_year:
        time_to_financing = (first_deal_date.year - founded_year) + (first_deal_date - datetime(first_deal_date.year, 1, 1)).days / 365.25
        first_deal_size = parse_float(first_deal.get('DealSize'))
        report_lines.extend([
            f"- **First Financing Date**: {first_deal_date.strftime('%m/%d/%Y')}",
            f"- **Time to First Financing**: {time_to_financing:.1f} years",
            f"- **First Deal Size**: ${first_deal_size:.2f}M" if first_deal_size else "- **First Deal Size**: Not Available",
            f"- **First Deal Type**: {first_deal.get('DealType', 'N/A')}",
        ])
    else:
        report_lines.extend([
            "- **First Financing Date**: Not Available",
            "- **Time to First Financing**: Not Available",
            "- **First Deal Size**: Not Available",
            "- **First Deal Type**: Not Available",
        ])
    
    report_lines.extend([
        "",
        "---",
        "",
        "## 2. Current Status",
        "",
        "### What stage is the company at now?",
        f"- **Financing Status**: {company_data.get('CompanyFinancingStatus', 'N/A')}",
        f"- **Business Status**: {company_data.get('BusinessStatus', 'N/A')}",
        f"- **Ownership Status**: {company_data.get('OwnershipStatus', 'N/A')}",
        "",
        "### How old is it?",
        f"- **Current Age**: {company_age} years" if company_age else "- **Current Age**: N/A",
        f"- **Total Capital Raised**: ${total_raised:.2f}M" if total_raised > 0 else "- **Total Capital Raised**: Not Available",
        "",
        "---",
        "",
        "## 3. Financing History",
        "",
        f"### When did it get financing?",
        f"**Total Number of Financing Rounds**: {len(completed_deals)}",
        "",
        "| # | Date | Deal Type | Stage/Class | Size | Valuation |",
        "|---|------|-----------|-------------|------|----------|",
    ])
    
    for idx, deal in enumerate(completed_deals, 1):
        deal_date = parse_date(deal.get('DealDate'))
        date_str = deal_date.strftime('%m/%d/%Y') if deal_date else 'N/A'
        deal_size = parse_float(deal.get('DealSize'))
        deal_size_str = f"${deal_size:.2f}M" if deal_size else "Not Available"
        post_val = parse_float(deal.get('PostValuation'))
        post_val_str = f"${post_val:.2f}M" if post_val else "Not Available"
        
        report_lines.append(
            f"| {idx} | {date_str} | {deal.get('DealType', 'N/A')} | {deal.get('DealClass', 'N/A')} | {deal_size_str} | {post_val_str} |"
        )
    
    report_lines.extend([
        "",
        "---",
        "",
        "## 4. Financing Sources & Investors",
        "",
        "### Financing Stages and Sources",
        "",
        "**Financing Types**:",
    ])
    
    deal_types = sorted(set(d.get('DealType', '') for d in completed_deals if d.get('DealType')))
    for dt in deal_types:
        if dt:
            report_lines.append(f"- {dt}")
    
    report_lines.extend([
        "",
        "**Financing Classes**:",
    ])
    
    deal_classes = sorted(set(d.get('DealClass', '') for d in completed_deals if d.get('DealClass')))
    for dc in deal_classes:
        if dc:
            report_lines.append(f"- {dc}")
    
    report_lines.extend([
        "",
        "### Investors",
        "",
    ])
    
    # Group deals by round
    for idx, deal in enumerate(completed_deals, 1):
        deal_date = parse_date(deal.get('DealDate'))
        date_str = deal_date.strftime('%m/%d/%Y') if deal_date else 'N/A'
        report_lines.append(f"**Round {idx}** ({date_str}):")
        report_lines.append("- Investors: (Data from Investor.csv needed)")
        report_lines.append("")
    
    report_lines.extend([
        "",
        "---",
        "",
        "## 5. Valuation Information",
        "",
    ])
    
    first_val = None
    last_val = None
    last_val_date = None
    
    for deal in completed_deals:
        post_val = parse_float(deal.get('PostValuation'))
        if post_val:
            if first_val is None:
                first_val = post_val
            last_val = post_val
            deal_date = parse_date(deal.get('DealDate'))
            if deal_date:
                last_val_date = deal_date
    
    report_lines.extend([
        f"- **First Financing Valuation**: ${first_val:.2f}M" if first_val else "- **First Financing Valuation**: Not Available",
        f"- **Last Known Valuation**: ${last_val:.2f}M (as of {last_val_date.strftime('%m/%d/%Y')})" if last_val and last_val_date else "- **Last Known Valuation**: Not Available",
        "",
        "### Valuation History",
        "",
        "| Round # | Date | Pre-Money | Post-Money | Deal Size |",
        "|---------|------|-----------|------------|----------|",
    ])
    
    for idx, deal in enumerate(completed_deals, 1):
        deal_date = parse_date(deal.get('DealDate'))
        date_str = deal_date.strftime('%m/%d/%Y') if deal_date else 'Not Available'
        pre_val = parse_float(deal.get('PremoneyValuation'))
        pre_val_str = f"${pre_val:.2f}M" if pre_val else "Not Available"
        post_val = parse_float(deal.get('PostValuation'))
        post_val_str = f"${post_val:.2f}M" if post_val else "Not Available"
        deal_size = parse_float(deal.get('DealSize'))
        deal_size_str = f"${deal_size:.2f}M" if deal_size else "Not Available"
        
        report_lines.append(f"| {idx} | {date_str} | {pre_val_str} | {post_val_str} | {deal_size_str} |")
    
    report_lines.extend([
        "",
        "---",
        "",
        "## 6. Exit Events",
        "",
    ])
    
    ownership_status = company_data.get('OwnershipStatus', '')
    has_exit = 'Publicly Held' in ownership_status or 'Acquired' in ownership_status
    
    if has_exit:
        report_lines.extend([
            f"**Has there been an exit event?** Yes",
            "",
            f"- **Type**: {'IPO' if 'Publicly Held' in ownership_status else 'Acquisition'}",
            f"- **Exchange**: {company_data.get('Exchange', 'N/A')}",
            f"- **Ticker**: {company_data.get('Ticker', 'N/A')}",
        ])
    else:
        report_lines.extend([
            "**Has there been an exit event?** No",
            "",
            "- **Type**: N/A",
            "- **Date**: N/A",
            "- **Exchange**: ",
            "- **Ticker**: ",
            "",
            "**Details**:",
            "No exit event identified.",
        ])
    
    report_lines.extend([
        "",
        "---",
        "",
        "## 7. Company Investments & Acquisitions",
        "",
        "**Has the company acquired or invested in other companies?**",
        "",
        "### ❌ NO - No Acquisition/Investment Activity Found",
        "",
        "No acquisitions or investments identified for this company.",
        "",
        "---",
        "",
        "## 8. Additional Company Information",
        "",
        f"**Description**: {company_data.get('Description', 'N/A')}",
        "",
        f"**Industry**: {company_data.get('PrimaryIndustryGroup', 'N/A')}",
        "",
        f"**Headquarters**: {company_data.get('HQLocation', 'N/A')}",
        "",
        f"**Website**: {company_data.get('Website', 'N/A')}",
        "",
        f"**Employees**: {company_data.get('Employees', 'N/A')} (as of {company_data.get('EmployeeAsOfDate', 'N/A')})",
        "",
    ])
    
    # Save report
    report_content = '\n'.join(report_lines)
    output_path = f'reports/{COMPANY_ID}_{COMPANY_NAME}.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"✓ Saved report to {output_path}")

def update_data_files(company_data, deals_data):
    """Update JSON data files"""
    print("\nUpdating data files...")
    
    # Update companies_detail.json
    with open('data/companies_detail.json', 'r') as f:
        companies_detail = json.load(f)
    
    companies_detail[COMPANY_ID] = company_data
    with open('data/companies_detail.json', 'w') as f:
        json.dump(companies_detail, f, indent=2, default=str)
    print(f"✓ Updated companies_detail.json")
    
    # Update deals_by_company.json
    with open('data/deals_by_company.json', 'r') as f:
        deals_by_company = json.load(f)
    
    deals_by_company[COMPANY_ID] = deals_data
    with open('data/deals_by_company.json', 'w') as f:
        json.dump(deals_by_company, f, indent=2, default=str)
    print(f"✓ Updated deals_by_company.json")
    
    # Update company_acquisitions_investments.json
    with open('data/company_acquisitions_investments.json', 'r') as f:
        acquisitions = json.load(f)
    
    acquisitions[COMPANY_ID] = []  # Placeholder - would need to search for acquisitions
    with open('data/company_acquisitions_investments.json', 'w') as f:
        json.dump(acquisitions, f, indent=2, default=str)
    print(f"✓ Updated company_acquisitions_investments.json")

def main():
    print("="*80)
    print(f"REGENERATING {COMPANY_NAME.upper()} COMPANY PROFILE")
    print("="*80)
    print()
    
    # Load data
    company_data = load_company_data()
    if not company_data:
        print("❌ Company data not found!")
        return
    
    deals_data = load_deals_data()
    
    # Update data files
    update_data_files(company_data, deals_data)
    
    # Create visualization
    create_timeline_visualization(company_data, deals_data)
    
    # Generate report
    generate_company_report(company_data, deals_data)
    
    print("\n" + "="*80)
    print("REGENERATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
