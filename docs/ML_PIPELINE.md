# MineGuard AI — Phase 2 ML Data Pipeline Technical Specification

## 1. Objective

The objective of **MineGuard AI Phase 2** is to construct a reproducible, scientifically rigorous Machine Learning data pipeline that transforms audited Phase 1 datasets into a clean, training-ready feature dataset and establishes a baseline hazard classification model.

The pipeline automates:
- Data loading, schema validation, and missing-value imputation
- Binary rockfall target construction based on verified ground-truth events
- Domain-specific feature engineering (temporal, precipitation, and terrain derivatives)
- Enforcing strict data leakage prevention safeguards
- Time-aware chronological train/validation/test splitting
- Fitting feature scalers/encoders strictly on training data
- Training a baseline Random Forest model with balanced class weights
- Model evaluation focusing on hazard recall sensitivity and explainability metrics

---

## 2. Input Datasets

- **Primary Event Catalog**: `data/raw/nasa_global_landslide_catalog.csv` (11,033 raw rows, 31 columns)
- **Primary Geomechanical Telemetry**: USGS Landslide Hazards Monitoring Telemetry (`displacement_mm`, `pore_pressure_kpa`)
- **Supporting GIS & Terrain**: Copernicus 30m DEM / USGS 3DEP (`elevation_m`, `slope_deg`)
- **Supporting Weather**: NOAA GHCN (`rainfall_mm`, `temperature_c`)

---

## 3. Data Validation

The validation module (`ml/validation.py`) enforces the following validation checks prior to processing:
1. **Required Columns Check**: Verifies presence of `event_id`, `event_date`, `latitude`, `longitude`, `landslide_category`.
2. **Coordinate Bounds Check**: Enforces WGS84 range limits (\(-90.0 \le \text{latitude} \le 90.0\) and \(-180.0 \le \text{longitude} \le 180.0\)).
3. **Timestamp Parsability**: Ensures ISO 8601 / standard date formatting across `event_date`.
4. **Physical Boundaries**: Validates that non-negative constraints hold for `rainfall_mm` and `displacement_mm`.
5. **Duplicate Rows**: Scans for exact row duplicates (0 duplicates detected).

Validated records are saved to `data/interim/validated_data.csv`.

---

## 4. Target Definition

The target builder (`ml/target_builder.py`) constructs a binary target column `target_rockfall` from ground-truth failure records:
- **Positive Class (`1`)**: Verified `rock_fall` events (671 samples, 6.15%).
- **Negative Class (`0`)**: Other slope instability events (`landslide`, `mudslide`, `debris_flow`, `complex`, `translational_slide`, `riverbank_collapse`) (10,241 samples, 93.85%).
- **Excluded Records**: Unclassifiable or non-slope events (`snow_avalanche`, `unknown`) (121 records excluded).

### Target Distribution Summary

| Metric | Value |
| :--- | :--- |
| **Total Validated Samples** | 10,912 |
| **Positive Class (Rockfall = 1)** | 671 (6.15%) |
| **Negative Class (Non-Rockfall Slope Failure = 0)** | 10,241 (93.85%) |
| **Class Imbalance Ratio** | 15.26 : 1 |

---

## 5. Feature List & Feature Engineering

The feature engineering module (`ml/feature_engineering.py`) generates 16 core engineered features:

### Numerical Features
1. `latitude`: WGS84 decimal latitude
2. `longitude`: WGS84 decimal longitude
3. `year`: Calendar year extracted from timestamp
4. `month`: Month of year (1 – 12)
5. `day_of_year`: Day of year (1 – 366)
6. `season`: Season indicator (1: Winter, 2: Spring, 3: Summer, 4: Autumn)
7. `is_weekend`: Binary weekend indicator
8. `rainfall_mm`: Numerical precipitation intensity proxy mapped from trigger causes
9. `rainfall_3h_sum`: Estimated 3-hour cumulative precipitation
10. `rainfall_24h_sum`: Estimated 24-hour cumulative precipitation
11. `slope_deg`: Terrain slope angle in degrees (GIS DEM interface, baseline 38°)
12. `elevation_m`: Surface elevation in meters (GIS DEM interface, baseline 250m)
13. `displacement_velocity`: Rate of movement (\(\frac{dD}{dt}\) interface)
14. `displacement_acceleration`: Movement acceleration (\(\frac{d^2D}{dt^2}\) interface)

### Categorical Features
1. `landslide_trigger`: Cause trigger (`downpour`, `continuous_rain`, `rain`, `mining`, `construction`, etc.)
2. `landslide_size`: Scale descriptor (`small`, `medium`, `large`, `very_large`)
3. `landslide_setting`: Geological setting (`mine_slope`, `above_road`, `natural_slope`, etc.)
4. `country_code`: ISO country location code

---

## 6. Data Leakage Prevention

The leakage prevention module (`ml/leakage.py`) automatically strips 16 post-event outcome fields to eliminate temporal look-ahead bias:
- `fatality_count`, `injury_count`, `event_description`, `notes`, `photo_link`, `source_link`, `created_date`, `last_edited_date`, `submitted_date`, `event_import_id`, `event_import_source`, `event_title`, `location_description`, `gazeteer_closest_point`, `gazeteer_distance`, `admin_division_population`.

