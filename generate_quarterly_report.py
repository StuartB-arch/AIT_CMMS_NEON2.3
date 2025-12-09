#!/usr/bin/env python3
"""
Quarterly KPI Report Generator Script
Run this script to generate quarterly KPI reports from your monthly data

Usage:
    python generate_quarterly_report.py --year 2025 --quarter 1
    python generate_quarterly_report.py --year 2025 --quarter 1 --save
    python generate_quarterly_report.py --list-quarters
    python generate_quarterly_report.py --help

Author: Claude
Date: 2025-12-09
"""

import argparse
import sys
from kpi_quarterly_calculator import KPIQuarterlyCalculator
from dbconnect import DatabaseConnectionPool
from datetime import datetime
import json


def create_db_pool():
    """Create and return database connection pool"""
    try:
        pool = DatabaseConnectionPool(
            min_connections=1,
            max_connections=5
        )
        return pool
    except Exception as e:
        print(f"ERROR: Could not connect to database: {str(e)}")
        sys.exit(1)


def list_available_quarters(calculator):
    """List all quarters that have monthly KPI data"""
    print("\n" + "="*70)
    print("AVAILABLE QUARTERS WITH KPI DATA")
    print("="*70)

    quarters = calculator.get_available_quarters()

    if not quarters:
        print("\nNo quarterly data available yet.")
        print("Please ensure you have entered monthly KPI data first.")
        return

    print(f"\nFound {len(quarters)} quarter(s) with data:\n")

    for q in quarters:
        quarter_info = calculator.get_quarter_info(q['year'], q['quarter'])
        print(f"  {q['display']:15} ({q['label']:10})  Months: {', '.join(quarter_info['periods'])}")

    print("\n" + "="*70)
    print("\nTo generate a report for a specific quarter:")
    print("  python generate_quarterly_report.py --year YYYY --quarter Q")
    print("\nExample:")
    print("  python generate_quarterly_report.py --year 2025 --quarter 1")
    print("="*70 + "\n")


