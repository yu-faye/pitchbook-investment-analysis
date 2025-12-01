# Valuation Trends Analysis

This folder contains valuation analysis for companies listed in `list.txt`.

## 📁 Folder Structure

```
analysis_valuation_trends/
├── README.md                           # This file
├── scripts/                            # Python analysis scripts
│   ├── valuation_trends_analysis.py   # Main analysis (disclosed valuations only)
│   ├── valuation_trends_analysis_v2.py # Enhanced analysis (includes undisclosed deals)
│   └── latest_valuation_table.py      # Generate latest valuation table
├── data/                               # Data files (CSV)
│   ├── valuation_data_detailed.csv    # All deals with valuation data
│   ├── valuation_summary_by_company.csv # Company-level summary
│   ├── all_deals_complete.csv          # All deals (disclosed + undisclosed)
│   ├── company_summary_complete.csv    # Summary with disclosure statistics
│   └── latest_valuation_table.csv     # Latest valuation table
├── visualizations/                     # Generated charts (PNG)
│   ├── valuation_trends_all_companies.png
│   ├── valuation_trends_individual.png
│   ├── valuation_trends_individual_enhanced.png
│   ├── valuation_trends_with_undisclosed.png
│   ├── latest_valuation_comparison.png
│   ├── valuation_growth_rate.png
│   └── deal_disclosure_by_company.png
└── docs/                               # Documentation
    ├── VALUATION_TRENDS_SUMMARY.md
    └── VALUATION_TRENDS_SUMMARY_ENHANCED.md
```

## Quick Start

### 🆕 Enhanced Visualizations (includes undisclosed deals)
- `visualizations/valuation_trends_with_undisclosed.png` - Timeline with hollow circles for undisclosed deals
- `visualizations/valuation_trends_individual_enhanced.png` - Individual charts with deal counts
- `visualizations/deal_disclosure_by_company.png` - Disclosure rate comparison

### 📊 Original Visualizations (disclosed valuations only)
- `visualizations/valuation_trends_all_companies.png` - All company valuations on one chart
- `visualizations/valuation_trends_individual.png` - Individual charts for each company
- `visualizations/latest_valuation_comparison.png` - Compare latest valuations with dates
- `visualizations/valuation_growth_rate.png` - Compare growth rates

### 📄 Documentation
- `docs/VALUATION_TRENDS_SUMMARY_ENHANCED.md` - Enhanced summary with disclosure analysis
- `docs/VALUATION_TRENDS_SUMMARY.md` - Original analysis summary

### 📈 Data Files
- `data/all_deals_complete.csv` - All 119 deals (disclosed + undisclosed)
- `data/company_summary_complete.csv` - Summary with disclosure statistics
- `data/valuation_data_detailed.csv` - All 40 deals with valuation data
- `data/valuation_summary_by_company.csv` - Summary statistics by company
- `data/latest_valuation_table.csv` - Latest valuation table for all companies

## Key Findings

### Top 5 Companies by Latest Valuation:
1. 🥇 **Peloton**: $8.10 billion (Sep 2019)
2. 🥈 **Oura**: $5.20 billion (Dec 2024) 
3. 🥉 **Whoop**: $3.60 billion (Aug 2021)
4. **Fitbit**: $2.10 billion (Jan 2021)
5. **Zepp Health**: $653.78 million (Feb 2018)

### Highest Growth Companies:
1. **Fitbit**: +199,900% growth
2. **Oura**: +85,571% growth
3. **Peloton**: +46,199% growth

### Data Coverage:
- **14 companies** analyzed
- **10 companies** with valuation data
- **40 total** valuation data points (disclosed)
- **119 total** deals (disclosed + undisclosed)
- **7-year** average tracking period

## How to Use This Analysis

### For Quick Insights:
1. Open `docs/VALUATION_TRENDS_SUMMARY.md` for executive summary
2. View `visualizations/latest_valuation_comparison.png` to see current valuations

### For Detailed Analysis:
1. Open `data/valuation_data_detailed.csv` in Excel or a data tool
2. Filter by company to see all deals and rounds
3. View `visualizations/valuation_trends_individual.png` for company-specific trends

### For Disclosure Analysis:
1. Read `docs/VALUATION_TRENDS_SUMMARY_ENHANCED.md`
2. Check `data/all_deals_complete.csv` for all deals
3. View `visualizations/deal_disclosure_by_company.png` for disclosure rates

## Regenerating Analysis

To regenerate the analysis with updated data:

```bash
cd /Users/yufei/SchoolWork/fin/stata/analysis_valuation_trends

# Run main analysis (disclosed valuations only)
python3 scripts/valuation_trends_analysis.py

# Run enhanced analysis (includes undisclosed deals)
python3 scripts/valuation_trends_analysis_v2.py

# Generate latest valuation table
python3 scripts/latest_valuation_table.py
```

**Note:** Make sure the following files are in the parent directory:
- `Deal.csv`
- `list.txt`

## Files Description

| Category | File | Description |
|----------|------|-------------|
| **Scripts** | `scripts/valuation_trends_analysis.py` | Main analysis script (disclosed valuations) |
| | `scripts/valuation_trends_analysis_v2.py` | Enhanced analysis (all deals) |
| | `scripts/latest_valuation_table.py` | Generate latest valuation table |
| **Data** | `data/valuation_data_detailed.csv` | All deals with valuation info |
| | `data/valuation_summary_by_company.csv` | Company-level statistics |
| | `data/all_deals_complete.csv` | All deals (disclosed + undisclosed) |
| | `data/company_summary_complete.csv` | Summary with disclosure stats |
| | `data/latest_valuation_table.csv` | Latest valuation table |
| **Visualizations** | `visualizations/valuation_trends_all_companies.png` | Timeline showing all companies |
| | `visualizations/valuation_trends_individual.png` | Grid of individual company charts |
| | `visualizations/latest_valuation_comparison.png` | Bar chart of latest valuations |
| | `visualizations/valuation_growth_rate.png` | Growth rate comparison |
| | `visualizations/valuation_trends_with_undisclosed.png` | Timeline with all deals |
| | `visualizations/valuation_trends_individual_enhanced.png` | Enhanced individual charts |
| | `visualizations/deal_disclosure_by_company.png` | Disclosure rate comparison |
| **Documentation** | `docs/VALUATION_TRENDS_SUMMARY.md` | Detailed analysis summary |
| | `docs/VALUATION_TRENDS_SUMMARY_ENHANCED.md` | Enhanced summary with disclosure analysis |

## Data Notes

- All valuations are in **USD millions**
- Valuation preference: Post-money (with pre-money fallback)
- Data source: Deal.csv from PitchBook
- Includes: VC rounds, IPOs, equity crowdfunding, PIPE deals
- Date range: 2007 to 2025

## Companies Included

### With Valuation Data (10):
✅ Whoop, Oura, Ultrahuman, Pulsetto, Catapult Sports, GOQii, Playmaker, Fitbit, Zepp Health, Peloton

### Without Valuation Data (4):
❌ ThingX, Flow Neuroscience, Empatica, Sensifai

---

**Analysis Date**: November 5, 2025  
**Folder Structure**: Organized by type (scripts/data/visualizations/docs)
