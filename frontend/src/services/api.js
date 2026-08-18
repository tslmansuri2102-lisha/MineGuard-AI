/**
 * MineGuard AI Service Layer
 * 
 * Provides an abstracted API client for interacting with the MineGuard AI backend.
 * Uses environment variable `VITE_API_BASE_URL` when available; seamlessly falls back
 * to the robust client-side mock data layer so the standalone frontend functions completely out-of-the-box.
 */

import { MOCK_ZONES } from '../data/mockZones';
import { 
  INITIAL_LIVE_TELEMETRY, 
  MOCK_TELEMETRY_HISTORY_1H, 
  MOCK_TELEMETRY_HISTORY_24H, 
  MOCK_TELEMETRY_HISTORY_7D,
  TELEMETRY_METRICS_INFO,
  generateHistorySeries
} from '../data/mockTelemetry';
import { MOCK_ALERTS } from '../data/mockAlerts';
import { MOCK_CURRENT_PREDICTION, MOCK_RISK_FACTORS, MOCK_PREDICTION_HISTORY, MOCK_AI_MODEL_INFO } from '../data/mockPredictions';
import { MOCK_SENSORS } from '../data/mockSensors';
import { MOCK_SYSTEM_STATUS } from '../data/mockSystemStatus';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

/**
 * Generic safe fetcher with fallback
 */
async function fetchWithFallback(endpoint, fallbackData, options = {}) {
  try {
    // Only attempt real fetch if custom VITE_API_BASE_URL was explicitly provided
    if (import.meta.env.VITE_API_BASE_URL) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...(options.headers || {})
        }
      });
      clearTimeout(timeoutId);
      if (res.ok) {
        return await res.json();
      }
    }
  } catch {
    // Graceful fallback to mock data on network error or standalone mode
  }
  return fallbackData;
}

export const apiService = {
  getBaseUrl() {
    return API_BASE_URL;
  },

  async testConnection(customUrl = null) {
    const targetUrl = customUrl || API_BASE_URL;
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2500);
      const res = await fetch(`${targetUrl}/health`, { signal: controller.signal });
      clearTimeout(timeoutId);
      return { success: res.ok, status: res.status, url: targetUrl };
    } catch (err) {
      return { success: false, error: err.message, url: targetUrl };
    }
  },

  async getOverview() {
    return fetchWithFallback('/overview', {
      risk: MOCK_CURRENT_PREDICTION,
      telemetry: INITIAL_LIVE_TELEMETRY,
      alerts: MOCK_ALERTS.slice(0, 3),
      criticalZonesCount: MOCK_ZONES.filter(z => z.riskLevel === 'CRITICAL' || z.riskLevel === 'HIGH').length,
      activeAlertsCount: MOCK_ALERTS.filter(a => a.status === 'ACTIVE').length,
      zones: MOCK_ZONES,
      lastSync: new Date().toLocaleTimeString()
    });
  },

  async getTelemetry() {
    return fetchWithFallback('/telemetry/live', INITIAL_LIVE_TELEMETRY);
  },

  async getTelemetryHistory(timeRange = '24H') {
    let history = MOCK_TELEMETRY_HISTORY_24H;
    if (timeRange === '1H') history = MOCK_TELEMETRY_HISTORY_1H;
    if (timeRange === '6H') history = generateHistorySeries(18);
    if (timeRange === '7D') history = MOCK_TELEMETRY_HISTORY_7D;

    return fetchWithFallback(`/telemetry/history?range=${timeRange}`, history);
  },

  async getTelemetryMeta() {
    return TELEMETRY_METRICS_INFO;
  },

  async getAlerts() {
    return fetchWithFallback('/alerts', MOCK_ALERTS);
  },

  async acknowledgeAlert(alertId) {
    return fetchWithFallback(`/alerts/${alertId}/acknowledge`, { success: true, alertId, status: 'ACKNOWLEDGED' }, { method: 'POST' });
  },

  async resolveAlert(alertId) {
    return fetchWithFallback(`/alerts/${alertId}/resolve`, { success: true, alertId, status: 'RESOLVED' }, { method: 'POST' });
  },

  async getRiskAnalysis() {
    return fetchWithFallback('/risk/analysis', {
      currentRisk: MOCK_CURRENT_PREDICTION,
      riskFactors: MOCK_RISK_FACTORS,
      modelInfo: MOCK_AI_MODEL_INFO,
      recentPredictions: MOCK_PREDICTION_HISTORY.slice(0, 5)
    });
  },

  async getMineZones() {
    return fetchWithFallback('/zones', MOCK_ZONES);
  },

  async getSensors() {
    return fetchWithFallback('/sensors', MOCK_SENSORS);
  },

  async getPredictionHistory() {
    return fetchWithFallback('/predictions/history', MOCK_PREDICTION_HISTORY);
  },

  async getSystemStatus() {
    return fetchWithFallback('/system/status', MOCK_SYSTEM_STATUS);
  }
};

export default apiService;
