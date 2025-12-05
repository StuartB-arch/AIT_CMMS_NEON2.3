"""
Real-time Failure Predictor
Provides interface for making predictions on equipment
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from .failure_prediction_model import FailurePredictionModel
from .feature_engineering import FailurePredictionFeatureEngineer


class FailurePredictor:
    """
    High-level interface for making failure predictions

    Handles feature extraction and prediction for equipment
    """

    def __init__(self, connection, model_path: str = 'ml/models/failure_prediction_model.pkl'):
        """
        Initialize predictor

        Args:
            connection: Database connection
            model_path: Path to trained model file
        """
        self.conn = connection
        self.model_path = model_path
        self.model = None
        self.feature_engineer = FailurePredictionFeatureEngineer(connection)

        # Load model if it exists
        try:
            self.model = FailurePredictionModel.load(model_path)
            print(f"Loaded failure prediction model from {model_path}")
        except FileNotFoundError:
            print(f"No trained model found at {model_path}")
            print("Please train a model first using train_model.py")

    def predict_all_equipment(self) -> pd.DataFrame:
        """
        Generate failure predictions for all active equipment

        Returns:
            DataFrame with equipment info and predictions
        """
        if self.model is None:
            raise ValueError("No model loaded. Train a model first.")

        print("Generating predictions for all equipment...")

        # Extract current features
        current_features = self.feature_engineer.extract_current_features()

        # Engineer features
        features_engineered = self.feature_engineer.engineer_features(current_features)

        # Get feature columns
        feature_cols = self.feature_engineer.get_feature_columns()

        # Make predictions
        predictions = self.model.predict_proba(features_engineered[feature_cols])
        binary_predictions = self.model.predict(features_engineered[feature_cols])

        # Add predictions to dataframe
        results = current_features[['bfm_equipment_no', 'description', 'location']].copy()
        results['failure_probability'] = predictions
        results['failure_prediction'] = binary_predictions
        results['risk_level'] = pd.cut(
            predictions,
            bins=[0, 0.2, 0.4, 0.7, 1.0],
            labels=['Low', 'Medium', 'High', 'Critical']
        )

        # Add recommendation
        results['recommendation'] = results.apply(self._generate_recommendation, axis=1)

        # Sort by probability (highest risk first)
        results = results.sort_values('failure_probability', ascending=False)

        print(f"Generated predictions for {len(results)} equipment")
        print(f"High risk (>0.4): {(results['failure_probability'] > 0.4).sum()}")
        print(f"Critical risk (>0.7): {(results['failure_probability'] > 0.7).sum()}")

        return results

    def predict_equipment(self, bfm_no: str) -> Dict:
        """
        Generate prediction for specific equipment

        Args:
            bfm_no: Equipment BFM number

        Returns:
            Dictionary with prediction details
        """
        if self.model is None:
            raise ValueError("No model loaded. Train a model first.")

        # Get all predictions
        all_predictions = self.predict_all_equipment()

        # Filter for specific equipment
        equipment_pred = all_predictions[all_predictions['bfm_equipment_no'] == bfm_no]

        if equipment_pred.empty:
            return {
                'error': f"Equipment {bfm_no} not found or not active"
            }

        row = equipment_pred.iloc[0]

        return {
            'bfm_equipment_no': row['bfm_equipment_no'],
            'description': row['description'],
            'location': row['location'],
            'failure_probability': float(row['failure_probability']),
            'risk_level': row['risk_level'],
            'recommendation': row['recommendation']
        }

    def get_high_risk_equipment(self, threshold: float = 0.4) -> pd.DataFrame:
        """
        Get equipment with high failure risk

        Args:
            threshold: Probability threshold for high risk

        Returns:
            DataFrame with high-risk equipment
        """
        all_predictions = self.predict_all_equipment()
        high_risk = all_predictions[all_predictions['failure_probability'] >= threshold]

        return high_risk

    def generate_risk_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate comprehensive risk report

        Args:
            output_file: Optional file path to save report

        Returns:
            Report text
        """
        predictions = self.predict_all_equipment()

        report = []
        report.append("=" * 80)
        report.append("EQUIPMENT FAILURE RISK REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")

        # Summary statistics
        report.append("RISK SUMMARY")
        report.append("-" * 80)
        report.append(f"Total equipment analyzed: {len(predictions)}")
        report.append(f"Critical risk (>0.7):    {(predictions['failure_probability'] > 0.7).sum()}")
        report.append(f"High risk (0.4-0.7):     {((predictions['failure_probability'] > 0.4) & (predictions['failure_probability'] <= 0.7)).sum()}")
        report.append(f"Medium risk (0.2-0.4):   {((predictions['failure_probability'] > 0.2) & (predictions['failure_probability'] <= 0.4)).sum()}")
        report.append(f"Low risk (<0.2):         {(predictions['failure_probability'] <= 0.2).sum()}")
        report.append("")

        # Top 20 highest risk equipment
        report.append("TOP 20 HIGHEST RISK EQUIPMENT")
        report.append("-" * 80)
        report.append(f"{'BFM #':<15} {'Description':<30} {'Location':<15} {'Prob':<8} {'Risk':<10}")
        report.append("-" * 80)

        for _, row in predictions.head(20).iterrows():
            report.append(
                f"{row['bfm_equipment_no']:<15} "
                f"{row['description'][:28]:<30} "
                f"{row['location']:<15} "
                f"{row['failure_probability']:<8.3f} "
                f"{row['risk_level']:<10}"
            )

        report.append("")

        # Recommendations
        critical = predictions[predictions['failure_probability'] > 0.7]
        if len(critical) > 0:
            report.append("CRITICAL EQUIPMENT REQUIRING IMMEDIATE ATTENTION")
            report.append("-" * 80)
            for _, row in critical.iterrows():
                report.append(f"• {row['bfm_equipment_no']} - {row['description']}")
                report.append(f"  Location: {row['location']}")
                report.append(f"  Failure Probability: {row['failure_probability']:.1%}")
                report.append(f"  Recommendation: {row['recommendation']}")
                report.append("")

        report_text = "\n".join(report)

        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"Risk report saved to {output_file}")

        return report_text

    def _generate_recommendation(self, row: pd.Series) -> str:
        """Generate recommendation based on risk level"""
        prob = row['failure_probability']

        if prob > 0.7:
            return "URGENT: Schedule immediate inspection and preventive maintenance"
        elif prob > 0.4:
            return "HIGH PRIORITY: Schedule PM within next 7 days"
        elif prob > 0.2:
            return "MODERATE: Monitor closely and schedule PM within next 30 days"
        else:
            return "LOW RISK: Continue normal PM schedule"


