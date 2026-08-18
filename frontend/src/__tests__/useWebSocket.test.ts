import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useWebSocket } from '../hooks/useWebSocket';

class MockWebSocketInstance {
  url: string;
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onerror: ((event: any) => void) | null = null;
  onclose: (() => void) | null = null;
  readyState = 0; // CONNECTING

  constructor(url: string) {
    this.url = url;
    setTimeout(() => {
      this.readyState = 1; // OPEN
      if (this.onopen) this.onopen();
    }, 5);
  }

  close() {
    this.readyState = 3; // CLOSED
    if (this.onclose) this.onclose();
  }

  send() {}
}

describe('useWebSocket Hook', () => {
  let originalWebSocket: any;

  beforeEach(() => {
    originalWebSocket = global.WebSocket;
    vi.stubGlobal('WebSocket', MockWebSocketInstance);
  });

  afterEach(() => {
    vi.stubGlobal('WebSocket', originalWebSocket);
  });

  it('initializes with default telemetry and connects to WebSocket', async () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws/sensors'));

    expect(result.current.telemetry.mine_id).toBe('MINE-001');
    expect(result.current.risk.level).toBe('LOW');

    await act(async () => {
      await new Promise((r) => setTimeout(r, 20));
    });

    expect(result.current.connectionState).toBe('CONNECTED');
  });

  it('handles incoming valid message payload and updates rolling history', async () => {
    let activeWs: any = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocketInstance {
        constructor(url: string) {
          super(url);
          activeWs = this;
        }
      }
    );

    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws/sensors'));

    await act(async () => {
      await new Promise((r) => setTimeout(r, 20));
    });

    const incomingPayload = {
      mine_id: 'MINE-001',
      zone_id: 'ZONE-003',
      sensor_id: 'SENSOR-003',
      timestamp: '2026-08-16T12:00:00Z',
      sensors: {
        displacement_mm: 15.4,
        strain: 0.45,
        pore_pressure_kpa: 48.0,
        rainfall_mm: 22.0,
        temperature_c: 29.0,
        vibration_g: 0.85,
      },
      risk: {
        score: 65.4,
        level: 'HIGH',
        confidence: 0.95,
        status: 'NORMAL',
        factors: [{ feature: 'displacement_rate', impact: 'HIGH' }],
        recommended_action: 'Restrict access to the affected zone.',
      },
    };

    act(() => {
      if (activeWs && activeWs.onmessage) {
        activeWs.onmessage({ data: JSON.stringify(incomingPayload) });
      }
    });

    expect(result.current.telemetry.sensors.displacement_mm).toBe(15.4);
    expect(result.current.risk.score).toBe(65.4);
    expect(result.current.risk.level).toBe('HIGH');
    expect(result.current.history.length).toBe(1);
    expect(result.current.history[0].riskScore).toBe(65.4);
  });

  it('survives malformed JSON messages without crashing', async () => {
    let activeWs: any = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocketInstance {
        constructor(url: string) {
          super(url);
          activeWs = this;
        }
      }
    );

    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws/sensors'));

    await act(async () => {
      await new Promise((r) => setTimeout(r, 20));
    });

    act(() => {
      if (activeWs && activeWs.onmessage) {
        activeWs.onmessage({ data: 'NON_JSON_CORRUPTED_STRING' });
      }
    });

    // Hook state remains valid and unharmed
    expect(result.current.connectionState).toBe('CONNECTED');
    expect(result.current.telemetry.mine_id).toBe('MINE-001');
  });
});
