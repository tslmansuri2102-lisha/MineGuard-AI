/**
 * MineGuard AI — Telemetry, Risk & Alert TypeScript Definitions
 * Strictly matches backend models in backend/models.py and API_CONTRACT.md.
 */

export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';

export type PredictionStatus = 'NORMAL' | 'DEGRADED' | 'INSUFFICIENT_DATA';

export type ScenarioType =
  | 'NORMAL'
  | 'HEAVY_RAIN'
  | 'PROGRESSIVE_INSTABILITY'
  | 'RAPID_DISPLACEMENT'
  | 'HIGH_VIBRATION'
  | 'CRITICAL_COMBINED'
  | 'SENSOR_FAILURE'
  | 'RECOVERY';

export interface SensorValues {
  displacement_mm: number;
  strain: number;
  pore_pressure_kpa: number;
  rainfall_mm: number;
  temperature_c: number;
  vibration_g: number;
}

export interface SensorTelemetryPayload {
  mine_id: string;
  zone_id: string;
  sensor_id: string;
  timestamp: string;
  sensors: SensorValues;
}

export interface RiskFactor {
  feature: string;
  impact: 'HIGH' | 'MEDIUM' | 'LOW' | string;
}

export interface RiskAssessment {
  score: number;
  risk_score?: number;
  level: RiskLevel;
  risk_level?: RiskLevel;
  confidence: number;
  status: PredictionStatus;
  factors: RiskFactor[];
  recommended_action: string;
}

export interface NormalizedRiskAssessment {
  score: number;
  level: RiskLevel;
  confidence: number;
  status: PredictionStatus;
  factors: RiskFactor[];
  recommended_action: string;
}

export interface UnifiedStreamPayload extends SensorTelemetryPayload {
  scenario?: ScenarioType | string;
  telemetry?: SensorTelemetryPayload;
  risk?: RiskAssessment;
}
export interface AlertEvent {
  alert_id: string;
  timestamp: string;
  mine_id: string;
  zone_id: string;
  sensor_id: string;
  risk_level: RiskLevel | string;
  risk_score: number;
  message: string;
  recommended_action: string;
  factors: RiskFactor[];
}

export interface SimulationStatus {
  status: string;
  is_running: boolean;
  mine_id: string;
  zone_id: string;
  sensor_id: string;
  scenario: ScenarioType | string;
  interval_seconds: number;
  reading_count: number;
  latest_reading?: SensorTelemetryPayload | null;
}

export interface SimulationStartRequest {
  mine_id?: string;
  zone_id?: string;
  sensor_id?: string;
  scenario: ScenarioType | string;
  interval?: number;
  seed?: number | null;
}

export interface HealthResponse {
  status: string;
  service: string;
}

export type ConnectionState = 'CONNECTED' | 'RECONNECTING' | 'DISCONNECTED';

export interface HistoricalTelemetryPoint {
  timestamp: string;
  timeLabel: string;
  riskScore: number;
  displacement_mm: number;
  strain: number;
  pore_pressure_kpa: number;
  rainfall_mm: number;
  temperature_c: number;
  vibration_g: number;
  status: PredictionStatus;
}
