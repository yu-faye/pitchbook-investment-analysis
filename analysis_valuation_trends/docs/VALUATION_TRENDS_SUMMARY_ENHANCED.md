# Enhanced Valuation Trends Analysis

## Overview
This enhanced analysis tracks ALL deals for 14 companies in the health & fitness wearables space, clearly distinguishing between deals with disclosed valuations and those without.

## Key Finding: Most Deals Don't Disclose Valuations! 🔍

**Overall Statistics:**
- **Total Deals**: 119
- **Deals with Disclosed Valuations**: 40 (33.6%)
- **Deals without Disclosed Valuations**: 79 (66.4%)

This means that **2 out of 3 deals don't publicly disclose their valuation!**

## Why This Matters

When you see a company with "only 1 valuation point," it doesn't mean they've only raised money once. It means:
- They've had multiple funding rounds
- Most valuations were kept confidential
- Only certain deals (like IPOs, major VC rounds) disclosed valuations

## Company-by-Company Breakdown

### High Activity Companies (10+ deals):

| Company | Total Deals | Disclosed | Undisclosed | Disclosure Rate |
|---------|-------------|-----------|-------------|-----------------|
| **Peloton** | 16 | 7 | 9 | 44% |
| **Oura** | 16 | 8 | 8 | 50% |
| **Whoop** | 15 | 7 | 8 | 47% |
| **Fitbit** | 13 | 7 | 6 | 54% |
| **Flow Neuroscience** | 11 | 0 | 11 | 0% ⚠️ |

### Medium Activity Companies (5-9 deals):

| Company | Total Deals | Disclosed | Undisclosed | Disclosure Rate |
|---------|-------------|-----------|-------------|-----------------|
| **GOQii** | 9 | 2 | 7 | 22% |
| **Empatica** | 7 | 0 | 7 | 0% ⚠️ |
| **Ultrahuman** | 6 | 4 | 2 | 67% ✅ |
| **Pulsetto** | 6 | 1 | 5 | 17% |
| **Catapult Sports** | 6 | 1 | 5 | 17% |
| **Sensifai** | 6 | 0 | 6 | 0% ⚠️ |
| **Zepp Health** | 5 | 2 | 3 | 40% |

### Low Activity Companies (1-2 deals):

| Company | Total Deals | Disclosed | Undisclosed | Disclosure Rate |
|---------|-------------|-----------|-------------|-----------------|
| **Playmaker** | 2 | 1 | 1 | 50% |
| **ThingX** | 1 | 0 | 1 | 0% |

## What Types of Deals DON'T Disclose Valuations?

Based on the data, deals without disclosed valuations typically include:

1. **Corporate funding** - Strategic investments from companies
2. **Accelerator programs** - Y Combinator, etc.
3. **PIPE deals** - Private Investment in Public Equity (post-IPO)
4. **Early angel rounds** - Smaller, private investments
5. **Debt financing** - Loans and credit facilities
6. **Grant funding** - Government or foundation grants

## What Types of Deals DO Disclose Valuations?

Valuations are most commonly disclosed in:

1. **IPOs** - Always disclosed (market cap)
2. **Major VC rounds** - Series A, B, C, etc. (often disclosed)
3. **Merger/Acquisition** - Transaction price
4. **Later stage VC** - Series D+ (more likely to be disclosed)
5. **Equity crowdfunding** - Usually disclosed

## Top Companies by Latest Valuation

| Rank | Company | Latest Valuation | Date | Total Deals | % Disclosed |
|------|---------|------------------|------|-------------|-------------|
| 1 | Peloton | $8.10B | 2019-09-26 | 16 | 44% |
| 2 | Oura | $5.20B | 2024-12-19 | 16 | 50% |
| 3 | Whoop | $3.60B | 2021-08-30 | 15 | 47% |
| 4 | Fitbit | $2.10B | 2021-01-14 | 13 | 54% |
| 5 | Zepp Health | $653.78M | 2018-02-08 | 5 | 40% |

