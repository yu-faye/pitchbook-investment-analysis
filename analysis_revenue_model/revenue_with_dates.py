import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# Company data with dates
companies_data = [
    {"name": "Whoop", "id": "64325-80", "revenue": None, "ebitda": None, "period": "N/A", "date": "N/A"},
    {"name": "Oura", "id": "110783-26", "revenue": 174.59, "ebitda": -34.18, "period": "TTM 4Q2023", "date": "09/30/2023"},
    {"name": "Ultrahuman", "id": "458417-44", "revenue": 100.0, "ebitda": None, "period": "TTM 4Q2025", "date": "03/31/2025"},
    {"name": "Pulsetto", "id": "495718-39", "revenue": 10.0, "ebitda": None, "period": "TTM 4Q2024", "date": "12/31/2024"},
    {"name": "ThingX", "id": "697387-24", "revenue": None, "ebitda": None, "period": "N/A", "date": "N/A"},
    {"name": "Flow Neuroscience", "id": "183205-63", "revenue": 3.12, "ebitda": -5.01, "period": "TTM 4Q2023", "date": "12/31/2023"},
    {"name": "Catapult Sports", "id": "56236-96", "revenue": 108.09, "ebitda": 13.38, "period": "TTM 2Q2025", "date": "09/30/2024"},
    {"name": "GOQii", "id": "65652-22", "revenue": 3.04, "ebitda": None, "period": "TTM 4Q2019", "date": "03/31/2019"},
    {"name": "Empatica", "id": "107433-19", "revenue": 12.19, "ebitda": -1.13, "period": "TTM 4Q2023", "date": "12/31/2023"},
    {"name": "Playermaker", "id": "142343-92", "revenue": None, "ebitda": None, "period": "N/A", "date": "N/A"},
    {"name": "Fitbit", "id": "50982-94", "revenue": 1000.0, "ebitda": None, "period": "TTM 4Q2023", "date": "12/31/2023"},
    {"name": "Zepp Health", "id": "100191-79", "revenue": 182.60, "ebitda": None, "period": "TTM 4Q2024", "date": "12/31/2024"},
    {"name": "Peloton", "id": "61931-08", "revenue": 2621.1, "ebitda": -94.2, "period": "TTM 2Q2025", "date": "12/31/2024"},
]

# Sort by revenue
companies_sorted = sorted(companies_data, key=lambda x: (x['revenue'] is None, -(x['revenue'] or 0)))

# Create main visualization with dates
fig, ax = plt.subplots(figsize=(18, 12))
fig.suptitle('Company Revenue Analysis with Data Period Dates', 
             fontsize=22, fontweight='bold', y=0.98)

# Prepare data
names = [c['name'] for c in companies_sorted]
revenues = [c['revenue'] if c['revenue'] is not None else 0 for c in companies_sorted]
has_revenue = [c['revenue'] is not None for c in companies_sorted]
colors_revenue = ['#2E86AB' if has else '#CCCCCC' for has in has_revenue]

# Create the bars
y_pos = np.arange(len(names))
bars = ax.barh(y_pos, revenues, color=colors_revenue, edgecolor='black', linewidth=1.5, height=0.7)

