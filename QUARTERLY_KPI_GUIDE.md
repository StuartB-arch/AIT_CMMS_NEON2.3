# Quarterly KPI Calculator - User Guide

**Author:** Claude
**Date:** 2025-12-09
**Version:** 1.0

## Overview

The Quarterly KPI Calculator aggregates your monthly KPI data into quarterly summaries for Q1, Q2, Q3, and Q4 reporting. This allows you to generate quarterly reports from your existing monthly KPI data without additional data entry.

## Table of Contents

1. [How It Works](#how-it-works)
2. [Quick Start](#quick-start)
3. [Using the Command-Line Script](#using-the-command-line-script)
4. [Integration with Dashboard](#integration-with-dashboard)
5. [Aggregation Methods](#aggregation-methods)
6. [Database Storage](#database-storage)
7. [API Reference](#api-reference)
8. [Examples](#examples)

---

## How It Works

### Quarter Definition

- **Q1** = January, February, March (months 01-03)
- **Q2** = April, May, June (months 04-06)
- **Q3** = July, August, September (months 07-09)
- **Q4** = October, November, December (months 10-12)

### Aggregation Process

The calculator automatically:

1. **Retrieves** monthly KPI data for the 3 months in the quarter
2. **Aggregates** the data using the appropriate method for each KPI
3. **Calculates** quarterly pass/fail status
4. **Generates** summary reports
5. **Optionally saves** results to database with period format `YYYY-QN` (e.g., `2025-Q1`)

---

## Quick Start

### Method 1: Command-Line Script (Easiest)

```bash
# List available quarters with data
python generate_quarterly_report.py --list-quarters

# Generate Q1 2025 report (preview only)
python generate_quarterly_report.py --year 2025 --quarter 1

# Generate and save to database
python generate_quarterly_report.py --year 2025 --quarter 1 --save

# Export to file
python generate_quarterly_report.py --year 2025 --quarter 1 --output q1_report.txt
```

### Method 2: Python Code

```python
from kpi_quarterly_calculator import KPIQuarterlyCalculator
from dbconnect import DatabaseConnectionPool

# Create database connection
pool = DatabaseConnectionPool(min_connections=1, max_connections=5)

# Create calculator
calculator = KPIQuarterlyCalculator(pool)

# Generate quarterly report
report = calculator.generate_quarterly_report(
    year=2025,
    quarter=1,
    save_to_db=True,
    calculated_by='your_username'
)

# Access results
print(f"Total KPIs: {report['statistics']['total_kpis']}")
print(f"Passing: {report['statistics']['kpis_passing']}")
print(f"Failing: {report['statistics']['kpis_failing']}")

# Print summary table
summary = calculator.export_quarterly_summary_table(2025, 1)
print(summary)
```

---

## Using the Command-Line Script

The `generate_quarterly_report.py` script provides easy command-line access to quarterly reporting.

### Commands

#### List Available Quarters

```bash
python generate_quarterly_report.py --list-quarters
```

Output:
```
======================================================================
AVAILABLE QUARTERS WITH KPI DATA
======================================================================

Found 4 quarter(s) with data:

  Q4 2024         (2024-Q4)     Months: 2024-10, 2024-11, 2024-12
  Q3 2024         (2024-Q3)     Months: 2024-07, 2024-08, 2024-09
  Q2 2024         (2024-Q2)     Months: 2024-04, 2024-05, 2024-06
  Q1 2024         (2024-Q1)     Months: 2024-01, 2024-02, 2024-03

======================================================================
```

#### Generate Quarterly Report

```bash
# Preview report (don't save to database)
python generate_quarterly_report.py --year 2025 --quarter 1

# Generate and save to database
python generate_quarterly_report.py --year 2025 --quarter 1 --save
```

#### Export to File

```bash
# Export to text file
python generate_quarterly_report.py --year 2025 --quarter 1 --output report.txt --format txt

# Export to JSON
python generate_quarterly_report.py --year 2025 --quarter 1 --output report.json --format json
```

#### Generate All Quarters

```bash
# Generate reports for all available quarters
python generate_quarterly_report.py --all --save
```

### Script Output

The script provides:

1. **Summary Table** - Overview of all KPIs with values and status
2. **Statistics** - Pass/fail rates and data completeness
3. **Detailed Results** - KPI details organized by function
4. **Save Confirmation** - Database save status

---

## Integration with Dashboard

### Option 1: Modify KPI Dashboard UI

You can add quarterly reporting to the existing KPI Dashboard (`kpi_ui.py`):

```python
# Add to kpi_ui.py imports
from kpi_quarterly_calculator import KPIQuarterlyCalculator

# Add to KPIDashboard.__init__()
self.quarterly_calculator = KPIQuarterlyCalculator(pool)

# Add quarterly period selector
def populate_periods(self):
    """Populate period dropdown with monthly and quarterly periods"""
    self.period_combo.clear()
    current = datetime.now()

    # Add quarterly periods
    for year in [current.year, current.year - 1]:
        for quarter in [4, 3, 2, 1]:
            period = f"{year}-Q{quarter}"
            display = f"Q{quarter} {year} (Quarterly)"
            self.period_combo.addItem(display, period)

    # Add monthly periods (existing code)
    for i in range(12):
        month = current.month - i
        year = current.year
        while month < 1:
            month += 12
            year -= 1
        period = f"{year}-{month:02d}"
        display = datetime(year, month, 1).strftime("%B %Y")
        self.period_combo.addItem(display, period)

# Add quarterly calculation button
def on_period_changed(self, text):
    """Handle period selection change"""
    period = self.period_combo.currentData()

    # Check if quarterly period
    if period and 'Q' in period:
        # Quarterly period selected
        year, quarter = period.split('-Q')
        self.calculate_quarterly_view(int(year), int(quarter))
    else:
        # Monthly period (existing code)
        self.current_period = period
        self.refresh_dashboard()
```

### Option 2: Create Standalone Quarterly Dashboard

Create a new file `kpi_quarterly_dashboard.py` based on the existing dashboard but focused on quarterly reporting.

---

## Aggregation Methods

Different KPIs use different aggregation methods to properly summarize quarterly performance:

### Methods Explained

| Method | Description | Use Case |
|--------|-------------|----------|
| **Average** | Mean of 3 monthly values | Performance rates, percentages |
| **Sum** | Total of 3 monthly values | Count-based metrics (incidents, totals) |
| **Latest** | Most recent month's value | Snapshot metrics (backlog, age) |
| **Min** | Minimum of 3 monthly values | Best-case scenarios |
| **Max** | Maximum of 3 monthly values | Worst-case scenarios |

### KPI Aggregation Mapping

| KPI | Method | Rationale |
|-----|--------|-----------|
| FR1 (Injury Frequency Rate) | Sum | Total injuries across quarter |
| Near Miss | Sum | Total near misses across quarter |
| TTR Adherence | Average | Average adherence rate |
| MTBF | Average | Average time between failures |
| Technical Availability | Average | Average availability percentage |
| MRT (Response Time) | Average | Average response time |
| WO opened vs closed | Latest | Current status at quarter end |
| WO Backlog | Latest | Current backlog at quarter end |
| WO age profile | Latest | Current age profile at quarter end |
| PM Adherence | Average | Average adherence across quarter |
| Top Breakdown | Latest | Most recent analysis |
| Process Confirmation | Average | Average confirmation score |
| Purchaser Satisfaction | Average | Average satisfaction |
| Non-Conformances Raised | Sum | Total raised across quarter |
| Non-Conformances Closed | Average | Average closure rate |
| Quote Delivery Time | Average | Average delivery time |
| Satisfaction Survey | Latest | Most recent survey (yearly) |

### Quarterly Pass/Fail Logic

For averaged/summed KPIs:
- **PASS**: At least 2 out of 3 months passed (majority rule)
- **FAIL**: Less than 2 months passed
- **N/A**: Insufficient data to determine

For latest KPIs:
- Uses the most recent month's pass/fail status

---

## Database Storage

### Storage Format

Quarterly results are stored in the existing `kpi_results` table using a special period format:

- **Monthly periods**: `YYYY-MM` (e.g., `2025-01`)
- **Quarterly periods**: `YYYY-QN` (e.g., `2025-Q1`)

This allows monthly and quarterly data to coexist in the same table.

### Schema

```sql
-- Quarterly results use the same table structure
INSERT INTO kpi_results (
    kpi_name,
    measurement_period,  -- Format: 'YYYY-QN' (e.g., '2025-Q1')
    calculated_value,
    calculated_text,
    target_value,
    meets_criteria,
    calculated_by,
    notes,
    calculation_date
) VALUES (...);
```

### Retrieving Quarterly Data

```python
# Get quarterly results from database
quarterly_results = calculator.get_quarterly_kpi_results(year=2025, quarter=1)

for result in quarterly_results:
    print(f"{result['kpi_name']}: {result['calculated_value']}")
```

---

## API Reference

### KPIQuarterlyCalculator Class

#### Constructor

```python
calculator = KPIQuarterlyCalculator(pool)
```

**Parameters:**
- `pool`: Database connection pool

#### Main Methods

##### `generate_quarterly_report(year, quarter, save_to_db, calculated_by)`

Generate complete quarterly report for all KPIs.

**Parameters:**
- `year` (int): Year (e.g., 2025)
- `quarter` (int): Quarter number (1-4)
- `save_to_db` (bool): Whether to save to database (default: False)
- `calculated_by` (str): Username for audit trail (default: 'system')

**Returns:** Dictionary with:
- `quarter_info`: Quarter metadata
- `quarterly_kpis`: List of quarterly KPI results
- `statistics`: Summary statistics
- `generated_date`: Generation timestamp
- `generated_by`: Who generated it

##### `calculate_quarterly_kpi(kpi_name, year, quarter)`

Calculate quarterly result for a single KPI.

**Parameters:**
- `kpi_name` (str): Name of the KPI
- `year` (int): Year
- `quarter` (int): Quarter number (1-4)

**Returns:** Dictionary with quarterly KPI data

##### `get_quarterly_kpi_results(year, quarter)`

Retrieve saved quarterly results from database.

**Parameters:**
- `year` (int): Year
- `quarter` (int): Quarter number

**Returns:** List of quarterly KPI results from database

##### `get_available_quarters()`

Get list of quarters that have monthly data available.

**Returns:** List of dictionaries with quarter information

##### `export_quarterly_summary_table(year, quarter)`

Generate text-based summary table.

**Parameters:**
- `year` (int): Year
- `quarter` (int): Quarter number

**Returns:** Formatted string with table

---

## Examples

### Example 1: Generate Q1 2025 Report

```python
from kpi_quarterly_calculator import KPIQuarterlyCalculator
from dbconnect import DatabaseConnectionPool

# Setup
pool = DatabaseConnectionPool(min_connections=1, max_connections=5)
calculator = KPIQuarterlyCalculator(pool)

# Generate report
report = calculator.generate_quarterly_report(
    year=2025,
    quarter=1,
    save_to_db=True,
    calculated_by='john.doe'
)

# Print summary
stats = report['statistics']
print(f"Q1 2025 Summary:")
print(f"  Total KPIs: {stats['total_kpis']}")
print(f"  Passing: {stats['kpis_passing']}")
print(f"  Failing: {stats['kpis_failing']}")

# Close connections
pool.close_all_connections()
```

### Example 2: Calculate Single KPI

```python
# Calculate just PM Adherence for Q2 2025
pm_result = calculator.calculate_quarterly_kpi(
    kpi_name='Preventive Maintenance Adherence',
    year=2025,
    quarter=2
)

print(f"PM Adherence Q2 2025:")
print(f"  Value: {pm_result['value']}")
print(f"  Status: {'PASS' if pm_result['meets_criteria'] else 'FAIL'}")
print(f"  Details: {pm_result['text']}")
print(f"  Method: {pm_result['aggregation_method']}")
print(f"  Data from: {', '.join(pm_result['periods'])}")
```

### Example 3: Generate Reports for All Quarters

```python
# Get all available quarters
available = calculator.get_available_quarters()

# Generate report for each
for quarter_info in available:
    print(f"\nGenerating {quarter_info['display']}...")

    report = calculator.generate_quarterly_report(
        year=quarter_info['year'],
        quarter=quarter_info['quarter'],
        save_to_db=True,
        calculated_by='batch_process'
    )

    print(f"  Passing: {report['statistics']['kpis_passing']}")
    print(f"  Failing: {report['statistics']['kpis_failing']}")
```

### Example 4: Export to File

```python
import json

# Generate report
report = calculator.generate_quarterly_report(year=2025, quarter=1)

# Export to JSON file
with open('q1_2025_report.json', 'w') as f:
    json.dump(report, f, indent=2, default=str)

# Export summary table to text file
summary = calculator.export_quarterly_summary_table(year=2025, quarter=1)
with open('q1_2025_summary.txt', 'w') as f:
    f.write(summary)
```

### Example 5: Compare Quarters

```python
# Compare Q1 and Q2 passing rates
q1_report = calculator.generate_quarterly_report(year=2025, quarter=1)
q2_report = calculator.generate_quarterly_report(year=2025, quarter=2)

q1_pass_rate = (q1_report['statistics']['kpis_passing'] /
                q1_report['statistics']['kpis_with_data'] * 100)

q2_pass_rate = (q2_report['statistics']['kpis_passing'] /
                q2_report['statistics']['kpis_with_data'] * 100)

print(f"Q1 Pass Rate: {q1_pass_rate:.1f}%")
print(f"Q2 Pass Rate: {q2_pass_rate:.1f}%")
print(f"Improvement: {q2_pass_rate - q1_pass_rate:+.1f}%")
```

---

## Troubleshooting

### "No data available for this quarter"

**Problem:** Monthly KPI data hasn't been entered yet.

**Solution:**
1. Use the KPI Dashboard to enter monthly data for all 3 months in the quarter
2. Verify data exists: `python generate_quarterly_report.py --list-quarters`

### "Not enough data points"

**Problem:** Only 1 or 2 months have data in the quarter.

**Solution:**
- The calculator still works with partial data
- Results will note how many months contributed (e.g., "2/3 months")
- Complete all 3 months for accurate quarterly reporting

### Quarterly results don't appear in dashboard

**Problem:** Dashboard period selector doesn't show quarterly periods.

**Solution:**
- Quarterly periods use format `2025-Q1` in the database
- Modify the dashboard's period selector to include quarterly periods
- Or use the command-line script to view quarterly reports

---

## Best Practices

1. **Enter monthly data consistently** - Complete all KPIs each month
2. **Review before saving** - Run without `--save` first to preview
3. **Generate at quarter end** - Wait until all 3 months are complete
4. **Document changes** - Note any data corrections or adjustments
5. **Export regularly** - Save reports as files for archival
6. **Compare trends** - Track quarterly improvements over time

---

## Support

For questions or issues:

1. Check this guide first
2. Review the code documentation in `kpi_quarterly_calculator.py`
3. Check example usage in `generate_quarterly_report.py`
4. Review monthly KPI data for accuracy

---

## Changelog

### Version 1.0 (2025-12-09)
- Initial release
- Support for all 17 KPIs
- Multiple aggregation methods
- Command-line script
- Database integration
- Export to JSON/text

---

## License

Part of AIT CMMS NEON 2.3 system
