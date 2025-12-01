import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# Company data from list.txt with revenue information
companies_data = [
    {"name": "Whoop", "id": "64325-80", "revenue": None, "ebitda": None, "period": "N/A"},
    {"name": "Oura", "id": "110783-26", "revenue": 174.59, "ebitda": -34.18, "period": "TTM 4Q2023"},
    {"name": "Ultrahuman", "id": "458417-44", "revenue": 100.0, "ebitda": None, "period": "TTM 4Q2025"},
    {"name": "Pulsetto", "id": "495718-39", "revenue": 10.0, "ebitda": None, "period": "TTM 4Q2024"},
    {"name": "ThingX", "id": "697387-24", "revenue": None, "ebitda": None, "period": "N/A"},
    {"name": "Flow Neuroscience", "id": "183205-63", "revenue": 3.12, "ebitda": -5.01, "period": "TTM 4Q2023"},
    {"name": "Catapult Sports", "id": "56236-96", "revenue": 108.09, "ebitda": 13.38, "period": "TTM 2Q2025"},
    {"name": "GOQii", "id": "65652-22", "revenue": 3.04, "ebitda": None, "period": "TTM 4Q2019"},
    {"name": "Empatica", "id": "107433-19", "revenue": 12.19, "ebitda": -1.13, "period": "TTM 4Q2023"},
    {"name": "Playermaker", "id": "142343-92", "revenue": None, "ebitda": None, "period": "N/A"},
    {"name": "Fitbit", "id": "50982-94", "revenue": 1000.0, "ebitda": None, "period": "TTM 4Q2023"},
    {"name": "Zepp Health", "id": "100191-79", "revenue": 182.60, "ebitda": None, "period": "TTM 4Q2024"},
    {"name": "Peloton", "id": "61931-08", "revenue": 2621.1, "ebitda": -94.2, "period": "TTM 2Q2025"},
]

# Sort by revenue (put None values at the end)
companies_sorted = sorted(companies_data, key=lambda x: (x['revenue'] is None, -(x['revenue'] or 0)))

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
fig.suptitle('Revenue & EBITDA Analysis - Wearable Technology Companies', 
             fontsize=20, fontweight='bold', y=0.995)

# Prepare data
names = [c['name'] for c in companies_sorted]
revenues = [c['revenue'] if c['revenue'] is not None else 0 for c in companies_sorted]
has_revenue = [c['revenue'] is not None for c in companies_sorted]
colors_revenue = ['#2E86AB' if has else '#CCCCCC' for has in has_revenue]

# Plot 1: Revenue Bar Chart
bars1 = ax1.barh(names, revenues, color=colors_revenue, edgecolor='black', linewidth=1.2)

# Add value labels on bars
for i, (bar, company) in enumerate(zip(bars1, companies_sorted)):
    if company['revenue'] is not None:
        ax1.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2, 
                f'${company["revenue"]:.1f}M', 
                va='center', fontsize=10, fontweight='bold')
        # Add period info
        ax1.text(5, bar.get_y() + bar.get_height()/2, 
                f'{company["period"]}', 
                va='center', fontsize=8, color='white', style='italic')
    else:
        ax1.text(5, bar.get_y() + bar.get_height()/2, 
                'No Data', 
                va='center', fontsize=9, color='#666666', style='italic')

ax1.set_xlabel('Revenue (USD Millions)', fontsize=13, fontweight='bold')
ax1.set_title('Annual Revenue by Company', fontsize=15, fontweight='bold', pad=15)
ax1.grid(axis='x', alpha=0.3, linestyle='--')
ax1.set_axisbelow(True)

# Add legend for revenue chart
legend_elements = [
    Patch(facecolor='#2E86AB', edgecolor='black', label='Revenue Available'),
    Patch(facecolor='#CCCCCC', edgecolor='black', label='No Revenue Data')
]
ax1.legend(handles=legend_elements, loc='lower right', fontsize=10)

# Plot 2: EBITDA Analysis
companies_with_ebitda = [c for c in companies_sorted if c['ebitda'] is not None]
names_ebitda = [c['name'] for c in companies_with_ebitda]
ebitda_values = [c['ebitda'] for c in companies_with_ebitda]
colors_ebitda = ['#06A77D' if val >= 0 else '#D62839' for val in ebitda_values]

