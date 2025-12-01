#!/usr/bin/env python3
"""
Script to regenerate APPENDIX file for Playermaker with real data
"""

import json
from datetime import datetime
from dateutil import parser

COMPANY_ID = "142343-92"
COMPANY_NAME = "Playermaker"

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

def generate_appendix():
    """Generate APPENDIX file"""
    print(f"Generating APPENDIX file for {COMPANY_NAME}...")
    
    # Load company data
    with open('data/companies_detail.json', 'r') as f:
        companies = json.load(f)
    company_data = companies.get(COMPANY_ID)
    
    if not company_data:
        print("❌ Company data not found!")
        return
    
    # Load deals data
    with open('data/deals_by_company.json', 'r') as f:
        deals_by_company = json.load(f)
    deals_data = deals_by_company.get(COMPANY_ID, [])
    
    # Filter completed deals and sort by date
    completed_deals = [d for d in deals_data if d.get('DealStatus') == 'Completed']
    completed_deals.sort(key=lambda x: parse_date(x.get('DealDate')) or datetime.min)
    
    # Calculate metrics
    founded_year_str = company_data.get('YearFounded', '')
    try:
        founded_year = int(founded_year_str) if founded_year_str else None
    except:
        founded_year = None
    
    current_year = 2024  # As per the format
    company_age = current_year - founded_year if founded_year else None
    
    first_deal = completed_deals[0] if completed_deals else None
    first_deal_date = parse_date(first_deal.get('DealDate')) if first_deal else None
    
    # Calculate time to first financing
    time_to_financing = None
    if first_deal_date and founded_year:
        time_to_financing = (first_deal_date.year - founded_year) + (first_deal_date - datetime(first_deal_date.year, 1, 1)).days / 365.25
    
    # Calculate total raised
    total_raised = 0
    for deal in completed_deals:
        deal_size = parse_float(deal.get('DealSize'))
        if deal_size:
            total_raised += deal_size
    
    # Get first and last valuations
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
    
    # Generate APPENDIX content
    lines = [
        f"# Appendix 8: {COMPANY_NAME}",
        "",
        f"**Company ID**: {COMPANY_ID}",
        "**Visualization**:",
        "",
        f"![Timeline Chart](../visualizations/{COMPANY_ID}_{COMPANY_NAME}_timeline.png)",
        "",
        "---",
        "",
        "## A8.1 Company Overview",
        "",
        "| Attribute | Value |",
        "|-----------|-------|",
        f"| **Company Name** | {COMPANY_NAME} |",
        f"| **Year Founded** | {founded_year or 'N/A'} |",
        f"| **Current Age** | {company_age} years (as of {current_year})" if company_age else "| **Current Age** | N/A |",
        f"| **Industry** | {company_data.get('PrimaryIndustryGroup', 'N/A')} |",
        f"| **Headquarters** | {company_data.get('HQLocation', 'N/A')} |",
        f"| **Website** | {company_data.get('Website', 'N/A')} |",
        f"| **Employees** | {company_data.get('Employees', 'N/A')} (as of {company_data.get('EmployeeAsOfDate', 'N/A')}) |",
        "",
        f"**Description**: {company_data.get('Description', 'N/A')}",
        "",
        "---",
        "",
        "## A8.2 Financing Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| **First Financing Date** | {first_deal_date.strftime('%m/%d/%Y') if first_deal_date else 'N/A'} |",
        f"| **Time to First Financing** | {time_to_financing:.1f} years" if time_to_financing else "| **Time to First Financing** | N/A |",
        f"| **First Deal Type** | {first_deal.get('DealType', 'N/A') if first_deal else 'N/A'} |",
        f"| **First Deal Size** | ${parse_float(first_deal.get('DealSize')):.2f}M" if first_deal and parse_float(first_deal.get('DealSize')) else "| **First Deal Size** | N/A |",
        f"| **Total Capital Raised** | ${total_raised:.2f}M" if total_raised > 0 else "| **Total Capital Raised** | N/A |",
        f"| **Number of Rounds** | {len(completed_deals)} |",
        f"| **Current Status** | {company_data.get('CompanyFinancingStatus', 'N/A')} |",
        f"| **Business Status** | {company_data.get('BusinessStatus', 'N/A')} |",
        "",
        "---",
        "",
        "## A8.3 Financing History",
        "",
        "| Round | Date | Deal Type | Deal Class | Amount | Pre-Money | Post-Money |",
        "|-------|------|-----------|------------|---------|-----------|------------|",
    ]
    
    for idx, deal in enumerate(completed_deals, 1):
        deal_date = parse_date(deal.get('DealDate'))
        date_str = deal_date.strftime('%m/%d/%Y') if deal_date else 'N/A'
        deal_size = parse_float(deal.get('DealSize'))
        deal_size_str = f"${deal_size:.2f}M" if deal_size else "N/A"
        pre_val = parse_float(deal.get('PremoneyValuation'))
        pre_val_str = f"${pre_val:.2f}M" if pre_val else "N/A"
        post_val = parse_float(deal.get('PostValuation'))
        post_val_str = f"${post_val:.2f}M" if post_val else "N/A"
        
        lines.append(
            f"| {idx} | {date_str} | {deal.get('DealType', 'N/A')} | {deal.get('DealClass', 'N/A')} | {deal_size_str} | {pre_val_str} | {post_val_str} |"
        )
    
    lines.extend([
        "",
        "---",
        "",
        "## A8.4 Valuation",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| **First Valuation** | ${first_val:.2f}M" if first_val else "| **First Valuation** | N/A |",
        f"| **Last Known Valuation** | ${last_val:.2f}M" if last_val else "| **Last Known Valuation** | N/A |",
        f"| **Last Valuation Date** | {last_val_date.strftime('%m/%d/%Y') if last_val_date else 'N/A'} |",
        "",
        "---",
        "",
        "## A8.5 Exit Events",
        "",
        "| Attribute | Value |",
        "|-----------|-------|",
    ])
    
    ownership_status = company_data.get('OwnershipStatus', '')
    has_exit = 'Publicly Held' in ownership_status or 'Acquired' in ownership_status
    
    if has_exit:
        lines.extend([
            f"| **Exit Event** | Yes ({'IPO' if 'Publicly Held' in ownership_status else 'Acquisition'}) |",
            f"| **Exit Details** | {company_data.get('Exchange', 'N/A')} {company_data.get('Ticker', '')} |",
            f"| **Ownership Status** | {ownership_status} |",
        ])
    else:
        lines.extend([
            "| **Exit Event** | No |",
            "| **Exit Details** |  |",
            f"| **Ownership Status** | {ownership_status} |",
        ])
    
    lines.extend([
        "",
        "---",
        "",
        "## A8.6 Investment & Acquisition Activity",
        "",
        "| Attribute | Value |",
        "|-----------|-------|",
        "| **Active as Investor/Acquirer** | No |",
        "",
        "",
        "---",
        "",
        "## A8.7 Key Investors",
        "",
        "| Investors (by round) |",
        "|---------------------|",
    ])
    
    # Add investor placeholders
    for idx in range(len(completed_deals)):
        lines.append(f"| {idx + 1} |")
    
    lines.extend([
        "",
        "",
        f"*Data extracted: {datetime.now().strftime('%B %d, %Y')}*",
    ])
    
    # Save APPENDIX file
    content = '\n'.join(lines)
    output_path = f'reports/APPENDIX_08_{COMPANY_NAME}.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Saved APPENDIX to {output_path}")

if __name__ == "__main__":
    generate_appendix()

