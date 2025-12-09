# Quarterly KPI Dashboard Integration - User Guide

**Date:** 2025-12-09
**Status:** ✅ Integrated and Ready to Use

---

## Overview

The quarterly KPI reporting is now **fully integrated** into your existing KPI Dashboard! You can now view and generate quarterly reports directly from the familiar dashboard interface - no command-line tools needed.

---

## What's New in the Dashboard

### 1. **Quarterly Period Selector**

The period dropdown now includes both quarterly and monthly periods:

```
╔════════════════════════════════════╗
║  QUARTERLY PERIODS                 ║
╠════════════════════════════════════╣
║  Q4 2025 (Quarterly)               ║
║  Q3 2025 (Quarterly)               ║
║  Q2 2025 (Quarterly)               ║
║  Q1 2025 (Quarterly)               ║
║  Q4 2024 (Quarterly)               ║
║  ...                               ║
╠════════════════════════════════════╣
║  MONTHLY PERIODS                   ║
╠════════════════════════════════════╣
║  December 2025                     ║
║  November 2025                     ║
║  October 2025                      ║
║  ...                               ║
╚════════════════════════════════════╝
```

### 2. **Quarterly Report Generation Button**

When you select a quarterly period, a special button appears:

```
┌─────────────────────────────────────────────────┐
│ 📊 Generate & Save Quarterly Report             │
└─────────────────────────────────────────────────┘
```

This button:
- Only appears for quarterly periods
- Calculates all 17 KPIs from your monthly data
- Saves results to the database
- Shows a detailed summary

### 3. **Automatic Quarterly Display**

When viewing a quarterly period, the dashboard automatically:
- Aggregates monthly data into quarterly results
- Shows "(Quarterly)" label on summary cards
- Displays quarterly KPI values and statuses
- Calculates pass/fail using quarterly logic

---

## How to Use Quarterly Reporting

### Step 1: Open KPI Dashboard

Launch the KPI Dashboard from your main application as usual.

### Step 2: Select a Quarterly Period

1. Click the **"Measurement Period"** dropdown
2. Select a quarterly period (e.g., **"Q1 2025 (Quarterly)"**)
3. The dashboard automatically refreshes

### Step 3: View Quarterly Results

The dashboard now shows:

**Summary Cards:**
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Total KPIs      │  │ ✓ Passing       │  │ ✗ Failing       │  │ ⏳ Pending      │
│ 15/17           │  │ 12              │  │ 3               │  │ 2               │
│ (Quarterly)     │  │                 │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

**KPI Overview Table:**
Shows all quarterly aggregated KPI results with pass/fail status.

### Step 4: Generate and Save (If Not Already Saved)

If this is the first time viewing this quarter:

1. Click **"📊 Generate & Save Quarterly Report"**
2. Watch the progress dialog
3. Review the summary popup

**Summary Popup Shows:**
```
✓ Quarterly Report Generated Successfully!

Quarter: 2025-Q1
Period: 2025-01-01 to 2025-03-31

Summary:
  Total KPIs: 17
  With Data: 15
  Passing: 12 (✓)
  Failing: 3 (✗)
  Pending: 2

Pass Rate: 80.0%

The quarterly results have been saved to the database.
You can now export them to PDF or Excel.
```

### Step 5: Export (Optional)

Use the existing export functions:
- **📄 Export to PDF** - Professional PDF report with quarterly data
- **📊 Export to Excel** - Excel workbook with quarterly results

---

## Workflow Comparison

### Monthly Workflow (Unchanged)
```
1. Select monthly period (e.g., "January 2025")
2. Enter KPI data or view calculated results
3. Export reports as needed
```

### Quarterly Workflow (New!)
```
1. Select quarterly period (e.g., "Q1 2025 (Quarterly)")
2. View auto-aggregated quarterly results
3. Click "Generate & Save Quarterly Report" (first time only)
4. Export quarterly reports to PDF/Excel
```

---

## Key Features

### ✅ Automatic Detection

The dashboard automatically detects quarterly periods and:
- Hides the manual data entry tab (not needed for quarterly)
- Shows the quarterly report generation button
- Calculates quarterly aggregations on-the-fly
- Updates labels to show "(Quarterly)"

### ✅ Smart Aggregation

Each KPI is aggregated using the appropriate method:

| KPI Type | Method | Example |
|----------|--------|---------|
| **Safety Incidents** | Sum | FR1: 0.5 + 1.2 + 0.8 = 2.5 |
| **Performance %** | Average | PM Adherence: (96% + 98% + 99%) / 3 = 97.7% |
| **Snapshots** | Latest | WO Backlog: Uses March value |

### ✅ Quarterly Pass/Fail

**Majority Rule:**
- Quarter **passes** if ≥2 out of 3 months passed
- Shows data completeness (e.g., "2/3 months")

### ✅ No Duplicate Work

Once generated and saved:
- Quarterly results are stored in the database
- No need to regenerate unless you update monthly data
- Instantly available when selecting that quarter again

---

## Example Usage Scenarios

### Scenario 1: Monthly Reporting (Business as Usual)

**Every Month:**
1. Open KPI Dashboard
2. Select current month (e.g., "December 2025")
3. Enter/review monthly KPI data
4. Export monthly reports

### Scenario 2: End-of-Quarter Reporting (New!)

**At Quarter End:**
1. Open KPI Dashboard
2. Select the quarter (e.g., "Q4 2025 (Quarterly)")
3. Review auto-calculated quarterly summary
4. Click "Generate & Save Quarterly Report"
5. Review pass/fail statistics
6. Export quarterly report to PDF for management

