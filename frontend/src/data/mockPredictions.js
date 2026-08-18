/**
 * Mock Predictions and AI Inference Engine Data
 * Contains AI model metadata, factor importance, confidence scores, and historical audit logs.
 */

export const MOCK_AI_MODEL_INFO = {
  modelName: "MineGuard Geotechnical Ensemble GNN-XGB",
  version: "v2.4.1-SIH-PROD",
  architecture: "Spatio-Temporal Graph Neural Network + Gradient Boosted Highwall Regressor",
  datasetTrained: "185,000+ Open-Pit Geotechnical Telemetry Hours & Terrestrial LiDAR Surveys",
  lastCalibrated: "2026-08-16 04:00 UTC",
  inferenceLatency: "38 ms",
  f1Score: "0.934",
  rocAuc: "0.968"
};

export const MOCK_CURRENT_PREDICTION = {
  currentRisk: "HIGH",
  riskScore: 72, // out of 100
  predictionStatus: "ELEVATED RISK",
  confidence: "91%",
  hazardType: "Planar Highwall Shear & Rockfall",
  projectedTimeToCritical: "45 - 90 mins",
  affectedPrimaryZone: "Zone A-03 (East Highwall)",
  affectedSecondaryZone: "Zone B-02 (South-West Bench)",
  modelSummary: "Multi-sensor cross-correlation indicates accelerating strain rate combined with high hydraulic head from recent precipitation event."
};

export const MOCK_RISK_FACTORS = [
  {
    factor: "Subsurface Displacement Rate",
    impact: "High impact",
    weight: 38,
    metric: "4.85 mm (+1.15 mm/hr)",
    severity: "CRITICAL",
    contributionText: "Inverse velocity analysis indicates tertiary creep phase along East Highwall shear plane.",
    color: "#EF4444"
  },
  {
    factor: "Cumulative Rainfall Infiltration",
    impact: "High impact",
    weight: 26,
    metric: "26.5 mm/h (78mm / 24h)",
    severity: "HIGH",
    contributionText: "Exceeded 24-hour critical saturation index of 65mm for weathered schist strata.",
    color: "#F97316"
  },
  {
    factor: "Peak Particle Velocity (Vibration)",
    impact: "High impact",
    weight: 21,
    metric: "12.4 mm/s PPV",
    severity: "HIGH",
    contributionText: "Persistent micro-seismic vibrations amplifying joint dilation in Zone A-03 and Zone B-02.",
    color: "#F97316"
  },
  {
    factor: "Piezometer Pore Water Pressure",
    impact: "Moderate impact",
    weight: 15,
    metric: "185.0 kPa (+14 kPa/h)",
    severity: "MODERATE",
    contributionText: "Hydrostatic uplift reducing effective normal stress on bench toe.",
    color: "#F59E0B"
  }
];

export const MOCK_PREDICTION_HISTORY = [
  {
    id: "PRD-2026-904",
    timestamp: "2026-08-17 13:30:00",
    zone: "Zone A-03",
    zoneName: "East Highwall Face",
    risk: "CRITICAL",
    score: 88,
    confidence: "94.2%",
    status: "ACTIVE HAZARD",
    keyTrigger: "Rapid Extensometer Strain + Heavy Rain",
    validation: "Confirmed by Radar Interferometry",
    actionTaken: "Level 3 Evacuation Triggered"
  },
  {
    id: "PRD-2026-903",
    timestamp: "2026-08-17 13:00:00",
    zone: "Zone B-02",
    zoneName: "South-West Transition Bench",
    risk: "HIGH",
    score: 72,
    confidence: "91.0%",
    status: "ELEVATED RISK",
    keyTrigger: "PPV Micro-seismic Surge (12.4 mm/s)",
    validation: "Verified by Geotechnical Engineer",
    actionTaken: "Haul Ramp Speed Restricted"
  },
  {
    id: "PRD-2026-902",
    timestamp: "2026-08-17 12:30:00",
    zone: "Zone A-02",
    zoneName: "North-East Haul Ramp",
    risk: "MODERATE",
    score: 54,
    confidence: "88.4%",
    status: "UNDER MONITORING",
    keyTrigger: "Post-Blasting Transient Shockwave",
    validation: "Stabilized Post-Blast",
    actionTaken: "Visual Inspection Completed"
  },
  {
    id: "PRD-2026-901",
    timestamp: "2026-08-17 12:00:00",
    zone: "Zone C-01",
    zoneName: "South Catchment Wall",
    risk: "MODERATE",
    score: 46,
    confidence: "86.1%",
    status: "STABILIZED",
    keyTrigger: "Runoff Sump Inflow Surge",
    validation: "Drainage Diverted Successfully",
    actionTaken: "Auxiliary Pumps Engaged"
  },
  {
    id: "PRD-2026-900",
    timestamp: "2026-08-17 11:30:00",
    zone: "Zone A-01",
    zoneName: "North Rim Crest",
    risk: "LOW",
    score: 24,
    confidence: "95.8%",
    status: "NORMAL",
    keyTrigger: "Routine Background Baselines",
    validation: "Zero Creep Detected",
    actionTaken: "Routine Shift Logged"
  },
  {
    id: "PRD-2026-899",
    timestamp: "2026-08-17 11:00:00",
    zone: "Zone C-02",
    zoneName: "South-East Waste Rock Dump",
    risk: "LOW",
    score: 28,
    confidence: "96.4%",
    status: "NORMAL",
    keyTrigger: "Settlement Sensor Drift (Negligible)",
    validation: "Dump Slopes Stable",
    actionTaken: "Routine Continuous InSAR Sync"
  },
  {
    id: "PRD-2026-898",
    timestamp: "2026-08-17 10:30:00",
    zone: "Zone B-01",
    zoneName: "Central Pit Floor",
    risk: "LOW",
    score: 16,
    confidence: "97.0%",
    status: "NORMAL",
    keyTrigger: "Water Level Nominal",
    validation: "Dry Pit Floor Confirmed",
    actionTaken: "All Clear Logged"
  }
];
