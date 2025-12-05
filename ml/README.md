# Equipment Failure Prediction - Machine Learning Module

## Overview

This module implements a **machine learning-based predictive maintenance system** for the AIT CMMS application. It predicts the probability of equipment failure in the next 30 days using historical maintenance and failure data.

## Features

- **Predictive Failure Model**: Random Forest classifier predicting equipment failure probability
- **Feature Engineering**: Automated extraction of 18+ features from CMMS database
- **Risk Scoring**: Equipment categorized into Low/Medium/High/Critical risk levels
- **UI Integration**: Tkinter-based interface integrated with CMMS application
- **Batch Predictions**: Generate predictions for all equipment at once
- **Risk Reports**: Automated risk assessment reports

## Architecture

```
ml/
├── __init__.py                  # Package initialization
├── feature_engineering.py       # Feature extraction and engineering
├── failure_prediction_model.py  # Model training and evaluation
├── predictor.py                 # Real-time prediction interface
├── train_model.py              # Training script
├── predict.py                  # Prediction script
├── ui_integration.py           # Tkinter UI components
├── models/                     # Saved model files
│   └── failure_prediction_model.pkl
└── README.md                   # This file
```

## Installation

### 1. Install Required Python Packages

```bash
pip install scikit-learn pandas numpy joblib
```

**Required packages:**
- `scikit-learn >= 1.3.0` - Machine learning algorithms
- `pandas >= 2.0.0` - Data manipulation (already installed)
- `numpy >= 1.24.0` - Numerical computing (already installed)
- `joblib >= 1.3.0` - Model serialization

### 2. Verify Installation

```bash
python -c "import sklearn; print(f'scikit-learn {sklearn.__version__}')"
```

## Quick Start

### Step 1: Train the Model

The first time you use this module, you need to train a model on historical data:

```bash
python -m ml.train_model
```

**What this does:**
- Extracts 12 months of historical equipment and failure data
- Creates time-windowed training samples
- Engineers 18+ predictive features
- Trains a Random Forest classifier
- Evaluates model performance
- Saves trained model to `ml/models/failure_prediction_model.pkl`

**Training time:** 2-10 minutes depending on data size

**Expected output:**
```
Training samples: 5000+
Positive samples (failures): 200-500
ROC-AUC Score: 0.75-0.85
Precision: 0.60-0.80
Recall: 0.50-0.70
```

### Step 2: Generate Predictions

Once trained, generate predictions for all equipment:

```bash
python -m ml.predict
```

**What this does:**
- Loads trained model
- Extracts current features for all active equipment
- Generates failure probability for each equipment
- Displays high-risk equipment
- Saves detailed risk report

**Example output:**
```
PREDICTION SUMMARY
Total equipment: 450
Critical risk (>0.7):  12 (2.7%)
High risk (0.4-0.7):   35 (7.8%)
Medium risk (0.2-0.4): 98 (21.8%)
Low risk (<0.2):       305 (67.8%)

HIGH RISK EQUIPMENT
BFM-001  Air Compressor #1    Building A   0.752  Critical
BFM-045  Hydraulic Press      Building B   0.623  High
...
```

### Step 3: Integrate with CMMS UI

Add the ML predictions to your CMMS application menu:

**Option A: Using the helper function (Recommended)**

In `AIT_CMMS_REV3.py`, add this to your `create_menu()` method:

```python
from ml.ui_integration import add_ml_menu_item

# After creating your other menus, add:
add_ml_menu_item(self, menubar, self.conn)
```

This creates an "Analytics" menu with:
- "Failure Risk Predictions" - View all predictions
- "Train Prediction Model" - Retrain the model

**Option B: Manual integration**

```python
from ml.ui_integration import FailurePredictionPanel

# Create menu item
def show_predictions():
    panel = FailurePredictionPanel(self, self.conn)
    panel.show_prediction_window()

analytics_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Analytics", menu=analytics_menu)
analytics_menu.add_command(label="Failure Risk Predictions", command=show_predictions)
```

