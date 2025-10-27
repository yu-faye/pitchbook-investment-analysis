# Wearable Tech Investment Analysis

This repository contains comprehensive analysis of 12 wearable technology companies and their investment patterns.

## 📁 Folder Structure

### Analysis Folders

```
stata/
├── analysis_entry_trends/          # Entry/entrance trends analysis
│   └── (Ready for future entry-specific analysis)
│
├── analysis_investment_trends/     # Overall investment patterns & trends
│   ├── investment_trends_analysis.py
│   ├── investment_trends_analysis.png
│   ├── investment_timeline.png
│   └── INVESTMENT_TRENDS_SUMMARY.md
│
├── analysis_exit_trends/           # Exit events & liquidity analysis
│   ├── exit_analysis.py
│   ├── exit_trends_analysis.png
│   └── EXIT_TRENDS_SUMMARY.md
│
├── analysis_investor_types/        # Investor category analysis
│   ├── investor_types_analysis.py
│   ├── investor_types_by_company.csv
│   ├── company_investor_type_details.csv
│   └── deals_with_investor_categories.csv
│
├── analysis_company_funding/       # Company-specific funding details
│   ├── company_funding_details.csv
│   └── funding_amounts_by_company.csv
│
└── old/                           # Legacy/archived analysis files
    ├── investor_funding_amounts.py
    ├── investor_funding_amounts.png
    ├── investor_types_by_deals.py
    └── investor_types_by_deals.png
```

### Data Files (Root Directory)

- **Company.csv** - Main company information dataset
- **Deal.csv** - Investment deals and funding rounds data
- **Investor.csv** - Investor information dataset
- **filtered_company.dta** - Filtered company data (Stata format)
- **list.txt** - List of 12 companies being analyzed

## 🎯 The 12 Companies Analyzed

1. Whoop
2. Oura
3. Ultrahuman
4. Pulsetto
5. ThingX
6. Flow Neuroscience
7. Catapult Sports (IPO exit in 2014)
8. Coros (Out of Business)
9. GOQii
10. Empatica
11. Sensifai
12. Playmaker

## 📊 Analysis Types

### 1. Entry Trends Analysis (Planned)
**Folder:** `analysis_entry_trends/`

Will analyze:
- When companies entered the market
- Entry mechanisms (seed, VC, accelerator, etc.)
- Market entry waves and timing patterns
- First funding characteristics

**Status:** Folder created, ready for dedicated entry analysis

### 2. Investment Trends Analysis
**Folder:** `analysis_investment_trends/`

**Key Findings:**
- 87 total funding rounds across 12 companies
- Peak investment years: 2021-2022 (11 deals each)
- Market leaders: Oura (16 rounds), Whoop (15 rounds)
- Average time between rounds: 439 days (1.2 years)

**Files:**
- `investment_trends_analysis.py` - Main analysis script
- `investment_trends_analysis.png` - 6-panel visualization dashboard
- `investment_timeline.png` - Timeline of all investments
- `INVESTMENT_TRENDS_SUMMARY.md` - Comprehensive written report

### 3. Exit Trends Analysis
**Folder:** `analysis_exit_trends/`

**Key Findings:**
- Only 1 exit: Catapult Sports (IPO Dec 2014, $55.5M valuation)
- 8.3% exit rate over 14 years
- 90.9% of companies still generating revenue
- Market leaders (Oura, Whoop) remain private despite maturity

**Files:**
- `exit_analysis.py` - Exit analysis script
- `exit_trends_analysis.png` - Exit patterns visualization
- `EXIT_TRENDS_SUMMARY.md` - Detailed exit analysis report

### 4. Investor Types Analysis
**Folder:** `analysis_investor_types/`

Analyzes:
- Types of investors by category
- Investor participation patterns
- Corporate vs VC vs Angel investment trends

**Files:**
- `investor_types_analysis.py` - Analysis script
- `investor_types_by_company.csv` - Investor breakdown by company
- `company_investor_type_details.csv` - Detailed investor categories
- `deals_with_investor_categories.csv` - Deal-level investor data

### 5. Company Funding Analysis
**Folder:** `analysis_company_funding/`

Company-specific funding data:
- Total funding raised by company
- Funding amounts breakdown

**Files:**
- `company_funding_details.csv` - Detailed funding by company
- `funding_amounts_by_company.csv` - Summary funding amounts

## 🔄 Future Analysis

When performing new analysis, create a new folder following the naming convention:
```
analysis_[topic_name]/
```

Examples:
- `analysis_valuation_trends/` - For valuation analysis
- `analysis_geographic_patterns/` - For location-based analysis
- `analysis_sector_comparison/` - For cross-sector comparisons

## 📝 Usage Notes

1. **Python Scripts**: All analysis scripts are Python-based and require pandas, matplotlib, seaborn
2. **Data Source**: Analysis uses Company.csv, Deal.csv, and Investor.csv as primary data sources
3. **Visualizations**: PNG files are high-resolution (300 DPI) suitable for reports
4. **Reports**: Markdown (.md) files contain detailed written analysis and insights

## 🎨 Analysis Workflow

```
1. Create new folder: analysis_[topic]/
2. Write analysis script: [topic]_analysis.py
3. Generate visualizations: [topic]_analysis.png
4. Document findings: [TOPIC]_SUMMARY.md
5. Export data: relevant CSV files
```

## 📈 Key Insights Summary

### Investment Trends
- **Peak Activity:** 2021-2022 (COVID-era health tech boom)
- **Market Leaders:** Oura & Whoop (15-16 rounds each)
- **Average Hold Period:** 1.2 years between funding rounds

### Exit Trends
- **Exit Rate:** 8.3% (1 of 12 companies)
- **Only Exit:** Catapult Sports IPO (2014)
- **Survival Rate:** 90.9% still generating revenue
- **Failure Rate:** 8.3% (Coros out of business)

### Entry Trends
- **First Wave (2011-2015):** Early pioneers
- **Second Wave (2017-2018):** AI/tech focus
- **Third Wave (2020-2021):** COVID health monitoring boom
- **Fourth Wave (2024+):** Latest innovations

---

*Last Updated: October 23, 2025*
*Total Companies: 12*
*Total Funding Rounds: 87*
*Analysis Period: 2011-2025*


