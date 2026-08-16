/**
 * MineGuard AI — Alerts Hook
 * Loads historical alerts from REST endpoint and listens for real-time critical events.
 */

import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import { AlertEvent, NormalizedRiskAssessment, SensorTelemetryPayload } from '../types/telemetry';

export function useAlerts(latestRisk?: NormalizedRiskAssessment, latestTelemetry?: SensorTelemetryPayload) {
  const [alerts, setAlerts] = useState<AlertEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getAlertHistory(50);
      setAlerts(data);
      setError(null);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch alert history');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAlerts();
    // Poll alert history periodically (every 5 seconds)
    const interval = setInterval(fetchAlerts, 5000);
    return () => clearInterval(interval);
  }, [fetchAlerts]);

  // When a new HIGH or CRITICAL risk event arrives via WebSocket, ensure alert list is refreshed
  useEffect(() => {
    if (latestRisk && (latestRisk.level === 'HIGH' || latestRisk.level === 'CRITICAL')) {
      fetchAlerts();
    }
  }, [latestRisk?.score, latestRisk?.level, fetchAlerts]);

  return {
    alerts,
    loading,
    error,
    refreshAlerts: fetchAlerts,
  };
}
