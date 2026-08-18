import { ScenarioType, RiskLevel } from '../types/telemetry';

export const SCENARIOS: Array<{
  id: ScenarioType;
  label: string;
  badge: string;
  description: string;
  expectedRisk: string;
}> = [
  {
    id: 'NORMAL',
    label: '1. Normal Baseline',
    badge: 'Baseline',
    description: 'Safe operating conditions with baseline micro-creep and diurnal variations',
    expectedRisk: '🟢 LOW',
  },
  {
    id: 'HEAVY_RAIN',
    label: '2. Heavy Rain Infiltration',
    badge: 'Storm',
    description: 'Rainfall accumulation driving groundwater pore pressure & moderate shear creep',
    expectedRisk: '🟡 MODERATE / 🟠 HIGH',
  },
  {
    id: 'PROGRESSIVE_INSTABILITY',
    label: '3. Progressive Instability',
    badge: 'Creep',
    description: 'Secondary-to-tertiary creep with accelerating shear strain and displacement',
    expectedRisk: '🟠 HIGH / 🔴 CRITICAL',
  },
  {
    id: 'RAPID_DISPLACEMENT',
    label: '4. Rapid Displacement',
    badge: 'Velocity',
    description: 'High-velocity tertiary displacement representing imminent rock mass failure',
    expectedRisk: '🔴 CRITICAL',
  },
  {
    id: 'HIGH_VIBRATION',
    label: '5. High Vibration (Blasting)',
    badge: 'Seismic',
    description: 'Intense dynamic shockwaves from heavy production blasting or seismic shock',
    expectedRisk: '🟠 HIGH',
  },
  {
    id: 'CRITICAL_COMBINED',
    label: '6. Critical Multi-Hazard',
    badge: 'Catastrophic',
    description: 'Compound disaster combining storm infiltration, high pore pressure, and displacement surge',
    expectedRisk: '🔴 CRITICAL (100.0)',
  },
  {
    id: 'SENSOR_FAILURE',
    label: '7. Sensor Failure / Dropout',
    badge: 'Hardware Fault',
    description: 'Hardware malfunction flatlining to zero telemetry with degraded data health',
    expectedRisk: '⚠️ DEGRADED',
  },
  {
    id: 'RECOVERY',
    label: '8. Post-Mitigation Recovery',
    badge: 'Stabilization',
    description: 'Bench stabilization decaying elevated parameters back toward baseline equilibrium',
    expectedRisk: '🟢 LOW (Stabilizing)',
  },
];

export const RISK_LEVEL_CONFIG: Record<
  RiskLevel,
  {
    label: string;
    badgeText: string;
    color: string;
    bgColor: string;
    borderColor: string;
    glowColor: string;
    textColor: string;
  }
> = {
  LOW: {
    label: 'LOW RISK',
    badgeText: '🟢 LOW',
    color: '#10b981', // Emerald 500
    bgColor: 'rgba(16, 185, 129, 0.12)',
    borderColor: 'rgba(16, 185, 129, 0.4)',
    glowColor: 'rgba(16, 185, 129, 0.25)',
    textColor: '#34d399',
  },
  MODERATE: {
    label: 'MODERATE RISK',
    badgeText: '🟡 MODERATE',
    color: '#f59e0b', // Amber 500
    bgColor: 'rgba(245, 158, 11, 0.12)',
    borderColor: 'rgba(245, 158, 11, 0.4)',
    glowColor: 'rgba(245, 158, 11, 0.25)',
    textColor: '#fbbf24',
  },
  HIGH: {
    label: 'HIGH RISK',
    badgeText: '🟠 HIGH',
    color: '#f97316', // Orange 500
    bgColor: 'rgba(249, 115, 22, 0.14)',
    borderColor: 'rgba(249, 115, 22, 0.5)',
    glowColor: 'rgba(249, 115, 22, 0.35)',
    textColor: '#fb923c',
  },
  CRITICAL: {
    label: 'CRITICAL RISK',
    badgeText: '🔴 CRITICAL',
    color: '#ef4444', // Red 500
    bgColor: 'rgba(239, 68, 68, 0.18)',
    borderColor: 'rgba(239, 68, 68, 0.65)',
    glowColor: 'rgba(239, 68, 68, 0.45)',
    textColor: '#f87171',
  },
};

export const SENSOR_METADATA: Record<
  string,
  {
    name: string;
    unit: string;
    normalMin: number;
    normalMax: number;
    description: string;
  }
> = {
  displacement_mm: {
    name: 'Displacement',
    unit: 'mm',
    normalMin: 0,
    normalMax: 10,
    description: 'Slope surface movement from datum',
  },
  strain: {
    name: 'Rock Shear Strain',
    unit: '',
    normalMin: 0,
    normalMax: 0.35,
    description: 'Dimensionless rock mass deformation',
  },
  pore_pressure_kpa: {
    name: 'Pore Water Pressure',
    unit: 'kPa',
    normalMin: 0,
    normalMax: 45,
    description: 'Groundwater hydraulic pressure',
  },
  rainfall_mm: {
    name: 'Precipitation',
    unit: 'mm',
    normalMin: 0,
    normalMax: 20,
    description: 'Surface storm rainfall accumulation',
  },
  temperature_c: {
    name: 'Bench Temperature',
    unit: '°C',
    normalMin: 15,
    normalMax: 40,
    description: 'Ambient slope rock temperature',
  },
  vibration_g: {
    name: 'Dynamic Vibration',
    unit: 'g',
    normalMin: 0,
    normalMax: 0.3,
    description: 'Seismic & blasting ground acceleration',
  },
};
