"""
Demo script showing how to use the ML prediction API

This demonstrates the Python API for failure predictions
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_utils import DatabaseConnectionPool
from ml.predictor import FailurePredictor, ModelTrainer
import pandas as pd


def demo_predictions():
    """Demo: Generate predictions and display results"""
    print("=" * 80)
    print("DEMO: Equipment Failure Predictions")
    print("=" * 80)

    # Get database connection
    pool = DatabaseConnectionPool()
    conn = pool.get_connection()

    try:
        # Create predictor
        print("\n1. Loading predictor...")
        predictor = FailurePredictor(conn)

        if predictor.model is None:
            print("   No model found. Please train a model first.")
            print("   Run: python -m ml.train_model")
            return

        # Generate predictions for all equipment
        print("\n2. Generating predictions for all equipment...")
        predictions = predictor.predict_all_equipment()

        # Display summary
        print(f"\n   Total equipment analyzed: {len(predictions)}")

        # Show top 10 highest risk
        print("\n3. Top 10 Highest Risk Equipment:")
        print("-" * 80)
        top_10 = predictions.head(10)

        for idx, row in top_10.iterrows():
            print(f"   {row['bfm_equipment_no']:15s} "
                  f"{row['description'][:30]:32s} "
                  f"Prob: {row['failure_probability']:.1%} "
                  f"({row['risk_level']})")

        # Get high-risk equipment
        print("\n4. High-risk equipment (probability > 0.4):")
        high_risk = predictor.get_high_risk_equipment(threshold=0.4)
        print(f"   Found {len(high_risk)} high-risk equipment")

        if len(high_risk) > 0:
            print("\n   Details:")
            for idx, row in high_risk.iterrows():
                print(f"\n   {row['bfm_equipment_no']} - {row['description']}")
                print(f"   Location: {row['location']}")
                print(f"   Failure Probability: {row['failure_probability']:.1%}")
                print(f"   Recommendation: {row['recommendation']}")

        # Predict specific equipment
        print("\n5. Predict specific equipment:")
        if len(predictions) > 0:
            sample_bfm = predictions.iloc[0]['bfm_equipment_no']
            result = predictor.predict_equipment(sample_bfm)

            print(f"   Equipment: {result['bfm_equipment_no']}")
            print(f"   Description: {result['description']}")
            print(f"   Failure Probability: {result['failure_probability']:.1%}")
            print(f"   Risk Level: {result['risk_level']}")
            print(f"   Recommendation: {result['recommendation']}")

        # Generate risk report
        print("\n6. Generating risk report...")
        report_file = "ml/demo_risk_report.txt"
        predictor.generate_risk_report(output_file=report_file)
        print(f"   Report saved to: {report_file}")

        print("\n" + "=" * 80)
        print("Demo completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        pool.putconn(conn)


def demo_feature_extraction():
    """Demo: Show how feature extraction works"""
    print("=" * 80)
    print("DEMO: Feature Extraction")
    print("=" * 80)

    pool = DatabaseConnectionPool()
    conn = pool.get_connection()

    try:
        from ml.feature_engineering import FailurePredictionFeatureEngineer

        print("\n1. Creating feature engineer...")
        engineer = FailurePredictionFeatureEngineer(conn)

        print("\n2. Extracting current features for all equipment...")
        current_features = engineer.extract_current_features()

        print(f"\n   Extracted features for {len(current_features)} equipment")
        print(f"\n3. Feature columns:")
        feature_cols = engineer.get_feature_columns()

        for i, col in enumerate(feature_cols, 1):
            print(f"   {i:2d}. {col}")

        print(f"\n4. Sample features (first equipment):")
        if len(current_features) > 0:
            sample = current_features.iloc[0]
            print(f"\n   Equipment: {sample['bfm_equipment_no']} - {sample['description']}")
            print("\n   Features:")

            for col in feature_cols:
                if col in sample:
                    print(f"   {col:40s} {sample[col]}")

        print("\n" + "=" * 80)
        print("Feature extraction demo completed!")
        print("=" * 80)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        pool.putconn(conn)


def demo_model_info():
    """Demo: Display model information"""
    print("=" * 80)
    print("DEMO: Model Information")
    print("=" * 80)

    pool = DatabaseConnectionPool()
    conn = pool.get_connection()

    try:
        predictor = FailurePredictor(conn)

        if predictor.model is None:
            print("\nNo model found. Train a model first.")
            return

        model = predictor.model

        print(f"\nModel Type: {model.model_type}")
        print(f"Training Date: {model.training_date}")
        print(f"Decision Threshold: {model.threshold}")
        print(f"\nNumber of Features: {len(model.feature_columns)}")

        if model.training_metrics:
            print("\nTraining Metrics:")

            if 'training' in model.training_metrics:
                metrics = model.training_metrics['training']
                print(f"  Training Set:")
                print(f"    ROC-AUC:   {metrics.get('roc_auc', 0):.3f}")
                print(f"    Precision: {metrics.get('precision', 0):.3f}")
                print(f"    Recall:    {metrics.get('recall', 0):.3f}")
                print(f"    F1 Score:  {metrics.get('f1', 0):.3f}")

            if 'validation' in model.training_metrics:
                metrics = model.training_metrics['validation']
                print(f"  Validation Set:")
                print(f"    ROC-AUC:   {metrics.get('roc_auc', 0):.3f}")
                print(f"    Precision: {metrics.get('precision', 0):.3f}")
                print(f"    Recall:    {metrics.get('recall', 0):.3f}")
                print(f"    F1 Score:  {metrics.get('f1', 0):.3f}")

            if 'test' in model.training_metrics:
                metrics = model.training_metrics['test']
                print(f"  Test Set:")
                print(f"    ROC-AUC:   {metrics.get('roc_auc', 0):.3f}")
                print(f"    Precision: {metrics.get('precision', 0):.3f}")
                print(f"    Recall:    {metrics.get('recall', 0):.3f}")
                print(f"    F1 Score:  {metrics.get('f1', 0):.3f}")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        pool.putconn(conn)


def main():
    """Run all demos"""
    print("\n" * 2)
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  FAILURE PREDICTION ML MODULE - DEMONSTRATION".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    demos = [
        ("Model Information", demo_model_info),
        ("Feature Extraction", demo_feature_extraction),
        ("Predictions", demo_predictions),
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n{'='*80}")
        print(f"Running Demo {i}/{len(demos)}: {name}")
        print(f"{'='*80}\n")

        try:
            demo_func()
        except Exception as e:
            print(f"Demo failed: {e}")

        if i < len(demos):
            input("\nPress Enter to continue to next demo...")

    print("\n" * 2)
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  ALL DEMOS COMPLETED!".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")


if __name__ == "__main__":
    main()