# Add revenue value labels
for i, (bar, company) in enumerate(zip(bars, companies_sorted)):
    if company['revenue'] is not None:
        # Revenue amount
        ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2, 
                f'${company["revenue"]:.2f}M', 
                va='center', fontsize=11, fontweight='bold', color='#1a1a1a')
        
        # Date label - positioned inside the bar on the left
        if bar.get_width() > 100:  # If bar is wide enough
            ax.text(10, bar.get_y() + bar.get_height()/2, 
                    f'📅 {company["date"]}', 
                    va='center', fontsize=9, color='white', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.4', facecolor=(0, 0, 0, 0.4), edgecolor='none'))
        else:  # For smaller bars, put date on the right
            ax.text(bar.get_width() + 250, bar.get_y() + bar.get_height()/2, 
                    f'📅 {company["date"]}', 
                    va='center', fontsize=9, color='#555555', style='italic')
    else:
        ax.text(10, bar.get_y() + bar.get_height()/2, 
                'No Revenue Data Available', 
                va='center', fontsize=10, color='#666666', style='italic')

ax.set_yticks(y_pos)
ax.set_yticklabels(names, fontsize=12, fontweight='bold')
ax.set_xlabel('Revenue (USD Millions)', fontsize=14, fontweight='bold')
ax.set_title('Annual Revenue by Company with Data Period End Dates', 
             fontsize=16, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=1)
ax.set_axisbelow(True)

# Add legend
legend_elements = [
    Patch(facecolor='#2E86AB', edgecolor='black', label='Revenue Data Available'),
    Patch(facecolor='#CCCCCC', edgecolor='black', label='No Revenue Data')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=11, framealpha=0.9)

# Add summary footer
revenue_count = sum(1 for c in companies_data if c['revenue'] is not None)
total_revenue = sum(c['revenue'] for c in companies_data if c['revenue'] is not None)
fig.text(0.5, 0.02, 
        f'📊 Data Summary: {revenue_count}/13 companies with revenue data | Total Revenue: ${total_revenue:,.1f}M | Source: PitchBook Company.csv',
        ha='center', fontsize=11, style='italic', 
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.4, pad=0.7))

plt.tight_layout(rect=[0, 0.04, 1, 0.97])
plt.savefig('/Users/yufei/SchoolWork/fin/stata/analysis_revenue_model/revenue_with_dates.png', 
            dpi=300, bbox_inches='tight')
print("✓ Revenue chart with dates saved: revenue_with_dates.png")

# Create detailed table visualization
fig2, ax2 = plt.subplots(figsize=(18, 14))
fig2.suptitle('Revenue Data Table - Complete Information with Dates', 
              fontsize=20, fontweight='bold')

ax2.axis('tight')
ax2.axis('off')

# Prepare table data
table_data = []
table_data.append(['#', 'Company Name', 'Company ID', 'Revenue (USD M)', 'EBITDA (USD M)', 
                   'Fiscal Period', 'Period End Date', 'Status'])

for idx, company in enumerate(companies_sorted, 1):
    revenue_str = f"${company['revenue']:.2f}M" if company['revenue'] is not None else "N/A"
    ebitda_str = f"${company['ebitda']:.2f}M" if company['ebitda'] is not None else "N/A"
    status = "✓ Available" if company['revenue'] is not None else "✗ No Data"
    
    table_data.append([
        str(idx),
        company['name'],
        company['id'],
        revenue_str,
        ebitda_str,
        company['period'],
        company['date'],
        status
    ])

# Create table
table = ax2.table(cellText=table_data, cellLoc='left', loc='center',
                 colWidths=[0.05, 0.18, 0.12, 0.12, 0.12, 0.12, 0.12, 0.10])

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.5)

# Style header row
for i in range(8):
    cell = table[(0, i)]
    cell.set_facecolor('#2E86AB')
    cell.set_text_props(weight='bold', color='white', fontsize=11)
    cell.set_edgecolor('white')
    cell.set_linewidth(2)

# Style data rows
for i in range(1, len(table_data)):
    # Alternate row colors
    row_color = '#F0F8FF' if i % 2 == 0 else 'white'
    
    for j in range(8):
        cell = table[(i, j)]
        cell.set_facecolor(row_color)
        cell.set_edgecolor('#CCCCCC')
        
        # Highlight companies with no data
        if table_data[i][7] == "✗ No Data":
            cell.set_facecolor('#FFE6E6')
    
    # Bold company names
    table[(i, 1)].set_text_props(weight='bold', fontsize=10)
    
    # Color-code status column
    status_cell = table[(i, 7)]
    if "Available" in table_data[i][7]:
        status_cell.set_text_props(color='#06A77D', weight='bold')
    else:
        status_cell.set_text_props(color='#D62839', weight='bold')

# Add summary box
summary_text = f"""
KEY STATISTICS:
• Companies with Revenue Data: {revenue_count}/13 ({revenue_count/13*100:.1f}%)
• Total Combined Revenue: ${total_revenue:,.2f}M
• Average Revenue: ${total_revenue/revenue_count:,.2f}M
• Highest Revenue: Peloton (${2621.1:.2f}M)
• Latest Data: 03/31/2025 (Ultrahuman)
• Oldest Data: 03/31/2019 (GOQii - ⚠️ outdated)
"""

