# Valuation Trends Analysis

## Overview
This analysis tracks the valuation changes over time for 14 companies in the health & fitness wearables space.

## Data Summary
- **Companies Analyzed**: 14 companies from list.txt
- **Companies with Valuation Data**: 10 companies
- **Total Valuation Data Points**: 40 deals with valuation information
- **Date Range**: 2007-2031 to 2025-02-17

## Companies Analyzed

### Companies with Multiple Valuation Points:
1. **Peloton** (61931-08) - 7 valuation points
2. **Whoop** (64325-80) - 7 valuation points
3. **Oura** (110783-26) - 8 valuation points
4. **Fitbit** (50982-94) - 7 valuation points
5. **Ultrahuman** (458417-44) - 4 valuation points
6. **GOQii** (65652-22) - 2 valuation points
7. **Zepp Health** (100191-79) - 2 valuation points

### Companies with Single Valuation Point:
8. **Pulsetto** (495718-39) - 1 valuation point
9. **Catapult Sports** (56236-96) - 1 valuation point
10. **Playmaker** (494786-80) - 1 valuation point

### Companies with No Valuation Data:
- ThingX (697387-24)
- Flow Neuroscience (183205-63)
- Empatica (107433-19)
- Sensifai (171678-43)

## Top Companies by Latest Valuation

| Rank | Company | Latest Valuation | Valuation Date | Growth Rate |
|------|---------|------------------|----------------|-------------|
| 1 | Peloton | $8.10 billion | 2019-09-26 | +46,199% |
| 2 | Oura | $5.20 billion | 2024-12-19 | +85,571% |
| 3 | Whoop | $3.60 billion | 2021-08-30 | +33,274% |
| 4 | Fitbit | $2.10 billion | 2021-01-14 | +199,900% |
| 5 | Zepp Health | $653.78 million | 2018-02-08 | +118% |
| 6 | Ultrahuman | $125.49 million | 2024-03-20 | +465% |
| 7 | GOQii | $108.90 million | 2018-11-26 | +247% |
| 8 | Catapult Sports | $55.55 million | 2014-12-19 | - |
| 9 | Playmaker | $42.19 million | 2023-07-03 | - |
| 10 | Pulsetto | $20.78 million | 2025-02-17 | - |

## Key Insights

### Valuation Growth Leaders
1. **Fitbit**: Achieved the highest growth rate of 199,900%, growing from $1.05M (2007) to $2.10B (2021)
2. **Oura**: Second highest growth at 85,571%, from $6.07M (2015) to $5.20B (2024)
3. **Peloton**: Third with 46,199% growth, from $17.5M (2012) to $8.10B (2019)

### Recent Activity (2020-2025)
- **Oura**: Most recent major valuation at $5.2B (Dec 2024) - shows strong recent growth
- **Pulsetto**: New entrant with valuation in Feb 2025
- **Ultrahuman**: Multiple rounds including recent $125M valuation (Mar 2024)

### IPO Companies
Three companies in the dataset went public:
1. **Fitbit**: IPO in June 2015 at $4.11B valuation
2. **Zepp Health**: IPO in Feb 2018 at $653.78M valuation
3. **Catapult Sports**: IPO in Dec 2014 at $55.55M valuation
4. **Peloton**: IPO in Sep 2019 at $8.10B valuation

## Files Generated

### Data Files:
1. **valuation_data_detailed.csv** - All 40 deals with valuation information
   - Includes: company info, deal dates, pre/post-money valuations, deal types, VC rounds
   
2. **valuation_summary_by_company.csv** - Summary statistics for each company
   - Includes: first/latest/peak valuations, growth rates, number of valuation points

### Visualizations:
1. **valuation_trends_all_companies.png** - All companies on one timeline chart
2. **valuation_trends_individual.png** - Individual company charts (3x4 grid)
3. **latest_valuation_comparison.png** - Bar chart comparing latest valuations
4. **valuation_growth_rate.png** - Growth rate comparison chart

## Methodology

### Data Sources:
- **Deal.csv**: Primary source for valuation data (PostValuation and PremoneyValuation fields)
- **list.txt**: List of target companies and their IDs

### Valuation Calculation:
- Preferred: Post-money valuation
- Fallback: Pre-money valuation (if post-money not available)
- All valuations are in USD millions

### Deal Types Included:
- Early Stage VC (Series A, B)
- Later Stage VC (Series C, D, E, F)
- Seed Rounds
- IPOs
- Equity Crowdfunding

## Analysis Date
Generated: October 29, 2025

## Notes
- Valuations are shown in USD millions in the data files
- Growth rates calculated from first to latest known valuation
- Some companies may have additional funding rounds without disclosed valuations
- IPO valuations represent market cap at offering

