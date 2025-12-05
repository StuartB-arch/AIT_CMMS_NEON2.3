"""
Failure Prediction Model
Trains and evaluates machine learning models for equipment failure prediction
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    precision_recall_curve,
    roc_curve,
    f1_score,
    precision_score,
    recall_score
)
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os


class FailurePredictionModel:
    """
    Random Forest-based equipment failure prediction model

    Predicts probability of equipment failure in next 30 days
    """

    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialize failure prediction model

        Args:
            model_type: Type of model ('random_forest' or 'logistic')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.threshold = 0.3  # Optimized threshold for predictions
        self.training_date = None
        self.training_metrics = {}

    def train(self,
             X_train: pd.DataFrame,
             y_train: pd.Series,
             X_val: Optional[pd.DataFrame] = None,
             y_val: Optional[pd.Series] = None) -> 'FailurePredictionModel':
        """
        Train the failure prediction model

        Args:
            X_train: Training features
            y_train: Training labels (1 = failure, 0 = no failure)
            X_val: Optional validation features
            y_val: Optional validation labels

        Returns:
            Self for chaining
        """
        print(f"Training {self.model_type} model...")
        print(f"Training samples: {len(X_train)}")
        print(f"Positive samples (failures): {y_train.sum()}")
        print(f"Negative samples (no failure): {(y_train == 0).sum()}")
        print(f"Class imbalance ratio: {(y_train == 0).sum() / y_train.sum():.2f}:1")

        # Store feature columns
        self.feature_columns = X_train.columns.tolist()

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)

        # Handle class imbalance with class weights
        # Failures are rare events, so we penalize false negatives more
        class_weight = {0: 1, 1: 10}

        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=20,
                min_samples_leaf=10,
                max_features='sqrt',
                class_weight=class_weight,
                random_state=42,
                n_jobs=-1,
                verbose=0
            )
        else:
            from sklearn.linear_model import LogisticRegression
            self.model = LogisticRegression(
                class_weight=class_weight,
                random_state=42,
                max_iter=1000
            )

        # Train
        self.model.fit(X_train_scaled, y_train)
        self.training_date = datetime.now()

        print("Model training complete!")

        # Evaluate on training set
        print("\n=== Training Set Performance ===")
        train_metrics = self.evaluate(X_train, y_train, dataset_name="Training")

        # Evaluate on validation set if provided
        if X_val is not None and y_val is not None:
            print("\n=== Validation Set Performance ===")
            val_metrics = self.evaluate(X_val, y_val, dataset_name="Validation")
            self.training_metrics['validation'] = val_metrics

        self.training_metrics['training'] = train_metrics

        # Print feature importance
        if self.model_type == 'random_forest':
            self._print_feature_importance()

        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict probability of failure

        Args:
            X: Features DataFrame

        Returns:
            Array of failure probabilities (0-1)
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        X_scaled = self.scaler.transform(X[self.feature_columns])
        return self.model.predict_proba(X_scaled)[:, 1]

    def predict(self, X: pd.DataFrame, threshold: Optional[float] = None) -> np.ndarray:
        """
        Predict failure (binary)

        Args:
            X: Features DataFrame
            threshold: Custom threshold (uses self.threshold if None)

        Returns:
            Array of binary predictions (1 = failure, 0 = no failure)
        """
        if threshold is None:
            threshold = self.threshold

        probabilities = self.predict_proba(X)
        return (probabilities >= threshold).astype(int)

    def evaluate(self,
                X_test: pd.DataFrame,
                y_test: pd.Series,
                dataset_name: str = "Test") -> Dict:
        """
        Evaluate model performance

        Args:
            X_test: Test features
            y_test: Test labels
            dataset_name: Name of dataset for display

        Returns:
            Dictionary of performance metrics
        """
        y_pred_proba = self.predict_proba(X_test)
        y_pred = (y_pred_proba >= self.threshold).astype(int)

        # Calculate metrics
        metrics = {
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }

        # Print results
        print(f"\n{dataset_name} Set Metrics (threshold={self.threshold}):")
        print(f"ROC-AUC Score: {metrics['roc_auc']:.3f}")
        print(f"Precision: {metrics['precision']:.3f}")
        print(f"Recall: {metrics['recall']:.3f}")
        print(f"F1 Score: {metrics['f1']:.3f}")

        print(f"\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(f"                Predicted")
        print(f"                No Fail  |  Fail")
        print(f"Actual No Fail:  {cm[0][0]:6d}  | {cm[0][1]:6d}")
        print(f"Actual Fail:     {cm[1][0]:6d}  | {cm[1][1]:6d}")

        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['No Failure', 'Failure'], zero_division=0))

        return metrics

    def optimize_threshold(self,
                          X_val: pd.DataFrame,
                          y_val: pd.Series,
                          metric: str = 'f1') -> float:
        """
        Optimize decision threshold for best performance

        Args:
            X_val: Validation features
            y_val: Validation labels
            metric: Metric to optimize ('f1', 'precision', 'recall')

        Returns:
            Optimal threshold
        """
        print(f"Optimizing threshold for best {metric}...")

        y_pred_proba = self.predict_proba(X_val)

        # Try different thresholds
        thresholds = np.arange(0.1, 0.9, 0.05)
        best_score = 0
        best_threshold = 0.5

        for threshold in thresholds:
            y_pred = (y_pred_proba >= threshold).astype(int)

            if metric == 'f1':
                score = f1_score(y_val, y_pred, zero_division=0)
            elif metric == 'precision':
                score = precision_score(y_val, y_pred, zero_division=0)
            elif metric == 'recall':
                score = recall_score(y_val, y_pred, zero_division=0)
            else:
                raise ValueError(f"Unknown metric: {metric}")

            if score > best_score:
                best_score = score
                best_threshold = threshold

        print(f"Optimal threshold: {best_threshold:.2f} (score: {best_score:.3f})")
        self.threshold = best_threshold

        return best_threshold

    def _print_feature_importance(self, top_n: int = 15):
        """Print top N most important features"""
        if self.model_type != 'random_forest':
            return

        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        print(f"\nTop {top_n} Most Important Features:")
        print("=" * 60)
        for idx, row in feature_importance.head(top_n).iterrows():
            print(f"{row['feature']:40s} {row['importance']:6.4f}")

    def cross_validate(self,
                      X: pd.DataFrame,
                      y: pd.Series,
                      cv: int = 5) -> Dict:
        """
        Perform cross-validation

        Args:
            X: Features
            y: Labels
            cv: Number of folds

        Returns:
            Dictionary of cross-validation scores
        """
        print(f"Performing {cv}-fold cross-validation...")

        # Use StratifiedKFold to maintain class distribution
        skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Perform cross-validation
        roc_auc_scores = cross_val_score(
            self.model,
            X_scaled,
            y,
            cv=skf,
            scoring='roc_auc',
            n_jobs=-1
        )

        results = {
            'mean_roc_auc': roc_auc_scores.mean(),
            'std_roc_auc': roc_auc_scores.std(),
            'fold_scores': roc_auc_scores.tolist()
        }

        print(f"Cross-validation ROC-AUC: {results['mean_roc_auc']:.3f} (+/- {results['std_roc_auc']:.3f})")

        return results

    def save(self, filepath: str = 'ml/models/failure_prediction_model.pkl'):
        """
        Save trained model to disk

        Args:
            filepath: Path to save model
        """
        if self.model is None:
            raise ValueError("No model to save. Train first.")

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'threshold': self.threshold,
            'model_type': self.model_type,
            'training_date': self.training_date,
            'training_metrics': self.training_metrics
        }

        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")

    @classmethod
    def load(cls, filepath: str = 'ml/models/failure_prediction_model.pkl') -> 'FailurePredictionModel':
        """
        Load trained model from disk

        Args:
            filepath: Path to model file

        Returns:
            Loaded FailurePredictionModel instance
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")

        model_data = joblib.load(filepath)

        instance = cls(model_type=model_data['model_type'])
        instance.model = model_data['model']
        instance.scaler = model_data['scaler']
        instance.feature_columns = model_data['feature_columns']
        instance.threshold = model_data['threshold']
        instance.training_date = model_data.get('training_date')
        instance.training_metrics = model_data.get('training_metrics', {})

        print(f"Model loaded from {filepath}")
        if instance.training_date:
            print(f"Model trained on: {instance.training_date}")

        return instance


