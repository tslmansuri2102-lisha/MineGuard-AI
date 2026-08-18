/**
 * MineGuard AI — Simulation Controls & State Hook
 * Manages simulation scenario switching, start, stop, and status polling.
 */

import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import { ScenarioType, SimulationStartRequest, SimulationStatus } from '../types/telemetry';

export function useSimulation() {
  const [status, setStatus] = useState<SimulationStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean>(false);

  // Poll backend health & simulation status periodically
  const fetchStatus = useCallback(async () => {
    try {
      const [healthRes, simStatus] = await Promise.all([
        api.getHealth().catch(() => null),
        api.getSimulationStatus().catch(() => null),
      ]);

      setBackendOnline(healthRes?.status === 'ok');
      if (simStatus) {
        setStatus(simStatus);
        setError(null);
      }
    } catch (err: any) {
      setBackendOnline(false);
      setError(err?.message || 'Backend connection error');
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const startScenario = async (
    scenario: ScenarioType | string,
    interval = 1.0,
    seed: number | null = 42
  ) => {
    setLoading(true);
    setError(null);
    try {
      const req: SimulationStartRequest = {
        scenario,
        interval,
        seed,
        mine_id: 'MINE-001',
        zone_id: 'ZONE-003',
        sensor_id: 'SENSOR-003',
      };
      const newStatus = await api.startSimulation(req);
      setStatus(newStatus);
      setBackendOnline(true);
      return newStatus;
    } catch (err: any) {
      setError(err?.message || 'Failed to start scenario');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const stopSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const newStatus = await api.stopSimulation();
      setStatus(newStatus);
      return newStatus;
    } catch (err: any) {
      setError(err?.message || 'Failed to stop simulation');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    status,
    loading,
    error,
    backendOnline,
    refreshStatus: fetchStatus,
    startScenario,
    stopSimulation,
  };
}
