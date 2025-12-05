"""
Feature Engineering Module for Failure Prediction
Extracts and engineers features from CMMS database for ML models
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import psycopg2


class FailurePredictionFeatureEngineer:
    """
    Extracts and engineers features for equipment failure prediction

    Creates time-windowed snapshots of equipment state to predict future failures
    """

    def __init__(self, connection):
        """
        Initialize feature engineer

        Args:
            connection: PostgreSQL database connection
        """
        self.conn = connection

    def extract_training_data(self,
                             lookback_months: int = 12,
                             prediction_window_days: int = 30,
                             snapshot_interval_days: int = 7) -> pd.DataFrame:
        """
        Extract historical data for training the failure prediction model

        Creates snapshots of equipment state at regular intervals, with features
        computed from historical data and labels indicating if failure occurred
        in the prediction window.

        Args:
            lookback_months: How many months of history to include
            prediction_window_days: Days into future to predict failures (target window)
            snapshot_interval_days: Days between snapshots

        Returns:
            DataFrame with engineered features and target variable
        """
        print(f"Extracting training data with {lookback_months} months lookback...")
        print(f"Prediction window: {prediction_window_days} days")
        print(f"Snapshot interval: {snapshot_interval_days} days")

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_months * 30)

        # Get all equipment
        equipment_df = self._get_equipment_list()
        print(f"Found {len(equipment_df)} equipment records")

        # Create time snapshots
        snapshots = []
        current_date = start_date

        while current_date < end_date - timedelta(days=prediction_window_days):
            print(f"Processing snapshot: {current_date.date()}")

            for _, equipment in equipment_df.iterrows():
                bfm_no = equipment['bfm_equipment_no']

                # Extract features for this equipment at this point in time
                features = self._extract_features_at_date(
                    bfm_no,
                    current_date,
                    equipment
                )

                # Extract target (did failure occur in prediction window?)
                target = self._extract_target(
                    bfm_no,
                    current_date,
                    prediction_window_days
                )

                # Combine
                snapshot = {
                    'snapshot_date': current_date,
                    'bfm_equipment_no': bfm_no,
                    **features,
                    'failure_in_next_30_days': target
                }

                snapshots.append(snapshot)

            current_date += timedelta(days=snapshot_interval_days)

        df = pd.DataFrame(snapshots)
        print(f"Created {len(df)} training samples")
        print(f"Positive samples (failures): {df['failure_in_next_30_days'].sum()}")
        print(f"Negative samples (no failure): {(df['failure_in_next_30_days'] == 0).sum()}")

        return df

    def _get_equipment_list(self) -> pd.DataFrame:
        """Get list of all equipment"""
        query = """
        SELECT
            bfm_equipment_no,
            description,
            location,
            status,
            monthly_pm,
            six_month_pm,
            annual_pm,
            created_date
        FROM equipment
        WHERE status IN ('Active', 'Run to Failure')
        ORDER BY bfm_equipment_no
        """

        return pd.read_sql(query, self.conn)

    def _extract_features_at_date(self,
                                  bfm_no: str,
                                  snapshot_date: datetime,
                                  equipment_info: pd.Series) -> Dict:
        """
        Extract all features for equipment at a specific date

        Features include:
        - PM compliance metrics
        - Failure history metrics
        - Equipment characteristics
        - Time-based features
        """
        cursor = self.conn.cursor()

        features = {}

        # Equipment characteristics
        features['location'] = equipment_info['location']
        features['monthly_pm_flag'] = int(equipment_info['monthly_pm']) if equipment_info['monthly_pm'] else 0
        features['six_month_pm_flag'] = int(equipment_info['six_month_pm']) if equipment_info['six_month_pm'] else 0
        features['annual_pm_flag'] = int(equipment_info['annual_pm']) if equipment_info['annual_pm'] else 0

        # Equipment age (days since created)
        if equipment_info['created_date']:
            created = equipment_info['created_date']
            if isinstance(created, str):
                created = datetime.strptime(created, '%Y-%m-%d')
            features['equipment_age_days'] = (snapshot_date - created).days
        else:
            features['equipment_age_days'] = 0

        # PM History Features (last 180 days)
        cursor.execute("""
            SELECT
                COUNT(*) as pm_count,
                MAX(completion_date) as last_pm_date,
                AVG(labor_hours + COALESCE(labor_minutes, 0) / 60.0) as avg_pm_hours
            FROM pm_completions
            WHERE bfm_equipment_no = %s
              AND completion_date::date BETWEEN %s AND %s
        """, (bfm_no,
              (snapshot_date - timedelta(days=180)).date(),
              snapshot_date.date()))

        pm_row = cursor.fetchone()
        features['pm_count_6mo'] = pm_row[0] if pm_row[0] else 0
        features['avg_pm_hours'] = float(pm_row[2]) if pm_row[2] else 0.0

        # Days since last PM
        if pm_row[1]:
            last_pm = datetime.strptime(pm_row[1], '%Y-%m-%d') if isinstance(pm_row[1], str) else pm_row[1]
            features['days_since_last_pm'] = (snapshot_date - last_pm).days
        else:
            features['days_since_last_pm'] = 9999  # Never had PM

        # Calculate expected PM count based on PM flags
        expected_pms = (
            (180 / 30) * features['monthly_pm_flag'] +  # ~6 monthly PMs
            (180 / 180) * features['six_month_pm_flag'] +  # 1 six-month PM
            (180 / 365) * features['annual_pm_flag']  # ~0.5 annual PMs
        )

        if expected_pms > 0:
            features['pm_compliance_rate'] = min(features['pm_count_6mo'] / expected_pms, 1.0)
        else:
            features['pm_compliance_rate'] = 0.0

        # Failure History Features (last 180 days)
        cursor.execute("""
            SELECT
                COUNT(*) as failure_count,
                MAX(reported_date) as last_failure_date,
                AVG(labor_hours) as avg_repair_hours,
                SUM(labor_hours) as total_repair_hours,
                AVG(CASE
                    WHEN priority = 'P1' THEN 4
                    WHEN priority = 'P2' THEN 3
                    WHEN priority = 'P3' THEN 2
                    WHEN priority = 'P4' THEN 1
                    ELSE 0
                END) as avg_failure_severity
            FROM corrective_maintenance
            WHERE bfm_equipment_no = %s
              AND reported_date::date BETWEEN %s AND %s
              AND status IN ('Closed', 'Completed')
        """, (bfm_no,
              (snapshot_date - timedelta(days=180)).date(),
              snapshot_date.date()))

        cm_row = cursor.fetchone()
        features['failure_count_6mo'] = cm_row[0] if cm_row[0] else 0
        features['avg_repair_hours'] = float(cm_row[2]) if cm_row[2] else 0.0
        features['total_repair_hours_6mo'] = float(cm_row[3]) if cm_row[3] else 0.0
        features['avg_failure_severity'] = float(cm_row[4]) if cm_row[4] else 0.0

        # Days since last failure
        if cm_row[1]:
            last_failure = datetime.strptime(cm_row[1], '%Y-%m-%d') if isinstance(cm_row[1], str) else cm_row[1]
            features['days_since_last_failure'] = (snapshot_date - last_failure).days
        else:
            features['days_since_last_failure'] = 9999  # Never failed

        # Failure rate (failures per month)
        features['failure_rate_per_month'] = features['failure_count_6mo'] / 6.0

        # PM overdue flag
        features['pm_overdue'] = 1 if features['days_since_last_pm'] > 45 else 0

        # Parts consumption (last 180 days)
        cursor.execute("""
            SELECT COUNT(*) as parts_count
            FROM cm_parts_requests
            WHERE bfm_equipment_no = %s
              AND requested_date::date BETWEEN %s AND %s
        """, (bfm_no,
              (snapshot_date - timedelta(days=180)).date(),
              snapshot_date.date()))

        parts_row = cursor.fetchone()
        features['parts_consumption_6mo'] = parts_row[0] if parts_row[0] else 0

        return features

    def _extract_target(self,
                       bfm_no: str,
                       snapshot_date: datetime,
                       prediction_window_days: int) -> int:
        """
        Extract target variable: did equipment fail in the prediction window?

        Args:
            bfm_no: Equipment number
            snapshot_date: Current snapshot date
            prediction_window_days: Days ahead to check for failures

        Returns:
            1 if failure occurred, 0 otherwise
        """
        cursor = self.conn.cursor()

        future_date = snapshot_date + timedelta(days=prediction_window_days)

        cursor.execute("""
            SELECT COUNT(*) as failure_count
            FROM corrective_maintenance
            WHERE bfm_equipment_no = %s
              AND reported_date::date > %s
              AND reported_date::date <= %s
        """, (bfm_no, snapshot_date.date(), future_date.date()))

        result = cursor.fetchone()
        failure_count = result[0] if result[0] else 0

        return 1 if failure_count > 0 else 0

    def extract_current_features(self) -> pd.DataFrame:
        """
        Extract current features for all active equipment (for prediction)

        Returns:
            DataFrame with current features for all equipment
        """
        print("Extracting current features for prediction...")

        # Get all active equipment
        equipment_df = self._get_equipment_list()

        current_date = datetime.now()
        current_features = []

        for _, equipment in equipment_df.iterrows():
            bfm_no = equipment['bfm_equipment_no']

            features = self._extract_features_at_date(
                bfm_no,
                current_date,
                equipment
            )

            current_features.append({
                'bfm_equipment_no': bfm_no,
                'description': equipment['description'],
                'location': equipment['location'],
                **features
            })

        df = pd.DataFrame(current_features)
        print(f"Extracted features for {len(df)} equipment")

        return df

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply feature engineering transformations

        Args:
            df: Raw features DataFrame

        Returns:
            DataFrame with engineered features
        """
        df = df.copy()

        # Handle missing values
        df['days_since_last_pm'].fillna(9999, inplace=True)
        df['days_since_last_failure'].fillna(9999, inplace=True)
        df['pm_compliance_rate'].fillna(0, inplace=True)
        df['avg_repair_hours'].fillna(0, inplace=True)
        df['total_repair_hours_6mo'].fillna(0, inplace=True)
        df['avg_failure_severity'].fillna(0, inplace=True)

        # Clip values to reasonable ranges
        df['pm_compliance_rate'] = df['pm_compliance_rate'].clip(0, 1)
        df['days_since_last_pm'] = df['days_since_last_pm'].clip(0, 9999)
        df['days_since_last_failure'] = df['days_since_last_failure'].clip(0, 9999)

        # Encode categorical variables
        df['location_encoded'] = pd.Categorical(df['location']).codes

        # Create interaction features
        df['pm_compliance_x_failure_rate'] = df['pm_compliance_rate'] * df['failure_rate_per_month']
        df['days_since_pm_x_failure_count'] = (
            (df['days_since_last_pm'] / 100.0) * df['failure_count_6mo']
        )

        return df

    def get_feature_columns(self) -> List[str]:
        """
        Get list of feature columns to use for training/prediction

        Returns:
            List of feature column names
        """
        return [
            # PM features
            'pm_count_6mo',
            'days_since_last_pm',
            'pm_compliance_rate',
            'avg_pm_hours',
            'pm_overdue',

            # Failure history features
            'failure_count_6mo',
            'days_since_last_failure',
            'failure_rate_per_month',
            'avg_repair_hours',
            'total_repair_hours_6mo',
            'avg_failure_severity',

            # Equipment characteristics
            'equipment_age_days',
            'monthly_pm_flag',
            'six_month_pm_flag',
            'annual_pm_flag',
            'location_encoded',

            # Parts
            'parts_consumption_6mo',

            # Interaction features
            'pm_compliance_x_failure_rate',
            'days_since_pm_x_failure_count'
        ]
