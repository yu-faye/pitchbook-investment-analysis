# Exit IPO Information Corrections

**Date**: November 26, 2025  
**Issue**: Company profiles incorrectly marked many privately-held companies as having IPO exits

---

## Summary of Corrections

### ✅ Companies with ACTUAL IPO Exits (3 companies)

1. **Catapult Sports** (56236-96)
   - Exchange: ASX
   - Ticker: CAT
   - IPO Date: December 19, 2014
   - Status: Publicly Held
   - ✓ Already correctly marked

2. **Peloton** (61931-08)
   - Exchange: NASDAQ
   - Ticker: PTON
   - IPO Date: September 26, 2019
   - Status: Publicly Held
   - ✓ Already correctly marked

3. **Zepp Health** (100191-79)
   - Exchange: NYSE
   - Ticker: ZEPP
   - IPO Date: February 8, 2018
   - Status: Publicly Held
   - ✓ Already correctly marked

---

### 🔄 Companies with Acquisition Exits (2 companies)

4. **Fitbit** (50982-94)
   - Previous Status: IPO'd June 18, 2015 (NYSE: FIT)
   - Acquisition: Acquired by Alphabet (Google) for $2.1B on January 14, 2021
   - Current Status: Privately Held (backing)
   - ✅ CORRECTED from "Yes (IPO)" to "Yes (Acquisition)"

5. **Playermaker** (142343-92)
   - Status: Venture Capital-Backed, Privately Held
   - ✅ CORRECTED from "Yes (IPO)" to "No"

---

### ❌ Companies INCORRECTLY Marked as IPO - Now Corrected (9 companies)

The following companies were **incorrectly marked as "Yes (IPO)"** but are actually **privately held** with no exit events:

6. **Empatica** (107433-19)
   - Status: Venture Capital-Backed, Privately Held
   - ✅ CORRECTED from "Yes (IPO)" to "No"

7. **Flow Neuroscience** (183205-63)
   - Status: Venture Capital-Backed, Privately Held
   - ✅ CORRECTED from "Yes (IPO)" to "No"

8. **GOQii** (65652-22)
   - Status: Venture Capital-Backed, Privately Held
   - ✅ CORRECTED from "Yes (IPO)" to "No"

9. **Oura** (110783-26)
   - Status: Venture Capital-Backed, Privately Held
   - Last Valuation: $5.2B (December 2024)
   - ✅ CORRECTED from "Yes (IPO)" to "No"

10. **Pulsetto** (495718-39)
    - Status: Venture Capital-Backed, Privately Held
    - ✅ CORRECTED from "Yes (IPO)" to "No"

11. **ThingX** (697387-24)
    - Status: Venture Capital-Backed, Privately Held
    - ✅ CORRECTED from "Yes (IPO)" to "No"

13. **Ultrahuman** (458417-44)
    - Status: Venture Capital-Backed, Privately Held
    - Last Valuation: $125.5M (March 2024)
    - ✅ CORRECTED from "Yes (IPO)" to "No"

14. **Whoop** (64325-80)
    - Status: Venture Capital-Backed, Privately Held
    - Last Valuation: $3.6B (August 2021)
    - ✅ CORRECTED from "Yes (IPO)" to "No"

---

## Files Corrected

### Individual Company Reports (APPENDIX files)
All 13 APPENDIX files have been updated:
- ✅ APPENDIX_01_Catapult_Sports.md
- ✅ APPENDIX_02_Empatica.md
- ✅ APPENDIX_03_Fitbit.md
- ✅ APPENDIX_04_Flow_Neuroscience.md
- ✅ APPENDIX_05_GOQii.md
- ✅ APPENDIX_06_Oura.md
- ✅ APPENDIX_07_Peloton.md
- ✅ APPENDIX_08_Playermaker.md
- ✅ APPENDIX_09_Pulsetto.md
- ✅ APPENDIX_10_ThingX.md
- ✅ APPENDIX_12_Ultrahuman.md
- ✅ APPENDIX_13_Whoop.md
- ✅ APPENDIX_14_Zepp_Health.md

### Master Document
- ✅ MASTER_DOCUMENT.md - All 13 company sections updated

---

## Verification

You can verify the corrections by running:

```bash
cd analysis_company_profiles/reports
grep -A 3 "Exit Events" MASTER_DOCUMENT.md | grep "Exit Event"
```

Expected output shows:
- 3 companies with "Yes (IPO)"
- 0 companies with "Yes (Acquisition)"
- 10 companies with "No"

---

## Root Cause

The original data extraction likely misinterpreted any company that had an IPO deal type in their financing history as having an IPO exit, without checking:
1. Current ownership status (Publicly Held vs Privately Held)
2. Whether the IPO was successful
3. Whether the company was subsequently acquired (like Fitbit)

The correct logic should be:
- **IPO Exit** = OwnershipStatus == "Publicly Held" AND has Exchange/Ticker
- **Acquisition Exit** = OwnershipStatus == "Acquired/Merged" OR acquired after IPO
- **No Exit** = OwnershipStatus == "Privately Held (backing)"

---

*Corrections completed: November 26, 2025*


