#!/usr/bin/env python3
"""
Industry Comparison Analysis: Wearable Tech vs Broader Market
- Compares wearable tech companies with the entire industry
- Only generates graphs when data is available
- Provides comparative trending and insights
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
import numpy as np
from datetime import datetime
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (20, 16)

def parse_company_ids(list_file):
    """Parse company IDs from list.txt"""
    company_data = []
    with open(list_file, 'r') as f:
        lines = f.readlines()
    
    for i in range(0, len(lines)-1, 2):
        name = lines[i].strip()
        company_id = lines[i+1].strip().strip('"')
        if name and company_id:
            company_data.append({'name': name, 'id': company_id})
    
    return company_data[:10]

def load_industry_sample(chunk_size=50000, sample_size=10000):
    """Load a sample of the entire industry for comparison"""
    print("Loading industry-wide data sample...")
    
    # Load Company data sample
    print("  - Sampling companies...")
    company_chunks = []
    total_companies = 0
    for chunk in pd.read_csv('Company.csv', 
                             usecols=['CompanyID', 'CompanyName', 'HQCountry', 
                                     'HQGlobalRegion', 'YearFounded', 'TotalRaised'],
                             chunksize=chunk_size, 
                             low_memory=False):
        if total_companies < sample_size:
            company_chunks.append(chunk.head(min(len(chunk), sample_size - total_companies)))
            total_companies += len(company_chunks[-1])
        else:
            break
    
    industry_companies = pd.concat(company_chunks, ignore_index=True) if company_chunks else pd.DataFrame()
    
    # Load Deal data for sampled companies
    print("  - Loading industry deals...")
    company_ids_set = set(industry_companies['CompanyID'].unique())
    
    deal_chunks = []
    for chunk in pd.read_csv('Deal.csv', 
                             usecols=['CompanyID', 'DealID', 'DealDate', 
                                     'DealType', 'DealSize', 'PostValuation'],
                             chunksize=chunk_size, 
                             low_memory=False):
        chunk_filtered = chunk[chunk['CompanyID'].isin(company_ids_set)]
        if not chunk_filtered.empty:
            deal_chunks.append(chunk_filtered)
        if len(deal_chunks) > 20:  # Limit to prevent memory issues
            break
    
    industry_deals = pd.concat(deal_chunks, ignore_index=True) if deal_chunks else pd.DataFrame()
    
    print(f"Loaded {len(industry_companies)} industry companies, {len(industry_deals)} deals")
    return industry_companies, industry_deals

def load_wearable_data(company_ids, chunk_size=50000):
    """Load data for wearable companies"""
    print("\nLoading wearable tech company data...")
    company_ids_set = set(company_ids)
    
    # Load Company data
    company_chunks = []
    for chunk in pd.read_csv('Company.csv', 
                             usecols=['CompanyID', 'CompanyName', 'HQCity', 'HQCountry', 
                                     'HQGlobalRegion', 'YearFounded', 'TotalRaised', 
                                     'BusinessStatus'],
                             chunksize=chunk_size, 
                             low_memory=False):
        chunk_filtered = chunk[chunk['CompanyID'].isin(company_ids_set)]
        if not chunk_filtered.empty:
            company_chunks.append(chunk_filtered)
    company_df = pd.concat(company_chunks, ignore_index=True) if company_chunks else pd.DataFrame()
    
    # Load Deal data
    deal_chunks = []
    for chunk in pd.read_csv('Deal.csv', 
                             usecols=['CompanyID', 'CompanyName', 'DealID', 'DealDate', 
                                     'DealType', 'DealSize', 'PostValuation'],
                             chunksize=chunk_size, 
                             low_memory=False):
        chunk_filtered = chunk[chunk['CompanyID'].isin(company_ids_set)]
        if not chunk_filtered.empty:
            deal_chunks.append(chunk_filtered)
    deal_df = pd.concat(deal_chunks, ignore_index=True) if deal_chunks else pd.DataFrame()
    
    print(f"Loaded {len(company_df)} wearable companies, {len(deal_df)} deals")
    return company_df, deal_df

def analyze_metrics(company_df, deal_df, label):
    """Analyze key metrics for a dataset"""
    print(f"\nAnalyzing {label} metrics...")
    
    results = {}
    current_year = datetime.now().year
    
    # Prepare deal data
    deal_df = deal_df.copy()
    deal_df['DealDate'] = pd.to_datetime(deal_df['DealDate'], errors='coerce')
    deal_df['Year'] = deal_df['DealDate'].dt.year
    deal_df = deal_df[deal_df['Year'].notna()].copy()
    
    # 1. Deal Activity by Year
    if len(deal_df) > 0:
        deals_by_year = deal_df.groupby('Year').agg({
            'DealID': 'count',
            'DealSize': lambda x: x[x.notna()].sum()
        }).reset_index()
        deals_by_year.columns = ['Year', 'DealCount', 'TotalFunding']
        deals_by_year['AvgDealSize'] = deal_df.groupby('Year')['DealSize'].mean().values
        results['deals_by_year'] = deals_by_year
    else:
        results['deals_by_year'] = pd.DataFrame()
    
    # 2. Company Age Distribution
    if len(company_df) > 0:
        company_df = company_df.copy()
        company_df['Age'] = current_year - company_df['YearFounded']
        company_df = company_df[company_df['Age'].notna() & (company_df['Age'] > 0) & (company_df['Age'] < 100)]
        results['age_stats'] = company_df['Age'].describe()
    else:
        results['age_stats'] = pd.Series()
    
    # 3. Valuation Trends
    valuation_data = deal_df[deal_df['PostValuation'].notna()].copy()
    if len(valuation_data) > 0:
        val_trends = valuation_data.groupby('Year')['PostValuation'].agg(['mean', 'median', 'count']).reset_index()
        results['valuation_trends'] = val_trends
    else:
        results['valuation_trends'] = pd.DataFrame()
    
    # 4. Geographic Distribution
    if len(company_df) > 0:
        geo_dist = company_df.groupby(['HQCountry', 'HQGlobalRegion']).agg({
            'CompanyID': 'count',
            'TotalRaised': lambda x: x.sum() if x.notna().any() else 0
        }).reset_index()
        geo_dist.columns = ['Country', 'Region', 'CompanyCount', 'TotalFunding']
        geo_dist = geo_dist.sort_values('TotalFunding', ascending=False)
        results['geographic'] = geo_dist
    else:
        results['geographic'] = pd.DataFrame()
    
    # 5. Growth Metrics
    if len(results['deals_by_year']) > 1:
        recent_5yr = results['deals_by_year'][results['deals_by_year']['Year'] >= current_year - 5]
        if len(recent_5yr) > 1:
            first_count = recent_5yr['DealCount'].iloc[0]
            last_count = recent_5yr['DealCount'].iloc[-1]
            if first_count > 0:
                cagr = ((last_count / first_count) ** (1/(len(recent_5yr)-1))) - 1
                results['deal_cagr'] = cagr
            else:
                results['deal_cagr'] = None
        else:
            results['deal_cagr'] = None
    else:
        results['deal_cagr'] = None
    
    # 6. Summary Statistics
    results['summary'] = {
        'total_companies': len(company_df),
        'total_deals': len(deal_df),
        'total_funding': results['deals_by_year']['TotalFunding'].sum() if not results['deals_by_year'].empty else 0,
        'avg_deal_size': results['deals_by_year']['AvgDealSize'].mean() if not results['deals_by_year'].empty else 0,
        'median_company_age': results['age_stats']['50%'] if len(results['age_stats']) > 0 else None
    }
    
    return results

def create_comparison_visualizations(wearable_data, industry_data, company_data):
    """Create comparative visualizations"""
    print("\nCreating comparison visualizations...")
    
    fig = plt.figure(figsize=(24, 16))
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)
    
    # Chart 1: Deal Activity Comparison
    ax1 = fig.add_subplot(gs[0, :2])
    if not wearable_data['deals_by_year'].empty and not industry_data['deals_by_year'].empty:
        # Normalize to show trends
        wear_deals = wearable_data['deals_by_year'].copy()
        ind_deals = industry_data['deals_by_year'].copy()
        
        # Get common years
        common_years = set(wear_deals['Year']) & set(ind_deals['Year'])
        if common_years:
            wear_deals = wear_deals[wear_deals['Year'].isin(common_years)].sort_values('Year')
            ind_deals = ind_deals[ind_deals['Year'].isin(common_years)].sort_values('Year')
            
            ax1_twin = ax1.twinx()
            
            # Wearable on left axis
            ax1.plot(wear_deals['Year'], wear_deals['DealCount'], marker='o', linewidth=2.5,
                    markersize=8, color='#e74c3c', label='Wearable Tech')
            ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Wearable Deal Count', fontsize=11, fontweight='bold', color='#e74c3c')
            ax1.tick_params(axis='y', labelcolor='#e74c3c')
            
            # Industry on right axis
            ax1_twin.plot(ind_deals['Year'], ind_deals['DealCount'], marker='s', linewidth=2.5,
                         markersize=8, color='#3498db', label='Industry Sample', alpha=0.7)
            ax1_twin.set_ylabel('Industry Deal Count', fontsize=11, fontweight='bold', color='#3498db')
            ax1_twin.tick_params(axis='y', labelcolor='#3498db')
            
            ax1.set_title('Deal Activity: Wearable Tech vs Industry', fontsize=14, fontweight='bold', pad=15)
            ax1.grid(True, alpha=0.3)
            
            # Combine legends
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax1_twin.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)
    
    # Chart 2: Growth Rate Comparison
    ax2 = fig.add_subplot(gs[0, 2])
    wear_cagr = wearable_data['deal_cagr']
    ind_cagr = industry_data['deal_cagr']
    
    if wear_cagr is not None or ind_cagr is not None:
        categories = []
        values = []
        colors = []
        
        if wear_cagr is not None:
            categories.append('Wearable\nTech')
            values.append(wear_cagr * 100)
            colors.append('#e74c3c' if wear_cagr > 0 else '#95a5a6')
        
        if ind_cagr is not None:
            categories.append('Industry\nSample')
            values.append(ind_cagr * 100)
            colors.append('#3498db' if ind_cagr > 0 else '#95a5a6')
        
        bars = ax2.bar(categories, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax2.set_ylabel('5-Year CAGR (%)', fontsize=11, fontweight='bold')
        ax2.set_title('Deal Growth Rate Comparison', fontsize=14, fontweight='bold', pad=15)
        ax2.grid(True, alpha=0.3, axis='y')
        
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:+.1f}%', ha='center', va='bottom' if value > 0 else 'top',
                    fontsize=11, fontweight='bold')
    
    # Chart 3: Average Deal Size Comparison
    ax3 = fig.add_subplot(gs[1, 0])
    wear_avg = wearable_data['summary']['avg_deal_size']
    ind_avg = industry_data['summary']['avg_deal_size']
    
    if wear_avg > 0 or ind_avg > 0:
        categories = ['Wearable\nTech', 'Industry\nSample']
        values = [wear_avg, ind_avg]
        colors = ['#e74c3c', '#3498db']
        
        bars = ax3.bar(categories, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax3.set_ylabel('Average Deal Size ($M)', fontsize=11, fontweight='bold')
        ax3.set_title('Average Deal Size Comparison', fontsize=14, fontweight='bold', pad=15)
        ax3.grid(True, alpha=0.3, axis='y')
        
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'${value:.1f}M', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
    
    # Chart 4: Company Age Distribution Comparison
    ax4 = fig.add_subplot(gs[1, 1])
    wear_age = wearable_data['age_stats']
    ind_age = industry_data['age_stats']
    
    if len(wear_age) > 0 and len(ind_age) > 0:
        age_metrics = ['Mean', 'Median']
        wear_values = [wear_age['mean'], wear_age['50%']]
        ind_values = [ind_age['mean'], ind_age['50%']]
        
        x = np.arange(len(age_metrics))
        width = 0.35
        
        bars1 = ax4.bar(x - width/2, wear_values, width, label='Wearable Tech',
                       color='#e74c3c', alpha=0.7, edgecolor='black', linewidth=1.5)
        bars2 = ax4.bar(x + width/2, ind_values, width, label='Industry Sample',
                       color='#3498db', alpha=0.7, edgecolor='black', linewidth=1.5)
        
        ax4.set_ylabel('Company Age (years)', fontsize=11, fontweight='bold')
        ax4.set_title('Company Age Comparison', fontsize=14, fontweight='bold', pad=15)
        ax4.set_xticks(x)
        ax4.set_xticklabels(age_metrics)
        ax4.legend(fontsize=10)
        ax4.grid(True, alpha=0.3, axis='y')
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}y', ha='center', va='bottom',
                        fontsize=9, fontweight='bold')
    
    # Chart 5: Geographic Distribution - Wearable
    ax5 = fig.add_subplot(gs[1, 2])
    if not wearable_data['geographic'].empty:
        geo_dist = wearable_data['geographic']
        top_geo = geo_dist[geo_dist['TotalFunding'] > 0].head(8)
        colors = sns.color_palette("Reds_r", len(top_geo))
        bars = ax5.barh(range(len(top_geo)), top_geo['TotalFunding'], color=colors,
                       edgecolor='black', linewidth=0.5)
        ax5.set_yticks(range(len(top_geo)))
        ax5.set_yticklabels(top_geo['Country'], fontsize=9)
        ax5.set_xlabel('Total Funding ($M)', fontsize=10, fontweight='bold')
        ax5.set_title('Wearable: Top Countries', fontsize=13, fontweight='bold', pad=12)
        ax5.grid(True, alpha=0.3, axis='x')
    
    # Chart 6: Geographic Distribution - Industry
    ax6 = fig.add_subplot(gs[2, 0])
    if not industry_data['geographic'].empty:
        geo_dist = industry_data['geographic']
        top_geo = geo_dist[geo_dist['TotalFunding'] > 0].head(8)
        colors = sns.color_palette("Blues_r", len(top_geo))
        bars = ax6.barh(range(len(top_geo)), top_geo['TotalFunding'], color=colors,
                       edgecolor='black', linewidth=0.5)
        ax6.set_yticks(range(len(top_geo)))
        ax6.set_yticklabels(top_geo['Country'], fontsize=9)
        ax6.set_xlabel('Total Funding ($M)', fontsize=10, fontweight='bold')
        ax6.set_title('Industry: Top Countries', fontsize=13, fontweight='bold', pad=12)
        ax6.grid(True, alpha=0.3, axis='x')
    
    # Chart 7: Summary Statistics Table
    ax7 = fig.add_subplot(gs[2, 1:])
    ax7.axis('tight')
    ax7.axis('off')
    
    # Create comparison table
    table_data = [
        ['Metric', 'Wearable Tech', 'Industry Sample', 'Difference'],
        ['', '', '', ''],
        ['Total Companies', f"{wearable_data['summary']['total_companies']}", 
         f"{industry_data['summary']['total_companies']}", '-'],
        ['Total Deals', f"{wearable_data['summary']['total_deals']}", 
         f"{industry_data['summary']['total_deals']}", '-'],
        ['Avg Deal Size ($M)', f"${wearable_data['summary']['avg_deal_size']:.1f}", 
         f"${industry_data['summary']['avg_deal_size']:.1f}",
         f"{((wearable_data['summary']['avg_deal_size'] / industry_data['summary']['avg_deal_size']) - 1) * 100:+.0f}%" if industry_data['summary']['avg_deal_size'] > 0 else '-'],
        ['5-Year CAGR', 
         f"{wearable_data['deal_cagr']*100:+.1f}%" if wearable_data['deal_cagr'] else 'N/A',
         f"{industry_data['deal_cagr']*100:+.1f}%" if industry_data['deal_cagr'] else 'N/A',
         f"{(wearable_data['deal_cagr'] - industry_data['deal_cagr'])*100:+.1f}pp" if wearable_data['deal_cagr'] and industry_data['deal_cagr'] else '-'],
        ['Median Age (years)', 
         f"{wearable_data['summary']['median_company_age']:.1f}" if wearable_data['summary']['median_company_age'] else 'N/A',
         f"{industry_data['summary']['median_company_age']:.1f}" if industry_data['summary']['median_company_age'] else 'N/A',
         f"{wearable_data['summary']['median_company_age'] - industry_data['summary']['median_company_age']:+.1f}y" if wearable_data['summary']['median_company_age'] and industry_data['summary']['median_company_age'] else '-'],
    ]
    
    table = ax7.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.35, 0.22, 0.22, 0.21])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # Style header
    for i in range(4):
        table[(0, i)].set_facecolor('#34495e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(2, len(table_data)):
        for j in range(4):
            table[(i, j)].set_facecolor(['#ecf0f1', 'white'][i % 2])
    
    ax7.set_title('Comparative Summary Statistics', fontsize=14, fontweight='bold', pad=20)
    
    plt.savefig('analysis_investment_landscape/wearable_vs_industry_comparison.png', 
                dpi=300, bbox_inches='tight')
    print("\nComparison visualization saved: wearable_vs_industry_comparison.png")
    plt.close()

def generate_comparison_report(wearable_data, industry_data, company_data):
    """Generate comprehensive comparison report"""
    print("\nGenerating comparison report...")
    
    report = []
    report.append("# Wearable Technology vs Industry Comparison")
    report.append("\n## Executive Summary\n")
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}")
    report.append(f"\n**Wearable Companies Analyzed:** {len(company_data)}")
    
    company_list = ", ".join([c['name'] for c in company_data])
    report.append(f"\n**Companies:** {company_list}")
    
    report.append(f"\n**Industry Sample Size:** {industry_data['summary']['total_companies']:,} companies (random sample of 10,000 companies from full dataset)")
    
    report.append("\n\nThis analysis compares the wearable technology sector against a broader industry sample, ")
    report.append("providing context on relative performance, trends, and positioning.")
    
    # Section 1: Key Comparisons
    report.append("\n\n---\n")
    report.append("## 1. Key Performance Comparisons\n")
    
    # Deal Activity
    report.append("### 1.1 Deal Activity\n")
    report.append(f"**Wearable Tech:** {wearable_data['summary']['total_deals']} deals")
    report.append(f"\n**Industry Sample:** {industry_data['summary']['total_deals']} deals")
    
    if wearable_data['summary']['total_companies'] > 0 and industry_data['summary']['total_companies'] > 0:
        wear_deals_per_co = wearable_data['summary']['total_deals'] / wearable_data['summary']['total_companies']
        ind_deals_per_co = industry_data['summary']['total_deals'] / industry_data['summary']['total_companies']
        report.append(f"\n**Deals per Company:**")
        report.append(f"\n- Wearable: {wear_deals_per_co:.2f}")
        report.append(f"\n- Industry: {ind_deals_per_co:.2f}")
        
        if wear_deals_per_co > ind_deals_per_co * 1.2:
            report.append(f"\n\n✅ **Wearable tech companies average {((wear_deals_per_co/ind_deals_per_co - 1)*100):.0f}% more deals** than industry average")
        elif wear_deals_per_co < ind_deals_per_co * 0.8:
            report.append(f"\n\n⚠️ **Wearable tech companies average {((1 - wear_deals_per_co/ind_deals_per_co)*100):.0f}% fewer deals** than industry average")
        else:
            report.append(f"\n\n**Wearable tech deal activity is comparable to industry average**")
    
    # Growth Rate
    report.append("\n\n### 1.2 Growth Rate\n")
    if wearable_data['deal_cagr'] is not None:
        report.append(f"**Wearable 5-Year CAGR:** {wearable_data['deal_cagr']*100:+.1f}%")
    if industry_data['deal_cagr'] is not None:
        report.append(f"\n**Industry 5-Year CAGR:** {industry_data['deal_cagr']*100:+.1f}%")
    
    if wearable_data['deal_cagr'] is not None and industry_data['deal_cagr'] is not None:
        diff = (wearable_data['deal_cagr'] - industry_data['deal_cagr']) * 100
        if abs(diff) > 5:
            if diff > 0:
                report.append(f"\n\n✅ **Wearable tech growing {diff:+.1f}pp faster** than industry")
            else:
                report.append(f"\n\n⚠️ **Wearable tech growing {abs(diff):.1f}pp slower** than industry")
        else:
            report.append(f"\n\n**Growth rates are comparable** (difference: {diff:+.1f}pp)")
    
    # Deal Size
    report.append("\n\n### 1.3 Deal Size\n")
    wear_avg = wearable_data['summary']['avg_deal_size']
    ind_avg = industry_data['summary']['avg_deal_size']
    
    report.append(f"**Wearable Average:** ${wear_avg:.1f}M")
    report.append(f"\n**Industry Average:** ${ind_avg:.1f}M")
    
    if wear_avg > 0 and ind_avg > 0:
        diff_pct = ((wear_avg / ind_avg) - 1) * 100
        if abs(diff_pct) > 20:
            if diff_pct > 0:
                report.append(f"\n\n✅ **Wearable deals are {diff_pct:+.0f}% larger** than industry average")
            else:
                report.append(f"\n\n⚠️ **Wearable deals are {abs(diff_pct):.0f}% smaller** than industry average")
        else:
            report.append(f"\n\n**Deal sizes are comparable** (difference: {diff_pct:+.0f}%)")
    
    # Company Maturity
    report.append("\n\n### 1.4 Company Maturity\n")
    if len(wearable_data['age_stats']) > 0 and len(industry_data['age_stats']) > 0:
        wear_age = wearable_data['age_stats']['50%']
        ind_age = industry_data['age_stats']['50%']
        
        report.append(f"**Wearable Median Age:** {wear_age:.1f} years")
        report.append(f"\n**Industry Median Age:** {ind_age:.1f} years")
        
        age_diff = wear_age - ind_age
        if abs(age_diff) > 2:
            if age_diff > 0:
                report.append(f"\n\n**Wearable companies are {age_diff:.1f} years older** (more mature)")
            else:
                report.append(f"\n\n**Wearable companies are {abs(age_diff):.1f} years younger** (less mature)")
        else:
            report.append(f"\n\n**Company ages are comparable**")
    
    # Section 2: Funding Analysis
    report.append("\n\n---\n")
    report.append("## 2. Funding Analysis\n")
    
    report.append("### 2.1 Total Funding\n")
    wear_total = wearable_data['summary']['total_funding']
    ind_total = industry_data['summary']['total_funding']
    
    report.append(f"**Wearable Tech:** ${wear_total:.1f}M across {wearable_data['summary']['total_companies']} companies")
    report.append(f"\n**Industry Sample:** ${ind_total:.1f}M across {industry_data['summary']['total_companies']} companies")
    
    if wearable_data['summary']['total_companies'] > 0 and industry_data['summary']['total_companies'] > 0:
        wear_per_co = wear_total / wearable_data['summary']['total_companies']
        ind_per_co = ind_total / industry_data['summary']['total_companies']
        
        report.append(f"\n\n**Funding per Company:**")
        report.append(f"\n- Wearable: ${wear_per_co:.1f}M")
        report.append(f"\n- Industry: ${ind_per_co:.1f}M")
    
    # Section 3: Geographic Comparison
    report.append("\n\n---\n")
    report.append("## 3. Geographic Distribution\n")
    
    if not wearable_data['geographic'].empty:
        report.append("### 3.1 Wearable Tech Geographic Clusters\n")
        wear_geo = wearable_data['geographic']
        report.append(f"**Countries Represented:** {len(wear_geo)}")
        report.append(f"\n\n**Top 5 Countries:**")
        for idx, row in wear_geo.head(5).iterrows():
            report.append(f"\n{idx+1}. {row['Country']}: ${row['TotalFunding']:.1f}M ({int(row['CompanyCount'])} companies)")
    
    if not industry_data['geographic'].empty:
        report.append("\n\n### 3.2 Industry Geographic Distribution\n")
        ind_geo = industry_data['geographic']
        report.append(f"**Countries Represented:** {len(ind_geo)}")
        report.append(f"\n\n**Top 5 Countries:**")
        for idx, row in ind_geo.head(5).iterrows():
            report.append(f"\n{idx+1}. {row['Country']}: ${row['TotalFunding']:.1f}M ({int(row['CompanyCount'])} companies)")
    
    # Section 4: Strategic Insights
    report.append("\n\n---\n")
    report.append("## 4. Strategic Insights and Positioning\n")
    
    report.append("### 4.1 Wearable Tech Positioning\n")
    
    insights = []
    
    # Deal activity insight
    if wearable_data['summary']['total_companies'] > 0 and industry_data['summary']['total_companies'] > 0:
        wear_deals_per_co = wearable_data['summary']['total_deals'] / wearable_data['summary']['total_companies']
        ind_deals_per_co = industry_data['summary']['total_deals'] / industry_data['summary']['total_companies']
        if wear_deals_per_co > ind_deals_per_co * 1.1:
            insights.append("**Higher Deal Frequency:** Wearable companies attract more investment rounds, suggesting active investor interest")
        elif wear_deals_per_co < ind_deals_per_co * 0.9:
            insights.append("**Lower Deal Frequency:** Wearable companies may face more selective funding environment")
    
    # Growth insight
    if wearable_data['deal_cagr'] and industry_data['deal_cagr']:
        if wearable_data['deal_cagr'] < industry_data['deal_cagr'] - 0.05:
            insights.append("**Slower Growth:** Wearable sector growing slower than broader market, indicating potential maturation")
        elif wearable_data['deal_cagr'] > industry_data['deal_cagr'] + 0.05:
            insights.append("**Faster Growth:** Wearable sector outpacing broader market, showing strong momentum")
    
    # Deal size insight
    if wear_avg > ind_avg * 1.2:
        insights.append("**Larger Deal Sizes:** Wearable companies command higher capital per round, suggesting capital-intensive business models")
    elif wear_avg < ind_avg * 0.8:
        insights.append("**Smaller Deal Sizes:** More modest capital requirements may indicate leaner business models")
    
    # Maturity insight
    if len(wearable_data['age_stats']) > 0 and len(industry_data['age_stats']) > 0:
        if wearable_data['age_stats']['50%'] > industry_data['age_stats']['50%'] + 2:
            insights.append("**More Mature Sector:** Older companies suggest established market with proven models")
        elif wearable_data['age_stats']['50%'] < industry_data['age_stats']['50%'] - 2:
            insights.append("**Younger Sector:** Emerging market with significant innovation potential")
    
    for insight in insights:
        report.append(f"\n- {insight}")
    
    # Section 5: Recommendations
    report.append("\n\n### 4.2 Strategic Recommendations\n")
    
    report.append("\n**For Investors:**")
    if wearable_data['deal_cagr'] and wearable_data['deal_cagr'] < 0:
        report.append("\n- Market consolidation creates opportunities to identify winners at attractive valuations")
        report.append("\n- Focus on companies with sustainable competitive advantages in niche verticals")
    else:
        report.append("\n- Growing market with continued opportunities across funding stages")
        report.append("\n- Evaluate companies based on differentiation from consumer tech giants")
    
    report.append("\n\n**For Companies:**")
    if wear_avg > ind_avg:
        report.append("\n- Leverage higher funding capacity to build defensible technology and market position")
        report.append("\n- Consider capital-efficient strategies given hardware development costs")
    else:
        report.append("\n- Focus on capital efficiency and rapid path to revenue")
        report.append("\n- Explore strategic partnerships to complement organic funding")
    
    report.append("\n\n**Market Outlook:**")
    if wearable_data['deal_cagr'] and industry_data['deal_cagr']:
        if wearable_data['deal_cagr'] < industry_data['deal_cagr']:
            report.append("\n- Wearable sector showing signs of maturation relative to broader market")
            report.append("\n- Expect continued consolidation with focus on proven business models")
            report.append("\n- Innovation opportunities exist in specialized verticals (medical, enterprise)")
        else:
            report.append("\n- Wearable sector momentum exceeds broader market trends")
            report.append("\n- Strong growth outlook with expanding applications")
            report.append("\n- Technology convergence (AI, sensors) creating new opportunities")
    
    # Conclusion
    report.append("\n\n---\n")
    report.append("## 5. Conclusion\n")
    report.append("\nThe wearable technology sector demonstrates distinct characteristics compared to the broader industry. ")
    
    if wearable_data['deal_cagr'] and wearable_data['deal_cagr'] < 0:
        report.append("While the sector faces consolidation pressures, ")
    else:
        report.append("With growing momentum, ")
    
    report.append("successful players will be those that can differentiate through specialized applications, ")
    report.append("proprietary technology, or unique market positioning. The sector's maturity level and funding patterns ")
    report.append("suggest opportunities for both growth-focused and consolidation-oriented strategies.")
    
    report.append(f"\n\n---\n\n*Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*")
    report.append(f"\n*Wearable tech analysis: {len(company_data)} companies*")
    report.append(f"\n*Industry comparison: {industry_data['summary']['total_companies']:,} companies sample*")
    
    return '\n'.join(report)

def main():
    print("="*80)
    print("WEARABLE TECHNOLOGY vs INDUSTRY COMPARISON ANALYSIS")
    print("="*80)
    
    # Parse wearable companies
    company_data = parse_company_ids('list.txt')
    company_ids = [c['id'] for c in company_data]
    
    print(f"\nWearable Technology Companies ({len(company_data)}):")
    for i, company in enumerate(company_data, 1):
        print(f"  {i:2d}. {company['name']}")
    
    # Load industry sample
    industry_companies, industry_deals = load_industry_sample(sample_size=10000)
    
    # Load wearable data
    wearable_companies, wearable_deals = load_wearable_data(company_ids)
    
    # Analyze both datasets
    print("\n" + "-"*80)
    wearable_data = analyze_metrics(wearable_companies, wearable_deals, "Wearable Tech")
    industry_data = analyze_metrics(industry_companies, industry_deals, "Industry Sample")
    
    # Create visualizations
    create_comparison_visualizations(wearable_data, industry_data, company_data)
    
    # Generate report
    report = generate_comparison_report(wearable_data, industry_data, company_data)
    
    with open('analysis_investment_landscape/WEARABLE_VS_INDUSTRY_REPORT.md', 'w') as f:
        f.write(report)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nOutput files:")
    print("  - WEARABLE_VS_INDUSTRY_REPORT.md (comparison analysis)")
    print("  - wearable_vs_industry_comparison.png (comparative visualizations)")
    
    # Save summary data
    summary_data = {
        'Metric': ['Total Companies', 'Total Deals', 'Total Funding ($M)', 'Avg Deal Size ($M)', 
                   '5-Year CAGR', 'Median Age (years)'],
        'Wearable Tech': [
            wearable_data['summary']['total_companies'],
            wearable_data['summary']['total_deals'],
            f"{wearable_data['summary']['total_funding']:.1f}",
            f"{wearable_data['summary']['avg_deal_size']:.1f}",
            f"{wearable_data['deal_cagr']*100:.1f}%" if wearable_data['deal_cagr'] else 'N/A',
            f"{wearable_data['summary']['median_company_age']:.1f}" if wearable_data['summary']['median_company_age'] else 'N/A'
        ],
        'Industry Sample': [
            industry_data['summary']['total_companies'],
            industry_data['summary']['total_deals'],
            f"{industry_data['summary']['total_funding']:.1f}",
            f"{industry_data['summary']['avg_deal_size']:.1f}",
            f"{industry_data['deal_cagr']*100:.1f}%" if industry_data['deal_cagr'] else 'N/A',
            f"{industry_data['summary']['median_company_age']:.1f}" if industry_data['summary']['median_company_age'] else 'N/A'
        ]
    }
    
    pd.DataFrame(summary_data).to_csv('analysis_investment_landscape/comparison_summary.csv', index=False)
    print("  - comparison_summary.csv (data summary)")

if __name__ == "__main__":
    main()
