/**
 * MineGuard AI — REST API Client
 * Interfaces strictly with existing FastAPI backend endpoints.
 */

import {
  AlertEvent,
  HealthResponse,
  RiskAssessment,
  SensorTelemetryPayload,
  SimulationStartRequest,
  SimulationStatus,
} from '../types/telemetry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

class ApiClient {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...options.headers,
    };

    try {
      const response = await fetch(url, { ...options, headers });
      if (!response.ok) {
        let errorDetail = `HTTP ${response.status} ${response.statusText}`;
        try {
          const errorData = await response.json();
          errorDetail = errorData.detail || errorDetail;
        } catch {
          // ignore json parse error on non-json body
        }
        throw new Error(errorDetail);
      }
      return (await response.json()) as T;
    } catch (err: unknown) {
      if (err instanceof Error) {
        throw err;
      }
      throw new Error(String(err));
    }
  }

  // System Health
  async getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  // Sensor Telemetry
  async getLatestSensor(): Promise<SensorTelemetryPayload> {
    return this.request<SensorTelemetryPayload>('/api/v1/sensors/latest');
  }

  async getSensorById(mineId: string, zoneId: string, sensorId: string): Promise<SensorTelemetryPayload> {
    return this.request<SensorTelemetryPayload>(`/api/v1/sensors/${mineId}/${zoneId}/${sensorId}`);
  }

  // Simulation Controls
  async getSimulationStatus(): Promise<SimulationStatus> {
    return this.request<SimulationStatus>('/api/v1/simulation/status');
  }

  async startSimulation(params: SimulationStartRequest): Promise<SimulationStatus> {
    return this.request<SimulationStatus>('/api/v1/simulation/start', {
      method: 'POST',
      body: JSON.stringify({
        mine_id: params.mine_id || 'MINE-001',
        zone_id: params.zone_id || 'ZONE-003',
        sensor_id: params.sensor_id || 'SENSOR-003',
        scenario: params.scenario,
        interval: params.interval ?? 1.0,
        seed: params.seed ?? null,
      }),
    });
  }

  async stopSimulation(): Promise<SimulationStatus> {
    return this.request<SimulationStatus>('/api/v1/simulation/stop', {
      method: 'POST',
    });
  }

  // AI Risk Assessment
  async getLatestRisk(): Promise<RiskAssessment> {
    return this.request<RiskAssessment>('/api/v1/risk/latest');
  }

  async getRiskHistory(limit = 50): Promise<RiskAssessment[]> {
    return this.request<RiskAssessment[]>(`/api/v1/risk/history?limit=${limit}`);
  }

  // Geotechnical Alert Center
  async getAlertHistory(limit = 50): Promise<AlertEvent[]> {
    return this.request<AlertEvent[]>(`/api/v1/alerts/history?limit=${limit}`);
  }
}

export const api = new ApiClient();
