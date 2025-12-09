#!/usr/bin/env python3
"""
Quick Example: Using the Quarterly KPI Calculator
This script shows simple usage examples for generating quarterly reports

Author: Claude
Date: 2025-12-09
"""

from kpi_quarterly_calculator import KPIQuarterlyCalculator
from dbconnect import DatabaseConnectionPool


def example_1_basic_report():
    """Example 1: Generate a basic quarterly report"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Generate Basic Quarterly Report")
    print("="*70 + "\n")

    # Create database connection
    pool = DatabaseConnectionPool(min_connections=1, max_connections=5)

    try:
        # Create calculator
        calculator = KPIQuarterlyCalculator(pool)

        # Generate Q1 2025 report (don't save to database)
        report = calculator.generate_quarterly_report(
            year=2025,
            quarter=1,
            save_to_db=False,
            calculated_by='example_script'
        )

        # Display summary
        print("Summary Statistics:")
        print(f"  Total KPIs:      {report['statistics']['total_kpis']}")
        print(f"  With Data:       {report['statistics']['kpis_with_data']}")
        print(f"  Passing:         {report['statistics']['kpis_passing']}")
        print(f"  Failing:         {report['statistics']['kpis_failing']}")

    finally:
        pool.close_all_connections()


def example_2_single_kpi():
    """Example 2: Calculate a single KPI"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Calculate Single KPI")
    print("="*70 + "\n")

    pool = DatabaseConnectionPool(min_connections=1, max_connections=5)

    try:
        calculator = KPIQuarterlyCalculator(pool)

        # Calculate just PM Adherence
        result = calculator.calculate_quarterly_kpi(
            kpi_name='Preventive Maintenance Adherence',
            year=2025,
            quarter=1
        )

        print("Preventive Maintenance Adherence - Q1 2025:")
        print(f"  Value:           {result.get('value', 'N/A')}")
        print(f"  Text:            {result.get('text', 'N/A')}")
        print(f"  Status:          {'PASS' if result.get('meets_criteria') else 'FAIL'}")
        print(f"  Aggregation:     {result.get('aggregation_method', 'N/A')}")
        print(f"  Data Points:     {result.get('months_with_data', 0)}/3 months")
        print(f"  Periods:         {', '.join(result.get('periods', []))}")

    finally:
        pool.close_all_connections()


def example_3_list_quarters():
    """Example 3: List available quarters"""
    print("\n" + "="*70)
    print("EXAMPLE 3: List Available Quarters")
    print("="*70 + "\n")

    pool = DatabaseConnectionPool(min_connections=1, max_connections=5)

    try:
        calculator = KPIQuarterlyCalculator(pool)

        # Get available quarters
        quarters = calculator.get_available_quarters()

        if quarters:
            print(f"Found {len(quarters)} quarter(s) with monthly data:\n")
            for q in quarters:
                print(f"  {q['display']:15} - {q['label']}")
        else:
            print("No quarters with data available yet.")
            print("Please enter monthly KPI data first.")

    finally:
        pool.close_all_connections()


def example_4_save_to_database():
    """Example 4: Generate and save to database"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Generate and Save to Database")
    print("="*70 + "\n")

    pool = DatabaseConnectionPool(min_connections=1, max_connections=5)

    try:
        calculator = KPIQuarterlyCalculator(pool)

        # Generate and SAVE to database
        report = calculator.generate_quarterly_report(
            year=2025,
            quarter=1,
            save_to_db=True,  # Save to database
            calculated_by='john.doe'
        )

        print("✓ Quarterly KPIs saved to database!")
        print(f"  Period: {report['quarter_info']['label']}")
        print(f"  Saved: {report['statistics']['kpis_with_data']} KPIs")
        print("\nYou can now view them in the KPI Dashboard by selecting period: 2025-Q1")

    finally:
        pool.close_all_connections()


def example_5_export_summary():
    """Example 5: Export summary table"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Export Summary Table")
    print("="*70 + "\n")

    pool = DatabaseConnectionPool(min_connections=1, max_connections=5)

    try:
        calculator = KPIQuarterlyCalculator(pool)

        # Generate summary table
        summary = calculator.export_quarterly_summary_table(year=2025, quarter=1)

        print(summary)

        # Optionally save to file
        with open('quarterly_summary_q1_2025.txt', 'w') as f:
            f.write(summary)

        print("\n✓ Summary also saved to: quarterly_summary_q1_2025.txt")

    finally:
        pool.close_all_connections()


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "QUARTERLY KPI CALCULATOR" + " "*24 + "║")
    print("║" + " "*26 + "Examples" + " "*34 + "║")
    print("╚" + "="*68 + "╝")

    try:
        # Run each example
        example_1_basic_report()
        example_2_single_kpi()
        example_3_list_quarters()

        # Uncomment to save to database:
        # example_4_save_to_database()

        example_5_export_summary()

        print("\n" + "="*70)
        print("All examples completed successfully!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n✗ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