if names_ebitda:
    bars2 = ax2.barh(names_ebitda, ebitda_values, color=colors_ebitda, 
                     edgecolor='black', linewidth=1.2)
    
    # Add value labels
    for bar, company in zip(bars2, companies_with_ebitda):
        x_pos = bar.get_width()
        offset = 2 if x_pos >= 0 else -2
        ha = 'left' if x_pos >= 0 else 'right'
        ax2.text(x_pos + offset, bar.get_y() + bar.get_height()/2, 
                f'${company["ebitda"]:.1f}M', 
                va='center', ha=ha, fontsize=10, fontweight='bold')
    
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=1.5)
    ax2.set_xlabel('EBITDA (USD Millions)', fontsize=13, fontweight='bold')
    ax2.set_title('EBITDA (Earnings Before Interest, Taxes, Depreciation & Amortization)', 
                  fontsize=15, fontweight='bold', pad=15)
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    ax2.set_axisbelow(True)
    
    # Add legend for EBITDA chart
    legend_elements_ebitda = [
        Patch(facecolor='#06A77D', edgecolor='black', label='Positive EBITDA (Profitable Operations)'),
        Patch(facecolor='#D62839', edgecolor='black', label='Negative EBITDA (Operating Losses)')
    ]
    ax2.legend(handles=legend_elements_ebitda, loc='lower right', fontsize=10)
else:
    ax2.text(0.5, 0.5, 'No EBITDA Data Available', 
            ha='center', va='center', fontsize=14, transform=ax2.transAxes)

# Add footer with summary statistics
revenue_count = sum(1 for c in companies_data if c['revenue'] is not None)
total_revenue = sum(c['revenue'] for c in companies_data if c['revenue'] is not None)
avg_revenue = total_revenue / revenue_count if revenue_count > 0 else 0

footer_text = (f'Data Summary: {revenue_count}/{len(companies_data)} companies with revenue data | '
              f'Total Revenue: ${total_revenue:,.1f}M | Average Revenue: ${avg_revenue:,.1f}M | '
              f'Source: PitchBook Company.csv')
fig.text(0.5, 0.01, footer_text, ha='center', fontsize=10, 
        style='italic', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.tight_layout(rect=[0, 0.02, 1, 0.99])
plt.savefig('/Users/yufei/SchoolWork/fin/stata/analysis_revenue_model/revenue_ebitda_visualization.png', 
            dpi=300, bbox_inches='tight')
print("✓ Revenue & EBITDA visualization saved as: revenue_ebitda_visualization.png")

# Create a second visualization: Revenue Distribution Pie Chart
fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(18, 8))
fig2.suptitle('Revenue Distribution & Market Share Analysis', 
              fontsize=18, fontweight='bold')

# Pie chart - companies with revenue
companies_with_rev = [c for c in companies_data if c['revenue'] is not None]
companies_with_rev_sorted = sorted(companies_with_rev, key=lambda x: -x['revenue'])

names_pie = [c['name'] for c in companies_with_rev_sorted]
revenues_pie = [c['revenue'] for c in companies_with_rev_sorted]

# Create color palette
colors_pie = plt.cm.Set3(np.linspace(0, 1, len(names_pie)))

wedges, texts, autotexts = ax3.pie(revenues_pie, labels=names_pie, autopct='%1.1f%%',
                                     colors=colors_pie, startangle=90,
                                     textprops={'fontsize': 10, 'fontweight': 'bold'},
                                     pctdistance=0.85)

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(9)

ax3.set_title('Revenue Market Share\n(Companies with Available Data)', 
             fontsize=14, fontweight='bold', pad=20)

# Bar chart comparing revenue segments
ax4.clear()
segments = {
    'Large Cap\n(>$500M)': sum(c['revenue'] for c in companies_with_rev if c['revenue'] > 500),
    'Mid Cap\n($100-500M)': sum(c['revenue'] for c in companies_with_rev if 100 <= c['revenue'] <= 500),
    'Small Cap\n($10-100M)': sum(c['revenue'] for c in companies_with_rev if 10 <= c['revenue'] < 100),
    'Micro Cap\n(<$10M)': sum(c['revenue'] for c in companies_with_rev if c['revenue'] < 10)
}

