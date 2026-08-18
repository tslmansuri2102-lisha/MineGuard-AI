# 🛡️ MineGuard AI — Frontend Command Center

> **Tagline:** AI-Powered Rockfall Risk & Early Warning System  
> **Target Event:** SIH 2026 Geotechnical Safety Prototype  
> **Tech Stack:** React 18, Vite, Vanilla CSS Design System, Lucide React

---

## 📖 Overview

**MineGuard AI** is a software-based open-pit mine safety platform that analyzes telemetry, AI predictions, geotechnical risk levels, mine zones, and alerts to identify potential rockfall risks before catastrophic highwall failure occurs.

This repository contains the **production-quality Standalone Frontend** designed for direct integration into the `frontend` directory of the MineGuard-AI project.

---

## ✨ Features & Views

1. **Overview Dashboard**: High-impact command center with circular Risk Gauge (0-100%), active hazard tickers, 24H risk trajectories, live sensor pulses, quick map previews, and sector summaries.
2. **Live Monitoring**: Real-time virtual telemetry monitors with animated waveforms, stream playback controls (1x, 2x, 5x), and live anomaly injection (Monsoon storm, Micro-seismic burst, Shear creep).
3. **Risk Analysis**: Explainable AI view with feature importance attribution (SHAP), GNN-XGB model metrics, geotechnical Factor of Safety (FoS) estimation, and recent prediction timelines.
4. **Mine Map (GIS)**: Interactive high-contrast SVG Open-Pit Mine map showing pit boundaries, bench levels (L1-L7), haul roads, sensor nodes, pulsing alert beacons, InSAR displacement heatmap overlays, and the **Geotechnical Zone Inspector** drawer.
5. **Alert Center**: Enterprise alert table with severity tabs (Critical, High, Moderate, Low, Resolved), search, acknowledgment workflows, and step-by-step emergency mitigation action checklists.
6. **Telemetry Deep Dive**: 6-parameter sensor telemetry with 1H, 6H, 24H, 7D multi-axis comparison charts and physical sensor fleet hardware health diagnostics.
7. **Prediction History**: AI inference audit log table with confidence metrics, precursor mechanisms, and simulated CSV audit exports.
8. **System Status**: Infrastructure health grid (Frontend, API Gateway, WebSocket Streamer, ML Inference Node, GIS Engine, Telemetry Broker).
9. **Settings**: Theme customization (Graphite, Midnight, Tactical Obsidian), telemetry sampling frequencies, threshold calibration, and live backend connection tester.

---

## ⚡ Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Start the Vite development server
npm run dev

# 3. Open your browser at
# http://localhost:3000
```

---

## 🔌 Connecting a Real Backend Later

The frontend is architected with a decoupled service layer (`src/services/api.js`) and a mock fallback layer (`src/data/`).

To connect your backend API:
1. Create a `.env` file in the root:
   ```env
   VITE_API_BASE_URL=http://your-backend-domain:8000/api/v1
   ```
2. When the backend is reachable, `apiService` automatically queries real endpoints. If the backend is offline or omitted, the frontend operates seamlessly in **Standalone Demo Mode**.

---

## ⚠️ Safety Notice

MineGuard AI is a decision-support and risk estimation prototype. Mine safety and evacuation decisions must follow certified geotechnical engineering procedures and applicable statutory regulations.