def train_and_evaluate_model(
    features_df: pd.DataFrame,
    feature_columns: List[str],
    test_size: float = 0.2,
    val_size: float = 0.1
) -> FailurePredictionModel:
    """
    Complete training pipeline with train/val/test split

    Args:
        features_df: DataFrame with features and target
        feature_columns: List of feature column names
        test_size: Proportion for test set
        val_size: Proportion for validation set

    Returns:
        Trained FailurePredictionModel
    """
    print("=" * 80)
    print("FAILURE PREDICTION MODEL TRAINING PIPELINE")
    print("=" * 80)

    # Separate features and target
    X = features_df[feature_columns]
    y = features_df['failure_in_next_30_days']

    # First split: separate test set
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y,
        test_size=test_size,
        stratify=y,
        random_state=42
    )

    # Second split: separate validation set from remaining data
    val_ratio = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp,
        test_size=val_ratio,
        stratify=y_temp,
        random_state=42
    )

    print(f"\nDataset split:")
    print(f"Training set: {len(X_train)} samples ({len(X_train)/len(X)*100:.1f}%)")
    print(f"Validation set: {len(X_val)} samples ({len(X_val)/len(X)*100:.1f}%)")
    print(f"Test set: {len(X_test)} samples ({len(X_test)/len(X)*100:.1f}%)")

    # Train model
    model = FailurePredictionModel(model_type='random_forest')
    model.train(X_train, y_train, X_val, y_val)

    # Optimize threshold on validation set
    model.optimize_threshold(X_val, y_val, metric='f1')

    # Final evaluation on test set
    print("\n" + "=" * 80)
    print("FINAL TEST SET EVALUATION")
    print("=" * 80)
    test_metrics = model.evaluate(X_test, y_test, dataset_name="Test")
    model.training_metrics['test'] = test_metrics

    return model
