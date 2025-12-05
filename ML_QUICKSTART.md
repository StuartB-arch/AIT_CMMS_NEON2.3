# Machine Learning Failure Prediction - Quick Start Guide

## What is This?

This ML module predicts which equipment is most likely to fail in the next 30 days, allowing you to take proactive maintenance actions before failures occur.

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Required Packages

```bash
pip install scikit-learn joblib
```

### Step 2: Train Your First Model

```bash
cd /home/user/AIT_CMMS_NEON2.3
python -m ml.train_model
```

**What happens:**
- Analyzes last 12 months of equipment and failure data
- Trains a machine learning model
- Saves model to `ml/models/failure_prediction_model.pkl`
- Takes 2-5 minutes

**Expected output:**
```
Training samples: 3000+
ROC-AUC Score: 0.75-0.85
Model saved successfully!
```

### Step 3: Generate Predictions

```bash
python -m ml.predict
```

**What happens:**
- Loads trained model
- Analyzes all active equipment
- Shows which equipment is at risk
- Generates detailed risk report

**Example output:**
```
HIGH RISK EQUIPMENT
BFM-001  Air Compressor     Prob: 75%  CRITICAL
BFM-045  Hydraulic Press    Prob: 62%  HIGH
```

### Step 4: View in CMMS Application

1. Open AIT_CMMS_REV3.py
2. In the main CMMS application, go to **Analytics → Failure Risk Predictions**
3. View color-coded risk levels for all equipment
4. Export detailed reports

## 📊 Understanding the Results

### Risk Levels

| Level | Probability | Color | Action |
|-------|-------------|-------|--------|
| 🔴 **Critical** | >70% | Red | Inspect immediately, schedule emergency PM |
| 🟠 **High** | 40-70% | Orange | Schedule PM within 7 days |
| 🟡 **Medium** | 20-40% | Yellow | Monitor closely, PM within 30 days |
| 🟢 **Low** | <20% | Green | Continue normal PM schedule |

### What the Probability Means

**75% failure probability** means:
- Based on similar equipment in the past
- With similar PM compliance and failure history
- There's a 75% chance this equipment will fail in the next 30 days

## 🎯 Use Cases

### 1. Daily Operations
Run predictions weekly to identify high-risk equipment:
```bash
python -m ml.predict
```

### 2. Maintenance Planning
Use predictions to prioritize PM scheduling:
- Focus on Critical/High risk equipment first
- Defer Low risk equipment if needed

### 3. Resource Allocation
Allocate technicians to high-risk areas:
- View predictions by location
- Plan parts inventory based on predicted failures

### 4. Management Reports
Generate executive summaries:
```bash
python -m ml.predict
# Creates ml/failure_risk_report.txt
```

## 🔧 Integration with CMMS

### Option A: UI Integration (Recommended)

Add to `AIT_CMMS_REV3.py`:

```python
# At top of file
from ml.ui_integration import add_ml_menu_item

# In create_menu() method
add_ml_menu_item(self, menubar, self.conn)
```

This adds "Analytics" menu with prediction viewer.

### Option B: Python API

```python
from ml.predictor import FailurePredictor

predictor = FailurePredictor(db_connection)

# Get all predictions
predictions = predictor.predict_all_equipment()

# Get high-risk equipment
high_risk = predictor.get_high_risk_equipment(threshold=0.4)

# Predict specific equipment
result = predictor.predict_equipment('BFM-001')
```

## 📈 Improving Model Performance

### Get Better Predictions

1. **More historical data**: Train on 18-24 months instead of 12
   ```python
   # Edit ml/train_model.py
   lookback_months = 24  # Instead of 12
   ```

2. **Retrain regularly**: Retrain every 3-6 months
   ```bash
   python -m ml.train_model
   ```

3. **Complete data**: Ensure PM completions and CM records are up-to-date

4. **Adjust threshold**: If too many false alarms, increase threshold
   ```python
   # In ml/failure_prediction_model.py
   self.threshold = 0.4  # Instead of 0.3
   ```

## ❓ Troubleshooting

### "No trained model found"
**Solution**: Run `python -m ml.train_model` first

### "Not enough failure samples"
**Problem**: Need at least 30 failures for training
**Solution**:
- Wait for more data (if new system)
- Increase lookback period to 18-24 months
- Increase prediction window to 60-90 days

### "Predictions seem random"
**Problem**: Low ROC-AUC score (<0.65)
**Possible causes**:
- Not enough data
- Failures are truly unpredictable
- Missing important features
**Solution**: Collect more data, ensure data quality

### "Too many false alarms"
**Problem**: Predicting failures that don't happen
**Solution**: Increase threshold from 0.3 to 0.4 or 0.5

### "Missing actual failures"
**Problem**: Not catching real failures
**Solution**: Decrease threshold to 0.2 or 0.25

## 📚 Next Steps

1. **Review full documentation**: See `ml/README.md`
2. **Run demo script**: `python -m ml.demo`
3. **Integrate with workflows**: Add to daily/weekly routines
4. **Train your team**: Show maintenance team how to use predictions
5. **Track results**: Monitor if predictions match actual failures

## 🔄 Maintenance Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| Generate predictions | Weekly | `python -m ml.predict` |
| Review high-risk equipment | Daily | Check reports |
| Retrain model | Quarterly | `python -m ml.train_model` |
| Evaluate performance | Monthly | Compare predictions vs actuals |

## 💡 Tips for Success

1. **Start simple**: Use default settings first
2. **Build trust gradually**: Compare predictions with technician intuition
3. **Track accuracy**: Record which predictions were correct
4. **Adjust as needed**: Fine-tune thresholds based on false positive/negative rate
5. **Combine with expertise**: Use ML as a tool, not a replacement for human judgment

## 📞 Support

- Documentation: `ml/README.md`
- Demo: `python -m ml.demo`
- Issues: Check error messages and database connection

---

**Ready to start?** Run:
```bash
pip install scikit-learn joblib
python -m ml.train_model
python -m ml.predict
```

**Questions?** Check `ml/README.md` for detailed documentation.
