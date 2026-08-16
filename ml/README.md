# MineGuard AI — ML Pipeline Package (`ml/`)

## 1. Overview

The `ml/` package houses the end-to-end Machine Learning data pipeline, feature engineering modules, data leakage prevention safeguards, preprocessing transformers, baseline model architectures, and evaluation systems for **MineGuard AI Phase 2**.

---

## 2. Directory & Module Structure

```
ml/
├── __init__.py           # Package initializer
├── config.py             # Global paths, constants, feature lists, and risk thresholds
├── utils.py              # Directory management, logging, and JSON serialization
├── data_loader.py        # Safe raw dataset loader
├── validation.py         # Data validation checks & quality reporting
├── target_builder.py     # Binary rockfall target construction
├── feature_engineering.py# Temporal, rainfall, and terrain feature generation
├── leakage.py            # Post-event outcome leakage prevention checks
├── split.py              # Time-aware chronological train/val/test splitting
├── preprocessing.py      # ColumnTransformer preprocessor (fitted strictly on X_train)
├── baseline_model.py     # Balanced Random Forest / Logistic Regression classifier
├── evaluate.py           # Model evaluation (Recall, ROC-AUC, Confusion Matrix, Explainability)
├── run_pipeline.py       # End-to-end pipeline execution orchestrator
└── README.md             # Package documentation
```

---

## 3. How to Run the Pipeline

### Virtual Environment Setup
Ensure the virtual environment dependencies are active. If using the project local `.venv`:

```bash
# Windows PowerShell
.\.venv\Scripts\python.exe -m ml.run_pipeline
```

Alternative entrypoint:
```bash
.\.venv\Scripts\python.exe -m ml.preprocessing
```

---

## 4. Running Unit Tests

To execute the test suite without requiring internet access:

```bash
.\.venv\Scripts\python.exe -m unittest discover tests
```

---

## 5. Generated Artifacts

- **Interim Data**: `data/interim/validated_data.csv`
- **Processed Features**: `data/processed/features.csv`
- **Dataset Splits**: `data/processed/train.csv`, `validation.csv`, `test.csv`
- **Fitted Preprocessor**: `models/baseline/preprocessor.joblib`
- **Trained Model**: `models/baseline/model.joblib`
- **Evaluation Report**: `models/baseline/metrics.json`
- **Pipeline Technical Documentation**: `docs/ML_PIPELINE.md`
