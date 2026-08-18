/**
 * MineGuard AI — Resilient WebSocket Telemetry & Risk Stream Hook
 * Manages WebSocket connection to ws://localhost:8000/ws/sensors
 * Implements exponential backoff, malformed protection, and memory-bounded rolling history.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import {
  ConnectionState,
  HistoricalTelemetryPoint,
  NormalizedRiskAssessment,
  PredictionStatus,
  RiskAssessment,
  RiskLevel,
  SensorTelemetryPayload,
  SensorValues,
  UnifiedStreamPayload,
} from '../types/telemetry';
import { normalizeRiskLevel, normalizeStatus, formatTimeOnly } from '../utils/formatting';

const DEFAULT_WS_URL = 'ws://localhost:8000/ws/sensors';
const MAX_HISTORY_POINTS = 50;

const DEFAULT_SENSORS: SensorValues = {
  displacement_mm: 4.2,
  strain: 0.21,
  pore_pressure_kpa: 31.5,
  rainfall_mm: 3.2,
  temperature_c: 28.4,
  vibration_g: 0.18,
};

const DEFAULT_RISK: NormalizedRiskAssessment = {
  score: 0.0,
  level: 'LOW',
  confidence: 0.95,
  status: 'NORMAL',
  factors: [{ feature: 'baseline_stability', impact: 'LOW' }],
  recommended_action: 'Continue normal monitoring.',
};

export function useWebSocket(url = DEFAULT_WS_URL) {
  const [connectionState, setConnectionState] = useState<ConnectionState>('DISCONNECTED');
  const [telemetry, setTelemetry] = useState<SensorTelemetryPayload>({
    mine_id: 'MINE-001',
    zone_id: 'ZONE-003',
    sensor_id: 'SENSOR-003',
    timestamp: new Date().toISOString(),
    sensors: DEFAULT_SENSORS,
  });
 const [risk, setRisk] = useState<NormalizedRiskAssessment>(DEFAULT_RISK);
const [scenario, setScenario] = useState<string>('NORMAL');
const [history, setHistory] = useState<HistoricalTelemetryPoint[]>([]);
  const [messageCount, setMessageCount] = useState<number>(0);
  const [lastError, setLastError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const retryCountRef = useRef<number>(0);
  const isMountedRef = useRef<boolean>(true);

  // Normalize incoming WebSocket payload
  const handlePayload = useCallback((raw: any) => {
    try {
      // 1. Extract telemetry values safely
      const rawTelemetry = raw.telemetry || raw;
      const rawSensors = raw.sensors || rawTelemetry.sensors || {};

      const cleanSensors: SensorValues = {
        displacement_mm: typeof rawSensors.displacement_mm === 'number' ? rawSensors.displacement_mm : 0.0,
        strain: typeof rawSensors.strain === 'number' ? rawSensors.strain : 0.0,
        pore_pressure_kpa: typeof rawSensors.pore_pressure_kpa === 'number' ? rawSensors.pore_pressure_kpa : 0.0,
        rainfall_mm: typeof rawSensors.rainfall_mm === 'number' ? rawSensors.rainfall_mm : 0.0,
        temperature_c: typeof rawSensors.temperature_c === 'number' ? rawSensors.temperature_c : 0.0,
        vibration_g: typeof rawSensors.vibration_g === 'number' ? rawSensors.vibration_g : 0.0,
      };
      const cleanScenario: string = raw.scenario || 'NORMAL';
      const cleanTelemetry: SensorTelemetryPayload = {
        mine_id: raw.mine_id || rawTelemetry.mine_id || 'MINE-001',
        zone_id: raw.zone_id || rawTelemetry.zone_id || 'ZONE-003',
        sensor_id: raw.sensor_id || rawTelemetry.sensor_id || 'SENSOR-003',
        timestamp: raw.timestamp || rawTelemetry.timestamp || new Date().toISOString(),
        sensors: cleanSensors,
      };

      // 2. Extract risk values safely
      const rawRisk: Partial<RiskAssessment> = raw.risk || {};
      const scoreVal = typeof rawRisk.risk_score === 'number' ? rawRisk.risk_score : (typeof rawRisk.score === 'number' ? rawRisk.score : 0.0);
      const levelVal = rawRisk.risk_level || rawRisk.level || 'LOW';
      const cleanLevel: RiskLevel = normalizeRiskLevel(levelVal);
      const cleanStatus: PredictionStatus = normalizeStatus(rawRisk.status);

      const cleanRisk: NormalizedRiskAssessment = {
        score: Math.max(0, Math.min(100, scoreVal)),
        level: cleanLevel,
        confidence: typeof rawRisk.confidence === 'number' ? Math.max(0, Math.min(1, rawRisk.confidence)) : 0.95,
        status: cleanStatus,
        factors: Array.isArray(rawRisk.factors) && rawRisk.factors.length > 0 ? rawRisk.factors : [{ feature: 'baseline_stability', impact: 'LOW' }],
        recommended_action: rawRisk.recommended_action || 'Continue normal monitoring.',
      };

      // 3. Update state
      setTelemetry(cleanTelemetry);
setRisk(cleanRisk);
setScenario(cleanScenario);
setMessageCount((c) => c + 1);

      // 4. Update rolling history bounded to MAX_HISTORY_POINTS
      setHistory((prev) => {
        const point: HistoricalTelemetryPoint = {
          timestamp: cleanTelemetry.timestamp,
          timeLabel: formatTimeOnly(cleanTelemetry.timestamp),
          riskScore: cleanRisk.score,
          displacement_mm: cleanSensors.displacement_mm,
          strain: cleanSensors.strain,
          pore_pressure_kpa: cleanSensors.pore_pressure_kpa,
          rainfall_mm: cleanSensors.rainfall_mm,
          temperature_c: cleanSensors.temperature_c,
          vibration_g: cleanSensors.vibration_g,
          status: cleanStatus,
        };

        const updated = [...prev, point];
        return updated.length > MAX_HISTORY_POINTS ? updated.slice(updated.length - MAX_HISTORY_POINTS) : updated;
      });
    } catch (err) {
      console.warn('[MineGuard WS] Error processing message payload:', err);
    }
  }, []);

  const connect = useCallback(() => {
    if (!isMountedRef.current) return;
    if (wsRef.current && (wsRef.current.readyState === WebSocket.CONNECTING || wsRef.current.readyState === WebSocket.OPEN)) {
      return;
    }

    try {
      setConnectionState((prev) => (prev === 'DISCONNECTED' && retryCountRef.current > 0 ? 'RECONNECTING' : 'RECONNECTING'));
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!isMountedRef.current) return;
        setConnectionState('CONNECTED');
        setLastError(null);
        retryCountRef.current = 0;
      };

      ws.onmessage = (event) => {
        if (!isMountedRef.current) return;
        try {
          const parsed = JSON.parse(event.data);
          handlePayload(parsed);
        } catch (jsonErr) {
          console.warn('[MineGuard WS] Malformed JSON received:', jsonErr);
        }
      };

      ws.onerror = () => {
        if (!isMountedRef.current) return;
        setLastError('WebSocket connection encountered an error');
      };

      ws.onclose = () => {
        if (!isMountedRef.current) return;
        setConnectionState('DISCONNECTED');
        wsRef.current = null;

        // Exponential backoff reconnect: 1s, 2s, 4s, capped at 8s
        const backoffMs = Math.min(1000 * Math.pow(1.5, retryCountRef.current), 8000);
        retryCountRef.current += 1;

        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, backoffMs);
      };
    } catch (e: any) {
      setLastError(e?.message || 'Failed to establish WebSocket connection');
      setConnectionState('DISCONNECTED');
    }
  }, [url, handlePayload]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnectionState('DISCONNECTED');
  }, []);

  useEffect(() => {
    isMountedRef.current = true;
    connect();

    return () => {
      isMountedRef.current = false;
      disconnect();
    };
  }, [connect, disconnect]);

  return {
  connectionState,
  telemetry,
  risk,
  scenario,
  history,
  messageCount,
  lastError,
  reconnect: connect,
};
}
