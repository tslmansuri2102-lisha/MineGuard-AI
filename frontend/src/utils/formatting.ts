/**
 * MineGuard AI — UI Formatting Utilities
 */

import { RiskLevel, PredictionStatus } from '../types/telemetry';

export function formatTimestamp(isoStr?: string): string {
  if (!isoStr) return '--:--:-- UTC';
  try {
    const dt = new Date(isoStr);
    if (isNaN(dt.getTime())) return isoStr;
    return dt.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
  } catch {
    return isoStr;
  }
}

export function formatTimeOnly(isoStr?: string): string {
  if (!isoStr) return '--:--:--';
  try {
    const dt = new Date(isoStr);
    if (isNaN(dt.getTime())) return isoStr;
    return dt.toTimeString().substring(0, 8);
  } catch {
    return isoStr;
  }
}

export function formatNumber(val?: number | null, decimals = 1): string {
  if (val === undefined || val === null || isNaN(val) || !isFinite(val)) {
    return '0.0';
  }
  return val.toFixed(decimals);
}

export function normalizeRiskLevel(level?: string): RiskLevel {
  if (!level) return 'LOW';
  const clean = level.toUpperCase().trim();
  if (clean === 'CRITICAL') return 'CRITICAL';
  if (clean === 'HIGH') return 'HIGH';
  if (clean === 'MODERATE') return 'MODERATE';
  return 'LOW';
}

export function normalizeStatus(status?: string): PredictionStatus {
  if (!status) return 'NORMAL';
  const clean = status.toUpperCase().trim();
  if (clean === 'DEGRADED') return 'DEGRADED';
  if (clean === 'INSUFFICIENT_DATA') return 'INSUFFICIENT_DATA';
  return 'NORMAL';
}

export function formatFeatureName(feature: string): string {
  const map: Record<string, string> = {
    displacement_mm: 'Displacement Magnitude',
    displacement_rate: 'Displacement Velocity',
    displacement_accel: 'Displacement Acceleration',
    pore_pressure_kpa: 'Pore Water Pressure',
    pore_pressure_rate: 'Pore Infiltration Rate',
    rainfall_mm: 'Precipitation Volume',
    rainfall_intensity: 'Rainfall Intensity',
    vibration_g: 'Dynamic Vibration (PGA)',
    vibration_severity: 'Vibration Shock Ratio',
    strain: 'Rock Mass Shear Strain',
    strain_severity: 'Shear Strain Ratio',
    combined_instability_index: 'Compound Instability Index',
    baseline_stability: 'Baseline Operating Equilibrium',
  };
  return map[feature] || feature.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

export function getImpactColor(impact: string): { bg: string; text: string; border: string } {
  const clean = (impact || '').toUpperCase();
  if (clean === 'HIGH') {
    return { bg: 'rgba(239, 68, 68, 0.15)', text: '#f87171', border: 'rgba(239, 68, 68, 0.4)' };
  }
  if (clean === 'MEDIUM') {
    return { bg: 'rgba(245, 158, 11, 0.15)', text: '#fbbf24', border: 'rgba(245, 158, 11, 0.4)' };
  }
  return { bg: 'rgba(16, 185, 129, 0.15)', text: '#34d399', border: 'rgba(16, 185, 129, 0.4)' };
}