ax2.text(0.5, 0.02, summary_text, transform=ax2.transAxes,
        fontsize=11, verticalalignment='bottom', horizontalalignment='center',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5, pad=1),
        family='monospace')

plt.tight_layout(rect=[0, 0.12, 1, 0.96])
plt.savefig('/Users/yufei/SchoolWork/fin/stata/analysis_revenue_model/revenue_data_table.png', 
            dpi=300, bbox_inches='tight')
print("✓ Revenue data table saved: revenue_data_table.png")

# Create timeline visualization showing when data was collected
fig3, ax3 = plt.subplots(figsize=(18, 10))
fig3.suptitle('Revenue Data Timeline - When Was Each Company\'s Revenue Reported?', 
              fontsize=20, fontweight='bold', y=0.97)

# Filter companies with dates AND revenue
companies_with_dates = [c for c in companies_data if c['date'] != 'N/A' and c['revenue'] is not None]

# Convert dates to sortable format
from datetime import datetime
for c in companies_with_dates:
    c['date_obj'] = datetime.strptime(c['date'], '%m/%d/%Y')

companies_by_date = sorted(companies_with_dates, key=lambda x: x['date_obj'])

# Create timeline
dates = [c['date_obj'] for c in companies_by_date]
names_timeline = [c['name'] for c in companies_by_date]
revenues_timeline = [c['revenue'] for c in companies_by_date]

# Create scatter plot with size based on revenue
sizes = [max(r/10, 50) if r else 50 for r in revenues_timeline]  # Scale for visibility
colors_timeline = ['#06A77D' if c['ebitda'] and c['ebitda'] > 0 else '#2E86AB' if c['ebitda'] and c['ebitda'] < 0 else '#FFA500' 
                   for c in companies_by_date]

scatter = ax3.scatter(dates, range(len(names_timeline)), s=sizes, c=colors_timeline, 
                     alpha=0.7, edgecolors='black', linewidth=2)

# Add labels
for i, (date, name, revenue) in enumerate(zip(dates, names_timeline, revenues_timeline)):
    ax3.text(date, i, f'  {name} (${revenue:.1f}M)', 
            va='center', fontsize=10, fontweight='bold')

ax3.set_yticks(range(len(names_timeline)))
ax3.set_yticklabels(['' for _ in names_timeline])
ax3.set_xlabel('Period End Date', fontsize=14, fontweight='bold')
ax3.set_title('Companies Ordered by Data Collection Date (Most Recent at Top)', 
             fontsize=14, pad=20)
ax3.grid(axis='x', alpha=0.3, linestyle='--')
ax3.invert_yaxis()  # Most recent at top

# Add legend
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#06A77D', 
               markersize=12, label='Positive EBITDA', markeredgecolor='black', markeredgewidth=1.5),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#2E86AB', 
               markersize=12, label='Negative EBITDA', markeredgecolor='black', markeredgewidth=1.5),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFA500', 
               markersize=12, label='EBITDA N/A', markeredgecolor='black', markeredgewidth=1.5)
]
ax3.legend(handles=legend_elements, loc='lower right', fontsize=11)

# Add note about data freshness
ax3.text(0.02, 0.98, '⚠️ Note: GOQii data is from 2019 - significantly outdated', 
        transform=ax3.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='#FFE6E6', alpha=0.8, pad=0.7))

plt.tight_layout(rect=[0, 0.02, 1, 0.96])
plt.savefig('/Users/yufei/SchoolWork/fin/stata/analysis_revenue_model/revenue_timeline.png', 
            dpi=300, bbox_inches='tight')
print("✓ Revenue timeline saved: revenue_timeline.png")

print("\n" + "="*70)
print("All visualizations with dates created successfully!")
print("="*70)
print("\nFiles created:")
print("1. revenue_with_dates.png - Main revenue chart with dates on each bar")
print("2. revenue_data_table.png - Complete data table with all information")
print("3. revenue_timeline.png - Timeline showing when data was collected")

