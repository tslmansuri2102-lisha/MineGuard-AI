/**
 * Mock Telemetry Data Layer
 * Contains initial real-time sensor metrics, multi-parameter time-series history,
 * and geotechnical threshold definitions.
 */

export const TELEMETRY_METRICS_INFO = {
  vibration: {
    id: "vibration",
    name: "Peak Particle Velocity (PPV)",
    shortName: "Vibration",
    unit: "mm/s",
    sensorType: "Triaxial Geophone / Seismograph",
    normalRange: "0.2 - 4.5 mm/s",
    warningThreshold: 8.0,
    criticalThreshold: 15.0,
    description: "Measures ground vibration velocity from bench blasting and micro-seismic events.",
    iconName: "Activity"
  },
  rainfall: {
    id: "rainfall",
    name: "Precipitation Rate & Accumulation",
    shortName: "Rainfall",
    unit: "mm/h",
    sensorType: "Optical Tipping Bucket Pluviometer",
    normalRange: "0.0 - 5.0 mm/h",
    warningThreshold: 18.0,
    criticalThreshold: 35.0,
    description: "Measures precipitation intensity triggering pore pressure surge and soil saturation.",
    iconName: "CloudRain"
  },
  displacement: {
    id: "displacement",
    name: "Subsurface Rock Displacement",
    shortName: "Displacement",
    unit: "mm",
    sensorType: "Multipoint Borehole Extensometer (MPBX)",
    normalRange: "0.1 - 1.8 mm",
    warningThreshold: 3.5,
    criticalThreshold: 6.0,
    description: "Tracks tension crack dilation and shear plane movement along active highwalls.",
    iconName: "MoveDiagonal"
  },
  porePressure: {
    id: "porePressure",
    name: "Piezometer Pore Water Pressure",
    shortName: "Pore Pressure",
    unit: "kPa",
    sensorType: "Vibrating Wire Piezometer",
    normalRange: "45 - 110 kPa",
    warningThreshold: 160.0,
    criticalThreshold: 240.0,
    description: "Monitors hydrostatic pressure within joint planes that weakens rock shear strength.",
    iconName: "Gauge"
  },
  temperature: {
    id: "temperature",
    name: "Ambient & Surface Temperature",
    shortName: "Temperature",
    unit: "°C",
    sensorType: "Infrared Thermopile Pyrometer",
    normalRange: "18.0 - 34.0 °C",
    warningThreshold: 42.0,
    criticalThreshold: 50.0,
    description: "Evaluates freeze-thaw thermal stress and rapid solar expansion on exposed cliff faces.",
    iconName: "Thermometer"
  },
  slopeStability: {
    id: "slopeStability",
    name: "Slope Factor of Safety (FoS)",
    shortName: "Slope Stability",
    unit: "FoS",
    sensorType: "Geotechnical Inclinometer & Radar",
    normalRange: "1.45 - 2.10 FoS",
    warningThreshold: 1.25,
    criticalThreshold: 1.05,
    description: "Calculated structural equilibrium factor. Below 1.0 indicates imminent failure risk.",
    iconName: "ShieldAlert"
  }
};

/** Initial live sensor snapshot (High Risk scenario active) */
export const INITIAL_LIVE_TELEMETRY = {
  vibration: { value: 12.4, status: "HIGH", delta: "+2.8", trend: "up", sparkline: [4.2, 5.1, 4.8, 6.7, 8.4, 10.2, 12.4] },
  rainfall: { value: 26.5, status: "HIGH", delta: "+8.2", trend: "up", sparkline: [2.0, 4.5, 9.0, 14.2, 19.5, 24.1, 26.5] },
  displacement: { value: 4.85, status: "HIGH", delta: "+1.15", trend: "up", sparkline: [1.2, 1.4, 2.1, 2.8, 3.6, 4.2, 4.85] },
  porePressure: { value: 185.0, status: "MODERATE", delta: "+14.0", trend: "up", sparkline: [80, 95, 115, 138, 158, 172, 185] },
  temperature: { value: 29.4, status: "NORMAL", delta: "-0.6", trend: "down", sparkline: [31.2, 31.0, 30.5, 30.1, 29.8, 29.5, 29.4] },
  slopeStability: { value: 1.14, status: "CRITICAL", delta: "-0.18", trend: "down", sparkline: [1.68, 1.55, 1.42, 1.30, 1.22, 1.18, 1.14] }
};

/** Generate multi-point realistic historical timeseries data */
export function generateHistorySeries(pointsCount = 30, scenario = "default") {
  const data = [];
  const now = Date.now();
  const intervalMs = 60 * 1000; // 1 min steps

  for (let i = pointsCount - 1; i >= 0; i--) {
    const timestamp = new Date(now - i * intervalMs);
    const timeLabel = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Progress normalized 0 to 1
    const p = (pointsCount - 1 - i) / (pointsCount - 1);

    let vib = 3.5 + Math.sin(p * 6) * 1.5 + (p > 0.5 ? p * 7.5 : 0) + (Math.random() * 0.8 - 0.4);
    let rain = (p > 0.3 ? (p - 0.3) * 35 : 1.2) + (Math.random() * 1.5);
    let disp = 1.1 + Math.pow(p, 1.8) * 3.8 + (Math.random() * 0.15);
    let pore = 85 + (p > 0.3 ? (p - 0.3) * 140 : 5) + (Math.random() * 4);
    let temp = 30.5 - p * 2.2 + (Math.random() * 0.4);
    let fos = Math.max(1.02, 1.75 - Math.pow(p, 1.5) * 0.65 + (Math.random() * 0.04));
    let risk = Math.min(94, Math.max(12, Math.round(20 + Math.pow(p, 1.6) * 58 + (Math.random() * 3))));

    data.push({
      time: timeLabel,
      fullDate: timestamp.toISOString(),
      vibration: Number(Math.max(0.1, vib).toFixed(2)),
      rainfall: Number(Math.max(0, rain).toFixed(1)),
      displacement: Number(Math.max(0.1, disp).toFixed(2)),
      porePressure: Number(Math.max(40, pore).toFixed(0)),
      temperature: Number(temp.toFixed(1)),
      slopeStability: Number(fos.toFixed(2)),
      riskScore: risk
    });
  }

  return data;
}

export const MOCK_TELEMETRY_HISTORY_24H = generateHistorySeries(24);
export const MOCK_TELEMETRY_HISTORY_1H = generateHistorySeries(12);
export const MOCK_TELEMETRY_HISTORY_7D = generateHistorySeries(28);