## How It Works

### Feature Engineering

The model uses **18 engineered features** extracted from the CMMS database:

**PM (Preventive Maintenance) Features:**
- `pm_count_6mo` - Number of PMs completed in last 6 months
- `days_since_last_pm` - Days since last PM
- `pm_compliance_rate` - Actual PMs / Expected PMs (0-1)
- `avg_pm_hours` - Average PM labor hours
- `pm_overdue` - Is PM overdue? (1/0)

**Failure History Features:**
- `failure_count_6mo` - Number of failures in last 6 months
- `days_since_last_failure` - Days since last failure
- `failure_rate_per_month` - Failures per month
- `avg_repair_hours` - Average repair time
- `total_repair_hours_6mo` - Total repair hours
- `avg_failure_severity` - Average failure priority (1-4)

**Equipment Characteristics:**
- `equipment_age_days` - Equipment age in days
- `monthly_pm_flag` - Has monthly PM? (1/0)
- `six_month_pm_flag` - Has 6-month PM? (1/0)
- `annual_pm_flag` - Has annual PM? (1/0)
- `location_encoded` - Location category

**Other:**
- `parts_consumption_6mo` - Parts used in last 6 months
- `pm_compliance_x_failure_rate` - Interaction feature
- `days_since_pm_x_failure_count` - Interaction feature

### Model Training Process

1. **Data Extraction**: Extract historical snapshots every 7 days for past 12 months
2. **Feature Engineering**: Calculate features for each snapshot
3. **Target Labeling**: Label samples where failure occurred in next 30 days
4. **Train/Val/Test Split**: 70% train, 10% validation, 20% test
5. **Model Training**: Random Forest with 200 trees, class weighting for imbalance
6. **Threshold Optimization**: Optimize decision threshold on validation set
7. **Evaluation**: Final evaluation on held-out test set

### Prediction Process

1. **Extract Current Features**: Calculate current state for all equipment
2. **Feature Engineering**: Apply same transformations as training
3. **Model Prediction**: Generate failure probability (0-1)
4. **Risk Categorization**:
   - **Low**: < 0.2 (20% probability)
   - **Medium**: 0.2 - 0.4
   - **High**: 0.4 - 0.7
   - **Critical**: > 0.7 (70%+ probability)
5. **Recommendations**: Generate action items based on risk level

## Usage Examples

### Python API

```python
from ml.predictor import FailurePredictor
from database_utils import DatabaseConnectionPool

# Get database connection
pool = DatabaseConnectionPool()
conn = pool.get_connection()

# Create predictor
predictor = FailurePredictor(conn)

# Predict all equipment
predictions = predictor.predict_all_equipment()

# Get high-risk equipment
high_risk = predictor.get_high_risk_equipment(threshold=0.4)

# Predict specific equipment
result = predictor.predict_equipment('BFM-001')
print(f"Failure probability: {result['failure_probability']:.1%}")
print(f"Risk level: {result['risk_level']}")

# Generate risk report
report = predictor.generate_risk_report(output_file='risk_report.txt')
```

### Training API

```python
from ml.predictor import ModelTrainer
from database_utils import DatabaseConnectionPool

pool = DatabaseConnectionPool()
conn = pool.get_connection()

# Create trainer
trainer = ModelTrainer(conn)

# Train new model
model = trainer.train_new_model(
    lookback_months=12,
    prediction_window_days=30,
    snapshot_interval_days=7
)

# Model is automatically saved to ml/models/failure_prediction_model.pkl
```

## Performance Metrics

### Model Evaluation

The model is evaluated using multiple metrics:

- **ROC-AUC Score**: Overall prediction quality (0.75-0.85 typical)
- **Precision**: When we predict failure, how often is it correct? (60-80%)
- **Recall**: Of all actual failures, how many did we catch? (50-70%)
- **F1 Score**: Harmonic mean of precision and recall

### Expected Performance