segment_names = list(segments.keys())
segment_values = list(segments.values())
segment_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

bars = ax4.bar(segment_names, segment_values, color=segment_colors, 
               edgecolor='black', linewidth=2)

for bar in bars:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
            f'${height:.0f}M',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

ax4.set_ylabel('Total Revenue (USD Millions)', fontsize=12, fontweight='bold')
ax4.set_title('Revenue Distribution by Company Size', fontsize=14, fontweight='bold', pad=20)
ax4.grid(axis='y', alpha=0.3, linestyle='--')
ax4.set_axisbelow(True)

plt.tight_layout()
plt.savefig('/Users/yufei/SchoolWork/fin/stata/analysis_revenue_model/revenue_distribution_analysis.png', 
            dpi=300, bbox_inches='tight')
print("✓ Revenue distribution analysis saved as: revenue_distribution_analysis.png")

# Create individual company cards visualization
fig3 = plt.figure(figsize=(20, 14))
fig3.suptitle('Company Revenue Cards - Detailed Overview', 
              fontsize=20, fontweight='bold', y=0.98)

# Create 4x4 grid for 13 companies
for idx, company in enumerate(companies_data):
    ax = plt.subplot(4, 4, idx + 1)
    
    # Card background
    if company['revenue'] is not None:
        bg_color = '#E8F4F8'
        status_color = '#2E86AB'
    else:
        bg_color = '#F5F5F5'
        status_color = '#999999'
    
    ax.set_facecolor(bg_color)
    
    # Remove axes
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Add border
    for spine in ax.spines.values():
        spine.set_edgecolor(status_color)
        spine.set_linewidth(3)
    
    # Company name
    ax.text(0.5, 0.85, company['name'], 
           ha='center', va='top', fontsize=14, fontweight='bold',
           transform=ax.transAxes, wrap=True)
    
    # Company ID
    ax.text(0.5, 0.72, f"ID: {company['id']}", 
           ha='center', va='top', fontsize=8, style='italic',
           transform=ax.transAxes, color='#666666')
    
    # Revenue
    if company['revenue'] is not None:
        ax.text(0.5, 0.55, f"${company['revenue']:.2f}M", 
               ha='center', va='center', fontsize=18, fontweight='bold',
               transform=ax.transAxes, color='#2E86AB')
        ax.text(0.5, 0.42, 'Revenue', 
               ha='center', va='center', fontsize=10,
               transform=ax.transAxes, color='#666666')
    else:
        ax.text(0.5, 0.50, 'No Revenue Data', 
               ha='center', va='center', fontsize=12, style='italic',
               transform=ax.transAxes, color='#999999')
    
    # EBITDA
    if company['ebitda'] is not None:
        ebitda_color = '#06A77D' if company['ebitda'] >= 0 else '#D62839'
        ax.text(0.5, 0.28, f"EBITDA: ${company['ebitda']:.1f}M", 
               ha='center', va='center', fontsize=10,
               transform=ax.transAxes, color=ebitda_color, fontweight='bold')
    
    # Period
    ax.text(0.5, 0.12, company['period'], 
           ha='center', va='center', fontsize=8,
           transform=ax.transAxes, color='#666666', style='italic')

# Remove empty subplots if any
for idx in range(len(companies_data), 16):
    ax = plt.subplot(4, 4, idx + 1)
    ax.axis('off')

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig('/Users/yufei/SchoolWork/fin/stata/analysis_revenue_model/company_revenue_cards.png', 
            dpi=300, bbox_inches='tight')
print("✓ Company revenue cards saved as: company_revenue_cards.png")

print("\n" + "="*60)
print("All visualizations created successfully!")
print("="*60)
print("\nFiles created:")
print("1. revenue_ebitda_visualization.png - Main revenue & EBITDA chart")
print("2. revenue_distribution_analysis.png - Market share & distribution")
print("3. company_revenue_cards.png - Individual company cards")

