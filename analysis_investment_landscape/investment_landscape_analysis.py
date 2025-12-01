#!/usr/bin/env python3
"""
Comprehensive Investment Landscape Analysis:
1. Investor Types and Evolution
2. Geographic Funding Clusters
3. Industry Stage and Prospects Assessment
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
plt.rcParams['figure.figsize'] = (20, 14)

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

def load_data(company_ids, chunk_size=50000):
    """Load all necessary data"""
    print("Loading data...")
    company_ids_set = set(company_ids)
    
    # Load Company data
    print("  - Loading company data...")
    company_chunks = []
    for chunk in pd.read_csv('Company.csv', 
                             usecols=['CompanyID', 'CompanyName', 'HQCity', 'HQState_Province', 
                                     'HQCountry', 'HQGlobalRegion', 'YearFounded', 
                                     'TotalRaised', 'BusinessStatus', 'CompanyFinancingStatus'],
                             chunksize=chunk_size, 
                             low_memory=False):
        chunk_filtered = chunk[chunk['CompanyID'].isin(company_ids_set)]
        if not chunk_filtered.empty:
            company_chunks.append(chunk_filtered)
    company_df = pd.concat(company_chunks, ignore_index=True) if company_chunks else pd.DataFrame()
    
    # Load Deal data
    print("  - Loading deal data...")
    deal_chunks = []
    for chunk in pd.read_csv('Deal.csv', 
                             usecols=['CompanyID', 'CompanyName', 'DealID', 'DealDate', 
                                     'DealType', 'DealType2', 'DealSize', 'Investors',
                                     'PostValuation', 'VCRound', 'SiteLocation', 'DealStatus'],
                             chunksize=chunk_size, 
                             low_memory=False):
        chunk_filtered = chunk[chunk['CompanyID'].isin(company_ids_set)]
        if not chunk_filtered.empty:
            deal_chunks.append(chunk_filtered)
    deal_df = pd.concat(deal_chunks, ignore_index=True) if deal_chunks else pd.DataFrame()
    
    # Load Investor data
    print("  - Loading investor data...")
    investor_chunks = []
    for chunk in pd.read_csv('Investor.csv', 
                             usecols=['InvestorID', 'InvestorName', 'PrimaryInvestorType',
                                     'HQCity', 'HQCountry', 'HQGlobalRegion'],
                             chunksize=chunk_size, 
                             low_memory=False):
        investor_chunks.append(chunk)
    investor_df = pd.concat(investor_chunks, ignore_index=True)
    
    print(f"Loaded {len(company_df)} companies, {len(deal_df)} deals, {len(investor_df)} investors")
    return company_df, deal_df, investor_df

def extract_investor_deals(deal_df, investor_df):
    """Extract and link investors to deals"""
    print("\nExtracting investor-deal links...")
    
    investor_deal_links = []
    for idx, row in deal_df.iterrows():
        if pd.notna(row['Investors']):
            investor_str = str(row['Investors'])
            for sep in [',', ';', '|']:
                if sep in investor_str:
                    investor_ids = [inv.strip() for inv in investor_str.split(sep)]
                    break
            else:
                investor_ids = [investor_str.strip()]
            
            for inv_id in investor_ids:
                if inv_id:
                    investor_deal_links.append({
                        'CompanyID': row['CompanyID'],
                        'CompanyName': row['CompanyName'],
                        'InvestorID': inv_id,
                        'DealDate': row['DealDate'],
                        'DealType': row['DealType'],
                        'DealType2': row['DealType2'],
                        'DealSize': row['DealSize'],
                        'PostValuation': row['PostValuation'],
                        'VCRound': row['VCRound']
                    })
    
    links_df = pd.DataFrame(investor_deal_links)
    
    # Merge with investor data
    if not links_df.empty:
        links_df = links_df.merge(investor_df, on='InvestorID', how='left')
        links_df['DealDate'] = pd.to_datetime(links_df['DealDate'], errors='coerce')
        links_df['Year'] = links_df['DealDate'].dt.year
    
    print(f"Found {len(links_df)} investor-deal links")
    return links_df

def analyze_investor_types_evolution(links_df):
    """Analyze investor types and their evolution over time"""
    print("\nAnalyzing investor types evolution...")
    
    # Overall distribution
    investor_type_dist = links_df.groupby('PrimaryInvestorType').size().reset_index(name='Count')
    investor_type_dist = investor_type_dist.sort_values('Count', ascending=False)
    
    # Evolution over time
    links_df_filtered = links_df[links_df['Year'].notna()].copy()
    investor_type_evolution = links_df_filtered.groupby(['Year', 'PrimaryInvestorType']).size().reset_index(name='Count')
    
    # By funding stage (using VCRound and DealType2)
    links_df['FundingStage'] = links_df['VCRound'].fillna(links_df['DealType2'])
    stage_investor_matrix = links_df.groupby(['FundingStage', 'PrimaryInvestorType']).size().reset_index(name='Count')
    
    return investor_type_dist, investor_type_evolution, stage_investor_matrix

def analyze_geographic_clusters(company_df, investor_df, links_df):
    """Analyze geographic distribution of companies, investors, and funding flows"""
    print("\nAnalyzing geographic clusters...")
    
    # Company locations
    company_geo = company_df.groupby(['HQCountry', 'HQGlobalRegion']).agg({
        'CompanyID': 'count',
        'TotalRaised': lambda x: x.sum() if x.notna().any() else 0
    }).reset_index()
    company_geo.columns = ['Country', 'Region', 'CompanyCount', 'TotalFunding']
    company_geo = company_geo.sort_values('TotalFunding', ascending=False)
    
    # Investor locations
    investor_geo = investor_df[investor_df['InvestorID'].isin(links_df['InvestorID'].unique())].groupby(['HQCountry', 'HQGlobalRegion']).size().reset_index(name='InvestorCount')
    investor_geo = investor_geo.sort_values('InvestorCount', ascending=False)
    
    # Funding flows (company country to investor country)
    links_with_geo = links_df.merge(
        company_df[['CompanyID', 'HQCountry']].rename(columns={'HQCountry': 'CompanyCountry'}),
        on='CompanyID', how='left'
    )
    
    funding_flows = links_with_geo.groupby(['CompanyCountry', 'HQCountry']).size().reset_index(name='FlowCount')
    funding_flows.columns = ['CompanyCountry', 'InvestorCountry', 'FlowCount']
    funding_flows = funding_flows.sort_values('FlowCount', ascending=False)
    
    # Cross-border vs domestic investment
    links_with_geo['IsCrossBorder'] = links_with_geo['CompanyCountry'] != links_with_geo['HQCountry']
    cross_border_stats = links_with_geo.groupby('IsCrossBorder').size()
    
    return company_geo, investor_geo, funding_flows, cross_border_stats

def assess_industry_stage(deal_df, links_df, company_df):
    """Assess the stage of the industry and its prospects"""
    print("\nAssessing industry stage and prospects...")
    
    # Parse deal dates
    deal_df_time = deal_df.copy()
    deal_df_time['DealDate'] = pd.to_datetime(deal_df_time['DealDate'], errors='coerce')
    deal_df_time['Year'] = deal_df_time['DealDate'].dt.year
    deal_df_time = deal_df_time[deal_df_time['Year'].notna()]
    
    # 1. Deal activity over time
    deals_by_year = deal_df_time.groupby('Year').agg({
        'DealID': 'count',
        'DealSize': lambda x: x[x.notna()].sum()
    }).reset_index()
    deals_by_year.columns = ['Year', 'DealCount', 'TotalFunding']
    
    # 2. Average deal size over time
    deals_by_year['AvgDealSize'] = deal_df_time.groupby('Year')['DealSize'].mean().values
    
    # 3. Funding stage distribution
    stage_distribution = deal_df_time.groupby('VCRound').size().reset_index(name='Count')
    stage_distribution = stage_distribution.sort_values('Count', ascending=False)
    
    # 4. Recent activity (last 2 years)
    current_year = datetime.now().year
    recent_deals = deal_df_time[deal_df_time['Year'] >= current_year - 2]
    recent_stage_dist = recent_deals.groupby('VCRound').size().reset_index(name='Count')
    
    # 5. Valuation trends
    valuation_trends = deal_df_time[deal_df_time['PostValuation'].notna()].groupby('Year')['PostValuation'].agg(['mean', 'median', 'count']).reset_index()
    
    # 6. Company maturity
    company_df['Age'] = current_year - company_df['YearFounded']
    age_distribution = company_df['Age'].describe()
    
    # 7. Business status
    business_status_dist = company_df.groupby('BusinessStatus').size().reset_index(name='Count')
    
    # 8. Growth indicators
    deal_growth_rate = None
    if len(deals_by_year) > 1:
        recent_5yr = deals_by_year[deals_by_year['Year'] >= current_year - 5]
        if len(recent_5yr) > 1:
            deal_growth_rate = ((recent_5yr['DealCount'].iloc[-1] / recent_5yr['DealCount'].iloc[0]) ** (1/len(recent_5yr))) - 1
    
    return {
        'deals_by_year': deals_by_year,
        'stage_distribution': stage_distribution,
        'recent_stage_dist': recent_stage_dist,
        'valuation_trends': valuation_trends,
        'age_distribution': age_distribution,
        'business_status': business_status_dist,
        'deal_growth_rate': deal_growth_rate
    }

def create_visualizations(investor_type_dist, investor_type_evolution, stage_investor_matrix,
                         company_geo, investor_geo, funding_flows, cross_border_stats,
                         industry_metrics, company_data):
    """Create comprehensive visualizations"""
    print("\nCreating visualizations...")
    
    fig = plt.figure(figsize=(24, 20))
    gs = fig.add_gridspec(5, 3, hspace=0.4, wspace=0.35)
    
    # Row 1: Investor Types
    # Chart 1: Investor Type Distribution
    ax1 = fig.add_subplot(gs[0, 0])
    if not investor_type_dist.empty:
        colors = sns.color_palette("Set2", len(investor_type_dist))
        bars = ax1.barh(investor_type_dist['PrimaryInvestorType'], investor_type_dist['Count'], color=colors)
        ax1.set_xlabel('Number of Investments', fontsize=11, fontweight='bold')
        ax1.set_title('Investor Type Distribution', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        for i, (bar, value) in enumerate(zip(bars, investor_type_dist['Count'])):
            ax1.text(value, i, f' {int(value)}', va='center', fontsize=9, fontweight='bold')
    
    # Chart 2: Investor Type Evolution
    ax2 = fig.add_subplot(gs[0, 1:])
    if not investor_type_evolution.empty:
        pivot_evolution = investor_type_evolution.pivot(index='Year', columns='PrimaryInvestorType', values='Count').fillna(0)
        pivot_evolution.plot(kind='area', stacked=True, ax=ax2, alpha=0.7, colormap='tab20')
        ax2.set_xlabel('Year', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Number of Investments', fontsize=11, fontweight='bold')
        ax2.set_title('Investor Type Evolution Over Time', fontsize=13, fontweight='bold')
        ax2.legend(title='Investor Type', bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
        ax2.grid(True, alpha=0.3)
    
    # Row 2: Geographic Analysis
    # Chart 3: Company Geographic Distribution
    ax3 = fig.add_subplot(gs[1, 0])
    if not company_geo.empty:
        top_countries = company_geo.head(15)
        colors = sns.color_palette("viridis", len(top_countries))
        bars = ax3.barh(range(len(top_countries)), top_countries['CompanyCount'], color=colors)
        ax3.set_yticks(range(len(top_countries)))
        ax3.set_yticklabels(top_countries['Country'], fontsize=9)
        ax3.set_xlabel('Number of Companies', fontsize=11, fontweight='bold')
        ax3.set_title('Top 15 Countries by Company Count', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='x')
        for i, (bar, value) in enumerate(zip(bars, top_countries['CompanyCount'])):
            ax3.text(value, i, f' {int(value)}', va='center', fontsize=8)
    
    # Chart 4: Total Funding by Geography
    ax4 = fig.add_subplot(gs[1, 1])
    if not company_geo.empty and company_geo['TotalFunding'].sum() > 0:
        top_funding = company_geo[company_geo['TotalFunding'] > 0].head(15)
        colors = sns.color_palette("plasma", len(top_funding))
        bars = ax4.barh(range(len(top_funding)), top_funding['TotalFunding'], color=colors)
        ax4.set_yticks(range(len(top_funding)))
        ax4.set_yticklabels(top_funding['Country'], fontsize=9)
        ax4.set_xlabel('Total Funding ($M)', fontsize=11, fontweight='bold')
        ax4.set_title('Top Countries by Total Funding', fontsize=13, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='x')
        for i, (bar, value) in enumerate(zip(bars, top_funding['TotalFunding'])):
            ax4.text(value, i, f' ${value:.1f}M', va='center', fontsize=8)
    
    # Chart 5: Cross-Border Investment
    ax5 = fig.add_subplot(gs[1, 2])
    if isinstance(cross_border_stats, pd.Series) and len(cross_border_stats) > 0:
        labels = ['Domestic', 'Cross-Border']
        values = [cross_border_stats.get(False, 0), cross_border_stats.get(True, 0)]
        colors = ['#2ecc71', '#3498db']
        wedges, texts, autotexts = ax5.pie(values, labels=labels, autopct='%1.1f%%',
                                            colors=colors, startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)
        ax5.set_title('Domestic vs Cross-Border Investment', fontsize=13, fontweight='bold')
    
    # Row 3: Industry Stage Analysis
    # Chart 6: Deal Activity Over Time
    ax6 = fig.add_subplot(gs[2, 0])
    if not industry_metrics['deals_by_year'].empty:
        deals_by_year = industry_metrics['deals_by_year']
        ax6.plot(deals_by_year['Year'], deals_by_year['DealCount'], marker='o', linewidth=2, 
                markersize=8, color='#e74c3c', label='Deal Count')
        ax6.set_xlabel('Year', fontsize=11, fontweight='bold')
        ax6.set_ylabel('Number of Deals', fontsize=11, fontweight='bold')
        ax6.set_title('Deal Activity Over Time', fontsize=13, fontweight='bold')
        ax6.grid(True, alpha=0.3)
        ax6.legend(fontsize=10)
    
    # Chart 7: Funding Amount Over Time
    ax7 = fig.add_subplot(gs[2, 1])
    if not industry_metrics['deals_by_year'].empty:
        deals_by_year = industry_metrics['deals_by_year']
        ax7.bar(deals_by_year['Year'], deals_by_year['TotalFunding'], color='#3498db', alpha=0.7)
        ax7.set_xlabel('Year', fontsize=11, fontweight='bold')
        ax7.set_ylabel('Total Funding ($M)', fontsize=11, fontweight='bold')
        ax7.set_title('Total Funding Over Time', fontsize=13, fontweight='bold')
        ax7.grid(True, alpha=0.3, axis='y')
    
    # Chart 8: Average Deal Size Over Time
    ax8 = fig.add_subplot(gs[2, 2])
    if not industry_metrics['deals_by_year'].empty and 'AvgDealSize' in industry_metrics['deals_by_year'].columns:
        deals_by_year = industry_metrics['deals_by_year']
        valid_avg = deals_by_year[deals_by_year['AvgDealSize'].notna()]
        if not valid_avg.empty:
            ax8.plot(valid_avg['Year'], valid_avg['AvgDealSize'], marker='s', linewidth=2,
                    markersize=8, color='#9b59b6')
            ax8.set_xlabel('Year', fontsize=11, fontweight='bold')
            ax8.set_ylabel('Average Deal Size ($M)', fontsize=11, fontweight='bold')
            ax8.set_title('Average Deal Size Trend', fontsize=13, fontweight='bold')
            ax8.grid(True, alpha=0.3)
    
    # Row 4: Funding Stage Analysis
    # Chart 9: Funding Stage Distribution
    ax9 = fig.add_subplot(gs[3, 0])
    if not industry_metrics['stage_distribution'].empty:
        stage_dist = industry_metrics['stage_distribution'].head(10)
        colors = sns.color_palette("coolwarm", len(stage_dist))
        bars = ax9.barh(range(len(stage_dist)), stage_dist['Count'], color=colors)
        ax9.set_yticks(range(len(stage_dist)))
        ax9.set_yticklabels(stage_dist['VCRound'], fontsize=9)
        ax9.set_xlabel('Number of Deals', fontsize=11, fontweight='bold')
        ax9.set_title('Funding Stage Distribution (All Time)', fontsize=13, fontweight='bold')
        ax9.grid(True, alpha=0.3, axis='x')
        for i, (bar, value) in enumerate(zip(bars, stage_dist['Count'])):
            ax9.text(value, i, f' {int(value)}', va='center', fontsize=8)
    
    # Chart 10: Recent Stage Distribution (Last 2 Years)
    ax10 = fig.add_subplot(gs[3, 1])
    if not industry_metrics['recent_stage_dist'].empty:
        recent_stage = industry_metrics['recent_stage_dist'].head(10)
        colors = sns.color_palette("YlOrRd", len(recent_stage))
        bars = ax10.barh(range(len(recent_stage)), recent_stage['Count'], color=colors)
        ax10.set_yticks(range(len(recent_stage)))
        ax10.set_yticklabels(recent_stage['VCRound'], fontsize=9)
        ax10.set_xlabel('Number of Deals', fontsize=11, fontweight='bold')
        ax10.set_title('Recent Funding Stage (Last 2 Years)', fontsize=13, fontweight='bold')
        ax10.grid(True, alpha=0.3, axis='x')
        for i, (bar, value) in enumerate(zip(bars, recent_stage['Count'])):
            ax10.text(value, i, f' {int(value)}', va='center', fontsize=8)
    
    # Chart 11: Valuation Trends
    ax11 = fig.add_subplot(gs[3, 2])
    if not industry_metrics['valuation_trends'].empty and len(industry_metrics['valuation_trends']) > 0:
        val_trends = industry_metrics['valuation_trends']
        ax11.plot(val_trends['Year'], val_trends['mean'], marker='o', linewidth=2,
                 markersize=6, color='#e67e22', label='Mean Valuation')
        ax11.plot(val_trends['Year'], val_trends['median'], marker='s', linewidth=2,
                 markersize=6, color='#16a085', label='Median Valuation')
        ax11.set_xlabel('Year', fontsize=11, fontweight='bold')
        ax11.set_ylabel('Valuation ($M)', fontsize=11, fontweight='bold')
        ax11.set_title('Post-Money Valuation Trends', fontsize=13, fontweight='bold')
        ax11.legend(fontsize=9)
        ax11.grid(True, alpha=0.3)
    
    # Row 5: Stage-Investor Matrix
    # Chart 12: Investor Types by Funding Stage (Heatmap)
    ax12 = fig.add_subplot(gs[4, :2])
    if not stage_investor_matrix.empty:
        pivot_matrix = stage_investor_matrix.pivot(index='FundingStage', columns='PrimaryInvestorType', values='Count').fillna(0)
        # Select top stages and investor types
        top_stages = pivot_matrix.sum(axis=1).nlargest(15).index
        top_investors = pivot_matrix.sum(axis=0).nlargest(10).index
        pivot_matrix_filtered = pivot_matrix.loc[top_stages, top_investors]
        
        sns.heatmap(pivot_matrix_filtered, annot=True, fmt='.0f', cmap='YlOrRd', 
                   linewidths=0.5, ax=ax12, cbar_kws={'label': 'Investment Count'})
        ax12.set_xlabel('Investor Type', fontsize=11, fontweight='bold')
        ax12.set_ylabel('Funding Stage', fontsize=11, fontweight='bold')
        ax12.set_title('Investor Types by Funding Stage', fontsize=13, fontweight='bold')
        plt.setp(ax12.get_xticklabels(), rotation=45, ha='right', fontsize=9)
        plt.setp(ax12.get_yticklabels(), rotation=0, fontsize=9)
    
    # Chart 13: Summary Statistics Table
    ax13 = fig.add_subplot(gs[4, 2])
    ax13.axis('tight')
    ax13.axis('off')
    
    # Create summary table
    summary_data = [
        ['Metric', 'Value'],
        ['', ''],
        ['COMPANIES', ''],
        [f"Total Companies", f"{len(company_data)}"],
        ['', ''],
        ['INVESTORS', ''],
        [f"Total Investor Types", f"{len(investor_type_dist)}"],
        [f"Top Investor Type", f"{investor_type_dist.iloc[0]['PrimaryInvestorType'] if len(investor_type_dist) > 0 else 'N/A'}"],
        ['', ''],
        ['GEOGRAPHY', ''],
        [f"Countries Represented", f"{len(company_geo)}"],
        [f"Cross-Border Deals", f"{cross_border_stats.get(True, 0) if isinstance(cross_border_stats, pd.Series) else 'N/A'}"],
        ['', ''],
        ['INDUSTRY STAGE', ''],
        [f"Deal Growth Rate", f"{industry_metrics['deal_growth_rate']*100:.1f}%" if industry_metrics['deal_growth_rate'] else 'N/A'],
    ]
    
    table = ax13.table(cellText=summary_data, cellLoc='left', loc='center',
                      colWidths=[0.6, 0.4])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # Style header
    for i in range(2):
        table[(0, i)].set_facecolor('#34495e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style section headers
    for row_idx in [2, 5, 9, 12]:
        for col_idx in range(2):
            table[(row_idx, col_idx)].set_facecolor('#95a5a6')
            table[(row_idx, col_idx)].set_text_props(weight='bold', color='white')
    
    ax13.set_title('Key Metrics Summary', fontsize=13, fontweight='bold', pad=20)
    
    plt.savefig('analysis_investment_landscape/investment_landscape_comprehensive.png', 
                dpi=300, bbox_inches='tight')
    print("Comprehensive chart saved as 'investment_landscape_comprehensive.png'")
    plt.close()

def generate_summary_report(investor_type_dist, company_geo, investor_geo, funding_flows, 
                           cross_border_stats, industry_metrics, company_data):
    """Generate a comprehensive markdown summary report"""
    print("\nGenerating summary report...")
    
    report = []
    report.append("# Investment Landscape Analysis")
    report.append("\n## Executive Summary\n")
    report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}")
    report.append(f"\nThis report provides a comprehensive analysis of the wearable technology industry's investment landscape, ")
    report.append("covering investor types, geographic funding clusters, and industry maturity assessment.\n")
    
    # Section 1: Investor Types
    report.append("\n---\n")
    report.append("## 1. Investor Landscape\n")
    report.append("### 1.1 Investor Type Distribution\n")
    
    if not investor_type_dist.empty:
        total_investments = investor_type_dist['Count'].sum()
        report.append(f"**Total Investment Instances:** {total_investments}\n")
        report.append("\n**Top Investor Types:**\n")
        for idx, row in investor_type_dist.head(10).iterrows():
            pct = (row['Count'] / total_investments) * 100
            report.append(f"- **{row['PrimaryInvestorType']}**: {int(row['Count'])} investments ({pct:.1f}%)")
        
        report.append("\n### Key Insights:\n")
        top_investor = investor_type_dist.iloc[0]
        report.append(f"- **{top_investor['PrimaryInvestorType']}** is the dominant investor type, representing {(top_investor['Count']/total_investments)*100:.1f}% of all investments")
        
        # Check for diversity
        top_3_pct = investor_type_dist.head(3)['Count'].sum() / total_investments * 100
        if top_3_pct > 75:
            report.append(f"- The market shows **concentration** in top 3 investor types ({top_3_pct:.1f}% of investments)")
        else:
            report.append(f"- The market shows **diverse** investor participation with top 3 types representing {top_3_pct:.1f}%")
    
    # Section 2: Geographic Analysis
    report.append("\n---\n")
    report.append("## 2. Geographic Funding Clusters\n")
    report.append("### 2.1 Company Distribution\n")
    
    if not company_geo.empty:
        report.append(f"**Countries with Wearable Tech Companies:** {len(company_geo)}\n")
        report.append("\n**Top 10 Countries by Company Count:**\n")
        for idx, row in company_geo.head(10).iterrows():
            funding_str = f"${row['TotalFunding']:.1f}M" if row['TotalFunding'] > 0 else "N/A"
            report.append(f"{idx+1}. **{row['Country']}**: {int(row['CompanyCount'])} companies, Total Funding: {funding_str}")
        
        report.append("\n### 2.2 Investor Distribution\n")
        if not investor_geo.empty:
            report.append(f"\n**Top 10 Countries by Investor Count:**\n")
            for idx, row in investor_geo.head(10).iterrows():
                report.append(f"{idx+1}. **{row['HQCountry']}**: {int(row['InvestorCount'])} investors")
    
    # Cross-border investment
    if isinstance(cross_border_stats, pd.Series) and len(cross_border_stats) > 0:
        domestic = cross_border_stats.get(False, 0)
        cross_border = cross_border_stats.get(True, 0)
        total = domestic + cross_border
        
        report.append("\n### 2.3 Investment Flow Analysis\n")
        report.append(f"- **Domestic Investments**: {int(domestic)} ({(domestic/total*100):.1f}%)")
        report.append(f"- **Cross-Border Investments**: {int(cross_border)} ({(cross_border/total*100):.1f}%)")
        
        if cross_border > domestic:
            report.append("\n**Insight:** The industry shows **strong international investment** with cross-border deals exceeding domestic investments.")
        else:
            report.append("\n**Insight:** The industry shows **regional investment patterns** with domestic investments dominating.")
    
    # Section 3: Industry Stage Assessment
    report.append("\n---\n")
    report.append("## 3. Industry Stage and Maturity Assessment\n")
    
    # Deal activity
    if not industry_metrics['deals_by_year'].empty:
        deals_by_year = industry_metrics['deals_by_year']
        latest_year = int(deals_by_year['Year'].max())
        latest_deals = deals_by_year[deals_by_year['Year'] == latest_year]['DealCount'].values[0]
        
        report.append(f"\n### 3.1 Deal Activity\n")
        report.append(f"- **Most Recent Year Analyzed**: {latest_year}")
        report.append(f"- **Deals in {latest_year}**: {int(latest_deals)}")
        
        if industry_metrics['deal_growth_rate']:
            growth_rate = industry_metrics['deal_growth_rate'] * 100
            report.append(f"- **5-Year CAGR**: {growth_rate:.1f}%")
            
            if growth_rate > 15:
                report.append("\n**Assessment:** The industry is in a **GROWTH** phase with strong deal activity expansion.")
            elif growth_rate > 5:
                report.append("\n**Assessment:** The industry is in a **MATURE GROWTH** phase with moderate expansion.")
            elif growth_rate > 0:
                report.append("\n**Assessment:** The industry is in a **MATURE** phase with stable deal activity.")
            else:
                report.append("\n**Assessment:** The industry is experiencing **CONTRACTION** in deal activity.")
    
    # Funding stage analysis
    if not industry_metrics['stage_distribution'].empty:
        report.append("\n### 3.2 Funding Stage Analysis\n")
        report.append("\n**All-Time Top Funding Stages:**\n")
        for idx, row in industry_metrics['stage_distribution'].head(5).iterrows():
            report.append(f"{idx+1}. {row['VCRound']}: {int(row['Count'])} deals")
        
        if not industry_metrics['recent_stage_dist'].empty:
            report.append("\n**Recent Activity (Last 2 Years):**\n")
            for idx, row in industry_metrics['recent_stage_dist'].head(5).iterrows():
                report.append(f"{idx+1}. {row['VCRound']}: {int(row['Count'])} deals")
            
            # Assess maturity based on stage mix
            recent_stages = industry_metrics['recent_stage_dist'].head(10)
            early_keywords = ['Seed', 'Angel', 'Series A', 'Series B']
            later_keywords = ['Series C', 'Series D', 'Series E', 'Series F', 'Later Stage']
            
            early_count = recent_stages[recent_stages['VCRound'].str.contains('|'.join(early_keywords), case=False, na=False)]['Count'].sum()
            later_count = recent_stages[recent_stages['VCRound'].str.contains('|'.join(later_keywords), case=False, na=False)]['Count'].sum()
            
            report.append("\n**Stage Mix Insights:**")
            if early_count > later_count * 1.5:
                report.append("- Recent activity shows **EARLY-STAGE FOCUS**, indicating new market entrants and innovation")
            elif later_count > early_count * 1.5:
                report.append("- Recent activity shows **LATE-STAGE FOCUS**, indicating market maturation and consolidation")
            else:
                report.append("- Recent activity shows **BALANCED STAGE MIX**, indicating a healthy, diverse ecosystem")
    
    # Valuation trends
    if not industry_metrics['valuation_trends'].empty and len(industry_metrics['valuation_trends']) > 1:
        val_trends = industry_metrics['valuation_trends']
        first_val = val_trends.iloc[0]['median']
        last_val = val_trends.iloc[-1]['median']
        val_growth = ((last_val / first_val) - 1) * 100 if first_val > 0 else 0
        
        report.append(f"\n### 3.3 Valuation Trends\n")
        report.append(f"- **Median Valuation Change**: {val_growth:+.1f}% over analysis period")
        
        if val_growth > 50:
            report.append("- **Insight:** Strong valuation growth indicates **high investor confidence** and **premium pricing**")
        elif val_growth > 0:
            report.append("- **Insight:** Positive valuation growth indicates **stable investor confidence**")
        else:
            report.append("- **Insight:** Declining valuations may indicate **market correction** or **pricing pressure**")
    
    # Company age
    report.append("\n### 3.4 Company Maturity\n")
    age_dist = industry_metrics['age_distribution']
    report.append(f"- **Mean Company Age**: {age_dist['mean']:.1f} years")
    report.append(f"- **Median Company Age**: {age_dist['50%']:.1f} years")
    report.append(f"- **Age Range**: {age_dist['min']:.0f} - {age_dist['max']:.0f} years")
    
    if age_dist['mean'] < 7:
        report.append("\n**Insight:** Companies are relatively **YOUNG**, suggesting an **EMERGING** industry")
    elif age_dist['mean'] < 12:
        report.append("\n**Insight:** Companies show **MODERATE MATURITY**, indicating a **GROWTH** industry")
    else:
        report.append("\n**Insight:** Companies are **WELL-ESTABLISHED**, indicating a **MATURE** industry")
    
    # Section 4: Prospects
    report.append("\n---\n")
    report.append("## 4. Industry Prospects\n")
    
    report.append("### 4.1 Market Outlook\n")
    
    # Synthesize insights
    prospects = []
    
    # Check growth rate
    if industry_metrics['deal_growth_rate'] and industry_metrics['deal_growth_rate'] > 0.10:
        prospects.append("✅ **Strong deal growth** indicates robust market expansion")
    elif industry_metrics['deal_growth_rate'] and industry_metrics['deal_growth_rate'] > 0:
        prospects.append("⚠️ **Moderate growth** suggests stable but slower expansion")
    else:
        prospects.append("⚠️ **Declining deal activity** may signal market challenges")
    
    # Check investor diversity
    if not investor_type_dist.empty:
        diversity_score = len(investor_type_dist[investor_type_dist['Count'] > 5])
        if diversity_score > 5:
            prospects.append("✅ **Diverse investor base** provides multiple funding pathways")
        else:
            prospects.append("⚠️ **Limited investor diversity** may constrain funding options")
    
    # Check international reach
    if isinstance(cross_border_stats, pd.Series):
        cross_border = cross_border_stats.get(True, 0)
        total = cross_border_stats.sum()
        if cross_border / total > 0.3:
            prospects.append("✅ **Strong international investment** indicates global market potential")
    
    # Check stage mix
    if not industry_metrics['recent_stage_dist'].empty:
        late_stage_recent = industry_metrics['recent_stage_dist'][
            industry_metrics['recent_stage_dist']['VCRound'].str.contains('Series C|Series D|Later', case=False, na=False)
        ]['Count'].sum()
        if late_stage_recent > 5:
            prospects.append("✅ **Active late-stage funding** indicates path to exits and maturity")
    
    for prospect in prospects:
        report.append(f"\n{prospect}")
    
    report.append("\n### 4.2 Strategic Recommendations\n")
    report.append("\n**For Investors:**")
    report.append("- Monitor emerging companies in underrepresented geographies for arbitrage opportunities")
    report.append("- Consider stage-appropriate strategies based on recent funding patterns")
    report.append("- Evaluate co-investment opportunities with established investor types")
    
    report.append("\n**For Companies:**")
    report.append("- Target investor types most active in your funding stage")
    report.append("- Consider geographic expansion to access diverse funding sources")
    report.append("- Build relationships with both domestic and international investors")
    
    report.append("\n**For Industry Stakeholders:**")
    report.append("- Industry shows characteristics of a maturing but still growing market")
    report.append("- Continued innovation and market education remain critical")
    report.append("- Geographic expansion and cross-border collaboration present opportunities")
    
    report.append("\n---\n")
    report.append(f"\n*Analysis generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    report.append(f"\n*Based on analysis of {len(company_data)} companies in the wearable technology sector*")
    
    return '\n'.join(report)

def save_data_exports(investor_type_dist, investor_type_evolution, company_geo, 
                     investor_geo, funding_flows, industry_metrics):
    """Save detailed data exports"""
    print("\nExporting data files...")
    
    investor_type_dist.to_csv('analysis_investment_landscape/investor_type_distribution.csv', index=False)
    investor_type_evolution.to_csv('analysis_investment_landscape/investor_type_evolution.csv', index=False)
    company_geo.to_csv('analysis_investment_landscape/company_geographic_distribution.csv', index=False)
    investor_geo.to_csv('analysis_investment_landscape/investor_geographic_distribution.csv', index=False)
    funding_flows.to_csv('analysis_investment_landscape/funding_flows.csv', index=False)
    industry_metrics['deals_by_year'].to_csv('analysis_investment_landscape/deals_by_year.csv', index=False)
    
    if not industry_metrics['stage_distribution'].empty:
        industry_metrics['stage_distribution'].to_csv('analysis_investment_landscape/stage_distribution.csv', index=False)
    
    print("Data files exported successfully")

def main():
    print("="*80)
    print("COMPREHENSIVE INVESTMENT LANDSCAPE ANALYSIS")
    print("="*80)
    
    # Parse companies
    company_data = parse_company_ids('list.txt')
    company_ids = [c['id'] for c in company_data]
    
    print(f"\nAnalyzing {len(company_data)} companies:")
    for i, company in enumerate(company_data, 1):
        print(f"  {i}. {company['name']}")
    
    # Load data
    company_df, deal_df, investor_df = load_data(company_ids)
    
    # Extract investor-deal links
    links_df = extract_investor_deals(deal_df, investor_df)
    
    # Analysis 1: Investor Types
    investor_type_dist, investor_type_evolution, stage_investor_matrix = analyze_investor_types_evolution(links_df)
    
    # Analysis 2: Geographic Clusters
    company_geo, investor_geo, funding_flows, cross_border_stats = analyze_geographic_clusters(
        company_df, investor_df, links_df)
    
    # Analysis 3: Industry Stage Assessment
    industry_metrics = assess_industry_stage(deal_df, links_df, company_df)
    
    # Create visualizations
    create_visualizations(investor_type_dist, investor_type_evolution, stage_investor_matrix,
                         company_geo, investor_geo, funding_flows, cross_border_stats,
                         industry_metrics, company_data)
    
    # Generate report
    report = generate_summary_report(investor_type_dist, company_geo, investor_geo, funding_flows,
                                    cross_border_stats, industry_metrics, company_data)
    
    with open('analysis_investment_landscape/INVESTMENT_LANDSCAPE_REPORT.md', 'w') as f:
        f.write(report)
    
    print("\nSummary report saved as 'INVESTMENT_LANDSCAPE_REPORT.md'")
    
    # Save data exports
    save_data_exports(investor_type_dist, investor_type_evolution, company_geo,
                     investor_geo, funding_flows, industry_metrics)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()