def generate_report(calculator, year, quarter, save_to_db, export_format, output_file):
    """Generate quarterly report"""
    print("\n" + "="*70)
    print(f"GENERATING QUARTERLY KPI REPORT")
    print("="*70)
    print(f"Year:    {year}")
    print(f"Quarter: Q{quarter}")
    print(f"Label:   {year}-Q{quarter}")
    print("="*70 + "\n")

    try:
        # Generate the report
        report = calculator.generate_quarterly_report(
            year=year,
            quarter=quarter,
            save_to_db=save_to_db,
            calculated_by='report_script'
        )

        # Display summary table
        summary_table = calculator.export_quarterly_summary_table(year, quarter)
        print(summary_table)

        # Display statistics
        stats = report['statistics']
        print("\n" + "="*70)
        print("QUARTERLY STATISTICS")
        print("="*70)
        print(f"  Total KPIs:             {stats['total_kpis']}")
        print(f"  KPIs with Data:         {stats['kpis_with_data']}")
        print(f"  KPIs Passing:           {stats['kpis_passing']} (✓)")
        print(f"  KPIs Failing:           {stats['kpis_failing']} (✗)")
        print(f"  KPIs Pending:           {stats['kpis_pending']}")
        print(f"\n  Pass Rate:              {(stats['kpis_passing'] / stats['kpis_with_data'] * 100) if stats['kpis_with_data'] > 0 else 0:.1f}%")
        print(f"  Data Completeness:      {(stats['kpis_with_data'] / stats['total_kpis'] * 100):.1f}%")
        print("="*70 + "\n")

        # Display detailed KPI results by function
        display_detailed_results(report['quarterly_kpis'])

        # Export to file if requested
        if output_file:
            export_to_file(report, output_file, export_format)

        # Show saved status
        if save_to_db:
            print("\n✓ Quarterly KPI results saved to database")
            print(f"  You can now view them in the KPI Dashboard by selecting period: {year}-Q{quarter}")
        else:
            print("\n⚠ Results NOT saved to database (use --save flag to save)")

        return 0

    except Exception as e:
        print(f"\n✗ ERROR generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def display_detailed_results(quarterly_kpis):
    """Display detailed KPI results organized by function"""
    print("="*70)
    print("DETAILED KPI RESULTS BY FUNCTION")
    print("="*70 + "\n")

    # Group by function
    functions = {}
    for kpi in quarterly_kpis:
        func_code = kpi.get('function_code', 'Unknown')
        if func_code not in functions:
            functions[func_code] = []
        functions[func_code].append(kpi)

    # Display each function's KPIs
    for func_code in sorted(functions.keys()):
        print(f"\n{func_code}")
        print("-" * 70)

        for kpi in functions[func_code]:
            kpi_name = kpi.get('kpi_name', 'Unknown')
            print(f"\n  KPI: {kpi_name}")

            if 'error' in kpi:
                print(f"    ERROR: {kpi['error']}")
                continue

            if kpi.get('value') is None:
                print(f"    Status: No data available")
                print(f"    Data points: {kpi.get('data_points', 0)}/3 months")
            else:
                print(f"    Value: {kpi['value']:.2f}")
                print(f"    Text: {kpi.get('text', 'N/A')}")

                if kpi.get('meets_criteria') is True:
                    print(f"    Status: ✓ PASS")
                elif kpi.get('meets_criteria') is False:
                    print(f"    Status: ✗ FAIL")
                else:
                    print(f"    Status: N/A")

                print(f"    Aggregation: {kpi.get('aggregation_method', 'N/A')}")
                print(f"    Data points: {kpi.get('months_with_data', 0)}/3 months")
                print(f"    Periods: {', '.join(kpi.get('periods', []))}")

            if kpi.get('acceptance_criteria'):
                print(f"    Target: {kpi['acceptance_criteria']}")

    print("\n" + "="*70 + "\n")


def export_to_file(report, output_file, export_format):
    """Export report to file"""
    try:
        if export_format == 'json':
            # Convert datetime objects to strings for JSON serialization
            json_report = json.dumps(report, indent=2, default=str)
            with open(output_file, 'w') as f:
                f.write(json_report)
            print(f"\n✓ Report exported to JSON: {output_file}")

        elif export_format == 'txt':
            with open(output_file, 'w') as f:
                f.write(f"QUARTERLY KPI REPORT\n")
                f.write(f"{'='*70}\n\n")
                f.write(f"Quarter: {report['quarter_info']['label']}\n")
                f.write(f"Period: {report['quarter_info']['start_date']} to {report['quarter_info']['end_date']}\n")
                f.write(f"Generated: {report['generated_date']}\n")
                f.write(f"Generated by: {report['generated_by']}\n\n")

                # Statistics
                stats = report['statistics']
                f.write(f"STATISTICS\n")
                f.write(f"{'-'*70}\n")
                f.write(f"Total KPIs:       {stats['total_kpis']}\n")
                f.write(f"With Data:        {stats['kpis_with_data']}\n")
                f.write(f"Passing:          {stats['kpis_passing']}\n")
                f.write(f"Failing:          {stats['kpis_failing']}\n")
                f.write(f"Pending:          {stats['kpis_pending']}\n\n")

                # KPI Details
                f.write(f"KPI DETAILS\n")
                f.write(f"{'-'*70}\n\n")

                for kpi in report['quarterly_kpis']:
                    f.write(f"KPI: {kpi.get('kpi_name', 'Unknown')}\n")
                    f.write(f"  Value: {kpi.get('value', 'N/A')}\n")
                    f.write(f"  Text: {kpi.get('text', 'N/A')}\n")
                    f.write(f"  Status: {kpi.get('meets_criteria', 'N/A')}\n")
                    f.write(f"  Method: {kpi.get('aggregation_method', 'N/A')}\n")
                    f.write("\n")

            print(f"\n✓ Report exported to text file: {output_file}")

    except Exception as e:
        print(f"\n✗ ERROR exporting report: {str(e)}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Generate Quarterly KPI Reports from Monthly Data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available quarters
  python generate_quarterly_report.py --list-quarters

  # Generate report for Q1 2025 (preview only, don't save)
  python generate_quarterly_report.py --year 2025 --quarter 1

  # Generate and save to database
  python generate_quarterly_report.py --year 2025 --quarter 1 --save

  # Generate and export to file
  python generate_quarterly_report.py --year 2025 --quarter 1 --output report.json --format json
  python generate_quarterly_report.py --year 2025 --quarter 1 --output report.txt --format txt

  # Generate all available quarters
  python generate_quarterly_report.py --all --save
        """
    )

    parser.add_argument('--year', type=int, help='Year (e.g., 2025)')
    parser.add_argument('--quarter', type=int, choices=[1, 2, 3, 4], help='Quarter number (1-4)')
    parser.add_argument('--save', action='store_true', help='Save quarterly results to database')
    parser.add_argument('--list-quarters', action='store_true', help='List available quarters with data')
    parser.add_argument('--all', action='store_true', help='Generate reports for all available quarters')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--format', type=str, choices=['json', 'txt'], default='txt',
                       help='Export format (json or txt)')

    args = parser.parse_args()

    # Create database pool
    pool = create_db_pool()
    calculator = KPIQuarterlyCalculator(pool)

    try:
        # List quarters mode
        if args.list_quarters:
            list_available_quarters(calculator)
            return 0

        # Generate all quarters mode
        if args.all:
            print("\n" + "="*70)
            print("GENERATING REPORTS FOR ALL AVAILABLE QUARTERS")
            print("="*70 + "\n")

            quarters = calculator.get_available_quarters()
            if not quarters:
                print("No quarters with data available.")
                return 1

            for q in quarters:
                print(f"\nProcessing {q['display']}...")
                result = generate_report(
                    calculator,
                    q['year'],
                    q['quarter'],
                    args.save,
                    args.format,
                    f"quarterly_report_{q['label']}.{args.format}" if args.output else None
                )
                if result != 0:
                    print(f"✗ Failed to generate report for {q['display']}")

            return 0

        # Generate specific quarter mode
        if args.year and args.quarter:
            return generate_report(
                calculator,
                args.year,
                args.quarter,
                args.save,
                args.format,
                args.output
            )

        # No valid arguments
        parser.print_help()
        print("\n⚠ Please specify either --list-quarters, --all, or --year and --quarter")
        return 1

    finally:
        pool.close_all_connections()


if __name__ == "__main__":
    sys.exit(main())