### Scenario 3: Historical Quarter Review

**Reviewing Past Quarters:**
1. Open KPI Dashboard
2. Select past quarter (e.g., "Q2 2024 (Quarterly)")
3. View saved quarterly results
4. Export for archival or comparison

---

## Visual Guide

### Dashboard with Monthly Period Selected

```
┌─────────────────────────────────────────────────────────┐
│  📅 Measurement Period: [November 2025 ▼]              │
│  [🔄 Refresh Dashboard]                                │
└─────────────────────────────────────────────────────────┘
```
*Normal monthly view - manual data entry available*

### Dashboard with Quarterly Period Selected

```
┌─────────────────────────────────────────────────────────┐
│  📅 Measurement Period: [Q4 2025 (Quarterly) ▼]        │
│  [📊 Generate & Save Quarterly Report] [🔄 Refresh]     │
└─────────────────────────────────────────────────────────┘
```
*Quarterly view - generation button appears automatically*

---

## Tips & Best Practices

### ✅ Do This

1. **Enter monthly data consistently** - Complete all 3 months before generating quarterly reports
2. **Generate quarterly reports at quarter end** - Wait until all monthly data is finalized
3. **Review before saving** - Check the auto-calculated values make sense
4. **Export for archival** - Save quarterly reports as PDF/Excel for records

### ⚠️ Avoid This

1. **Don't generate incomplete quarters** - Ensure all 3 months have data first
2. **Don't regenerate unnecessarily** - Once saved, quarterly data is available instantly
3. **Don't mix up periods** - Make sure you select the right quarter/month

---

## Understanding the Display

### Summary Cards

```
┌─────────────────┐
│ Total KPIs      │
│ 15/17           │  ← 15 KPIs have data out of 17 total
│ (Quarterly)     │  ← Indicates this is quarterly data
└─────────────────┘
```

### KPI Table

| Column | Description |
|--------|-------------|
| **Function** | KPI function code (F1, F2.1, etc.) |
| **KPI Name** | Name of the KPI |
| **Value** | Aggregated quarterly value |
| **Target** | Target/acceptance criteria |
| **Status** | ✓ PASS / ✗ FAIL / N/A |
| **Date** | When quarterly report was generated |
| **Notes** | Aggregation details and source periods |

---

## Troubleshooting

### "No data available for this quarter"

**Cause:** Monthly KPI data hasn't been entered for all 3 months.

**Solution:**
1. Switch to monthly view
2. Enter data for each month in the quarter
3. Return to quarterly view and regenerate

### "Generate button doesn't appear"

**Cause:** A monthly period is selected.

**Solution:**
1. Click the period dropdown
2. Select a quarterly period (shows "Quarterly" label)
3. Button will appear automatically

### "Numbers look wrong"

**Cause:** May need to understand aggregation method.

**Solution:**
1. Check the KPI's aggregation method (average/sum/latest)
2. Verify monthly data is correct
3. See notes column for calculation details

---

## Data Storage

### Database Format

Quarterly results are stored alongside monthly data:

| measurement_period | Type |
|--------------------|------|
| `2025-01` | Monthly (January 2025) |
| `2025-02` | Monthly (February 2025) |
| `2025-03` | Monthly (March 2025) |
| `2025-Q1` | **Quarterly** (Q1 2025) |

### Notes Field

Contains aggregation details:
```
"Quarterly aggregation (average) from periods: 2025-01, 2025-02, 2025-03.
Calculated on 2025-12-09 14:30:15"
```

---

## Benefits of Integrated Quarterly Reporting

✅ **No Command-Line Required** - Everything in the familiar UI
✅ **Automatic Calculations** - No manual quarterly data entry
✅ **Consistent Interface** - Same dashboard for monthly and quarterly
✅ **One-Click Generation** - Simple button click to create reports
✅ **Instant Access** - View any past quarter immediately
✅ **Professional Output** - Export to PDF/Excel like monthly reports
✅ **No Extra Training** - Uses existing dashboard skills

---

## Complete User Journey

### End-to-End Example: Q1 2025 Report

**January 2025:**
1. Enter monthly KPI data for January
2. Review and export monthly report

**February 2025:**
1. Enter monthly KPI data for February
2. Review and export monthly report

**March 2025:**
1. Enter monthly KPI data for March
2. Review and export monthly report

**Early April 2025 (Quarter End):**
1. Open KPI Dashboard
2. Select **"Q1 2025 (Quarterly)"** from period dropdown
3. Review auto-calculated quarterly summary
4. Click **"📊 Generate & Save Quarterly Report"**
5. Review success popup showing:
   - 17 KPIs processed
   - 15 with data, 2 pending
   - 12 passing, 3 failing
   - 80% pass rate
6. Click **"📄 Export to PDF"**
7. Present professional quarterly report to management ✓

---

## Summary

The quarterly KPI reporting is now **seamlessly integrated** into your existing dashboard:

- ✅ Select quarterly periods from the same dropdown
- ✅ View auto-aggregated quarterly results
- ✅ Generate reports with one button click
- ✅ Export to PDF/Excel like monthly reports
- ✅ No changes to your monthly workflow

**Everything you need for quarterly reporting is now in the dashboard you already know!**

---

**Questions?** Refer to the full guide in `QUARTERLY_KPI_GUIDE.md` or the summary in `QUARTERLY_SUMMARY.md`.
