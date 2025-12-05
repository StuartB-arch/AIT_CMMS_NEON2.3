"""
Standalone script to train the failure prediction model

Usage:
    python -m ml.train_model

This will:
1. Extract historical data from the database
2. Engineer features
3. Train a Random Forest model
4. Evaluate performance
5. Save the trained model
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_utils import DatabaseConnectionPool
from ml.predictor import ModelTrainer


def main():
    """Main training pipeline"""
    print("=" * 80)
    print("FAILURE PREDICTION MODEL TRAINING")
    print("=" * 80)
    print()

    # Get database connection
    print("Connecting to database...")
    pool = DatabaseConnectionPool()

    # Note: You'll need to initialize the pool with your database config
    # This assumes the pool is already initialized by the main application
    # If running standalone, you may need to add initialization here

    try:
        conn = pool.get_connection()
        print("Database connection established!")
    except Exception as e:
        print(f"ERROR: Could not connect to database: {e}")
        print("\nPlease ensure:")
        print("1. Database connection pool is initialized")
        print("2. Database credentials are correct")
        print("3. You have network access to the database")
        return

    try:
        # Create trainer
        trainer = ModelTrainer(conn)

        # Configure training parameters
        print("\n" + "=" * 80)
        print("TRAINING CONFIGURATION")
        print("=" * 80)

        lookback_months = 12
        prediction_window_days = 30
        snapshot_interval_days = 7

        print(f"Lookback period: {lookback_months} months")
        print(f"Prediction window: {prediction_window_days} days")
        print(f"Snapshot interval: {snapshot_interval_days} days")
        print()

        # Train model
        model = trainer.train_new_model(
            lookback_months=lookback_months,
            prediction_window_days=prediction_window_days,
            snapshot_interval_days=snapshot_interval_days,
            save_path='ml/models/failure_prediction_model.pkl'
        )

        if model:
            print("\n" + "=" * 80)
            print("SUCCESS!")
            print("=" * 80)
            print("Model training completed successfully.")
            print("You can now use the model for predictions in the CMMS application.")

    except Exception as e:
        print(f"\nERROR during training: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Return connection to pool
        if conn:
            pool.putconn(conn)


if __name__ == "__main__":
    main()