class ModelTrainer:
    """
    Helper class for training new models
    """

    def __init__(self, connection):
        """
        Initialize trainer

        Args:
            connection: Database connection
        """
        self.conn = connection
        self.feature_engineer = FailurePredictionFeatureEngineer(connection)

    def train_new_model(self,
                       lookback_months: int = 12,
                       prediction_window_days: int = 30,
                       snapshot_interval_days: int = 7,
                       save_path: str = 'ml/models/failure_prediction_model.pkl') -> FailurePredictionModel:
        """
        Train a new failure prediction model

        Args:
            lookback_months: Months of historical data to use
            prediction_window_days: Days ahead to predict failures
            snapshot_interval_days: Days between training snapshots
            save_path: Where to save the trained model

        Returns:
            Trained model
        """
        from .failure_prediction_model import train_and_evaluate_model

        print("=" * 80)
        print("TRAINING NEW FAILURE PREDICTION MODEL")
        print("=" * 80)

        # Extract training data
        print("\nStep 1: Extracting training data...")
        training_data = self.feature_engineer.extract_training_data(
            lookback_months=lookback_months,
            prediction_window_days=prediction_window_days,
            snapshot_interval_days=snapshot_interval_days
        )

        # Engineer features
        print("\nStep 2: Engineering features...")
        training_data_engineered = self.feature_engineer.engineer_features(training_data)

        # Get feature columns
        feature_columns = self.feature_engineer.get_feature_columns()

        # Check if we have enough positive samples
        positive_samples = training_data_engineered['failure_in_next_30_days'].sum()
        if positive_samples < 30:
            print(f"\nWARNING: Only {positive_samples} failure samples found.")
            print("This may not be enough for reliable model training.")
            print("Consider:")
            print("- Increasing lookback_months")
            print("- Increasing prediction_window_days")
            print("- Using a different snapshot_interval_days")

            response = input("\nContinue anyway? (yes/no): ")
            if response.lower() != 'yes':
                print("Training cancelled.")
                return None

        # Train model
        print("\nStep 3: Training model...")
        model = train_and_evaluate_model(
            training_data_engineered,
            feature_columns,
            test_size=0.2,
            val_size=0.1
        )

        # Save model
        print(f"\nStep 4: Saving model to {save_path}...")
        model.save(save_path)

        print("\n" + "=" * 80)
        print("MODEL TRAINING COMPLETE!")
        print("=" * 80)
        print(f"Model saved to: {save_path}")
        print(f"Training date: {model.training_date}")
        print("\nYou can now use this model for predictions with FailurePredictor class")

        return model