With 12 months of historical data:
- **ROC-AUC**: 0.75 - 0.85 (Good to Excellent)
- **Precision**: 0.60 - 0.80 (Good)
- **Recall**: 0.50 - 0.70 (Moderate to Good)

**Note**: Performance improves with more historical data and higher data quality.

## Recommendations by Risk Level

| Risk Level | Probability | Action |
|------------|-------------|--------|
| **Critical** | > 0.7 (70%) | Schedule immediate inspection and PM |
| **High** | 0.4 - 0.7 | Schedule PM within next 7 days |
| **Medium** | 0.2 - 0.4 | Monitor closely, schedule PM within 30 days |
| **Low** | < 0.2 (20%) | Continue normal PM schedule |

## Retraining the Model

The model should be retrained periodically to maintain accuracy:

**Recommended retraining schedule:**
- **Monthly**: If equipment/processes change frequently
- **Quarterly**: Standard recommendation
- **Annually**: Minimum for stable environments

**When to retrain:**
- After 3-6 months of operation
- When new equipment types are added
- When maintenance processes change significantly
- If prediction accuracy degrades

**To retrain:**
```bash
python -m ml.train_model
```

The old model will be overwritten. Consider backing up the old model first.

## Troubleshooting

### "No trained model found"
**Solution**: Train the model first using `python -m ml.train_model`

### "Not enough failure samples"
**Problem**: Less than 30 failures in training data
**Solutions**:
- Increase `lookback_months` (try 18 or 24 months)
- Increase `prediction_window_days` (try 60 or 90 days)
- Wait for more historical data to accumulate

### "ROC-AUC score is low (<0.65)"
**Problem**: Model is not learning patterns well
**Possible causes**:
- Not enough historical data
- Failures are truly random (not predictable from current features)
- Data quality issues
**Solutions**:
- Collect more historical data
- Check data quality (missing values, incorrect dates)
- Consider adding more features

### "High false positive rate"
**Problem**: Predicting failures that don't happen
**Solution**: Increase the threshold (default 0.3, try 0.4 or 0.5)

### "Missing too many actual failures"
**Problem**: Low recall, not catching real failures
**Solution**: Decrease the threshold (try 0.2 or 0.25)

## Technical Details

### Database Queries

The feature engineering module queries these tables:
- `equipment` - Equipment master data
- `pm_completions` - PM history
- `corrective_maintenance` - Failure history
- `cm_parts_requests` - Parts consumption

**Performance**: Queries are optimized with date filters and proper indexing. Typical extraction time: 30-120 seconds for 500 equipment over 12 months.

### Model File

The trained model is saved as a pickle file containing:
- Trained Random Forest classifier
- Feature scaler (StandardScaler)
- Feature column names
- Optimal threshold
- Training metrics

**File size**: 10-50 MB typical

### Memory Requirements

- **Training**: 500 MB - 2 GB RAM
- **Prediction**: 100 MB - 500 MB RAM

Should run fine on any modern computer or server.

## Future Enhancements

Potential improvements for future versions:

1. **More sophisticated models**: XGBoost, Neural Networks
2. **Multi-window predictions**: Predict for 7, 30, 60, 90 days
3. **Failure type classification**: Predict what type of failure (mechanical, electrical, etc.)
4. **Root cause prediction**: Suggest likely failure causes
5. **Remaining Useful Life (RUL)**: Estimate days until failure
6. **Anomaly detection**: Flag unusual equipment behavior
7. **What-if analysis**: "If we skip this PM, what's the risk?"
8. **Cost optimization**: Balance PM cost vs failure risk

## Support

For questions or issues:
1. Check this README
2. Review error messages carefully
3. Check database connection and data availability
4. Verify all dependencies are installed

## Version History

- **v1.0.0** (2025-12-05): Initial release
  - Random Forest failure prediction
  - 18 engineered features
  - Tkinter UI integration
  - Training and prediction scripts

## License

Part of AIT CMMS NEON 2.3 application.