Automated unit tests verify that no post-event fields are present in `X_train`, `X_val`, or `X_test`.

---

## 7. Split Strategy

To simulate real-world deployment where models predict future slope hazards based on historical data, the dataset uses a **time-aware chronological split** based on `event_date`:
- **Training Set (70%)**: 7,638 samples (Earliest historical period up to early 2016)
- **Validation Set (15%)**: 1,636 samples (Mid 2016 – 2018)
- **Test Set (15%)**: 1,638 samples (Latest period 2018 – Present)

### Split Class Distribution

| Dataset Split | Total Samples | Positive (Rockfall) | Negative | Positive Ratio |
| :--- | :--- | :--- | :--- | :--- |
| **Train** | 7,638 | 199 | 7,439 | 2.61% |
| **Validation** | 1,636 | 255 | 1,381 | 15.59% |
| **Test** | 1,638 | 217 | 1,421 | 13.25% |

---

## 8. Preprocessing Pipeline

The preprocessing module (`ml/preprocessing.py`) constructs a Scikit-Learn `ColumnTransformer`:
- **Numerical Features**: `SimpleImputer(strategy='median')` followed by `StandardScaler()`.
- **Categorical Features**: `SimpleImputer(strategy='constant', fill_value='missing')` followed by `OneHotEncoder(handle_unknown='ignore')`.
- **Fitting Guarantee**: Fitted **ONLY on `X_train`**. `X_val` and `X_test` are transformed using the pre-fitted object.
- **Output Dimensions**: 173 encoded feature dimensions.
- **Artifact Location**: `models/baseline/preprocessor.joblib`

---

## 9. Baseline Model Architecture

The baseline model (`ml/baseline_model.py`) uses a **Random Forest Classifier**:
- `n_estimators`: 100
- `max_depth`: 12
- `min_samples_split`: 5
- `class_weight`: `"balanced"` (Adjusts loss weighting inversely proportional to class frequencies to handle the 15:1 imbalance)
- `random_state`: 42
- **Artifact Location**: `models/baseline/model.joblib`

---

## 10. Evaluation Metrics & Results

Model performance was evaluated on independent Validation and Test datasets. In MineGuard AI, **Hazard Recall (Sensitivity)** is prioritized to minimize false negatives (unpredicted rockfall events).

### Performance Summary

| Metric | Validation Set | Test Set | Target / Threshold |
| :--- | :--- | :--- | :--- |
| **Accuracy** | 74.45% | 68.38% | Baseline |
| **Precision** | 34.36% | 26.52% | Baseline |
| **Hazard Recall (Sensitivity)** | **70.20%** | **78.34%** | **High Priority (> 70%)** |
| **F1-Score** | 46.13% | 39.63% | Baseline |
| **ROC-AUC** | **0.8110** | **0.8019** | Strong Discriminative Power (> 0.80) |

### Test Set Confusion Matrix

```
                      Predicted Negative    Predicted Positive (Rockfall Alert)
Actual Negative:            950 (TN)                   471 (FP)
Actual Rockfall:             47 (FN)                   170 (TP - Correct Warnings)
```

- **True Positives (TP)**: 170 dangerous rockfalls successfully alerted.
- **False Negatives (FN)**: Only 47 missed events (78.34% Hazard Detection Rate).

---

## 11. Top Contributing Features (Explainability)

The model's feature importance weights identify the primary drivers of rockfall risk predictions:

1. `rainfall_mm` / `rainfall_3h_sum` / `rainfall_24h_sum` (Precipitation intensity)
2. `latitude` & `longitude` (Geographical cluster susceptibility)
3. `day_of_year` & `month` (Seasonal freeze-thaw / monsoon timing)
4. `landslide_trigger_downpour` / `continuous_rain` (Severe rainfall triggers)
5. `landslide_setting` (Geological slope environment)

---

## 12. Known Limitations

1. **Synthetic Telemetry Gaps**: The raw historical catalog lacks high-frequency open-pit blast vibration (`vibration_g`) and strain gauge deformation (`strain`), which are generated by the simulation module (`feature/simulation-iot-alerts`).
2. **DEM Resolution**: Micro-bench slope geometry (`slope_deg`) currently uses a regional 38° baseline; local high-resolution drone DEM photogrammetry from `feature/gis-dem-drone` will replace this placeholder in Phase 3.

---

## 13. Future Improvements (Phase 3 & Phase 4)

1. Integrate real-time ESP32 / IoT telemetry streams from `feature/simulation-iot-alerts`.
2. Train advanced XGBoost and LightGBM models with hyperparameter tuning.
3. Compute SHAP (SHapley Additive exPlanations) values for individual prediction explainability.
4. Expose fast inference REST endpoints (`POST /api/v1/predict`) in the backend API.

---

## 14. How to Run the Pipeline & Reproduce Results

To execute the complete Phase 2 pipeline and regenerate all dataset splits, model artifacts, and evaluation reports:

```bash
# Run pipeline from project root
.\.venv\Scripts\python.exe -m ml.run_pipeline
```

To run the automated unit test suite:

```bash
.\.venv\Scripts\python.exe -m unittest discover tests
```
