# MineGuard AI

AI-based rockfall prediction and early-warning decision-support prototype system for open-pit mines.

---

## System Architecture & Phases

- **Phase 0 — Integration Contracts Setup**: Standardized API contract (`API_CONTRACT.md`), Data Dictionary (`docs/ML_DATA_DICTIONARY.md`), and payload specifications.
- **Phase 1 — Dataset Acquisition & Audit**: Acquired and audited 11,033 real-world ground-truth failure records (`data/raw/nasa_global_landslide_catalog.csv`).
- **Phase 2 — ML Data Pipeline & Training**: Built clean data pipeline, feature engineering, data leakage prevention, time-aware split, preprocessor, and Random Forest baseline model (`models/baseline/model.joblib`).
- **Phase 3 — Real-Time Sensor, Simulation, Inference & Risk Engine**: Built canonical telemetry schema (`iot/sensor_schema.py`), deterministic scenario simulator (`simulation/sensor_simulator.py`), rolling temporal feature buffer, real-time ML inference predictor (`inference/predictor.py`), risk fusion engine (`risk_engine/risk_calculator.py`), alert escalation manager (`alerts/alert_manager.py`), and FastAPI REST & WebSocket server (`api/main.py`).

---

## Quickstart & Execution Commands

### 1. Environment Setup
```bash
# Create virtual environment and install dependencies
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pandas numpy scikit-learn joblib scipy fastapi uvicorn pydantic websockets requests httpx
```

### 2. Run All Unit Tests (Phase 2 & Phase 3)
```bash
.\.venv\Scripts\python.exe -m unittest discover tests
```

### 3. Run Phase 2 ML Data Pipeline
```bash
.\.venv\Scripts\python.exe -m ml.run_pipeline
```

### 4. Start Real-Time FastAPI & WebSocket Server
```bash
.\.venv\Scripts\python.exe -m api.main
```
The server will be available at:
- **API Base Path**: `http://localhost:8000/api/v1`
- **Swagger Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/v1/health`
- **WebSocket Feed**: `ws://localhost:8000/ws`

### 5. Run Telemetry Simulator CLI
```bash
# Run NORMAL scenario
.\.venv\Scripts\python.exe -m simulation.sensor_simulator --scenario NORMAL --duration 10 --interval 1.0

# Run CRITICAL_ROCKFALL scenario and post live telemetry to running API
.\.venv\Scripts\python.exe -m simulation.sensor_simulator --scenario CRITICAL_ROCKFALL --duration 10 --interval 0.5 --api-url http://localhost:8000/api/v1/telemetry
```

---

## System Documentation

- [`API_CONTRACT.md`](file:///E:/MineGuard-AI/API_CONTRACT.md) — Base API contract specifications
- [`docs/ML_DATA_DICTIONARY.md`](file:///E:/MineGuard-AI/docs/ML_DATA_DICTIONARY.md) — ML Data dictionary
- [`docs/DATASET_INVENTORY.md`](file:///E:/MineGuard-AI/docs/DATASET_INVENTORY.md) — Dataset inventory
- [`docs/ML_PIPELINE.md`](file:///E:/MineGuard-AI/docs/ML_PIPELINE.md) — Phase 2 ML Data Pipeline technical specification
- [`docs/PHASE3_REALTIME_ARCHITECTURE.md`](file:///E:/MineGuard-AI/docs/PHASE3_REALTIME_ARCHITECTURE.md) — Phase 3 Real-time architecture specification

---

## Safety Disclaimer

MineGuard AI is a decision-support and risk estimation prototype for open-pit mine bench monitoring. Evacuation procedures and bench safety management must always adhere to certified geotechnical engineering regulations.
