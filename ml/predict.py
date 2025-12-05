"""
Standalone script to generate failure predictions

Usage:
    python -m ml.predict

This will generate predictions for all equipment and display high-risk items
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_utils import DatabaseConnectionPool
from ml.predictor import FailurePredictor


def main():
    """Main prediction pipeline"""
    print("=" * 80)
    print("EQUIPMENT FAILURE PREDICTIONS")
    print("=" * 80)
    print()

    # Get database connection
    print("Connecting to database...")
    pool = DatabaseConnectionPool()

    try:
        conn = pool.get_connection()
        print("Database connection established!")
    except Exception as e:
        print(f"ERROR: Could not connect to database: {e}")
        return

    try:
        # Create predictor
        predictor = FailurePredictor(conn)

        # Generate predictions for all equipment
        print("\nGenerating predictions for all equipment...")
        predictions = predictor.predict_all_equipment()

        # Display summary
        print("\n" + "=" * 80)
        print("PREDICTION SUMMARY")
        print("=" * 80)

        total = len(predictions)
        critical = (predictions['failure_probability'] > 0.7).sum()
        high = ((predictions['failure_probability'] > 0.4) &
                (predictions['failure_probability'] <= 0.7)).sum()
        medium = ((predictions['failure_probability'] > 0.2) &
                  (predictions['failure_probability'] <= 0.4)).sum()
        low = (predictions['failure_probability'] <= 0.2).sum()

        print(f"Total equipment: {total}")
        print(f"Critical risk (>0.7):  {critical} ({critical/total*100:.1f}%)")
        print(f"High risk (0.4-0.7):   {high} ({high/total*100:.1f}%)")
        print(f"Medium risk (0.2-0.4): {medium} ({medium/total*100:.1f}%)")
        print(f"Low risk (<0.2):       {low} ({low/total*100:.1f}%)")

        # Display high-risk equipment
        high_risk = predictions[predictions['failure_probability'] > 0.4]

        if len(high_risk) > 0:
            print("\n" + "=" * 80)
            print("HIGH RISK EQUIPMENT (Probability > 0.4)")
            print("=" * 80)
            print(f"{'BFM #':<15} {'Description':<35} {'Location':<15} {'Prob':<8} {'Risk'}")
            print("-" * 80)

            for _, row in high_risk.iterrows():
                desc = row['description'][:33] if len(row['description']) > 33 else row['description']
                print(f"{row['bfm_equipment_no']:<15} "
                      f"{desc:<35} "
                      f"{row['location']:<15} "
                      f"{row['failure_probability']:<8.3f} "
                      f"{row['risk_level']}")

            # Show recommendations for critical equipment
            critical_equip = predictions[predictions['failure_probability'] > 0.7]
            if len(critical_equip) > 0:
                print("\n" + "=" * 80)
                print("CRITICAL EQUIPMENT - IMMEDIATE ACTION REQUIRED")
                print("=" * 80)

                for _, row in critical_equip.iterrows():
                    print(f"\n{row['bfm_equipment_no']} - {row['description']}")
                    print(f"  Location: {row['location']}")
                    print(f"  Failure Probability: {row['failure_probability']:.1%}")
                    print(f"  Recommendation: {row['recommendation']}")

        else:
            print("\nNo high-risk equipment found. All equipment below 0.4 threshold.")

        # Generate and save risk report
        print("\n" + "=" * 80)
        print("Generating detailed risk report...")
        report_file = "ml/failure_risk_report.txt"
        predictor.generate_risk_report(output_file=report_file)
        print(f"Detailed report saved to: {report_file}")

    except FileNotFoundError as e:
        print("\nERROR: No trained model found!")
        print("Please train a model first using: python -m ml.train_model")

    except Exception as e:
        print(f"\nERROR during prediction: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Return connection to pool
        if conn:
            pool.putconn(conn)


if __name__ == "__main__":
    main()