## Notable Findings

### 🏆 Best Disclosure Rate: **Ultrahuman (67%)**
- 4 out of 6 deals disclosed valuations
- Strong transparency with investors
- All major VC rounds disclosed

### ⚠️ Zero Disclosure: 4 Companies
- **Flow Neuroscience** (11 deals, 0 disclosed)
- **Empatica** (7 deals, 0 disclosed)
- **Sensifai** (6 deals, 0 disclosed)
- **ThingX** (1 deal, 0 disclosed)

These companies either:
- Are very early stage (ThingX)
- Rely on grants/corporate funding
- Prefer complete privacy
- Haven't had major institutional VC rounds

### 📊 Most Active but Secretive: **Flow Neuroscience**
- 11 total deals (tied for most active)
- 0 valuations disclosed
- Likely grant-funded or early-stage corporate deals

## Visualizations Explained

### 1. Timeline Chart
**File**: `valuation_trends_with_undisclosed.png`
- **Solid circles** = Disclosed valuation
- **Hollow circles** = Undisclosed valuation deal occurred
- Position of hollow circles = last known valuation (for context)

### 2. Individual Company Charts
**File**: `valuation_trends_individual_enhanced.png`
- Each chart shows company name + deal counts
- **Blue filled** = Disclosed post-money valuation
- **Purple square** = Disclosed pre-money valuation
- **Red hollow** = Undisclosed valuation
- Title shows: "X disclosed, Y undisclosed"

### 3. Disclosure Rate Chart
**File**: `deal_disclosure_by_company.png`
- **Green bar** = Deals with disclosed valuations
- **Red bar** = Deals without disclosed valuations
- Shows relative transparency of each company

## Files Generated

### Enhanced Data Files:
1. **all_deals_complete.csv** - All 119 deals (disclosed + undisclosed)
2. **company_summary_complete.csv** - Summary with disclosure statistics
3. **valuation_data_detailed.csv** - Only the 40 deals with valuations (original)

### Enhanced Visualizations:
1. **valuation_trends_with_undisclosed.png** - Timeline with hollow circles for undisclosed
2. **valuation_trends_individual_enhanced.png** - Individual charts with deal counts
3. **deal_disclosure_by_company.png** - NEW: Disclosure rate comparison
4. **latest_valuation_comparison.png** - Bar chart of latest valuations (original)
5. **valuation_growth_rate.png** - Growth rate comparison (original)

## Implications for Analysis

### What This Means:
1. **Gaps in data are normal** - Most companies don't disclose most valuations
2. **IPO companies show more** - Public offerings require disclosure
3. **Early stage = less disclosure** - Smaller companies keep valuations private
4. **Strategic funding is opaque** - Corporate investments rarely disclose valuations

### What to Watch:
- Companies with many deals but few valuations may be:
  - Raising debt instead of equity
  - Getting corporate strategic investments
  - Using non-traditional funding (grants, revenue-based financing)
  
- Companies with high disclosure rates may be:
  - More transparent with stakeholders
  - Raising from institutional VCs (who sometimes require disclosure)
  - In competitive fundraising environments

## Analysis Date
Generated: October 29, 2025

## Methodology

### Data Source:
- PitchBook Deal.csv database
- Includes all deal types: VC, corporate, debt, IPO, M&A, etc.

### Disclosure Classification:
- **Disclosed**: Has PremoneyValuation OR PostValuation field populated
- **Undisclosed**: Both valuation fields empty/null

### Visualization Rules:
- Hollow circles placed at last known valuation height (for context)
- Companies with no disclosed valuations shown on x-axis timeline only
- All dates converted to datetime for accurate chronological ordering

---

💡 **Key Takeaway**: When analyzing venture funding, remember that disclosed valuations are the exception, not the rule. A company with "only 1 valuation" may actually have 10+ funding events!

